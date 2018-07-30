# Reading Note of Native Client

Native Client 的论文一共有两篇：
Native Client: A Sandbox for Portable, Untrusted x86 Native Code 和
Adapting Software Fault Isolation to Contemporary CPU Architectures

第一篇论文中， NaCl运行在x86-32位平台上，主要介绍NaCl的Control flow integrity做法。对于数据区的隔离，直接使用Segment 机制。第二篇论文介绍如何将NaCl拓展到x86-64和ARM架构上，主要介绍的是如何在没有段机制的情况下实现data sandbox policy。

## Motivation
在现代的浏览器中，需要能够给用户提供很多很好地图形交互，这样就带来了性能的需求问题。Native Client 希望能够直接在本地运行原生（native）代码，这样能够提供最大的性能保证，但是为了安全，同时要能够提供隔离机制，保证用户的不可信代码不会对机器产生影响。   

## Threat Model
NaCl要能够处理从任何网站来的不可信代码，而NaCl需要能够强制这些代码的行为。如果代码拒绝被conform，则系统拒绝这个代码。

## 系统架构
### 使用场景
Browser 需要解析和运行网页代码（HTML+JavaScript)，然后通过IMC 调用service runtime，service runtime 中运行 NaCl的moudule，也是不可信的代码。

一个X86的intra-process 被叫做Inner Sandbox。 processes之间称作 outer sandbox。
inner sandbox 通过静态分析找到security defects。这种方法不允许自修改代码和overlapping instructions。inner sandbox 可以用来在一个操作系统进程中创建一个 安全的 subdomain，因此可信的service runtime 可以和 inner sandbox 运行在同一个进程中。

## 实现
为了保证Inner Sandbox 的安全，NaCl定义了7个约束（Constraints）
C1. 一旦程序被加载进内存，可执行程序就不可写
C2. binary被静态的链接到起始地址为0，第一个代码段在64K。
C3. 所有的非直接调用使用一个nacljmp 伪指令
C4. binary 使用 至少一个hlt 指令 填充到下一页。
C5. binary中没有指令或伪指令 overlapping 32 byte界限
C6. 所有有效的指令地址都可以通过在load（base）地址开始的反汇编到达。   
C7. 所有的直接调用都只能跳转到合法的目标地址。
为了保证不可信代码的执行不会对系统有side effect，需要解决下面的几个问题：
1. Data integrity
2. Reliable disassembly
3. No unsafe instructions
4. Control flow integrity
Inner Sandbox 的数据完整性由X86的 segment 机制保证。

下面的指令不允许出现在 不可信代码中：
syscall 和int
lds
ret
ret 需要被替代为pop 和jump 指令。

为了解决第四个问题，Control flow integrity， 对于每个direct branch， NaCl 静态的计算目标地址并进行验证。Indirect branch 通过 X86的段机制和 sandbox 指令做到：
首先通过x86段机制保证每个执行的代码段是一个0开始的 4K倍数的地址。 因此每个 indirect branch 都可以被32 整除 对其，因此添加下面的指令：
```
and %eax, 0xffffffe0
jmp *%eax
```

这两条指令就是nacljmp。
###Execption
对于Exceptions, 因为NaCl修改了ss, 导致堆栈不一致，而windows和linux 都需要堆栈传递异常，因此nacl不支持异常

## 开发工具

NaCl 需要对整个工具链进行要求——即只能使用特殊修改后的工具链。

第二篇论文将NaCl拓展到ARM和X86-64位平台上，这里我只关注64位平台。
在NaCl之前，SFI的工作对于data sandbox 持有怀疑态度，因为之前的SFI的工作显示，一般这种工作的开销都很大（25%，被认为不可接受）但是这个工作的开销只有7%（x64)。

在对X64扩展时，对于CFI的做法和之前类似，但是因为没有了Segment机制，因此所有的跳转地址都需要磨平上32位，然后再采取之前的CFI措施。抹平的方法就是将跳转地址放在 eax中，因为eax只有32位，高位自动为零。

因为segment 机制缺失，同时需要对 data 需要额外的处理。 NaCl的处理方式依赖于X64平台巨大的寻址空间，一个4GB的可用空间加上上下个10个4GB的Guard zone，guard zone不映射内存。
然后将R15 拿出来当做RZP，然后初始化为一个4GB对齐的基地址给不可信内存。所有的rip更新必须使用rzp。
为了保证所有的rsp和rbp都包含正确的地址，必须如下处理：
1. rbp可以不经过检查，从RSP中copy来
2. rsp 可以不经过检查从rbp中copy 来
3. 其他的rsp和rbp 修改都需要通过一个 伪指令来进行，伪指令如下：
```
%esp = %eax
lea (%RZP, %rsp, 1), %rsp
```

这样保证rsp的高32位清空。
然后大多数的store 指令依赖于rsp rbp 或者rzp的，都会通过如下方式访问：
```
add $0x00abcdef, %ecx
mov %eax, disp32(%RZP, %rcx, scale)
```
目标地址实际为
```
basereg + indexreg *scale + disp32
```
其中scale 的倍数不超过8，因此上下各需保留9*4GB。整个地址空间需要19*4GB。
