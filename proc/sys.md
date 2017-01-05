# procfs
## sys
Access to dynamically-configurable kernel options under /proc/sys. 
Under /proc/sys appear directories representing the areas of kernel, containing readable and writable virtual files.
For example, a commonly referenced virtual file is /proc/sys/net/ipv4/ip_forward, because it is necessary for routing firewalls or tunnels. The file contains either a '1' or a '0': if it is 1, the IPv4 stack forwards packets not meant for the local host, if it is 0 then it does not.

目录下的文件不仅能提供系统的有关信息，而且还允许用户立即停止或开启内核的某些特性及功能。

/proc/sys/net/子目录更是与网络息息相关，我们可以通过设置此目录下的某些文件来开启与网络应用相关的特殊功能，同时，也可以通过设置这个目录下的某些文件来保护我们的网络安全。


### abi 
### crypto  
### debug
### dev
### fs
### kernel
### net
/proc/sys/net

 The interface to the networking parts of the kernel is located in /proc/sys/net. The following table shows all possible subdirectories. You may see only some of them, depending on your kernel's configuration. Our main focus will be on IP networking since AX15, X.25, and DEC Net are only minor players in the Linux world. Should you wish review the online documentation and the kernel source to get a detailed view of the parameters for those protocols not covered here. In this section we'll discuss the subdirectories listed above. As default values are suitable for most needs, there is no need to change these values.



#### core
Network core options

##### bpf_jit_enable
基于时间规则的编译器，用于基于PCAP（packet capture library）并使用伯克利包过滤器（Berkeley Packet Filter，如tcpdump）的用户工具，可以大幅提升复杂规则的处理性能。
0：禁止
1：开启
2：开启并请求编译器将跟踪数据时间写入内核日志

##### bpf_jit_harden
##### busy_poll
默认对网络设备进行poll和select操作的超时时间(us)，具体数值最好以sockets数量而定


##### busy_read
默认读取在设备帧队列上数据帧的超时时间(us)，推荐值：50

##### default_qdisc
##### dev_weight
Work quantum for packet processing scheduler. The default value is 64.


##### flow_limit_cpu_bitmap
##### flow_limit_table_len
##### max_skb_frags

##### message_burst
A higher message_cost factor, results in fewer messages that will be written.
设置每十秒写入多少次请求警告；此设置可以用来防止DOS攻击
##### message_cost
 These parameters are used to limit the warning messages written to the kernel log from the networking code. They enforce a rate limit to make a denial-of-service attack impossible.  Message_burst controls when messages will be dropped. The default settings limit warning messages to one every five seconds.
 设置每一个警告的度量值，缺省为5，当用来防止DOS攻击时设置为0
##### netdev_budget
每次软中断处理的网络包个数

##### netdev_max_backlog
Maximum number of packets, queued on the INPUT side, when the interface receives packets faster than kernel can process them.
设置当个别接口接收包的速度快于内核处理速度时允许的最在的包序列，缺省为300；
```
cat netdev_max_backlog 
1000

```

##### netdev_rss_key
##### netdev_tstamp_prequeue
##### optmem_max
Maximum ancillary buffer size allowed per socket. Ancillary data is a sequence of struct cmsghdr structures with appended data.
设置每个socket的最大补助缓存大小,
表示每个socket所允许的最大缓冲区的大小(字节)

##### rmem_default
The default setting of the socket receive buffer in bytes.

##### rmem_max
The maximum receive socket buffer size in bytes.

##### rps_sock_flow_entries
##### somaxconn
##### tstamp_allow_data
##### warnings
##### wmem_default
The default setting (in bytes) of the socket send buffer.

##### wmem_max
The maximum send socket buffer size in bytes.

##### xfrm_acq_expires
##### xfrm_aevent_etime
##### xfrm_aevent_rseqth
##### xfrm_larval_drop


#### ipv4

##### cipso_cache_bucket_size
cipso_cache_enable
cipso_rbm_optfmt
cipso_rbm_strictvalid
##### conf
fib_multipath_use_neigh
fwmark_reflect
##### icmp_echo_ignore_all
##### icmp_echo_ignore_broadcasts
设置内核不应答icmp echo包，或指定的广播，值为0是允许回应，值为1是禁止；
Turn on (1) or off (0), if the kernel should ignore all ICMP ECHO requests, or just those to broadcast and multicast addresses.

Please note that if you accept ICMP echo requests with a broadcast/multicast destination address your network may be used as an exploder for denial of service packet flooding attacks to other hosts.

##### icmp_errors_use_inbound_ifaddr


##### icmp_ignore_bogus_error_responses
默认值是0.
某些路由器违背RFC1122标准，其对广播帧发送伪造的响应来应答。这种违背行为通常会被以告警的方式记录在系统日志中。如果该选项设置为True，内核不会记录这种警告信息。(我个人而言推荐设置为1)

icmp_msgs_burst
icmp_msgs_per_sec
##### icmp_ratelimit
限制发向特定目标的匹配icmp_ratemask的ICMP数据报的最大速率。0表示没有任何限制，否则表示jiffies数据单位中允许发送的个数。(如果在icmp_ratemask进行相应的设置Echo Request的标志位掩码设置为1,那么就可以很容易地做到ping回应的速度限制了)

icmp_ratemask
igmp_link_local_mcast_reports
igmp_max_memberships
igmp_max_msf
igmp_qrv
##### inet_peer_maxttl
##### inet_peer_minttl
##### inet_peer_threshold
INET对端存储器某个合适值，当超过该阀值条目将被丢弃。该阀值同样决定生存时间以及废物收集通过的时间间隔。条目越多﹐存活期越低﹐GC 间隔越短

##### ip_default_ttl
默认值为 64.
表示IP数据报的Time To Live值(在网络传递中,每经过一"跳",该值减少1,当ttl为0的时候，丢弃该包.该值越大,即在网络上可以经过的路由器设备的数量越多,但一个错误的包，也会越发浪费生存周期.根据目前的实际情形而看，设置为32已经足够普通网络访问Internet的需求了)

##### ip_dynaddr
默认值是0,
假如甚至为非0值,那么将支持动态地址.如果是设置为>1的值,将在动态地址改写的时候发一条内核消息。(如要用动态界面位址做 dail-on-demand ﹐那就设定它。一旦请求界面起来之
后﹐所有看不到回应的本地 TCP socket 都会重新捆绑(rebound)﹐以获得正确的位址。
假如遇到该网络界面的连线不工作﹐但重新再试一次却又可以的情形﹐设定这个可解决这
个问题。)


ip_early_demux
##### ip_forward
Enable or disable forwarding of IP packages between interfaces. Changing this value resets all other parameters to their default values. They differ if the kernel is configured as host or router.

ip_forward_use_pmtu

#### ipfrag_high_thresh
##### ipfrag_low_thresh

用来组装分段的IP包的最大内存量。两个文件分别表示用于重组IP分段的内存分配最低值和最高值，一旦达到最高内存分配值，其它分段将被丢弃，直到达到最低内存(ipfrag_low_thresh 见下文)分配值。

(根据我个人理解,就是达到最高后,就"关门打狗",直到处理到最低值的时候才又开门放分段的ip包进来处理.如果最高/最低差距过小,很可能很快又达到限制又开始丢弃包;而设置过大,又会造成某段时间丢包时间持续过久.因此需要适当地考虑,默认值中给出的最低/最高比率值为3/4.此外补充说明,kernel中,对内存的使用单位,都是以byte为单位的.当TCP数据包传输发生错误时，开始碎片整理。有效的数据包保留在内存，同时损坏的数据包被转发。我在1G内存的NAT机器上,分别设置最低为262144,最高为393216)


ipfrag_max_dist
ipfrag_secret_interval
##### ipfrag_time
保存一个IP分片在内存中的时间。
##### ip_local_port_range
Range of ports used by TCP and UDP to choose the local port. Contains two numbers, the first number is the lowest port, the second number the highest local port. Default is 1024-4999. Should be changed to 32768-61000 for high-usage systems.

定于TCP和UDP使用的本地端口范围，第一个数是开始，第二个数是最后端口号，默认值依赖于系统中可用的内存数：
\> 128Mb 32768-61000
1024-4999 or even less.
该值决定了活动连接的数量，也就是系统可以并发的连接数(做nat的时候,我将它设置为了1024 65530 工作正常)

ip_local_reserved_ports
ip_nonlocal_bind
##### ip_no_pmtu_disc
默认值为FALSE(0)
关闭路径MTU探测(典型的瓶颈原理,一次成功的传输中,mtu是由网络上最"窄"的位置决定的.如果IP层有一个数据报要传，而且数据的长度比链路层的MTU还大，那么IP层就需要进行分片（fragmentation），把数据报分成若干片，这样每一片都小于MTU。



```
16Mb/ s令牌网(IBM)　　17914
4Mb/ s令牌网(IEEE 802.5)　4464
FDDI　　　　　　　　　 4352
以太网　　　　　　　　 1500
IEEE 802.3/802.2　　　　　1492
X.25　　　　　　　　　　576
点对点(低延时)　　　　　296
```




##### neigh
ping_group_range
##### route
tcp_abort_on_overflow
tcp_adv_win_scale
tcp_allowed_congestion_control
tcp_app_win
tcp_autocorking
tcp_available_congestion_control
tcp_base_mss
tcp_challenge_ack_limit
tcp_congestion_control
tcp_dsack
tcp_early_retrans
##### tcp_ecn

 This file controls the use of the ECN bit in the IPv4 headers, this is a new feature about Explicit Congestion Notification, but some routers and firewalls block traffic that has this bit set, so it could be necessary to echo 0 to /proc/sys/net/ipv4/tcp_ecn, if you want to talk to this sites. For more info you could read RFC2481.
 
tcp_ecn_fallback
tcp_fack
tcp_fastopen
tcp_fastopen_key
tcp_fin_timeout
tcp_frto
tcp_fwmark_accept
tcp_invalid_ratelimit
tcp_keepalive_intvl
tcp_keepalive_probes
tcp_keepalive_time
tcp_limit_output_bytes
tcp_low_latency
tcp_max_orphans
tcp_max_reordering
tcp_max_syn_backlog
tcp_max_tw_buckets
tcp_mem
tcp_min_rtt_wlen
tcp_min_tso_segs
tcp_moderate_rcvbuf
tcp_mtu_probing
tcp_no_metrics_save
tcp_notsent_lowat
tcp_orphan_retries
tcp_pacing_ca_ratio
tcp_pacing_ss_ratio
tcp_probe_interval
tcp_probe_threshold
tcp_recovery
tcp_reordering
tcp_retrans_collapse
##### tcp_retries1
Defines how often an answer to a TCP connection request is retransmitted before giving up.


##### tcp_retries2
Defines how often a TCP packet is retransmitted before giving up.


tcp_rfc1337
tcp_rmem
tcp_sack
tcp_slow_start_after_idle
tcp_stdurg
tcp_synack_retries
tcp_syncookies
tcp_syn_retries
tcp_thin_dupack
tcp_thin_linear_timeouts
tcp_timestamps
tcp_tso_win_divisor
tcp_tw_recycle
tcp_tw_reuse
tcp_window_scaling
tcp_wmem
tcp_workaround_signed_windows
udp_mem
udp_rmem_min
udp_wmem_min
xfrm4_gc_thresh


#### ipv6
#### netfilter
#### nf_conntrack_max
#### unix


### sunrpc
### vm
