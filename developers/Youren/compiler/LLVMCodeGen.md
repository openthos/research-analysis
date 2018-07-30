The LLVM Target-Independent Code Generator¶
 
意思并不是这个code generator 处理的是target independent，而是说这个code generator 提供了一个平台无关的框架，任何的target 都可以方便的拓展进来。
 
这个代码生成器主要包括六个部件：
	1.	Abstract target description。 主要是描述目标机器的不同的方面，如何使用它们，代码在include/llvm/target
	2.	用来表示对应一个机器代码如何生成的类，这个类需要足够抽象来表示任意一个目标机器。 这个类被定义在 include/llvm/CodeGen，在这个层面，类似于'constant pool entries 和 jump table 被显式暴露
	3.	类和算法用来在对象文件层面表示代码，也就是MC layer 这些类表示汇编层次的构造，例如lables sections 和指令
	4.	Target-independent algorithm。 这个用来实现不同的阶段的native code 生成。（寄存器分配，调度，堆栈表示）这个代码 在lib/Target
	5.	对特定对象的抽象的对象描述接口的实现（Implementations of the abstract target description interfaces）。这个机器的描述使用LLVM提供的 component，而且可以选择用户自定的target-specific passes， 来构建一个完整的code generator。在lib/target 下
	6.	Target-independent jit components。
 
取决于对code generator 的哪个部分感兴趣，不论如何，都需要熟悉 target description 和 machine code representation 类。 如果希望能够给新的target添加一个后端，则需要熟悉和实现5，同时了解llvm IR的语法。
如果对实现一个新的代码生成算法，只需要依赖于 目标描述和机器代码表示的类。
 
 
Code generator的高层设计：
代码生成分为以下的几个步骤
	1.	Instruction selection
这个步骤将LLVM code 转换为 目标的指令集，同时使用virtual registers 和physical registers（特定约束或者调用中使用），这个过程中将IR转换为目标机器指令的DAG图，也就是selectionDAG图。
	1.	Scheduling and formation
这个步骤将之前生成的DAG图（SelectionDAG），决定指令之间的顺序，然后将指令发射出去。此时称为MachineInstr
	1.	SSA-based Machine Code optimizations
采用一系列的 machine code 的优化，优化的输入是之前的instruction selector 生成的SSA-form 。modulo-scheduling 或者peephole optimization 在这里工作。 
	1.	Register allocation
寄存器分配，将虚拟寄存器用物理寄存器替代，涉及到register spilling
	1.	Prolog/Epilog Code inserttion
在函数被调用时，需要一段代码保存和恢复堆栈信息，Prolog code 是指用来保存现场的代码， Epilog是指用来恢复现场的代码。
当寄存器分配完成时，一个函数需要使用的堆栈已经确定（alloc 数据和register spill），实际的 Prolog 和Epilog 代码可以插入，而之前的 abstract stack location references 可以被消除。这个步骤是负责实现像frame-pointer 消除和 stack packing 优化的。
	1.	Late Machine code optimization
最终代码的优化，例如spill code scheduling 和 peephold 优化
	1.	Code Emission
打印代码，binary 格式或者汇编格式。
 
其中我们应该在Epilog Code生成之后对ret 进行插桩，此处需要注意。
 
使用TableGen 描述target
Target description 类需要对目标架构非常详细的描述。这些架构描述通常都有大量的共有的信息（例如add 和sub 几乎一样） 为了能够尽可能的将共有性分解出来，LLVM 使用tablegen 来描述目标平台的big chunks， 使得 能够使用domain-specific 和target-specific 的抽象来降低重复的工作。

接下来介绍具体的
LLVM 目标描述类：
LLVM  target description 类（在 include/llvm/Target 目录中）提供一个独立于任何特别的client 的目标机器的抽象描述。这些类被设计来描述 目标机器的抽象描述（指令和寄存器），不和任意的特定的代码生成算法相关。
所有的目标描述类（除了datalayout）被设计为特定的target 实现的子类，而且virtual methods implemented。 为了get 这些实现，targetmachine 提供了 accessors，这个accessors 应该被实现。
 
TargetMachine 类
TargetMachine 类提供virtual method，用来访问target-specific 实现。通过get \*Info(getInstrInfo, getRegisterInfo, getFrameInfo, etc)。 这个类被设计为特定的架构实现（例如X86TargetMachine)。 唯一被需要类是Datalayout 类，但是如果其他的code generator components被使用，则其他的接口也必须被实现。
 
Datalayout 类
 
这个是一个唯一被需要的类，而且也是一个不可拓展的类。 Datalayout 指明目标平台如何组织内存结构，不同数据的对齐的要求，pointer的size，是大端还是小端
 
TargetLowering 类
TargetLowering 呗SelectionDAG用来指明如何将LLVM code 下降到 selectionDag 操作。
 
TargetRegisterInfo
 
机器代码描述类
Machine code description classes
 
从高层次看，LLVM code 被翻译成一个特定的机器表示格式，MachineFunction MachineBasicBlock和MachineInstr实例。这个设计可以保证即能显示SSA-Form，也可以在register allocation 之后显示 non-SSA form的。
 
MachineInst 类用来表示一条机器指令，这个类非常的简单，只是用来记录一个opcode 和一系列的operand。

MC layer
MC layer 用来在raw machine code 层面表示代码。完全没有了高层级的信息表示，例如constant pool， jump tables 和global variables。 在这个层级，LLVM 处理label name， machine instruction 和sections 之类的东西。 这个layer 中的代码用来处理一系列重要的目标：code generator 最后用他来写.s 或者.o 文件，llvm-mc 用它做汇编或者反汇编。
 
MCStreamer API
MCStreamer 是一个最好的assembler API。
 
MCContext
MCContext 是一系列特有的数据结构的拥有者，包括symbols, sections等等。 因此这个类是创建symbols 和 sections 时需要使用的类。 这个类不能成为子类
 
MCSymbols
MCSymbols 代表一个assembly中的符号。被MCContext 创建，并且是唯一的。这意味着MCSymbols 可以直接通过指针的比较判断是否是唯一的。但是指针不同不代表地址不同（不同的symbols 可以指向同一个位置）
 
MCSections
代表着目标文件中一个特殊的类。
MCInst 类
Target Independent 代码生成算法
 
指令选择
指令选择是将llvm code 转换为 target-specific machine instruction。LLVM使用selectionDAG来做。
 
部分 DAG instruction selector 是基于target description 文件(.td) 生成的，但是还有部分需要C++ 代码实现。
 
SelectionDAG提供了一个非常底层的表示，方便执行一些非常底层但是目标无关的优化。SelectionDAG是一个Directed-Acyclic-Graph 图，每个Node是SDNode，在include/llvm/CodeGen/ISDOpcodes.h文件中。
 
尽管大多数的操作被定义为一个值 （single value）,图中节点可能定义多个值。例如，一个合并的 div/rem 操作需要定义除数和余数。每个节点都有一些操作数，是通向定义这个使用的节点（def-use)，因为nodes 也许定义多个不同的values，edges 被表示为SDValue 类，<SDNode, unsigned> 。 SDNode产生的每个 value有关联的 MVT（Machine value type） ，表明这个value的类型。
 
SelectionDAG 包含两种不同的值，表示data-flow 和表示control-flow依赖的。Data values 是简单的有着integer 或者floating pointer value类型的边。Control edges 被表现为 类型为MVT:: Other 的chain edges。这些边提供一个有side effect 的节点的顺序。
 
SelectionDAG有特定的 Entry和 Root 节点。
 
写一个简单的 llvm backend pass
Llvm backend pass 并不是官方提供的。
