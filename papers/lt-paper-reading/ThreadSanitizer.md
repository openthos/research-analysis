# ThreadSanitizer – data race detection in practice

这篇论文是2009年，Google发表的ThreadSanitizer，其检测data race的方法和MTSE的方法原理非常相似，但不是用在符号执行中。这篇论文也是Ibing A在2016年发表的那篇论文[1]的核心部分，需要仔细研究。



## 1 文章概述

准确检测数据竞争在[2]中证明了是一个NP-hard的问题。但是可以在损失一定精度的前提下检测数据竞争问题。检测的方法可以分为三类：static，on-the-fly，postmortem。其中，on-the-fly和postmortem经常被称为dynamic方法。

典型的静态检测数据竞争的方法需要在程序中增加annotations，而Google内部的程序都很庞大，很复杂，增加annotations的代价太高。所以Google选择用动态方法。

动态方法会分析程序执行的轨迹，on-the-fly在程序执行的过程中并行地分析，postmortem则是将程序执行的轨迹记录下来，等程序执行完后再分析。大部分的动态方法都基于下面的算法之一：happens-before，lockset，both（混合前两者）。这些算法的具体介绍在[3]中。

Google在2008年实现了ThreadSanitizer工具。



## 2 算法

ThreadSanitizer将程序的执行看作一串event的序列，其中最重要的是memory access event和synchronization event：

* memory access event：包括Read和Write
* synchronization event：包括locking event和happens-before event：
  * locking event：包括WRLock，RDLock，WRUnlock，RDUnlock
  * happens-before event：包括SIGNAL和WAIT

![Example of happens-before relation](https://raw.githubusercontent.com/lighttime0/pictures/master/Example%20of%20happens-before%20relation.jpg)

具体来说，和MTSE检测data race的思路几乎一样，详见论文4.1-4.4。



### 2.2 dynamic annotations

所有的dynamic检测方法都必须理解被检测程序所使用的同步互斥机制，否则没法工作。对于只使用POSIX mutex的程序来说，可以将这个信息直接写在检测工具里（大多数检测工具都是这么做的），但是如果被测试程序使用了其他的同步互斥原语，我们必须将它们解释给检测工具。为此，这篇文章开发了一套race detection API——dynamic annotations。每个dynamic annotation都是一个C语言的宏，可以自动添加到被测程序源代码中。

通过dynamic annotations，可以消除所有的误报（LT：需要进一步验证）。



## 附录

1. Ibing A. Efficient data-race detection with dynamic symbolic execution[C]//2016 Federated Conference on Computer Science and Information Systems (FedCSIS). IEEE, 2016: 1719-1726.
2. R. H. B. Netzer and B. P. Miller. What are race conditions?: Some issues and formalizations. ACM Letters on Programming Languages and Systems (LOPLAS), 1(1):74–88, 1992.
3. R. O’Callahan and J.-D. Choi. Hybrid dynamic data race detection. In PPoPP ’03: Proceedings of the ninth ACM SIGPLAN symposium on Principles and practice of parallel programming, pages 167–178, New York, NY, USA, 2003. ACM.