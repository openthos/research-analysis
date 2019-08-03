# Efﬁcient Data-Race Detection with Dynamic Symbolic Execution

这篇2016年的论文和MTSE非常相似，需要仔细研究它的论文思路作为参考。

## 1 文章概述

这篇文章的思路可以分成两部分来看：

* Data race detection是通过Google在2009年发表的ThreadSanitizer，用动态分析的方法来检测
* 符号执行用来探索单个CPU上FIFO调度的多线程程序的execution tree

但是文章写的挺奇怪的，挺短挺好懂的，但是仔细读了几遍都没看出来它是怎么结合符号执行和data race detection的。好像只说了符号执行中加入多线程后execution tree如何处理，data race detection使用Google的ThreadSanitizer直接检测的？？？



## 2 技术细节

### 2.1 Dynamic Race Detection

文章使用2009年Google发布的ThreadSanitizer来在concrete execution的时候检测data races，关于ThreadSanitizer这篇论文可以参考[这篇阅读报告](https://github.com/openthos/research-analysis/blob/a9cb7b40ae6b2e387b5471e838cb34887c66f28b/papers/lt-paper-reading/ThreadSanitizer.md)。



## 3 MTSE可以学习的部分

* 这篇文章用的测试用例[1]可以学习一下，里面包含5-7个threads，38个data race，挺不错的测试样例。

* 这篇文章的Related Work部分挺有价值的。



## 附录

1. T. Boland and P. Black, “Juliet 1.1 C/C++ and Java test suite,” IEEE Computer, vol. 45, no. 10, 2012. [Online]. Available: http://dx.doi.org/10.1109/MC.2012.345