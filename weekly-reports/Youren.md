本周工作进展和下周计划  
2018.10.1~2018.10.14  
本周主要工作如下：  
首先，关于性能测试，目前glibc都是没有被插桩的，因此最终的结果，在对glibc也进行插桩之后，overhead会高于目前的测试结果。  
1. 测试CFI_LABEL（插入noop 指令和control flow guard 以及将memory call 替换成register call）的overhead 大约是在3%左右。  

2. 阅读论文   
[Osr 07]Singularity  
[SP13] SoK:Eternal war in Memory  

下周工作：
对Data access 进行优化，目前写的overhead大约在26%。使用range analysis看能否将其overheard 降至15%左右。

计划还在讨论。性能直接和论文的有效性相关，因此希望11月之前能够确定性能大概的范围。

2018.10.1~2018.10.14
这两周主要的工作包括：

1\. 为了准备开题，阅读了如下方面的论文：

secure storage方向：

Access Pattern disclosure on Searchable Encryption: Ramification, Attack and Mitigation

Generic attacks on secure outsourced database

内核隔离方向：

XFI: Software Guards for System Address Spaces

Software fault isolation with API integrity and multi-principal modules

对插桩后没有任何优化的程序 进行基本测试：

| Target | CFI | CFI+L1 | CFI+L2 | 
| -------- | ----- | ----- | ------ |
| Average | 0.1183125 | 0.36502549 | 0.56537093 |   

Overhead 较高。未来两周主要精力在优化性能上。


2018.9.17~2018.9.30 
这两周主要工作包括：
1.  修改LD中的PLT机制，保证其能够符合我们的机制。
2. 花了3天时间写Linker script，将不同的
3. 给出论文中verifier设计的伪代码，以弄清楚verifier 的功能。
4. 写出论文的编译器架构实现部分和安全分析部分。
5. 测试编译出来的代码在spec 2006上跑的效果。保证插桩后的代码语义没有被修改，运行结果依然一样。同时顺便看看性能如何。

阅读和access pattern 存储相关的论文
Access pattern disclosure on Searchable Encryption: Ramification, Attack and Mitigation.
阅读报告在developer/Youren中。

2018.9.10~2018.9.16 
本周工作

本周二有了security analysis 的第二版本，在第二个版本中，主要改进是：

1\. 之前没有考虑到的Reliable disassembly问题，现在将其加入到security analysis，主要是描述我们如何能够简单而且正确的对binary 进行disassembly。

2\. 整个工作的结构如下：

Reliable disassembly  
  function identication and CFG rebuild
verification
  invalid instruction check
  control transfer verification
  data access verification

这个写法中引入了很多复杂的概念，同时各个section中各个概念交织在一起，非常的混乱难懂。

因此根据第二版本的反馈，这周重写了一遍security analysis，重写的重点主要是：

1\. 从验证的方法上，希望进一步简化各个section，将一些不需要的复杂的概念去除掉。

2\. 将各个section中用到的概念简化之后，希望各个section都是完全正交的，同时给出每个section 中的伪代码。

下周任务：   
现在第三版本，希望能够达到三个目标：很难，有用，清楚

我们做的每个东西都是有难度的

我们的解决办法是有效的

最后，我们为什么这么做能够说清楚。

洪亮：

上周工作：载入和运行一个Hello World程序（不依赖于libc，直接调用syscall）。为此，完成下面的子任务：

1\. 运行一个创建好的Process Image；

2\. 实现用户态和内核态的切换（即支持syscall）；

3\. 实现write和exit的syscall。

下周目标：实现spawn、open、read、write、close、brk和mmap等syscall

本月目标：移植部分libc以支持一个用C编写的最简单的shell

2018.9.3~2018.9.9 
本周编写 系统的安全分析给出新的威胁模型：
我们不信任compiler ，系统的可信代码基为library OS 和 verifier。verifier 在检查加载的binary的时候确保以下7点：

C1. All prefix of LABELs is at the start of instructions
C2. All reachable code in binary is verified.
C3. Direct call with static target, the target is marked with a LABEL.
C4. A well-formed control flow guard is before every indirect control flow transfer immediately and they are in one basic block
C5. The CFI_LABEL of one code domain will never appear at other code domain and library OS.
C6. All data access can be statically determined within the corresponding range.
C7. Forbidden instructions is not appear at binary like MPX related or indirect instruction with memory operand

Theorem 1： No control flow guard can be bypassed
C1 and C2 imply all the code and LABELs are considered.
C3 and C4 ensure both jump and call can’t jump into middle of control flow guard and control flow transfer. 
Theorem 2: Code can’t jump to other code domain or library OS
With T1 and C5, T2 can be ensure.
Theorem3: 
Ensured with C6.

2018.8.27~2018.9.2 


本周主要工作如下：

1. 不同的线程可能共享同一段代码，也就要求代码中不能有绝对地址，因此需要使用PIC寻址。 PIC寻址的binary中，有部分和RIP地址相关。对于不同的进程，我们需要将RIP寻址的地址指向不同的数据段，所以需要在Kernel前面加入fs相对寻址。  
因此通过修改编译器后端，对每一个RIP相关的寻址前面加上fs 偏移量。  

下周主要计划：  
1. 完成range analysis  
  包括任务   
a. 跟踪range的结构体(one day)  
b. Range analysis 分析框架(two day)   
c. 测试效果(one day)  

阅读论文：  
XFI: Software Guards for system address spaces.    
Software fault isolation with API  integrity and multi-principal modules    
Enforcing Kernel Security Invariants with Data Flow     


2018.8.20~2018.8.26


这周主要的时间都是在写PPT上，因此上周定下的计划没有按时完成。同时因为在外无法很好地更新周计划。

总结了一个写slides 的经验，给自己之后做参考。
http://yourenis.me/how-to-make-a-presentation-for-your-paper-as-a-non-native-english-speaker/

已经更新阅读过的论文列表。
https://github.com/openthos/research-analysis/blob/master/developers/Youren/Paperlist.md

>>chyyuu20180828 　本周要读的论文在哪？如没有，我可以指定。

2018.8.12~2018.8.19
1. 阅读Tock 的论文，总结，并交流，关于tock的笔记已上传。
2. 阅读 肖奇学的博士论文并交流
3. 阅读了一篇Range Analysis的论文：
http://laure.gonnord.org/pro/research/ER03_2015/RangeAnalysis.pdf
https://pdfs.semanticscholar.org/83c6/974c1692b930833ed8f8a7f0419a122c1545.pdf
Range Analysis 也是DataFlow 的一种，我们可以得出我们的Range Analysis的Data Flow equation：
inrange(n) = outrange(m) 的交集 ,m是n的前驱节点
Outrange(n) = inrange(n) 并newrange交 killedrange的非  
其中inrange是一个basic block 的输入range，outrange是一个basic block 的输出range。
newrange 是分析过程中新确定的range 范围，killedrange是分析中发现失效的range（例如 从内存中读取数据放入register中）
我们的分析中不包括对指针的alias 和 dependency分析，因为我们不信任内存。

然后为了能够加速分析，论文的作者对SCC（强连通分量，即Loop）单独先分析，之后再综合分析，直接使用之前的强连通分量的结果，可以加速分析速度。我们可以参考这种做法。

>>chyyuu20180828 这是你认为重要的论文吗？如果是，希望有更详细的阅读报告。

4. 阅读Ownership is Theft: Experiences Building an Embedded OS in Rust
了解Rust 的ownership机制，为什么rust 能够保证内存安全。 

>>chyyuu20180828 为什么rust 能够保证内存安全？有进一步的简明描述或详细说明吗？

下周计划：
1. 初步实现Range Analysis的框架
2. 阅读论文：
XFI: Software Guards for system address spaces.
Software fault isolation with API  integrity and multi-principal modules
Enforcing Kernel Security Invariants with Data Flow
了解之前的工作为了隔离内核模块有哪些手段。

>>chyyuu20180828 对于觉得比较重要的论文，这样读论文还不够细致，有进一步的简明描述或详细说明吗？

2018.8.07~2018.8.12
本周主要是将上周周报告中的工作进行测试，调通。
另外希望能够实现一个很强壮的Range analysis，将之前的简单的range analysis 进行升级，能够追踪到每个寄存器大概的值，以此实现更多的优化。
因此本周还阅读了Range Analysis 相关的一些资料。
另外阅读了论文Tock，将在之后上传Tock的总结。

2018.7.30~2018.8.06

本周主要有两个方面的工作：

1\. 修改论文，修改之后洪亮再修改。

2\. 继续编写代码。

修改论文主要是对out of enclave 进行解释，对我上周写的sample code 进行解释。

添加未来的工作，写verifier 和支持JIT。

描写我们的系统中Library OS需要做哪些事情。

其中代码的工作主要有以下3点

1\. 之前的工作报告中有一个伪代码，关于在后端如何扫描一个function。但是那个算法在实现的时候发现有问题。

我们在扫描每个basicblock 的时候，如果将checkedRegs 定义为这个basicblock 的状态的话，那么这个basicblock 的进状态应该等于他前驱basicblock的出状态。但是每个basicblock 都会有多个前驱basicblock。因此，当我们在扫描function的时候，发现需要扫描的basicblock，需要将这个basicblock 的前驱节点的出状态也一起入栈。然后按照前驱节点的出状态进行扫描。

为了方便写程序，在算法中，每个check函数都默认是可以消除的，如果扫描的过程中发现了不可消除的check函数，则标记为不可消除的。对basicblock中任意一趟扫描将check函数标记为不可消除，那之后的lowering check过程就会翻译这个check函数，否则直接讲check函数删除。

新版的伪代码如下：

```c
//if a register is checked, we put it in set
//if a register is changed, remove it from set
set checked = {}
Vector Worklist = {}
FirstBB = function.entrynode();

Worklist.push_back(FirstBB, checked);

while worklist is not empty:
	curBB,checked = worklist.pop();
	Scan(curBB);
	//after scan, checkedRegs has changed
	If(curBB is not visited)
		Worklist.push(curBB.all_successor,checked);

func Scan(BasicBlock BB):
	For(InstrIterator I: BB):
		If(I is checkfunc):
			movI = I.front();
			Checkreg = movl.getoperand()
			If(checkreg not in checked)
				MarkUnremovable(I)
				checked.insert(checkreg)
			else if (movl.getoperand(others) is constant)
				continue;
		Else:
			If (I modified register R ):
				If(R in checked):
					Checked.remove(R)

```

2\. 我们觉得如果优化又在IR层做，又在后端做，对于安全性比较难解释。另外后端无论如何都要写代码（register spill 检测）而register spill的检测过程的代码和后端优化的代码可以用同一个架构，代码类似。 因此我们决定将优化的工作全部放在后端做。但是如果对于每条指令是否是内存操作，是否需要添加check也放在后端，会增加很多的工作量（在后端判断一个指令是否有内存操作，需要判断每条指令的含义，他们的操作数。而IR层将内存操作单独拿出来两条指令load/store，以及memcpy/memmov等操作）所以我将所有的check 的添加依然保留在check层，但是决定所有的优化都在后端做。

上周的工作之一就是将整个工作的架构改成如上所述。

另外，为了更好的进行优化，我们发现在IR层插入check的时候，最好在三个位置都插入：

a. 每一个内存操作前

b. 每一个指针定义之后

c. 函数的参数如果是指针，则在函数开头插入对这个指针的check.

3\. 为了执行后端的优化，很重要的一点就是根据X64的寻址模式，来进行一系列的优化。

x86有较为复杂的地址模式，SegmentReg:Base + [1,2,4,8] \* IndexReg + disp32

为了能够表示这个寻址模式，LLVM对每一个这种形式的内存操作数，跟踪不少于5个的operands。这意味着类似 mov 中load 有以下的形式：

    Index:        0     |    1        2       3           4          5
    Meaning:   DestReg, | BaseReg,  Scale, IndexReg, Displacement Segment
    OperandTy: VirtReg, | VirtReg, UnsImm, VirtReg,   SignExtImm  PhysReg

本质上如下：

    Base + [1,2,4,8] \* IndexReg + Disp32

后端因为直接可以看到寄存器有哪些，因此后端的优化具有比较直观的特性，我们提出如下的优化手段：

如上，X86的寻址本质上是 X + c\*Y + d;（X:basereg, c: Scale, Y: Index, d:Disp32)

如果只有一个变量X，也就是X + d, 我们只要保证X在 region中， d不超过guardzone即可。

如果只有Y变量，c\*Y +d，首先D要在 region中（这个不用check？），其次对Y进行range 分析，如果y\*scale的值不会超过 guardzone，则可以不check，否则都必须将整个数传递进去。

如果x和y都在，那么我们暂时不考虑优化。如果要优化的话，只要Base在region里面，然后IndexReg 具有range，那么也许可以优化。

因此我们只是将X和Y是否check过进行保存。也就是说，我们只check 寄存器，而不是目标地址。

其中第一种优化已经实现。

4\. 为了保证上述所做优化都是对的，我们提出一个invariant：

在每个内存操作之前的任意一个路径，一定有一个check 函数，check 这个内存操作对应的寄存器。

并且在之后的verifier 中对这个invariant进行检查。

另一种优化方法是在Loop中，如果有检查到顺序访问，即每个loop递增一定的偏移量，且偏移量不超过guardzone size，那么可以将这个访问的check 移动到loop 之外。

这个优化正准备做。

之后的工作：

a\. 插CFI\_LABEL

b\. 重新规划优化的代码架构

c\. 对之前总结的优化，还没有实现的进行实现

d\. 总结一下自己的代码中的遍历算法和优化方法，写成文档给人看。

希望这两天可以将所有的优化做完，初步完成这个工作。

2018.7.23~2018.7.29

本周主要工作是讨论APSys 2018的论文reviews，并且进行修改。

review 的意见主要集中在对Security 和Implementation上。

我们主要准备修改的地方包括：

1\. 添加对out-of-enclave bug 的解释，并且写了一个小的sample

2\. 添加对CFI\_LABEL的解释，关于CFI\_LABEL如何生成的，为什么不是sercet.

3\. 为了能够解释关于TCB太大，以及如何支持JIT，我们在最后添加一个future work。描述如何对插桩好的代码进行validate，以及对JIT的支持主要是动态添加的代码验证后再拷贝到用户空间指定位置。

4\. 对于实现，我们添加一个章节，描述更多library OS的内容。

包括syscall 是如何实现的。fork 如何实现，以及context switch 如何实现。

另外为了能够在LLVM后端能够分析寄存器是否是被修改了，对llvm 中的MIR文档进行阅读，了解LLVM后端中对寄存器各种状态的定义。

2018.7.16~2018.7.22  
目前，整个后端的工作分为了三个部分：
1. Control Flow Integrity 的插桩
2. 检查是否要删除一个check的intrinsic（register spill check）
2. 最后是对这个Intrinsic 的翻译（如何翻译可以最高效，最少指令）

一共三个方面的工作，第一个部分之前已经完成。第二个部分进展如下：

将上周遇见的插入Intrinsic 的bug进一步的修复，并且编写register spill check 算法，并且做了一定的优化：
一个小的后端可做的优化是，我们可以根据地址的转换，如果是某个已经check过的寄存器的常数偏移量的地址，那么只要常数偏移量不大，也不对这个load store 进行check。

伪代码如下：
```
//if a register is checked, we put it in set
//if a register is changed, remove it from set
set checked = {}
Vector Worklist = {}
FirstBB = function.entrynode();
 
Worklist.push_back(FirstBB);
 
while worklist is not empty:
	curBB = worklist.pop();
	If(curBB is not visited)
		Worklist.push(curBB.all_successor);
	Scan(curBB);

func Scan(BasicBlock BB):
	For(InstrIterator I: BB):
		If(I is checkfunc):
			movI = I.front();
			Checkreg = movl.getoperand()
			If(checkreg not in checked)
				MarkUnremovable(I)
				Checked.insert(checkreg)
			else if (movl.getoperand(others) is constant)
				continue;
		Else:
			If (I modified register R ):
				If(R in checked):
					Checked.remove(R)

```

目前残留的问题是，如何判断一个指令是否修改了某个寄存器。

另外load/store指令究竟使用的是哪个寄存器作为指针存取数据也是个问题。找到这个寄存器涉及到编译器如何将一个地址的参数传给Intrinsic的。进行了一个初步的观察，如果是O0 编译，那么编译器会将一个地址传递给一个中间寄存器，然后intrinsic check的是中间寄存器。这种情况我们的实现是错误的（没有正确的跟踪到寄存器）。
在O3 编译下，编译器可能会优化掉传参的过程，这个时候我们能够轻易的获得对应的寄存器。但是没有100%的把握编译器一定会优化掉传参过程。因此能否直接使用。还是值得商榷的。

另外，还根据review意见，对APSys的论文进行阅读，提出修改计划，周一和洪亮商量之后，将对应的计划发给shepherd:

review 意见：
1. 详细介绍如何实现的isolation 缩短对intel sgx 的解释，加多对isolation 实现的介绍
传统的SFI有一些局限性，需要描述清楚局限性，以及tradeoff。

2. 威胁模型不现实，CFI太弱，没有详细描述out of enclave bug
3. TCB 的问题，如果能够和其他的方案比较一下更好

总结review：
1. fork 如何实现，以确保不同的CFI_LABEL是不同的
2. review 中说的一些场景下的攻击方式，如何防御，thread model 需要更加详细的定义。具体的攻击方式是针对CFI_LABEL的，使用fork 函数，对child 进行brute-force attack。
如何保证syscall不被abuse
3. 如果解释需要太多的空间，缩减对Intel SGX的解释

我们计划的修改方法：
1. 修改Intruction 中 关于Out of enclave bug 的描述。
1. 在Implementation 中加入关于Libos中如何做dynamic loader以及如何插入CFI，包括dynamic loader，以解释第一个问题
2. 增加部分关于SFI与其他实现的比较，对各种局限性进行描述。

2018.7.09~2018.7.15  
本周工作：  
前述说到，为了实现Register spill check算法，需要将之前的inline asm 转换为intrinsic。  
已经将Data sandbox 的check 成功使用Intrinsic实现，期间遇到了一些bug，记入在专门的文件中。  

发现存在三个问题如下：  
```  
IR的指令是   
checkstore %addr //对addr 地址进行check  
store 100 %addr  // 将100 存入addr指向的内存中  
翻译成机器指令表示为:  
mov 10(rsp) eax //将addr 赋值给eax  
bndcu bnd1 eax  // check eax  
bndcl bnd1 eax  
mov 100 10(rsp) //store  
```  
1. Intrinsic 插入的时候，依然是一个call，因此有传参的过程，依然会将这个参数传递给一个寄存器，而后对寄存器进行检查，这样就多了一条move 指令，同时这个参数也不是真的要检测的register 。   
2. 第二个问题是如果rsp 的偏移量进行访问， 如果这个偏移量是一个常数，是不是也可以不用check，只要这个常数不超过 guardzone的大小。  
3. 第三个问题是bitcast，IR中的bitcase 可能是不同类型的变量，指向同一个地址，因此只需要check 其中一个即可。  

为了解决这三个问题Register spill check 算法实现中采用下面的方法：   
当扫描到一条进行check 的intrinsic 时，读取上一条指令，这条指令的左操作数是真实的目标地址。然后将左操作数中的寄存器入栈。并且在之后的boundcheck 指令中，只对该真实寄存器进行check。  
如果左操作数中的偏移量是常数，且不超过guardzone，则我们可以认为这个数和 其寄存器是等同的。如果下一次遇见对16（rsp），也不进行check.（range不会超过）  

因此上面的机器指令可以翻译为：
bndcu rsp
bndcl rsp
mov ebx 10(rsp)
这种方法的缺陷是虽然少了传参的mov，但是对于eax的占用依然存在（因为这是在寄存器分配之后的工作，寄存器压力无法缓解）

目前下一步工作是，将之前的后端pass重构为三个部分
第一是constraintcheck，通过之前的扫描算法，将可以移除的intrinsic 标记为可以移除。
第二是 checklowering， 将check的 intrinsic 展开，可以移除的移除。
第三是之前的CFIInstrument，对Ret 的CFI插桩在后端进行处理。
预计该工作两天内可以完成。

2018.7.02~2018.7.08
本周工作：
本周先将之前的Control flow integrity 插桩的工作在后端完成，将bug 解决掉，并且通过了spec 2006测试。
而后继续在后端进行 register spill 的工作。
首先是参考如下的文章，学习如何在LLVM中进行 control flow analysis
https://eli.thegreenplace.net/2013/09/16/analyzing-function-cfgs-with-llvm

基于这篇文章，我可以得出结论，基于LLVM的控制流分析是基于LLVM已经组织好的Basic block 结构，使用图算法进行分析。为了实现我们的register spill检测功能，我们需要自己实现算法进行检测。
算法的大概思路如下：
首先这个算法基于观察到，该算法本质上是想找到所有的针对某个register check 函数之间是否有 将该register 的值放入内存中的行为。
首先我们维护一个set，如果一个register 在这个set 中，则证明这个register是被check 过的。

我们基于Function 进行分析，从function的第一个basic block开始扫描，如果找到check函数，且该check函数对应的register 不在set中，则标记该check函数生效，并且将该register放入set中。

扫描完当前的basic block 之后，对该block 标记为visited，接着扫描该basic block 的后继节点（深度优先或者广度优先都可）。当访问到visit 标记的basicblock时，需要继续检查该basicblock，并且停止检查其后继节点。

目前正在实现该算法，需要解决的问题有两个：
上述文章中是基于IR的分析，后端中实现该算法，需要重新找API实现，而API的文档不是很全，需要试错。

其次是如何将在IR层得到的信息，传递到后端。
下述邮件中说，可以使用pass直接传递消息或使用metadata。
http://lists.llvm.org/pipermail/llvm-dev/2014-July/074930.html
之前是用的metadata，但是根据下面的邮件，IR到machine instr没有一对一的关系，目前没有找到很好地办法将在IR插入的metadata 对应的机器指令找到。
http://lists.llvm.org/pipermail/llvm-dev/2013-August/064673.html

2018.6.25~2018.7.01
本周工作：
很遗憾，本周没有实质性的进展
从上周到本周还在进行CFI的查桩。
首先是因为对caller save和callee save register 的理解失误，使用了错误的寄存器，导致程序行为异常。
其次是对LLVM后端代码的API理解错误，当指令选择结束以后，应该使用getOpcode 直接判断指令编码，而不是通过isReture/isBranch判断。因为后者保留的是IR的信息，可能在优化中IR翻译成了不同的机器码。例如尾调用
outfun{
Infun();}
被翻译成
{Call infun
Ret}
优化过后，就是{Jmp infun}

最后在使用BuildMI API 插入指令的时候，因为对LLVM后端的实现不熟，也没有详细的文档，难以参考类似的代码，遇到了各种的问题：
首先是pop指令的插入，使用如下代码插入：
BuildMI(MBB, MI, DL, TII->get(X86::POP64r)).addReg(X86::R10);
BuildMI(MBB, MI, DL, TII->get(X86::POP64r)).addDef(X86::R10).addReg(X86::R10);
BuildMI(MBB, MI, DL, TII->get(X86::POP64r)).addDef(X86::R10);

都会提示将operand插入已经完成的指令的错误。
改成如下形式就可以了
BuildMI(MBB, MI, DL, TII->get(X86::POP64r), X86::R10);

类似的，在进行JMP的插桩时，遇见了类似的问题：

BuildMI(MBB, MI, DL, TII->get(X86::JMP64r)).addReg(X86::R10);

后来发现要在td（target description）文件中找到合适的指令编码，这里找到JMP64r。然后得到对应的操作数以及操作数的顺序，可以参考如下命令：
echo "jmp r10" | llvm-mc -x86-asm-syntax=intel -output-asm-variant=1 -show-inst

目前在进行bndcu的插入的时候，会发生在根据td文件自动生成的代码中，访问第三个操作数的情况。
而bndcu ptr bndcu;应该只有两个操作数。 这一点可以依据上面给出的指令确定。
目前没找到问题的原因，以及解决办法，发送邮件给 llvm-dev mail-list 寻求帮助了。

2018.6.18~2018.6.24
1. 完成后端的代码编写，完成对CFI 相关的正确插桩。
完成情况：依然有bug。

这个链接讨论如何创建一个backend pass 来对load 和store 插桩
http://lists.llvm.org/pipermail/llvm-dev/2017-February/110598.html
 
这个链接里面讨论了如何确定pass 运行的顺序
http://lists.llvm.org/pipermail/llvm-dev/2015-November/092492.html
 
主要是在TargetMachine.cpp 中，依据添加addPass 函数在不同的位置。
 
LLVM Writing a Backend Pass
http://aviral.lab.asu.edu/llvm-writing-a-backend-pass/

PassConfig 的调用逻辑是LLVMTargetMachine.cpp  中的LLVMTargetMachine 调用 new PassConfig， 然后调用PassConfig->addMachinePass.
TargetPassConfig类中 addMachinePass调用各种pass，将IR翻译成 asm code。在addMachinePass中，调用了一系列的hook函数，addpostregalo之类的，由特定的子类override。

因此我们在LLVM后端，addEmitPre2 中添加我们的Pass， 并且进行上周描述中的CFI的插桩。

目前实现仍然有一些问题，可能是对llvm 的后端实现不够了解，因此插桩指令的时候会崩溃，依然在解决中。

2018.6.11~2018.6.17

本周的主要工作依然是学习，并且给出一个对未来工作难点和解决方法的估计：

发现后端是完全不同的一个领域，因此又有很多需要学习的内容，阅读LLVM的两篇文档：
https://llvm.org/docs/CodeGenerator.html
https://llvm.org/docs/WritingAnLLVMBackend.html
其次阅读书籍engineering a compiler 第11章。

那么对我们现在的工作需要解决的问题总结如下：

如果基于源代码编译时插桩（类似NaCl方案），需要的处理的不限于IR：

首先做个试验，找一些C和C++程序进行翻译，看翻译出来的程序什么寻址方法比较常见

之前有一个简单的不正确的实现版本，需要进行如下的处理：

1. 之前有一些优化是不正确的实现，例如对loop中的check插桩的优化
GEP指令的优化（IR中的getelementptr指令，用来寻址数据结构中的成员的地址，或者数组成员的寻址）是不正确的，需要修改。之前的实现没有考虑GEP指令可能的range，直接进行了优化。

另一方面，alloc 的指针可以不进行check，因为是堆栈上顺序增长，不可能直接超过，只需要对rsp的操作插入check 函数。

2. check 函数的正确翻译
这个问题可以
之前的check 函数是用的内联汇编函数实现的，被翻译为机器码的情况如下：
一个函数被翻译如下
```
int *a,c;
boundchecker(a)
c = *a
```

```
movq %rax, %rcx
bndcu %rcx, %bnd1
movq (%rax), %rcx
```

其实在这里是可以直接bndcu %rax 的，但是我们用的是内联汇编函数，所以会有传参的现象，因此多了一条指令。
可以再IR层将 check 函数换成伪指令，在后端进行lowering，判断性能最佳的check插桩。

3. 插入CFI_Label

CFI 正确插桩，之前的插桩没有插入CFI_Label（参考论文的正确插桩方式）。

另外还有一个labeled jump 的小问题：
我们的CFI没有ID，所以如果一个函数中，如果有indirect jump，那么对应的label 的位置，其他的函数也可能跳转过来，因为这里是一个被标识为可以跳转的位置，并没有违反规则。那么从其他函数跳转到这个位置，之前的check 都被跳过了，因此之后的check 都不能被优化掉。

4. register spilling 需要解决

在llvm后端解决，每次spill 的时候，加入check。

5. ret 指令没有正确的插桩
在后端解决 在Epilog 之后处理

6. 无法处理嵌入式汇编
这个问题可以最后处理，优先级最低。。

在后端进行插桩
将汇编lifting 到IR层，然后统一处理。
根据论文中的描述，这种方法有一定的失败的概率。

基于源代码编译时插桩有两种参考做法，例如在IR层做或者在后端做。

陈渝老师的建议：
论文看的不够多，可能会有坑。 比如实现是错误的，或者对问题理解错误。

1. 别人已经做了，我们有什么新的内容？
2. 正确性怎么保证？
3. 如果做了register spilling， 性能会否有较大的损失？

2018.6.4~2018.6.10
学习内容：
这周的主要内容是学习，学习的内容比较杂，总结如下：

看Native Client 论文两篇，了解Native Client的工作。

看UIUC CS526，学些lattice 理论以及在data flow analysis中的应用。
学习了dependence 分析的理论

看了书籍《Engineering a compiler》 第8章，第9章。
书籍的内容和课程的内容相比比较简单直接，而且更和编译器相关，而不是分析。第8章第9章讲了一些编译器会使用的优化方法，这些方法可以和LLVM 中的一些pass对照来看，详细解释了这些优化方法的算法。是不错的学习参考资料，也值得看。但是和UIUC直接介绍SSA-Form相比（更关注于基于SSA-form的优化），Engineering a compiler 会把优化和SSA-Form 的一些生成方法交叉介绍。
目前的学习程度只能保证了解，不能保证熟悉。

看了论文：Superset Disassembly: Statically Rewriting x86 Binaries Without Heuristics
这篇论文是关于如何在没有外界信息帮助（debug信息，不依赖于特定编译器）以及不使用启发式方法来对bianry 反汇编同时重写。可以快速了解如果我们的工作在binary 做会遇见什么困难。


那么对我们现在的工作需要解决的问题总结如下：
如果基于源代码编译时插桩（类似NaCl方案），需要的处理的不限于IR：
之前有一个简单的不正确的实现版本：
1. 之前有一些优化是不正确的实现，例如对loop中的check 插桩的优化
2. register spilling 需要解决
3. ret 指令没有正确的插桩
4. 无法处理嵌入式汇编

如果基于binary 进行处理：
1. 我们需要能够正确的反汇编二进制程序并且静态分析，重建程序的信息，这些应该有一些框架可以使用例如bap，可参考下面的链接[1]。
2. 我们需要能够正确的插桩，需要除了5个问题（参考 superset 论文的notes）

ref:
[1].https://reverseengineering.stackexchange.com/questions/10604/how-to-generate-cfg-from-assembly-instructions?utm_medium=organic&utm_source=google_rich_qa&utm_campaign=google_rich_qa

2018.5.26~2018.6.3
这周的主要工作包括：
1. 测试
在测试的过程中遇到了不少的问题，spec 2006的源代码比较古老，因此在使用LLVM进行测试的时候遇到了不少的问题。
首先是ubuntu 下编译spec，会提示没有可用的tools，需要自己编译tools
因此解压 tools下的源代码文件，然后运行tools/src/buildtools

可能会碰见各种编译错误，可以参考下面三个链接一一解决
https://www.okqubit.net/runspec.html
http://ardorem.blogspot.hk/2015/04/spec-2000-build-error.html
https://blog.csdn.net/koala002/article/details/6362473

llvm 编译spec 2006时，还会有一些小问题需要修复
参考链接：
https://dmz-portal.mips.com/wiki/LLVM_SPEC_2006

C++程序需要指明 clang++ 处理，否则会报链接错误。


发现hmmer的overhead特别的高。使用gprof 分析发现有一个函数占比最多，阅读优化后的llvm IR发现是因为他的C代码中使用了多级指针，翻译成IR以后就是需要反复的从内存中读取指针，再用该指针读取数据。因此我们的三个优化手段都失效。
进一步我们发现这个函数有多个实现，我们在Makefile 中传参-DSLOW，使用了另一个该函数的直接但是绝对性能稍差的实现，让我们的优化效果稍微好些。

2. 在测试过程中发现我们发现一些小bug，进行修复。

下一步工作

长期来看，接下来我的主要工作包括两个部分
1. 继续做优化
现在的优化没有保证安全性，同时也有一些过优化的地方，我们需要找到一个方法能够完整的实现并进行优化。
2. loader
这个loader需要能够将二进制程序加载进Enclave中，将程序块分配到固定的地址空间并且写上CFI_LABEL，保证控制流的完整性。

因此，短期我准备两周系统的学习UIUC CS526课程的内容，完成Project，给之后的工作打下基础。


2018.5.12~2018.5.18
1. 这周阅读相关的论文，了解相关的使用software fault isolation的实现方式和优化手段。
结合我们的工作，给出相应的优化手段。
所有的优化都是针对内存的读写的（即data region 的保护），因为control flow integrity的插桩没有太多优化的余地（每一个call 和ret，jump都必须插桩，无法避免）。

首先我们需要的工作需要分为三个步骤：
第一个步骤是在IR层对所有可能的load store 指令插入对应的check 函数。这个步骤在上周已经完成。
第二个步骤是在IR层进行相应的优化处理，有一些无法确定的优化，则放在第三步进行处理。
第三个步骤是在后端，当寄存器分配完成后，对指令插桩进行检查，如果符合条件，则删除这个插桩。

其中第二个步骤无法确定优化能否apply，主要是因为存在register spill问题。
register spilling 的意思是，在IR层，虚拟寄存器是无限多的，但是实际上硬件上的寄存器是有限的。因此可能存在某个指针因为硬件寄存器不够用而被写回到内存上之后再读出来的情况。这就是register spill。
因为根据CFI的威胁模型，内存是不可信的，被写回内存的指针需要重新检查。因此我们几乎所有的优化都必须到寄存器分配之后才能确定该优化是否可行。

因此我确定的优化手段主要有一下三点（都是基于观察的启发式的优化）：
1. 当一个指针被check过，那么之后使用这个指针进行读取值都不应该再check（如果该指针被写回到内存中后，则需要check）
2. 对数组读写进行优化，gep指令，如果index不超过guard zone，则只对数组基址check 一次（如果数组基址写回内存，则需要重新check）
3. 对loop 进行检查，如果循环次数可以大概确定，则可将检查上提。

以上是三个高层次的检查，为了了解清楚如何使用llvm 实现这些检查，同时还阅读了UIUC course CS526
Iterative Dataflow Framework 123 三节，并对照算法分析llvm 中的 ConstantProp.cpp pass。
http://misailo.web.engr.illinois.edu/courses/526/  

同时我们对之前的代码进行了一定的改正，例如将之前的调用C函数的内联汇编改为调用LLVM的内联汇编。

阅读的论文主要是上周周报中提到的两篇论文。相应的阅读报告也已放在github上。
Combining Control-Flow Integrity and Static Analysis for Efficient and Validated Data Sandboxing
Strato: A Retargetable Framework for Low-Level Inlined-Reference Monitors

洪亮：
负责benchmark 的移植，使用我们的工作对spec 2006中的程序进行插桩，结果大概是51.3%的overhead。

下周计划：
1. 实现初步的优化，将spec 2006中51.3%的overhead 降低到20%
2. 基本完成（90%）论文的内容。

2018.5.5~2018.5.11
这周完成拥有最基础功能的software fault isolation 实现，我们需要对一个应用程序进行两个部分的处理：
1. 数据访问的检查
2. 代码跳转的检查
因此这周完成的llvm pass 主要有以下两个功能：

1. 对所有的load store 指令进行插桩
在IR层，所有对内存的访问都是load 和store 指令
所以我们对load 进行读内存的检查，只能读取可读区域。
对store 进行写内存检查，可以读取该程序所有区域。

2. 对所有的indirect call、indirectbr 和ret指令进行修改

IR层区分direct和indirect call/jump，direct指的是直接对某个函数或labeled的地址进行跳转、调用
indirect是指目标地址来自寄存器或内存，因此我们只需要对indirect进行检查。

因为我们初期只需要模拟性能，在每一个需要检查的跳转指令之前插入一条add指令和一条mpx指令即可。
对于ret 指令，首先使用llvm.returnaddress 获得当前函数的返回值，再插入add 指令和mpx指令以及jmp指令。


下周计划：
1. benchmark spec 2006基准测试现有实现的性能。
2. 研究现有SFI的优化技术，设计我们的SFI优化方案。为此，需要读下面几篇论文：
读论文
Principles and Implementation Techniques of Software-Based Fault Isolation
range/loop analysis
这是一篇关于Software fault isolation的 survey。
Combining Control-Flow Integrity and Static Analysis for Efficient and Validated Data Sandboxing
Strato: A Retargetable Framework for Low-Level Inlined-Reference Monitors
这两篇是Software fault isolation实现优化的文章。

2018.4.29~2018.5.4
1. knowing llvm

What is llvm infrastructure
http://www.aosabook.org/en/llvm.html

llvm getting start （build a llvm from source code)
write a simple Hello world pass
http://releases.llvm.org/5.0.1/docs/WritingAnLLVMPass.html

how to write a useful pass in llvm:
http://llvm.org/docs/ProgrammersManual.html

了解 LLVM 的IR格式：
http://llvm.org/docs/LangRef.html

上述LLVM的文档都是选读略读。

2. knowing compiler background

Reading "Engineering a compiler" chapter 1 and 5.
Knowing what's IR and the consideration when compiler design a IR format.
Knowing what's SSA and why ssa can be use for control flow and data flow analysis.

read below course slides 1 and 2:
http://misailo.web.engr.illinois.edu/courses/526/
了解SSA form 是什么，为什么要用SSA，因为LLVM的IR是SSA 形式的，我们的代码也是对IR修改，未来的优化也是如此。

3. 代码写了一个简单的开头.

阅读memsentry的源代码.
write a pass iterator all store/load instructions.

Plan:
10 May.
write a minimal working implementation that instruments every store/load and call/ret of a sample enclave program，而且链接初始化MPX的库。
需要解决问题：如何在SGX中初始化MPX，sgx程序没有初始化阶段。
target： workable pass

17 May.
Learning control flow and data-flow opt.
compare instrumented programs and uninstrumented programs.
Spec 2006 Benchmark

24 May.
pass with optimization function.能够对指令的插入进行优化。
optimized benchmark data. 优化后的数据。



2018.4.22~2018.4.28
- 本周工作计划1：了解MPX以及 Software fault isolation 内容
- 完成情况：大概了解
- 本周工作计划2：学习llvm
- 完成情况：根据如下课程要求，编译了LLVM，并写了个hello的pass。
http://misailo.web.engr.illinois.edu/courses/526
目前在学习课程的slides，已学习两课。

下周计划：
对llvm有一定的了解，可以给出一个方案做原型系统

2018.4.9~2018.4.22
- 本周工作计划1：学习Rust语言
- 完成情况：大概了解
- 本周工作计划2：看Graphene-sgx 和Scone等Libos的实现方式
- 完成情况：了解
- 本周工作计划2：了解MPX以及 Software fault isolation 内容
- 完成情况：在看论文


2018.4.2~2018.4.8
- 本周工作计划1：开题准备
- 完成情况： 已失败
- 本周工作计划2：休息
- 完成情况：压力太大，休息了几天

下周计划：
想论文能否放宽条件
学习rust sgx sdk。

2018.3.26~2018.4.1
- 本周工作计划1：开题准备
- 完成情况： 已放弃
- 本周工作计划2：论文
- 完成情况：写了个introduction

下周工作计划：
写论文

2018.3.19~2018.3.25
- 本周工作计划1：进行存储工作测试
- 完成情况： 延迟在50 ms左右，仍有优化空间。较其他工作要好。
- 本周工作计划2：写一个文件系统的测试，比较原生文件系统和SGXSDK 中的protected fs 之间性能差距，判断优化空间
- 完成情况：已完成，小block (256B)读写时，性能差距很大，有较大的优化空间

下周工作计划：
专心完成开题报告。
最近事情有点多，可能助教作业的批改进度有点慢。


2018.3.12~2018.3.18
- 本周工作计划1：进行测试
- 完成情况： 延迟在50 ms左右，仍有优化空间。较其他工作要好。
- 本周工作计划2：熟悉switchless现状
- switchless分了几个小点，包括fastcall负责加速系统调用，memory management帮助用户实现自定义内存管理。

下周工作计划：
- 写一些小的bench，测试SGX sdk中文件操作的性能。
- 写开题报告。

2018.3.4~2018.3.11
- 本周工作计划1：完善工作
- 完成情况： coding
直接随机的proxy并不是一个可靠的机制，我重新考虑这个问题，这涉及到网络拓扑结构，我们需要一个网络拓扑结构，满足以下两点：
1. 从任意一个index，通过proxy 都可以到达集群中所有的节点
2. 任意一个proxy都可以到达集群中所有的节点。
总结成一句话，任意一个index，通过任意一个proxy，都可以到达任意节点。
最简单的情况是当集群中机器数量比较小的时候，full connect是可以接受的。
但是当集群中的机器数量很大的时候，full connect 导致traffic 很大，不能scale out，所以我们需要将机器分组，加入集群机器2500台，如下处理：
1. 将2500台机器分成50组，每个组50台。
2. 机器每一次给group中其他机器都发送一个包。保证group内部是full connect的。
3. 机器每一次在每一个group中随机一个机器发送一个包。
这样，每个机器每个round都只需要发送99个包，集群中的流量从full connect的N^2 降低到 2*N^(3/2)
当一个请求过来的时候，index先随机找group A内部一个机器X负责转发，X找到对应目标机器（store）的group，在这个group B中随机选择一个机器Y发送，最后由Y发送给目标机器Store。
因此机器的延迟理论上变成当前的4倍。

在我们的工作中，因为只有10台机器，所以上面的机制不需要实现。代码上，已经将proxy机制改为了full connect。
另外也将Oblivious 的API替换。
并行的工作进行中。
关于匿名通信的文章，从远到近可以看得包括：
sosp 15：vuvuleza
osdi 16：pung
sosp 17： Stadium 和 atom

还有Prifi

相应的论文中都有对之前匿名通信的总结。

2018.2.26~2018.3.4
- 本周工作计划1：完善工作
- 完成情况： coding

准备写oblivious的话，接下来的工作计划可以分为两个部分：
代码：
1. Oblivious中，需要将原来的objectkey，value改成（indexkey，key，value）
2. 并行化处理，对相同的文件的请求需要进行并行化处理，两个put如何并行？
3. 测试，性能优化

论文：
1. 从性能上分析是否需要proxy，还是只需要mixnet。
2. 如何证明安全性，如何证明是oblivious的


2018.1.15~2018.1.19
- 本周工作计划1：code
- 完成情况： coding

现在机器之间的通信已经建立起来了，接下来是写协议

年度总结：
去年想要基于Intel SGX做一些系统相关的研究，为此花了三个月了解SGX，而后6月份开始着手如何隐藏文件的位置保证用户数据的安全。中间反复讨论过很多次，一直到12月有比较成熟的想法。这一个多月一直在实现。因为工作比较复杂，所以实现的很慢，中间还遇见很多坑。
除了具体的事物，去年阅读了很多的论文，学会了如何通过阅读论文快速了解一个领域，相信之后对其他的领域也能快速上手。

明年计划：
想要将手上的工作尽快完结，之后可以协助田洪亮做switchless OS，他在Enclave中关于性能优化有一些新的idea。
之后还没有安排。
约谈：
平时most of time都在122，大部分时间都可以。

2018.1.3~2018.1.12
- 本周工作计划1：code
- 完成情况： coding

- 下周计划工作：
  最近一直在coding

2017.12.25~2018.1.2
- 本周工作计划1：code
- 完成情况： 本来想这周写完的，但是openssl的RSA,PKCS 不太了解，所以写的稍微慢

- 下周计划工作：
  写论文安全分析部分


2017.12.15~2017.12.24  
- 本周工作计划点1：code  
- 完成情况：完成SSL性能测试，和enclave 中执行aes 128 gcm加密速度和普通的运行环境速度类似。对于4k或8K的块加密，速度达到5Gb/s   
- 本周工作计划点2：code 实现论文逻辑的主体  
- 完成情况： 主要分为两个部分，一个部分是非安全部分的负责将数据包通过网络发送出去，或者接受其他机器发送过来的数据。或者读取磁盘和写磁盘。安全部分和非安全部分通过四个lock-free的queue交互。这些代码之前已经写完了。
另一部分是系统的关键流程，在enclave中运行，根据两个DHT和两个 table处理用户的数据。这个部分正在写。  

2017.12.11~2017.12.15
- 本周工作计划点1：code
- 写ssl性能测试。

2017.12.4~2017.12.10
- 本周工作计划点1: write implement
- 完成情况：half，写了整个系统的序列图，定义详细系统的行为。
- 本周工作计划点2：code
- 开始写ssl性能测试。

- 下周计划：
- 想想怎么写implement 中的Oblivious shuffle
- code

2017.11.27~2017.12.3

- 本周工作计划点1: write Design
- 完成情况：finished


- 下周计划：
- 想想怎么写implement 中的Oblivious shuffle
- code

2017.11.19~2017.11.26

- 本周工作计划点1: write problem definiation
- 完成情况：finished
- 本周工作计划点2: Fix two problem: Oblivious response time issue and Crash may not good under virtual node.
- 完成情况：Done.

2017.11.13~2017.11.18

- 本周工作计划点1: write introduction
- 完成情况：finish half
- 本周工作计划点1: reading oblivious paper
- 完成情况：summary will be update later

2017.10.6~2017.11.10

- 本周工作计划点1: Reading oblivious store papers
- 完成情况：figure out some consideration.
- 本周工作计划点1: Finish abstract
- 完成情况：Finished, but not reviewed by kang chen.

- 下周计划：
- Finish design of paper

2017.10.23~2017.11.4

- 本周工作计划点1: Reading paper of sosp 17 and attend it.
- 完成情况：Finished
- 本周工作计划点1: Finished Slides of intel sgx storage
- 完成情况：Finished

- 下周计划：
- Finish project of Intel SGX storage.
- Finish introduction part.

2017.10.16~2017.10.22

- 本周工作计划点1: Understanding Oblivious storage.
- 完成情况：Finished
- 本周工作计划点1: Find the fix of our approach
- 完成情况：Finished

- 下周计划：
- Update the draft of paper.
- Finish project of Intel SGX storage.

2017.10.09~2017.10.13

- 本周工作计划点1: Finish project of Intel SGX storage.
- 完成情况：Finished outside enclave world including rpc server and client, file server. Finished some enclave function. Finished the interface between enclave and host Application.
The problem is I have to understand oblivious store to continue the functionality inside enclave.

- 下周计划：
- Finish project of Intel SGX storage.
- Understanding Oblivious Memory and store.

2017.09.23~2017.09.30

- 本周工作计划点1: Finish project of Intel SGX storage.
- 完成情况：Almost finished outside part. build an RPC server as network connection part.

- 本周工作计划点2:Finish the PHD thesis proposal
- 完成情况：Failed.

- 本周工作计划点3:Finish Compiler PA2 testcase and homework.
- 完成情况：Finished


- 下周计划：
- Finish project of Intel SGX storage.

2017.09.16~2017.09.22

- 本周工作计划点1: Finish project of Intel SGX storage.
- 完成情况：Starting

- 本周工作计划点2:Finish another idea.
- 完成情况：Finished. For more detail, check the proposal repo in github.

- 本周工作计划点3:Finish PA3 of Compiler.
- 完成情况：Finished


- 下周计划：
- Give the final talk of Phd proposal
- Finish project of Intel SGX storage



2017.09.11~2017.09.15

- 本周工作计划点1: give a talk to about proposal of Phd Thesis.
- 完成情况：Finished but one idea missing
Maybe Database is an good idea. We do not need to consider the memory limit, just think about oblivious store.

- 本周工作计划点1: PA3 of Complier course
- 完成情况：Finished two feature of five.

- 下周计划：
- Finish project of Intel SGX storage.
- Finish another idea.
- Finish PA3 of Compiler.


2017.09.05~2017.09.10

- 本周工作计划点1: Give full version of Phd Proposal
- 完成情况：Finsh almostly except I still need one idea.
在目前这个我们想出来的场景“OS不安全的云中心中保护用户的数据”，用户是谁？用户的特点是啥？用户的应用特点是啥？用户最想得到的安全保证是哪些？这些安全保证是否有个优先级？针对哪些用户应用，我们可以解决哪些安全保证？当前是否已经有一些安全保证的相关/类似实现了？我们比它们好在哪里？或者我们是最早做的，没有可比性？如何评价我们的技术方案？
用户是谁：用户是使用对象存储的人，一般是程序员。比如Facebook中的对象存储的用户是Facebook，Facebook将Facebook用户上传至Facebook的图片和视频上传至对象存储系统中。这些数据通常在Facebook的系统中不会有备份。
用户的特点是啥，用户的应用特点是啥：用户的特点就是会一定的程序开发，使用对象存储开发出程序给第三方使用。
用户最想得到的安全保障是哪些？这些安全保证是否有个优先级？：数据不能丢失>数据不能被破坏>数据不能被泄露。前两个保障在以前的系统中已经完成的较好了。我们不能退步。
当前是否已经有一些安全保证的相关/类似实现了？关于前两个保障是其他领域，关于数据泄露有Facebook的对象存储F4，或者很多安全公司的加密存储系统产品。
我们比他们好在哪：我们的所有机器都可以处理加解密操作，同时所提供的保障更强。
如何评价我们的技术方案：暂时可以考虑的如下，
1. 安全性，包括可以容忍多少台机器的崩溃
2. 性能，普通请求处理的性能。机器崩溃后重启的性能。

>> chy 20170912 没看到上周的周报告

另外，我希望，合理安排时间，确定下面事情的重要性，给出时间表，顺利完成：

- 开题
- 做原型系统
- 读论文
- 写论文

对于课题，我希望了解：在目前这个我们想出来的场景“OS不安全的云中心中保护用户的数据”，用户是谁？用户的特点是啥？用户的应用特点是啥？用户最想得到的安全保证是哪些？这些安全保证是否有个优先级？针对哪些用户应用，我们可以解决哪些安全保证？当前是否已经有一些安全保证的相关/类似实现了？我们比它们好在哪里？或者我们是最早做的，没有可比性？如何评价我们的技术方案？做个表，一个一个列清楚，大家可以比较容易理解。

>> chy 20170904 没看到上周五的周报告。8月缺了1/4

2017.08.29~2017.09.04

- 本周工作计划点1: Survey Database for SGX
- 完成情况：Read paper :
Architecture of a Database System.
Queue encrypted data
[dbsec17]HardIDX- Practical and Secure Index with SGX
[NDSI17]Opaque- An Oblivious and Encrypted Distributed Analytics Platform
[SIGMOD17]Cryptanalysis of Comparable Encryption in SIGMOD’16


2017.08.21~2017.08.28

- 本周工作计划点1: Think more detailed about Problem in Phd proposal.
For Enclave migration, I have consider three problem:  
1. Is it worth to do it? Is it needed in Datacenter?   
Of course it is. For one aspect, the load-balance is needed for energy efficiency(Online migration). On the other hand, the machine requires update(Off line).   
2. How can we do it?  (functionality)
It's not possible to do it from host application/OS since the Intel SGX is designed to against them. And one of important principles is that every chips keeps there secret themselves. So only the enclave can do it.   
How to do it is a subtle job. we can implement an module in enclave or a LibOS in enclave to migrate the whole enclave. The other way is we defined some jobs and only transform the pre-defined states in enclave.   
3. How to make it secure?(security)  
How to make sure the migration How to persuade the customer that the migration/transform will not break the security guarantee.   



2017.08.14~2017.08.20

- 本周工作计划点1: give three ideas/problem for PhD Thesis Proposal.  


- 完成情况：
Our topic is the security for enterprises using public clouds. We have found three points:
1. The security of Storage resource.
2. The security of Compute resource
For computer resource in SGX, we consider two potential idea: Enclave migration and malicious code detection.
3. The security of communication
we may leverage the trusted execution environment to develop an decentralized anonymous communication system under fully compromised infrastructure.

- 下周计划：
1. For the code of storage project, finished remote attestation.
2. For the Phd proposal, read two papers about process migration on ASPLOS 2017 and anonymous communication system on OSDI 16.


2017.06.08~2017.06.16

- 本周工作计划点1: Give a full solution of replication of SGX

- 完成情况： finished execpt the network traffic attack remains to be fix

For now, the discussion of idea for Date 2018 is almost finished. Here is my plan:
1. Finish the project and paper of this paper before August.
2. Start discuss Fast paper once I finished prior works (expected to be finished at July).
3. Finished the project at August
4. Start to write the paper at begining of September.



2017.05.26~2017.06.07

- 本周工作计划点1: Give a sketch of solution

- 完成情况： Gived a model of Data layer, called Replication on Intel SGX.


2017.05.18~2017.05.25

- 本周工作计划点1: Reading papers about blob storage

- 完成情况： half

- 本周工作计划点2: Try Minio and read its code

- 完成情况：Begining.

I have tried several open source SGX program (TaLoS, Panoply and Graphene). The Graphene is the most complete project. I have build a simple file server with SSL and encryption and decryption on files on graphene and carefully work around all the bugs in Graphene. Trying to figure out the data path and control should be in our project.   
However, things turns out that most of people still do not know how to write SGX programs: Is the compatibility really important? Is it necessary to run POSIX program inside SGX? Is the library OS is the ultimate way runnning inside the SGX?
What we need is not put everything in SGX, but separate sensitive path of the program.

- 下周计划：
  1. Reading papers about blob storage
	2. give a sketch of solution of current ideas
	3.


2017.05.07~2017.05.18

- 本周工作计划点1: give a sketch of solution of current ideas

- 完成情况： No

- 本周工作计划点2: Know more about SGX

- 完成情况：YES.

- 下周计划：
  1. Reading papers about blob storage
	2. give a sketch of solution of current ideas
	3. Try Minio and read its code( which is a open source blob storage solution)


2017.04.27~2017.05.6

- 本周工作计划点1: Read more papers

- 完成情况： finished.

- 本周工作计划点2: find new idea

- 完成情况： Finished.


- 下周计划：
	1. give a sketch of solution of current ideas

2017.04.20~2017.04.27

- 本周工作计划点1: Know serverless.

- 完成情况： finished.

- 本周工作计划点2: Reading papers and find new ideas/problems.

- 完成情况： Finished.


- 下周计划：
	1. Know serverless and it's tech, and think about what's the benefit with sgx, what's the challenge it might encounter.

>> chyyuu： serverless service+的综述在问题？值得与SGX结合的地方在哪里？目前已有的研究现状如何？ 你对此serverless service+SGX的想法啥？有何创新性？ Tian Hongliang's Ph.D Thesis有关第4章的内容，请分析如何定位问题的，发现了哪些问题，具体解决方法是什么，如何做测试分析评价的，还有哪些问题没有解决，引入了哪些新问题，能否重现其实验结果？希望周四能够看到你的汇报。

如何定位问题
实际在使用SGX 的SDK 开发应用程序时，这些问题很快就会暴露出来。
发现了哪些问题
SGX中的Library OS 需要syscall的支持，而Syscall需要换入换出Enclave
具体解决方法
实现异步的换入换出和可抢占的enclave 内多线程
如何测试分析评价
分别对单线程和多线程的程序进行性能测试。
哪些问题没有解决
SGX 内存过小的问题。

引入了哪些新问题
将非核心功能下放至host 操作系统，SGXkernel 对kernel 的需求更多，attack surface 更大。

重现实验结果
可以基于开源的graphene系统，将他的工作重现，并测试。

2017.04.13~2017.04.20

- 本周工作计划点1: Reading the Intel SGX explained.

- 完成情况： finished.

- 本周工作计划点2: Reading and use the Intel SGX SDK

- 完成情况： Finished.


- 下周计划：
	1. Know serverless and it's tech, and think about what's the benefit with sgx, what's the challenge it might encounter.

2017.04.03~2017.04.13

- 本周工作计划点1: Reading the Intel SGX explained.

- 完成情况： Ongoing.

- 本周工作计划点2: Reading the Kernel driver of SGX

- 完成情况： Finished.


- 下周计划：
	1. Learning to use the SDK in user level.
	2. finished SGX explained



2017.03.06~2017.03.10

- 本周工作计划点1: Finish the paper on OSDI using SGX.

- 完成情况：Finished.




- 下周计划：
	1. Reading the Intel SGX explained
	2. Think about the problem of SGX, and it's mechanism.


- 其他事宜：

Updated paper list.


本周工作进展和下周计划

2017.03.20~2017.04.02 For two weeks

- 本周工作计划点1: Reading the Intel SGX explained.

- 完成情况： Ongoing.

Finished knowing the the Intel architecture, secure attacks, and SGX programming model.


- 下周计划：
	1. Finished the Intel SGX explained
	2. Read the paper recently published about SGX in paper list



2017.03.06~2017.03.10

- 本周工作计划点1: Finish the paper on OSDI using SGX.

- 完成情况：Finished.




- 下周计划：
	1. Reading the Intel SGX explained
	2. Think about the problem of SGX, and it's mechanism.


- 其他事宜：

Updated paper list.

```
chy: 第二周
上周我提出的问题好像没看到解答。 你写的论文阅读报告可进一步清晰和深入，我觉得如可能，需要实验一下，并对照论文再阅读，比如你说性能是问题，具体测试情况如何。
对于你的想法，建议对一个潜在研究方向，建立一个单独的文件进行撰写。重点论文，需要自己尽量理解清楚，了解相关领域研究现状，并能够给大家清晰的讲解（这一点，在我听到的两次你面向大家的汇报中，觉得还有很大提升空间）。

建议看看 MIT的Sanctum : minimal architectural extensions for isolated execution ，并与SGX对比一下。

对于对于论文阅读报告，请写到单独的文档中，一篇论文一个报告。建议写出：

– Summary of major innovations
– What the problems the paper mentioned?
– How about the important related works/papers?
– What are some intriguing aspects of the paper?
– How to test/compare/analyze the results?
– How can the research be improved?
– If you write this paper, then how would you do?
– Did you test the results by yourself? If so, What’s your test Results?
– Give the survey paper list in the same area of the paper your reading.

建议本周能够给大家汇报一次  Virtual Ghost 或 SGX，最好结合实际的实验。

```
