shroud 阅读笔记
保护好用户的数据隐私很重要，一方面data access pattern可能会泄露信息，其次一个数据访问频率会泄露邮件访问频率[6]等
所以推出shroud.
shroud 提供一个分布式的数据块的接口，用户可以get 的数据从1 到N，N最大可以是2^35。复杂的应用可以基于shroud 使用。
为了隐藏用户的access pattern， shroud 使用 ORAM算法。之前的ORAM算法都只能访问几千个文件，shroud 想要访问几千万个10K block，低延迟的。 
shroud 首先使用很多的secure coprocessors 作为client proxy。
其次，shroud 在数据中心中使用新的通信协议，实现一个分布式的，并行的ORAM算法，同时保证ORAM算法安全。
最后，Shroud考虑了如何保证恶意的server不会破坏文件，以及安全协处理器的错误处理。
shroud 是直接部署在大规模硬件上的。

 [6]. “Access pattern disclosure on searchable encryption: Ram- ification, attack and mitigation