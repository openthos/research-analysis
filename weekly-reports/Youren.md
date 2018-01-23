本周工作进展和下周计划  
2018.1.15~2018.1.19
- 本周工作计划1：code
- 完成情况： coding

现在机器之间的通信已经建立起来了，接下来是写协议

年度总结：
去年想要基于Intel SGX做一些系统相关的研究，为此花了三个月了解SGX，而后6月份开始着手如何隐藏文件的位置保证用户数据的安全。中间反复讨论过很多次，一直到12月有比较成熟的想法。这一个多月一直在实现。因为工作比较复杂，所以实现的很慢，中间还遇见很多坑。
除了具体的事物，去年阅读了很多的论文，学会了如何通过阅读论文快速了解一个领域，相信之后对其他的领域也能快速上手。

明年计划：
想要将手上的工作尽快完结，之后可以协助田洪亮做switchless OS，他在Enclave中关于性能优化有一些新的idea。
之后还没有安排。
约谈：
平时most of time都在122，大部分时间都可以。

2018.1.3~2018.1.12
- 本周工作计划1：code
- 完成情况： coding

- 下周计划工作：
  最近一直在coding

2017.12.25~2018.1.2
- 本周工作计划1：code
- 完成情况： 本来想这周写完的，但是openssl的RSA,PKCS 不太了解，所以写的稍微慢

- 下周计划工作：
  写论文安全分析部分


2017.12.15~2017.12.24  
- 本周工作计划点1：code  
- 完成情况：完成SSL性能测试，和enclave 中执行aes 128 gcm加密速度和普通的运行环境速度类似。对于4k或8K的块加密，速度达到5Gb/s   
- 本周工作计划点2：code 实现论文逻辑的主体  
- 完成情况： 主要分为两个部分，一个部分是非安全部分的负责将数据包通过网络发送出去，或者接受其他机器发送过来的数据。或者读取磁盘和写磁盘。安全部分和非安全部分通过四个lock-free的queue交互。这些代码之前已经写完了。
另一部分是系统的关键流程，在enclave中运行，根据两个DHT和两个 table处理用户的数据。这个部分正在写。  

2017.12.11~2017.12.15
- 本周工作计划点1：code
- 写ssl性能测试。

2017.12.4~2017.12.10
- 本周工作计划点1: write implement
- 完成情况：half，写了整个系统的序列图，定义详细系统的行为。
- 本周工作计划点2：code
- 开始写ssl性能测试。

- 下周计划：
- 想想怎么写implement 中的Oblivious shuffle
- code

2017.11.27~2017.12.3

- 本周工作计划点1: write Design
- 完成情况：finished


- 下周计划：
- 想想怎么写implement 中的Oblivious shuffle
- code

2017.11.19~2017.11.26

- 本周工作计划点1: write problem definiation
- 完成情况：finished
- 本周工作计划点2: Fix two problem: Oblivious response time issue and Crash may not good under virtual node.
- 完成情况：Done.

2017.11.13~2017.11.18

- 本周工作计划点1: write introduction
- 完成情况：finish half
- 本周工作计划点1: reading oblivious paper
- 完成情况：summary will be update later

2017.10.6~2017.11.10

- 本周工作计划点1: Reading oblivious store papers
- 完成情况：figure out some consideration.
- 本周工作计划点1: Finish abstract
- 完成情况：Finished, but not reviewed by kang chen.

- 下周计划：
- Finish design of paper

2017.10.23~2017.11.4

- 本周工作计划点1: Reading paper of sosp 17 and attend it.
- 完成情况：Finished
- 本周工作计划点1: Finished Slides of intel sgx storage
- 完成情况：Finished

- 下周计划：
- Finish project of Intel SGX storage.
- Finish introduction part.

2017.10.16~2017.10.22

- 本周工作计划点1: Understanding Oblivious storage.
- 完成情况：Finished
- 本周工作计划点1: Find the fix of our approach
- 完成情况：Finished

- 下周计划：
- Update the draft of paper.
- Finish project of Intel SGX storage.

2017.10.09~2017.10.13

- 本周工作计划点1: Finish project of Intel SGX storage.
- 完成情况：Finished outside enclave world including rpc server and client, file server. Finished some enclave function. Finished the interface between enclave and host Application.
The problem is I have to understand oblivious store to continue the functionality inside enclave.

- 下周计划：
- Finish project of Intel SGX storage.
- Understanding Oblivious Memory and store.

2017.09.23~2017.09.30

- 本周工作计划点1: Finish project of Intel SGX storage.
- 完成情况：Almost finished outside part. build an RPC server as network connection part.

- 本周工作计划点2:Finish the PHD thesis proposal
- 完成情况：Failed.

- 本周工作计划点3:Finish Compiler PA2 testcase and homework.
- 完成情况：Finished


- 下周计划：
- Finish project of Intel SGX storage.

2017.09.16~2017.09.22

- 本周工作计划点1: Finish project of Intel SGX storage.
- 完成情况：Starting

- 本周工作计划点2:Finish another idea.
- 完成情况：Finished. For more detail, check the proposal repo in github.

- 本周工作计划点3:Finish PA3 of Compiler.
- 完成情况：Finished


- 下周计划：
- Give the final talk of Phd proposal
- Finish project of Intel SGX storage



2017.09.11~2017.09.15

- 本周工作计划点1: give a talk to about proposal of Phd Thesis.
- 完成情况：Finished but one idea missing
Maybe Database is an good idea. We do not need to consider the memory limit, just think about oblivious store.

- 本周工作计划点1: PA3 of Complier course
- 完成情况：Finished two feature of five.

- 下周计划：
- Finish project of Intel SGX storage.
- Finish another idea.
- Finish PA3 of Compiler.


2017.09.05~2017.09.10

- 本周工作计划点1: Give full version of Phd Proposal
- 完成情况：Finsh almostly except I still need one idea.
在目前这个我们想出来的场景“OS不安全的云中心中保护用户的数据”，用户是谁？用户的特点是啥？用户的应用特点是啥？用户最想得到的安全保证是哪些？这些安全保证是否有个优先级？针对哪些用户应用，我们可以解决哪些安全保证？当前是否已经有一些安全保证的相关/类似实现了？我们比它们好在哪里？或者我们是最早做的，没有可比性？如何评价我们的技术方案？
用户是谁：用户是使用对象存储的人，一般是程序员。比如Facebook中的对象存储的用户是Facebook，Facebook将Facebook用户上传至Facebook的图片和视频上传至对象存储系统中。这些数据通常在Facebook的系统中不会有备份。
用户的特点是啥，用户的应用特点是啥：用户的特点就是会一定的程序开发，使用对象存储开发出程序给第三方使用。
用户最想得到的安全保障是哪些？这些安全保证是否有个优先级？：数据不能丢失>数据不能被破坏>数据不能被泄露。前两个保障在以前的系统中已经完成的较好了。我们不能退步。
当前是否已经有一些安全保证的相关/类似实现了？关于前两个保障是其他领域，关于数据泄露有Facebook的对象存储F4，或者很多安全公司的加密存储系统产品。
我们比他们好在哪：我们的所有机器都可以处理加解密操作，同时所提供的保障更强。
如何评价我们的技术方案：暂时可以考虑的如下，
1. 安全性，包括可以容忍多少台机器的崩溃
2. 性能，普通请求处理的性能。机器崩溃后重启的性能。

>> chy 20170912 没看到上周的周报告

另外，我希望，合理安排时间，确定下面事情的重要性，给出时间表，顺利完成：

- 开题
- 做原型系统
- 读论文
- 写论文

对于课题，我希望了解：在目前这个我们想出来的场景“OS不安全的云中心中保护用户的数据”，用户是谁？用户的特点是啥？用户的应用特点是啥？用户最想得到的安全保证是哪些？这些安全保证是否有个优先级？针对哪些用户应用，我们可以解决哪些安全保证？当前是否已经有一些安全保证的相关/类似实现了？我们比它们好在哪里？或者我们是最早做的，没有可比性？如何评价我们的技术方案？做个表，一个一个列清楚，大家可以比较容易理解。

>> chy 20170904 没看到上周五的周报告。8月缺了1/4

2017.08.29~2017.09.04

- 本周工作计划点1: Survey Database for SGX
- 完成情况：Read paper :
Architecture of a Database System.
Queue encrypted data
[dbsec17]HardIDX- Practical and Secure Index with SGX
[NDSI17]Opaque- An Oblivious and Encrypted Distributed Analytics Platform
[SIGMOD17]Cryptanalysis of Comparable Encryption in SIGMOD’16


2017.08.21~2017.08.28

- 本周工作计划点1: Think more detailed about Problem in Phd proposal.
For Enclave migration, I have consider three problem:  
1. Is it worth to do it? Is it needed in Datacenter?   
Of course it is. For one aspect, the load-balance is needed for energy efficiency(Online migration). On the other hand, the machine requires update(Off line).   
2. How can we do it?  (functionality)
It's not possible to do it from host application/OS since the Intel SGX is designed to against them. And one of important principles is that every chips keeps there secret themselves. So only the enclave can do it.   
How to do it is a subtle job. we can implement an module in enclave or a LibOS in enclave to migrate the whole enclave. The other way is we defined some jobs and only transform the pre-defined states in enclave.   
3. How to make it secure?(security)  
How to make sure the migration How to persuade the customer that the migration/transform will not break the security guarantee.   



2017.08.14~2017.08.20

- 本周工作计划点1: give three ideas/problem for PhD Thesis Proposal.  


- 完成情况：
Our topic is the security for enterprises using public clouds. We have found three points:
1. The security of Storage resource.
2. The security of Compute resource
For computer resource in SGX, we consider two potential idea: Enclave migration and malicious code detection.
3. The security of communication
we may leverage the trusted execution environment to develop an decentralized anonymous communication system under fully compromised infrastructure.

- 下周计划：
1. For the code of storage project, finished remote attestation.
2. For the Phd proposal, read two papers about process migration on ASPLOS 2017 and anonymous communication system on OSDI 16.


2017.06.08~2017.06.16

- 本周工作计划点1: Give a full solution of replication of SGX

- 完成情况： finished execpt the network traffic attack remains to be fix

For now, the discussion of idea for Date 2018 is almost finished. Here is my plan:
1. Finish the project and paper of this paper before August.
2. Start discuss Fast paper once I finished prior works (expected to be finished at July).
3. Finished the project at August
4. Start to write the paper at begining of September.



2017.05.26~2017.06.07

- 本周工作计划点1: Give a sketch of solution

- 完成情况： Gived a model of Data layer, called Replication on Intel SGX.


2017.05.18~2017.05.25

- 本周工作计划点1: Reading papers about blob storage

- 完成情况： half

- 本周工作计划点2: Try Minio and read its code

- 完成情况：Begining.

I have tried several open source SGX program (TaLoS, Panoply and Graphene). The Graphene is the most complete project. I have build a simple file server with SSL and encryption and decryption on files on graphene and carefully work around all the bugs in Graphene. Trying to figure out the data path and control should be in our project.   
However, things turns out that most of people still do not know how to write SGX programs: Is the compatibility really important? Is it necessary to run POSIX program inside SGX? Is the library OS is the ultimate way runnning inside the SGX?
What we need is not put everything in SGX, but separate sensitive path of the program.

- 下周计划：
  1. Reading papers about blob storage
	2. give a sketch of solution of current ideas
	3.


2017.05.07~2017.05.18

- 本周工作计划点1: give a sketch of solution of current ideas

- 完成情况： No

- 本周工作计划点2: Know more about SGX

- 完成情况：YES.

- 下周计划：
  1. Reading papers about blob storage
	2. give a sketch of solution of current ideas
	3. Try Minio and read its code( which is a open source blob storage solution)


2017.04.27~2017.05.6

- 本周工作计划点1: Read more papers

- 完成情况： finished.

- 本周工作计划点2: find new idea

- 完成情况： Finished.


- 下周计划：
	1. give a sketch of solution of current ideas

2017.04.20~2017.04.27

- 本周工作计划点1: Know serverless.

- 完成情况： finished.

- 本周工作计划点2: Reading papers and find new ideas/problems.

- 完成情况： Finished.


- 下周计划：
	1. Know serverless and it's tech, and think about what's the benefit with sgx, what's the challenge it might encounter.

>> chyyuu： serverless service+的综述在问题？值得与SGX结合的地方在哪里？目前已有的研究现状如何？ 你对此serverless service+SGX的想法啥？有何创新性？ Tian Hongliang's Ph.D Thesis有关第4章的内容，请分析如何定位问题的，发现了哪些问题，具体解决方法是什么，如何做测试分析评价的，还有哪些问题没有解决，引入了哪些新问题，能否重现其实验结果？希望周四能够看到你的汇报。

如何定位问题
实际在使用SGX 的SDK 开发应用程序时，这些问题很快就会暴露出来。
发现了哪些问题
SGX中的Library OS 需要syscall的支持，而Syscall需要换入换出Enclave
具体解决方法
实现异步的换入换出和可抢占的enclave 内多线程
如何测试分析评价
分别对单线程和多线程的程序进行性能测试。
哪些问题没有解决
SGX 内存过小的问题。

引入了哪些新问题
将非核心功能下放至host 操作系统，SGXkernel 对kernel 的需求更多，attack surface 更大。

重现实验结果
可以基于开源的graphene系统，将他的工作重现，并测试。

2017.04.13~2017.04.20

- 本周工作计划点1: Reading the Intel SGX explained.

- 完成情况： finished.

- 本周工作计划点2: Reading and use the Intel SGX SDK

- 完成情况： Finished.


- 下周计划：
	1. Know serverless and it's tech, and think about what's the benefit with sgx, what's the challenge it might encounter.

2017.04.03~2017.04.13

- 本周工作计划点1: Reading the Intel SGX explained.

- 完成情况： Ongoing.

- 本周工作计划点2: Reading the Kernel driver of SGX

- 完成情况： Finished.


- 下周计划：
	1. Learning to use the SDK in user level.
	2. finished SGX explained



2017.03.06~2017.03.10

- 本周工作计划点1: Finish the paper on OSDI using SGX.

- 完成情况：Finished.




- 下周计划：
	1. Reading the Intel SGX explained
	2. Think about the problem of SGX, and it's mechanism.


- 其他事宜：

Updated paper list.


本周工作进展和下周计划

2017.03.20~2017.04.02 For two weeks

- 本周工作计划点1: Reading the Intel SGX explained.

- 完成情况： Ongoing.

Finished knowing the the Intel architecture, secure attacks, and SGX programming model.


- 下周计划：
	1. Finished the Intel SGX explained
	2. Read the paper recently published about SGX in paper list



2017.03.06~2017.03.10

- 本周工作计划点1: Finish the paper on OSDI using SGX.

- 完成情况：Finished.




- 下周计划：
	1. Reading the Intel SGX explained
	2. Think about the problem of SGX, and it's mechanism.


- 其他事宜：

Updated paper list.

```
chy: 第二周
上周我提出的问题好像没看到解答。 你写的论文阅读报告可进一步清晰和深入，我觉得如可能，需要实验一下，并对照论文再阅读，比如你说性能是问题，具体测试情况如何。
对于你的想法，建议对一个潜在研究方向，建立一个单独的文件进行撰写。重点论文，需要自己尽量理解清楚，了解相关领域研究现状，并能够给大家清晰的讲解（这一点，在我听到的两次你面向大家的汇报中，觉得还有很大提升空间）。

建议看看 MIT的Sanctum : minimal architectural extensions for isolated execution ，并与SGX对比一下。

对于对于论文阅读报告，请写到单独的文档中，一篇论文一个报告。建议写出：

– Summary of major innovations
– What the problems the paper mentioned?
– How about the important related works/papers?
– What are some intriguing aspects of the paper?
– How to test/compare/analyze the results?
– How can the research be improved?
– If you write this paper, then how would you do?
– Did you test the results by yourself? If so, What’s your test Results?
– Give the survey paper list in the same area of the paper your reading.

建议本周能够给大家汇报一次  Virtual Ghost 或 SGX，最好结合实际的实验。

```
