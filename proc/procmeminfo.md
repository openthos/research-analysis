# procfs
## proc
### meminfo
meminfo:机器的内存使用信息
```
(example)
cat /proc/meminfo
MemTotal:        8098644 kB   所有可用RAM大小 （即物理内存减去一些预留位和内核的二进制代码大小）
MemFree:         2256520 kB   LowFree与HighFree的总和，被系统留着未使用的内存
MemAvailable:    5212720 kB   
Buffers:          764376 kB   用来给文件做缓冲大小
Cached:          2582784 kB   被高速缓冲存储器（cache memory）用的内存的大小
SwapCached:            0 kB   被高速缓冲存储器（cache memory）用的交换空间的大小 已经被交换出来的内存，但仍然被存放在swapfile中。用来在需要的时候很快的被替换而不需要再次打开I/O端口
Active:          3916628 kB   在活跃使用中的缓冲或高速缓冲存储器页面文件的大小
Inactive:        1416784 kB
Active(anon):    1989080 kB
Inactive(anon):   455696 kB
Active(file):    1927548 kB
Inactive(file):   961088 kB
Unevictable:         176 kB
Mlocked:             176 kB
SwapTotal:       2928636 kB   交换空间的总大小
SwapFree:        2928636 kB
Dirty:               232 kB   等待被写回到磁盘的内存大小
Writeback:             0 kB   正在被写回到磁盘的内存大小
AnonPages:       1986424 kB   未映射页的内存大小
Mapped:           949956 kB   设备和文件等映射的大小
Shmem:            458552 kB
Slab:             368420 kB   内核数据结构缓存的大小，可以减少申请和释放内存带来的消耗
SReclaimable:     320980 kB   可收回Slab的大小
SUnreclaim:        47440 kB
KernelStack:       11392 kB
PageTables:        54132 kB   管理内存分页页面的索引表的大小
NFS_Unstable:          0 kB   不稳定页表的大小
Bounce:                0 kB
WritebackTmp:          0 kB
CommitLimit:     6977956 kB
Committed_AS:    7573536 kB
VmallocTotal:   34359738367 kB   可以vmalloc虚拟内存大小
VmallocUsed:      308296 kB
VmallocChunk:   34358947836 kB
HardwareCorrupted:     0 kB
AnonHugePages:    739328 kB
CmaTotal:              0 kB
CmaFree:               0 kB
HugePages_Total:       0
HugePages_Free:        0
HugePages_Rsvd:        0
HugePages_Surp:        0
Hugepagesize:       2048 kB
DirectMap4k:      162640 kB
DirectMap2M:     7100416 kB
DirectMap1G:     1048576 kB
```        

