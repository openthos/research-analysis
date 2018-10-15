LXFI 阅读报告：
## 问题定义
对内核模块的隔离已经有一些研究，例如XFI和BGI，但是XFI只是关注于Module 内部的安全，而我们知道，Module和内核之间拥有大量的接口，如果不保证这些interface 的安全，那么模块也没法保证内核安全。在LXFI中，作者提出了两个额外的module 的问题：

1. Privileges in shared module

一个module中的代码，如果具有多个context，那么他们通常也需要对应于不同的特权级。例如dm-crypt 加密文件系统模块负责管理系统中的所有的加密存储设备，因此这个模块可能对所有的加密存储设备都具有读写能力。但是如果一个usb设备是恶意的并且利用了模块中的某个bug，那么dm-crypt就可以破坏所有的加密存储设备。

2. 在Kernel 和module 之间缺少API integrity

API integrity指的是内核的API会按照其所设计的一样，执行相应的操作。BGI考虑了内核和模块之间的交互，但是他是通过重新设计和实现接口来保证安全的，这个不适合在Linux kernel 中应用于复杂的Linux kernel 和module 之间。
在LXFI中，将API的integrity定义为API会和设计的一样，执行相应的操作，而不会有其他额外的影响。LXFI中希望通过定义API的contract，然后保证API的contract 被follow，来保证API的integrity。为了弄清楚有哪些Contract 需要定义，我们西安看看API 的integrity被打破会有哪些影响呢？这些影响是如何发生的：

### memory safty and control flow integrity
这两点保证一个module 只能访问自己所能访问的，同时保证只能执行自己所能执行的代码以及调用core kernel的代码。这个和传统的SFI的定义一样，所不同的是在内核的环境中，一个module 的代码和数据是分开存放的，这导致传统的 SFI无法使用。但是性能较差细粒度的比较还是没有问题的。   
同时，仅保证这两点，无法完整保证API 的integrity。

### Function call integrity   
一个内核模块怎么可以调用核心内核的函数。Function call integrity 主要是只module 调用kernel函数的时候提供的argument是否是合适。
因此LXFI定义了一个叫做ownership的概念。一个典型的ownership的概念是是否可以写一块内存。某块内存是否可以给这个module 写。
另一个问题是callback function。当kernel 在调用module提供的callback 函数的指针可能指向的不是可以调用的位置上。
另一个是当module 调用kernel的callback函数时，则需要像之前的调用一样，检查目标地址是否正确，以及参数是否正确。

### Data structure integrity
包括 两个方面，其一是需要保证写的数据是可写的。
另一种是写callback的function pointer的时候，需要验证写的pointer 是正确的函数起始地址
因此在写callback 指针的时候，LXFI会验证writer 是否可以调用这个函数。

### API integrity in Linux 
通常来说想要表达所有的contract 来保证API integrity是很困难的，但是在Linux Kernel中的API通常都是有着良好的设计的，也会有很多的检测。因此LXFI希望kernel developer可以给自己的API加上注解，然后LXFI根据注解进行插桩，强制API和module 之间的contract

## Annotations
high level来看，LXFI的工作流程分为4步：
1. kernel developer 对core kernel 和module 的API进行注解。
2. module 开发者对module中需要不同的principle 的部分进行注解
3. LXFI编译，对相应的代码进行插桩
4. 运行时，插桩点会对contract 进行检查，保证其符合调用规定。

### Principals
通常一个模块中的代码可能会被好几个不同的实例调用，例如econet 模块提供一个接口可以初始化特殊的socket。
为了保证攻击者在一个模块中所能处理特权的最小化，LXFI将一个module分解为很多个principals，每个principals对应一个模块的实例。每个实例只有一部分的privileges，而不是整个模块的privileges。
Principals包括三个机制：
1. 模块开发者可以在模块内部定义principals
2. 模块开发者可以定义当调用某个模块代码时，依据参数，哪个principals被使用。
3. 为了操作全局的变量，定义global principals函数。还有shared principals代表所有的principals都能访问的。

### Capabilites
Capabilities表示的是这个module 的principal 具有哪些能力，这些能力包括：

1. WRITE （ptr,size)
2. REF(t,a)
3. CALL(a)   

write意思是能够写从ptr 开始的，size大小的内存
REF意思是对于a这个变量，能够以类型T作为参数调用。
例如kernel中有函数func(t x)，module 有t类型的参数a和b，有REF(t,a)
那么module中func(a)是允许的，func(b)不被允许，因此该module没有对应的REF

CALL(a)意思是能够调用函数a 

### Interface annotations
为了标明API会对principals 的capabilites 造成哪些影响，或者进行哪些检查，module 的开发者需要对函数调用进行标注。
标注的语法如下：
```
annotation::= pre(action) | post(action) | princial(c-expr)
action::= copy(caplist)
        | transfer(caplist)
        | check(caplist)
        | if(c-expr) action
caplist::= (c,ptr,[size])
        | iterator-func(c-expr)
```

pre 和post 是指在函数调用完成前执行动作还是调用完成后执行动作。princial是指哪个princial应该用来执行这个函数。copy是从某个module中将对应的cap copy。如果是pre，则是caller copy 到callee。如果是post，则是从callee copy 到caller。transfer 类似。但是transfer是move，不是copy。同时transfer 会将所有的princial中的cap都收集起来，不只是当前这一层。Transfer 保证所有的princial 都不会有对应的cap的copy。 例如kfree调用的时候，需要将所有这块内存的cap的copy都收集起来。
check会检查当前的princial 是否有对应的cap
为了支持条件action，if 被加入。只有if满足的时候才会执行action。
princial 以对应的参数的地址为princial的名字。但是有些时候不同的参数对应的是同一个princial，例如网络的子系统在pci里面对应的是pci\_dev，在网络中对应net\_device 所以LXFI提供一个lxfi\_princ\_alias表示同一个princial

## compile-time rewriting

### rewriteing the core kernel 
core kernel 在调用module 函数的时候，需要确保callback 是这个module 可以调用的函数以及参数。因此在kernel中callback 函数调用前，插入检查：
1. 检查提供这个callback 函数的module princial是否有调用这个函数的cap。
2. 保证这个函数的注解和funciton pointer type 一样。

实现这个check 的方式是在kernel 中所有的indirect call 前面插入检查：lxfi_check_incall(pptr,ahash)。 runtime 会检查将f的地址写入pptr的 module 是否可以call f这个函数。同时通过比较ahash（annotation的hash值），比较f和function pointer 的annotation是否一样。

为了优化这个比较的过程，LXFI实现了一个write-set 的跟踪。如果没有princial 可以写这个function pointer，那么在lxfi_check_incall的时候就可以直接跳过检查。为了能够获得所有的函数指针本来的内存位置，LXFI进行一个简单的程序分析，找到函数指针原始的位置（解决 handler = opt->handler; call handler的情况)

### Rewriting modules
#### annotation propagation
将function相关的指针所有的annotation 都apply 到这个函数上。

#### Function Wrappers
LXFI为所有的模块定义的函数，kernel-exported function 和indirect callsite 都加上一层wrapper，实现对应的actions

#### 模块初始化代码
对每个模块的初始化，LXFI都生成一个初始化函数。
初始化的内容包括：call 
write
初始化的都是shared princials。

#### memory writes
对所有的内存写都插入检查


