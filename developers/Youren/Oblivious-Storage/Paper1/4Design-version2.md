### Basic system architecture
在上一个章节中我们看到我们已经可以简单的基于Intel SGX构建一个DHT的存储系统，但是这样的系统无法防止流量分析和一个active 的攻击者。

前文已经说到，对于每个用户请求，机器之间的通信每次都使用不同的同步秘钥，因此攻击者无法从密文中推断出信息。但是攻击者还是可能从数据包的大小得出数据包之间的关系并进行追踪，找到用户请求发往的机器。因此我们将Object分为固定大小的chunk，保证集群中所有的通信都是通过同样大小的数据包发送。大小不足的数据包则进行padding后再加密。

为了追踪磁盘上的数据，我们对每个Object维护一个Index。所有的Object的Index 组成一个列表。一个Index包括Object对应的每个chunk的MAC值和对应chunk的存储位置，以及加密秘钥。这些加密秘钥是在存储文件时随机生成的。

为了应对真实世界中时常发生的crash等，系统中需要部署一些crash恢复机制：将Indexs使用Sealing  key存储在持久化存储中，当机器crash重启后，从磁盘中读取Indexs并标记为不安全，不安全的Index可以通过其他的机器验证。这不是这篇论文主要讨论的。

### Randomly store file
一个固定位置的object无法防止攻击者通过流量分析来定位。拥有较热对象的机器总是会有更多的入流量。因此我们需要将object的位置随机存储。
随机存储的含义包括对于每一次用户请求的读写，我们都需要修改文件的位置。

但是在DHT中，每个机器都可能接到用户的请求，如果将用户数据的存储位置随机化，如何让每个机器都知道当前文件的位置呢？
我们将key -> hash之后负责处理的机器作为该文件存储的代理，每个机器接收到用户请求后将请求发给该机器，我们称该机器为这个object的index location，记该机器为Mk。
在Mk中，存储着每个object当前的每个chunk的storage loaction，这个storage location代表着当前chunk存储的位置。而这个location是随机生成的。
当一个用户的写请求到达Mk时，Mk检查该object是否存在，如果不存在则随机生成一个storage location，并将chunk存储在这个location对应的三台机器中。如果用户的读请求请求不存在的object，则返回错误。
当用户的读写请求到达Mk，并且Mk存在时，Mk从index 中读取当前storage location，并且随机生成一个new storage location，sl‘。将请求和sl’发送给storage location的机器。storage location 的机器接收到请求后，将数据（如果是写请求则将用户请求中的数据，如果是读请求则是storage location上的数据）发送到Sl’上。sl‘处理完后发回结果给storage location的机器。storage location 机器将结果返回给 index server。Index 收到处理完成的请求之后，将sl替换为sl’。

我们之后会看到，这样做的好处是：sl’不需要直接和index server通信，如果能够隐藏sl的位置，则sl’也保护起来了。

这样做的缺陷是我们无法保护Index location，因此Index server是暴露给攻击者的，包括其DHT。

### Hide direct connection
如果Index server直接访问存储文件的位置，攻击者可以随机deny 一些请求，如果该请求无法返回则可以认为对应的机器是对应的文件。因此我们需要将关键index server发出和返回的数据包的真实位置隐藏起来。因此我们规定，当index 在和storage server通信时，随机选取一台机器作为proxy，代为转发请求。

这样做的好处是，一个是即使攻击者知道哪个数据包负责了用户的请求，也无法通过index server直接知道：其必须通过proxy来找到，而Proxy的机器范围是index server一次发出的数据包的机器，因此攻击者无法对大规模的机器进行攻击。


当旧的storage server 处理完请求的结果之后，将结果返回给index Server时，依然需要转发。


###Hide replica/DHT
Replic如果暴露给攻击者，那么攻击者可以随机的crash三台机器，因此我们还想将replication给隐藏起来。
首先是crash 恢复机制，我们使用virutual node。
某个机器同时联络三个replic，也可能会照成信息泄露。因此任意一个机器如果需要同时和三个replic通信，都随机的选取三个机器做中转。
