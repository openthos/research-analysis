## Problem Definiation

#### User request
从高层次看，我们的系统是一个Key-value store。用户的数据以Object的形式存储起来， 每个Object通过Key决定存储位置。远端的用户通过get(key), put(key, value)来获取文件。
每个用户在向服务器发送请求时，通过一个IP层的load-balance随机选择集群中的任意一台机器进行通信。 Client 中拥有PKca，每次和server的连接都采用标准的SSL通信流程：先协商同步秘钥，之后再使用该同步秘钥加密通信。因此每次请求都会使用不同的秘钥。与用户通信的机器收到用户的请求之后，成为一个代理delegation，通过key找到对应的机器，并请对应机器完成请求后返回给用户。 这个过程对于用户来说是透明的。
我们希望系统可以兼容已有的API，当Client简单地只是想要将数据安全的存储在云端，则通过像传统的对象存储系统一样的API工作。例如一个service provider 需要将存储的数据开放给公众用户使用。
在此，我们将用户请求，数据包，和网络包描述清楚。用户请求是指一个client 通过API发起一个对数据进行操作的请求。数据包是指，机器与机器之间通信时发送的加密数据。而网络包则是网络层的概念。 

#### Harden System with Intel SGX

我们采用DHT的方式组织整个系统，DHT中每个机器都是对等的，同时DHT的系统可以很好的横向拓展(horizontal scaling)。DHT集群中机器的状态使用Goissip协议维护。

其中一个问题是如何使机器之间互相信任，并通信。Intel SGX中的remote attestation 机制可以让两个机器之间互相验证身份，并且建立一个可靠地连接。但是server之间每次都使用remote attestation会带来以下几个问题：
1. remote attestation需要向Intel remote attestation service请求，带来较大的延迟
2. 每个机器之间互相验证会导致系统的维护变得复杂O(n2)

为了避免机器之间每次通信都需要用remote attestation，我们将PKI机制和remote attestation机制相结合。 在部署集群时，设置一个CA。当集群中每个机器启动的时候，首先在Enclave中生成一个公私钥对PK,，以及对应的certificate 文件。而后向CA发送一个attestation，CA检验过server的attestation report之后，对Server的Certificate 文件进行签名。 每个server在编程的时候，都需要将PKca hard  code在Enclave中，这样做可以避免server信任错误的机器，保证public key不会被替换。
对于用户来说，他信任CA，所以他可以不用在乎集群中的Intel SGX技术，只使用SSL进行通信。另一方面，用户使用SGX remote attestation可能会带来隐私的忧虑。[remoteinsuff]

每个机器上的程序分为两个部分，安全部分和非安全部分。由于安全部分不能直接操作IO，因此，非安全部分负责网络通信和磁盘读写。安全部分从内存中读出数据或写回。在实现中我们会描述，如何控制能够高效且安全的在安全部分和非安全部分进行交互。
Intel SGX并不是必须的技术，任何一种可以保护程序安全运行的技术都可以使用。只要能够保证敏感数据的处理是安全且不会被窥探。

### Threat Model（攻击者有什么能力，我们的目标是防止什么攻击）
我们认为cloud service provider的公司是正直的，但是cloud service 内部并不是所有员工都是可信的。破坏用户的系统取得坏名声损害自己的利益并不是一个正规的cloud service 公司愿意做的。攻击者控制着集群中所有机器的存储系统的不安全部分，但是无法access 安全部分的内容。
文件的confidential 和 Integrity通过在Intel SGX内部进行加密保证，但是如果程序崩溃则无法保证 Freshness。 因此攻击者想要进行Rollback attack需要：
1， 修改磁盘数据。2，破坏程序安全部分的运行。
一旦安全部分的数据丢失了，则失去了对存储文件状态的跟踪，导致攻击者可以实施攻击。

攻击者可以恶意的破坏某些机器，使其发生 temporary failure or permanent failure，使用的手段包括DoS或者恶意crash，并将这些行为伪装成系统正常的failure：在系统中，failure总是会发生。但是攻击者不能同时大规模地恶意攻击集群中所有的机器，这不正常。

因此攻击者想要找到目标文件对应的机器，并实施Rollback攻击。

为了防止攻击者找到目标，我们修改Oblivious store的安全定义：对于Client 的一个请求的数据Di，攻击者假设其请求的机器是M0，M1，M2，猜中的概率是
p(n)- C3n < e e是无穷小的数。

攻击者不能知道请求是否被成功的处理了—— 一个timeout是需要的。

这个定义中隐藏的意义是：攻击者无法确定负责请求的是集群中某些机器。因为如果攻击者知道该请求由某个子集负责，则其下一次可以可以找到下一个子集并对两个子集求交集，直到交集中只有一台机器。所以通过这个定义，我们提供的是一个All-or-none的防御：攻击者需要crash 所有的机器，不然的话无法找到自己的文件。

攻击者可以知道集群中每个机器每时每刻在和哪台机器通信，也知道哪些机器向哪个磁盘进行了存储。但是因为攻击者不知道机器之间通信的秘钥，因此无法得知机器通信的内容和存储的内容，同时也无法将一个数据包的目标机器改变——其他机器并不知道对应通信的秘钥。同时因为机器之间通信有一个nonce防止reply 攻击。
攻击者可以想办法对流量进行跟踪，或者对系统中的网络信息和磁盘信息进行统计分析。以及通过crash或DoS部分机器破坏系统的正常执行，来寻找自己需要的数据。

攻击者会对单机进行side channel攻击，例如通过memory access pattern猜出数据包发送的位置，因此我们也需要降低这种攻击发生的可能性。

我们并不处理针对硬件本身的攻击，所有针对硬件攻击的防护均来自Intel SGX。Intel SGX技术本身存在于CPU内部，而对于CPU内部本身的逆向工程和破解依然难以实现。

### Challenge(Why it's hard).
尽管我们将文件的处理过程都交给Intel SGX保护，但是一个更加强力的攻击者依然有很多方法可以找到文件对应的位置。
攻击者可以通过长时间的流量分析来找到文件可能的位置。尽管有副本存在，攻击者依然可能通过crash其中一个副本，再通过流量分析找到另外两个副本。[traffic analysis papers]
