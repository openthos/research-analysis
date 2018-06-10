#Reading notes of superset disassembly

## Motivation
有太多的工作需要对binary进行逆向分析。但是这些工作都有一些限制：
可能需要 compiler 或者对compiler 有一定的需求。或者需要compiler 特定的debug 信息来对binary反汇编。NaCl需要一个特别的编译器来编译特别的程序。
更近一些的工作  放宽了对compiler 协同的假设，但是他们还是有一些启发式的方法。尤其是对position-independent code (PIC) and callbacks. CCFIR使用relocation metadata来转换 binary。Secondwrite 重写 binary，但是不依靠之前的两个信息（debug或者relocation）,但是他通过将binary 提高到LLVM IR，然后在IR层面重写。最近的工作URBOROS提供了一个使用一系列的启发式学习的方法来rewrite binary，但是其依然有 false positive（spec 2006）
从上面可以看出，之前的工作都有一定的限制性，因此这篇文章推出一个完全不基于启发式的方法。为了达到目标，需要解决两个问题：
1. 如何反汇编二进制代码
2. 如何重新汇编重写指令，同时保证程序的语义不变。

为了解决第一个问题，提出了一个superset 反汇编技术。 创建一个所有的可使用的指令的superset
为了解决第二个问题，作者从Dynamic binary instrumentation 中借鉴一个技术， 解析所有的indirect CFT，在rewrite时重定向他们到新的目标地址。新的目标地址来自于一个映射表。

## Challenges
### C1:识别并且重定位静态内存地址
### C2:处理动态计算的内存地址
### C3:区别代码和数据
### C4:处理函数的函数指针参数
想一想qsort，需要传递一个cmp函数指针给qsort函数
### C5:处理PIC

##Solution
### 保证原来的数据空间intact
### 创建一个从旧的代码空间到新的代码空间的映射。
### 粗鲁的强制反汇编所有可能的代码
### 重写所有的用户代码和库
一个可能能解决C4的办法是识别所有的使用了指针参数的函数，包括外部库，这样所有的callback 函数都可能被正确的调用。
### 重写所有的call指令，来处理PIC
将所有的call指令重写为push + jump
