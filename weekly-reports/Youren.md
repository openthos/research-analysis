本周工作进展和下周计划
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
