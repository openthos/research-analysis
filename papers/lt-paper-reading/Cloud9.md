# Parallel Symbolic Execution for Automated Real-World Software Testing

这是2011年发表的Cloud9的论文，是MTSE模型的重要参考。

## 1 文章概述

Cloud9的主要贡献是在分布式集群上部署符号执行任务，来帮助解决路径爆炸的问题。另外，Cloud9不仅可以处理单线程的程序，还可以处理多线程的程序。Cloud9也是第一个支持所有主要POSIX接口的，包括processes, threads, synchronization, networking, IPC等。

符号执行是一种很有效的软件测试方法，但是在工业中的应用非常有限。Cloud9提升了符号执行的三个能力来让其更能够应用在工业界：scalability, applicability, and usability。具体来说有三点：

（1）解决路径爆炸（scalablity）：在文章发表前，没有任何符号执行引擎可以完整地测试数千行以上的程序。Cloud9通过分布式并行来帮助解决这个问题。

（2）支持主要的POSIX接口（applicablity）：工业应用中的程序会通过系统调用、库函数等方式与环境有大量的交互，也会通过socket、IPC、shared memory等方式与其他组件进行交互。对于一个要在实际中方便应用的工具，需要能处理这些交互才行。

（3）创建了一个易用的编写“符号测试”的平台（usability）：应用到工业中的另一道巨大障碍是，为了使用符号执行工具做测试，使用者必须和开发者一样精通符号执行工具中的各种技术才行。Cloud9提供了一套易用的API，让使用者可以在不理解符号执行背后原理的情况下，方便地指定输入和环境，不需要指定那些输入要去符号化等等。



## 2 技术原理

文章中，第3章介绍了分布式的原理，第4章介绍了POSIX模型的建立，第5章介绍了Cloud9设计的易用的符号执行测试工具。我们主要关心的是第4章。

Cloud9对多线程的支持除了在runtime中对函数建模，还对Klee核心做了两个重要的修改：

* 每个state中支持多个address space。这一点是为了支持多进程，和多线程没关系。
* 支持进程和线程的调度



## 3 MTSE和Cloud9的对比

* Cloud9在单机上的时间性能比较差，可以用来做对比。（虽然Cloud9可以分布式跑……）
* 测试数据集上，Cloud9用的是一些比较大的实际程序。这一点MTSE比不了，我们和Cloud9只比多线程支持这部分。