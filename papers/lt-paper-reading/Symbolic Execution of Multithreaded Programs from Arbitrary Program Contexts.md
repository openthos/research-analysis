# Symbolic Execution of Multithreaded Programs from Arbitrary Program Contexts

这篇2014年的论文是基于Cloud实现的，目标和我们比较相似，需要好好对比一下性能和原理。

## 1 文章概述

这篇文章的目标是可以对C语言写的多线程程序scalable地进行符号执行。

文章的重点并不在于多线程的建模，这部分是直接从Cloud9借鉴过来的。文章的重点在于将多线程程序切片，然后**让符号执行可以从任意程序上下文中执行一段程序切片**。因为是对程序切片进行符号执行，所以可以同时跑多个程序切片，从而达到scalable的目标。

这个技术的优势在于可以只分析大型程序中的关键并行部分，或者分析程序中某段代码；但是trade-off是有一些精度的损失。

## 2 技术原理

这篇文章要实现从任意程序上下文开始符号执行的话，最重要的的问题就是初始的ExecutionState。

ExecutionState是符号执行了最重要的数据结构，代表了一条执行路径，保存了程序开始到当前指令为止所有的约束等信息，还负责管理内存。要获取从任意程序切片的第一行开始符号执行所需的初始ExecutionState，最精确的获取方法是从程序入口开始，将所有程序入口到程序切片第一行之间的所有路径都符号执行一边，最后merge起来，构造成所需的初始ExecutionState。

但是这种方法并不scalable，所以文章中使用了approximation的方法，构造一个“大概”的初始状态。最简单的构造办法是给所有的内存区域赋一个新的符号量。这样做可以保证所有的约束和内存状态等都不会被错过，但是缺点是太overhead了，会让符号执行进入到很多不可能出现的代码路径中去。

这篇文章是用了一种介于上面两种极端之间的办法：使用context-specific dataflow analysis来构建一个over-approximnation的“大概”的初始ExecutionState，然后使用在符号执行的过程中加上同步互斥的约束条件，比如locksets，来让符号执行避免进入一些不可能出现的路径中。论文中的Figure 1是一个小例子，可以简答说明增加的同步互斥约束如何减少一些不可能出现的路径。

总的来说，**将数据流分析和符号执行两种技术结合起来，用数据流分析构造任意程序切片的初始ExecutionState，然后在符号执行中增加同步互斥约束来减少一些不可能出现的路径**。

## 3 一些细节

### 3.1 用数据流分析的方法构造任意程序切片的初始ExecutionState

这是整篇文章中最核心的重难点，在文章的2.3、3.3、4.4三段进行介绍，比较复杂，还没有太看懂。



### 3.2 对data race的处理

这篇文章讲data race看作runtime error，并停止符号执行，没有更多的处理了。



## 4 Performance

### 4.1 代码覆盖率

这篇文章从standard multithreaded benchmark suites[1, 2]中选取了一些，并人工构造了一些程序上下文，进行代码覆盖率的测试。详见论文中的Table 1



### 4.2 横向对比

文章中没有对不同符号执行工具的时间性能做一个横向对比，之横行对比了支持的功能，详见下图：

![table2](https://github.com/lighttime0/pictures/raw/master/2019-07-27_20-46-31.jpg)



## 5 MTSE和这篇文章对比

* 这篇文章是基于Cloud9实现的，所以时间性能上还是会比较差，我们可以在时间性能上做对比。但是，这篇文章的代码没有开源……

* 这篇文章的优缺点很明显，我们现在的优点是不损失精度，但也要考虑如何应用在更大型的软件上，如果没有办法的话，文章中就不要提应用在大型软件上了，毕竟这不是MTSE的目标，不可能面面俱到。

* 这篇文章测试覆盖率的benchmark可以参考：standard multithreaded benchmark suites[1, 2]

  

## 6 附录

1. C. Bienia, S. Kumar, J. P. Singh, and K. Li. The PARSEC Benchmark Suite: gi and Architectural Implications. In PACT, 2008.
2. S. C. Woo, M. Ohara, E. Torrie, J. P. Singh, and A. Gupta. The SPLASH-2 Programs: Characterization and Methodological Considerations. In ISCA, 1995.