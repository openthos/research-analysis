# Reading notes
Combining Control-Flow Integrity and Static Analysis for Efficient and Validated Data Sandboxing

这篇论文通过静态检查，优化对内存读的检查。
这篇论文中仅考虑软件方案。

这篇论文中提出了一系列的高效的数据沙盒优化方法。  
使用 range analysis来检查优化是否有效  
通过static analysis，提出两种方法加速cfi  

## Thread model
这篇论文采用CFI的攻击模型，这种模型简单实用。     
在这个模型中，代码和数据是分开的。assumption之一是攻击者无法修改寄存器中的内容。数据区可以修改可以但是不可执行。
代码区需要保证control-flow security，即所有的跳转都只能跳转到某些可能的位置，不能破坏程序的CFG，而不能是随意的位置。   
可以简单的理解为只能在basicblock中间跳转。
数据区需要保证 data sandboxing policy。
## 优化方法
首先我们需要了解一下程序的原样，来了解我们需要做什么样的优化，以下是一段代码在原始的情况下的样子：
```
ebx := [ecx + 4]
```
这段代码以ecx为基地址，偏移量为4的内存地址中的数据取出来放到ebx中。对这个内存读取请求进行插桩未优化时的代码如下：
```  
push eflags   
push eax   
eax := ecx + 4     
eax := eax & $DMask    
ebx := [eax]
pop eax   
pop eflags   
```  
上面这段代码中第四行是通过DMask来判断请求的地址是否在合法范围内。
因为涉及到加法，所以首先需要将eflag
### liveness分析
liveness分析是对一个寄存器的使用范围进行分析。如果当前的寄存器之后都不会再使用，则我们可以将push 和pop eax两行删掉

### in-place sandboxing
在设计隔离机制的时候，每个region 附近有一段guard zone。而对一个以基址寻址的来说，如果基地址在data region中， 偏移量大小不超过guard zone的大小，那么这个访问肯定是可以执行的（访问guardzone触发缺页中断）

### Range 分析
range分析是指对一个register可能的值进行分析。通常理论上一个register的值可能是正无穷到负无穷，这个并不能带来新的信息，但是很多情况下我们可以给register一个大概的值的范围。
Range 优化可以做两件事，
1  多余的check 的消除   
这个分为两步做  
	A. 对输入 程序进行 range analysis   
	B. 使用分析的结果   

如果我们发现一个register 的range 在data region + guard zone之内，那么对这个register的访问的check就可以删掉。

2. Loop check 的转移
如果一个loop的循环次数较小，即其偏移量较小，则我们可以将loop中的check移至loop开始的地方。
