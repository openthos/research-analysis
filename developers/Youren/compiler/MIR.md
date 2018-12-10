为了能够很好地处理和扫描指令，我需要了解MIR指令具体的格式，知道每个寄存器flags的标记。

在之前的尝试时，我已经知道了整个后端的工作流程本质上还是以pass为单位组织的。只是pass 读取的不再是IR，而是IR翻译成的DAG，MIR等。而一个目标文件的组织在MIR层面看来是：MachineFunction MachineBasicBlock， MachineInstr， MachineOperand 的层次一路扫描下来的。 其中MachineFunction可以获得对应的 function 的IR。 MachineOperand 由很多的flags 不是很了解

之前每次都要靠猜才能知道大概自己是哪里错了。但是可以参考如下的链接

<https://llvm.org/docs/MIRLangRef.html>

1. 如何测试自己的MIR pass呢

首先使用 llc --stop-after= pass some.ll 选项，生成一个mir 文件

之后可以使用这个mir测试自己的pass， 使用 -run-pass 测试

例如 llc -o - %s -mtriple=x86\_64-- -run-pass=postrapseudos

接下来是关于整个MIR文件的结构。

MachineFunction 是一个MIR的主要结构，会描述这个MachineFunction 的各种属性，包括：名字，trackRegLiveness, liveins 等。

然后是这个MachineFunction的body，body包括很多的machinebasicblock。 body是yaml解析的字符串。

MachineBasicBlocks的定义是一个block ID，也可以有Block Name

```c
bb.0:
  <instructions>
bb.1:
  <instructions>
bb.0.entry:       ; This block '' s name is "entry"
  <instructions>
```

Blockname必须和IR的name一样。

在block的开头，会是这个block的successors和LiveIn registers

```c
bb.0.entry:
  successors: %bb.1.then(32), %bb.2.else(16)
  liveins: $edi, $esi
```

根据<https://jonathan2251.github.io/lbd/llvmstructure.html> 的解释，LivesIn register 和 livesout register的意思是：

LivesIn: 这个register 在前驱结点中定义，在这个basicblock中会被使用。

LivesOut:这个register 在这个basicblock中定义，在后继节点中会被使用。

每个basicBlock都包含很多个Machininstr

每个Machineinstr 包括 name, machine operand, instruction flag, 和machine Memory operand

指令的名字通常在操作数之前，除非有显示定义的register operand。

例如：

```c
movsbl  piece_def(,%rax,4), %ecx
//对应的MIR为
renamable $ecx = MOVSX32rm8 $noreg, 4, renamable $rax, @piece_def, $noreg, implicit-def $rcx, debug-location !263 :: (load 1 from %ir.arrayidx2, align 4, !tbaa !258); meteor.c:92:12 @[ meteor.c:205:29 ]
//需要注意的是，如果目标地址是一个内存，那么是不会在操作数之前的。例如
movb  %cl, piece_def(,%rax,4)
//对应的MIR为
MOV8mr $noreg, 4, renamable $rax, @piece_def, $noreg, renamable $cl, implicit killed $ecx, debug-location !267 :: (store 1 into %ir.arrayidx2, align 4, !tbaa !258); meteor.c:205:27
```

Bundled Instructions 的语法是
```
BUNDLE first instruction {
Other instructions
}
```
第一个指令是bundle header，其他的指令buundle 第一个指令。

Register

register 是MIR主要的要素之一，通常使用在指令中，LiveIn中也会使用。

physical register 由$开头

virtual register 由 %开头

%0 或者$noreg 表示空寄存器（不需要使用寄存器，占位）

Machine Operands

机器的操作数包括好几类，立即数操作数是最简单的

register operands 用来表示register machine operands。 通常有着 可选的register flags 和subregister index

```c
[<flags>] <register> [ :<subregister-idx-name> ] [ (tied-def <tied-op>) ]
```

llvm::RegState 中标明有可能的寄存器flag，但是Regstate 中没有具体的写每个flag的含义：

FlagInternal Value`implicit``RegState::Implicit``implicit-def``RegState::ImplicitDefine``def``RegState::Define``dead``RegState::Dead``killed``RegState::Kill``undef``RegState::Undef``internal``RegState::InternalRead``early-clobber``RegState::EarlyClobber``debug-use``RegState::Debug``renamable``RegState::Renamable`

关于每个 flag具体的含义，可以参考文件llvm/CodeGen/MachineOperand.h中的注释。

这个文件很重要，可以好好地阅读。如何还是不能特别的理解，可以通过比较一个文件输出的mir和.s 来猜测

implicit 的意思是这可能是一个implicit def or use，即在这个指令并不是显示的出现在 .s 文件的对应的汇编语句中，但是这个寄存器被def 或者use 或者跟着对应的操作了。如下例子：

```c
MOV8mr $noreg, 4, renamable $rax, @piece_def, $noreg, renamable $cl, implicit killed $ecx, debug-location !267:: (store 1 into %ir.arrayidx2, align 4, !tbaa !258); meteor.c:205:27
movb  %cl, piece_def(,%rax,4)
```

def 意味着这个定义了一个register，也就是这个register 被赋予了一个新的值。如果不是def，那就是use

Implicit-def 意思是这个寄存器也定义了一个新的值，经常出现于 对少bit 寄存器赋值之后，原来的高 bit 寄存器就是 implicit def。如上面的例子就是implicit killed，之前的ecx。

killed 和dead是一个对应的关系，一个register 的use 是kill，一个寄存器的def 可以用dead

dead 意味着这条指令到下一个def 这个寄存器的过程中，都没有指令使用这个寄存器。

kill 意味着这是这个寄存器的下一个def之前的最后一个use。

还是有一些细微的差别的。

Renameable的意思是这个寄存器可以随便换成其他的等效的寄存器，比如rax换成RBX。不能换的情况一般是ABI要求或者指令要求。

undef的意思是这个值未定义。也就是这个寄存器具体是多少，并不重要。例如加入程序员从一个未初始化的内存中读取数据，并进行操作，就是undef的。

但是如果一个指令中有两个undef，则也许这两个undef 可能有关系，例如

```assembly
%1 = XOR undef %2, undef %2
```

这里意味着%2必须是同一个寄存器

IsInternalRead

意思是operand 读取了同一个指令或者bundle中def的寄存器

EarlyClobber 的意思是def operand 在这个MachineInstr 的其他的input register 读取之前就会被写。

Debug-use的意思是这个use 是一个debug pseudo，而不是一个真正的指令
