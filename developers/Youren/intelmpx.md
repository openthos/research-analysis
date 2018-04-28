Reading notes for Intel MPX explained.
=========================
这里主要介绍当使用intel mpx 进行pointer based check 的方法。

Intel MPX主要通过给编译器写扩展在某些访存指令前面插桩，进行bound check来保证程序的内存安全。
如下，例如下面这段代码，
struct中有100个char存数据，一个int 存长度。
一共有10个struct obj，for 循环中读取len统计 10个obj的总长度

```
struct obj { char buf[100]; int len }
obj∗ a[10]
total = 0
for(i = 0; i < M; i ++):
  ai = a + i
  objptr = load ai
  lenptr = objptr + 100
  len = load lenptr
  total += len
```
使用MPX 对以上代码进行检查，插入的指令如下：

```
1 obj∗ a[10]
2 total = 0
3 a_b = bndmk a, a+79
4 for(i = 0; i < M; i ++):
5   ai = a + i
6   bndcl a_b, ai
7   bndcu a_b, ai + 7
8   objptr = load ai
9   objptr_b = bndldx ai
10  lenptr = objptr + 100
11  bndcl objptr_b, lenptr
12  bndcu objptr_b, lenptr+3
13  len = load lenptr
14  total += len
```
其中，第3行为一个pointer创建一个bound

第6行和第7行对ai 进行bound check，查看该pointer 是否越界

第9行，当将一个pointer 赋值给另一个pointer时，需要将bound一起赋值，因此使用bndldx，将ai赋值给objptr_b

第11行和12行检查 lenptr是否越界。

所有的这些新的指令，在不支持MPX的CPU上都会被当成NOP指令。
从上往下看，MPX需要修改如下部分来支持：
1. 硬件上： 添加了新的指令和4个128 位的寄存器    
2. 操作系统层面： 需要一个新的#BR 异常处理程序，主要完成以下功能 (1) 分配bounds的内存 (2) 当违反bound check出现时，发送给程序信号。
3. 编译器： 编译器的transformation passes 需要能够插入MPX指令，来创建，赋值，存储和检查bounds。额外的运行时库提供初始化和结束时的操作，以及对一些标准C 库函数的包装。
4. 在应用层，MPX的程序 也许需要修改部分的不适应的C代码。

以上的除了硬件上的修改，其他都是基于Pointer-based bound check应用所需要的修改。


其中，编译器的支持需要额外的关注， 使用如下指令可以进行编译：
```
 gcc −fcheck−pointer−bounds −mmpx test.c
```

其对原程序进行如下插桩：
1. 为全局变量创建 static bounds，stack 变量使用bndmk指令
2. 对每个pointer store 和load 之前，插入 bndcl bndcu 指令
3. 当一个新的pointer 从旧的pointer 创建的时候，使用bndmov 指令为这个pointer创建bounds
4. 当bounds register不够时将bounds register存在栈上。
5. 当对应的pointer 从memory中load/store的时候，使用bndldx/bndstx将bounds load/store

除了上述工作以外，compiler还需要尽力的进行优化：
1. 当编译器发现可以statically的证明不会越界，则可以移除。
2. 将bounds check 移动到简单的循环外。
例如当 代码中的M 永远比10小。

因为我们的工作中并不是pointer-based 的，所以4个寄存器应该够用，因此这个notes 中没有记录 关于 Bounds table （bounds 太多，寄存器不够用需要存在内存中）管理的内容。
