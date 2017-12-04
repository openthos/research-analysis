
##abstract
It's important to hide outsourcing data's location to prevent unauthorized touch. Hence we present Yard, a distributed storage system based on Intel SGX and distributed hash table. Our system provide high security meantime maintain reliability and horizontal scaliability with a more powerful active adversary who controls whole cluster and crash part of system.  
To address such adversary, we enhance the definiation of the oblivious store: with each request, the sever don't konw which group of machine are handling it. we achieve this with the oblivious shuffle inside Intel SGX.
At last, we discuss such system's application in real world.

## Introduction
1. 故事背景
2. cloud，也可以用在公司内部。
秘钥不是client自己管理，方便分享。

3. Yard 是什么
4. 为什么不用ME/TPM counter
Counter 和merkle tree 是违反storage并行性的。

5. 为什么不用Oblivious RAM。 Oblivious不能防止攻击者的攻击。同时
6. Crash，攻击者可能是active的。

4. Yard怎么做的。

5.  Scaliability 很重要。

6. 威胁模型的改变：client可能不可信。Crash会发生。

7. 带来的挑战

8. contribution



## Background Related work
###Background
Intel SGX 保护什么，不保护什么
Sealing key and performance
加密过程不会成为系统的瓶颈。


###Related work
Oblivious store : shroud, oblivstore, taostore
Intel sgx rollback protection: ROTE.
WatchIT
## Problem Definiation


### Execution Model(What's this system for)

### Threat Model

### Challenge(Why it's hard).

## Design
证明这么做效率高于oblivious RAM.
### Basic system architecture

To protect user's data from
Gossip protocal
### Router
### Virtual Node
### Store content randomly

### Optimization
bloom-filter 加速查询
stash在index上。
## Implementation
### Oblivious batch shuffle algroithm
####Timer problem.

###Seq of opeartion
####Access 的过程

## Security analysis
### 转发数量\batch 数量
###可能的攻击方式：修改包的数量，dos。


## evaluation
加密带来的开销
如何优化加密
协议带来的开销

## Future work
data model
object Storage-> relational model
## Experiment
