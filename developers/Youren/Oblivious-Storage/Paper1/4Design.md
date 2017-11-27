
## Basic system architecture
在上一个章节中我们看到我们已经可以简单的基于Intel SGX构建一个DHT的存储系统，但是这样的系统无法防止流量分析和一个强有力的active 的攻击者。

前文已经说到，对于每个用户请求，机器之间的通信每次都使用不同的同步秘钥，因此攻击者无法从密文中推断出信息。但是攻击者还是可能从数据包的大小得出数据包之间的关系并进行追踪，找到用户请求发往的机器。因此我们将Object分为固定大小的chunk，保证集群中所有的通信都是通过同样大小的数据包发送。大小不足的数据包则进行padding后再加密。

为了能够保证用户的数据没有被篡改，我们对每个Object维护一个Index。所有的Object的Index 组成一个列表。一个Index包括Object对应的每个chunk的MAC值和对应chunk的存储位置，以及加密秘钥。这些加密秘钥是在存储文件时随机生成的。
为了应对真实世界中时常发生的crash等，系统中需要部署一些crash恢复机制：将Indexs使用Sealing  key存储在持久化存储中，当机器crash重启后，从磁盘中读取Indexs并标记为不安全，不安全的Index可以通过其他的机器验证。这不是这篇论文主要讨论的。

## Split key and value
作为一个Cloud Storage，通常都是提供public service。 因此我们认为Client是不可信的，攻击者可以知道自己的访问频率。因此，攻击者

每一次对文件的read，write或者modify都看做一个新的数据产生。

## One layer Mix Network
为什么这么做
好处
可能带来的代价

## Virtual Node
攻击者可能想随意破坏一些数据。
普通的DHT中攻击者随意的删除文件。
