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

### stat
stat:实时追踪自系统上次启动以来的多种统计信息
```
(example)
cat /proc/stat
cpu  2018907 8270 2713334 37434321 169720 0 4332 0 0 0   八个值分别表示以1/100（jiffies）秒为单位的统计值(依次为：user（用户太时间）、nice（nice值为负的进程所占用的CPU时间）、system（核心）、idle（除硬盘IO等待时间以外其它等待时间）、iowait、irq（硬中断时间）、softirq（软中断时间）)
cpu0 515361 2314 683293 9322930 39474 0 1482 0 0 0
cpu1 508524 1140 679219 9351987 51097 0 760 0 0 0
cpu2 499244 2783 675439 9372749 42000 0 1973 0 0 0
cpu3 495776 2032 675382 9386654 37147 0 116 0 0 0
intr 772741507 22 11 0 0 0 0 0 0 1 0 0 0 2 0 0 0 0 0 59 311201 0 0 0 0 0 0 0 107111 542126 3240772 8530961 21 591 663 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0     中断的信息，第一个为自系统启动以来，发生的所有的中断的次数；然后每个数对应一个特定的中断自系统启动以来所发生的次数
ctxt 4042696239   自系统启动以来CPU发生的上下文交换的次数
btime 1483494110  从系统启动到现在为止的时间，单位为秒
processes 19373   系统启动以来所创建的任务的个数目
procs_running 1   当前运行队列的任务的数目
procs_blocked 0   当前被阻塞的任务的数目
softirq 48508837 5 18240586 21946 3278362 596054 0 18229 16346722 0 10006933

```

### swaps 
swaps:系统上的交换分区及其空间利用信息，如果有多个交换分区的话，则会每个交换分区的信息分别存储于/proc/swap目录中的单独文件中，而其优先级数字越低，被使用到的可能性越大
```
(example)
cat /proc/swaps
Filename		Type		Size	  Used 	Priority
/dev/sda6   partition	 2928636	  0	     -1
```

### cmdline
cmdline:在启动时传递至内核的相关参数信息,这些信息通常由lilo或grub等启动管理工具进行传递
```
(example)
cat /proc/amdline
BOOT_IMAGE=/vmlinuz-4.2.0-42-generic root=UUID=600a1c05-f70e-475b-9cc6-0579a3756133 ro quiet splash vt.handoff=7
```
### uptime
uptime:系统上次启动以来的运行时间，如下所示，其第一个数字表示系统运行时间，第二个数字表示系统空闲时间，单位是秒
```
(example)
cat /proc/uptime
110815.76 394338.98
```
### version
version:系统运行的内核版本号
```
(example)
cat /proc/version
Linux version 4.2.0-42-generic (buildd@lgw01-54) (gcc version 5.2.1 20151010 (Ubuntu 5.2.1-22ubuntu2) ) #49-Ubuntu SMP Tue Jun 28 21:26:26 UTC 2016
```
### mounts
mounts:系统当前挂载的所有文件系统.第一列表示挂载的设备，第二列表示在当前目录树中的挂载点，第三点表示当前文件系统的类型，第四列表示挂载属性（ro或者rw），第五列和第六列用来匹配/etc/mtab文件中的转储（dump）属性
```
(example)
cat /proc/mounts
sysfs      /sys  sysfs rw,nosuid,nodev,noexec,relatime 0 0
proc       /proc proc rw,nosuid,nodev,noexec,relatime 0 0
udev       /dev devtmpfs rw,nosuid,relatime,size=4031008k,nr_inodes=1007752,mode=755 0 0
devpts     /dev/pts devpts rw,nosuid,noexec,relatime,gid=5,mode=620,ptmxmode=000 0 0
tmpfs      /run tmpfs rw,nosuid,noexec,relatime,size=809868k,mode=755 0 0
/dev/sda1  /ext4 rw,relatime,errors=remount-ro,data=ordered 0 0
/dev/sda9  /usr ext4 rw,relatime,data=ordered 0 0
securityfs /sys/kernel/security securityfs rw,nosuid,nodev,noexec,relatime 0 0
tmpfs      /dev/shm tmpfs rw,nosuid,nodev 0 0
tmpfs      /run/lock tmpfs rw,nosuid,nodev,noexec,relatime,size=5120k 0 0
tmpfs      /sys/fs/cgroup tmpfs rw,mode=755 0 0
cgroup     /sys/fs/cgroup/systemd cgroup rw,nosuid,nodev,noexec,relatime,xattr,release_agent=/lib/systemd/systemd-cgroups-agent,name=systemd 0 0
pstore     /sys/fs/pstore pstore rw,nosuid,nodev,noexec,relatime 0 0
cgroup     /sys/fs/cgroup/hugetlb cgroup rw,nosuid,nodev,noexec,relatime,hugetlb,release_agent=/run/cgmanager/agents/cgm-release-agent.hugetlb 0 0
cgroup     /sys/fs/cgroup/memory cgroup rw,nosuid,nodev,noexec,relatime,memory 0 0
cgroup     /sys/fs/cgroup/perf_event cgroup rw,nosuid,nodev,noexec,relatime,perf_event,release_agent=/run/cgmanager/agents/cgm-release-agent.perf_event 0 0
cgroup     /sys/fs/cgroup/devices cgroup rw,nosuid,nodev,noexec,relatime,devices 0 0
cgroup     /sys/fs/cgroup/net_cls,net_prio cgroup rw,nosuid,nodev,noexec,relatime,net_cls,net_prio 0 0
cgroup     /sys/fs/cgroup/blkio cgroup rw,nosuid,nodev,noexec,relatime,blkio 0 0
cgroup     /sys/fs/cgroup/cpu,cpuacct cgroup rw,nosuid,nodev,noexec,relatime,cpu,cpuacct 0 0
cgroup     /sys/fs/cgroup/freezer cgroup rw,nosuid,nodev,noexec,relatime,freezer 0 0
cgroup     /sys/fs/cgroup/cpuset cgroup rw,nosuid,nodev,noexec,relatime,cpuset,clone_children 0 0
systemd-1  /proc/sys/fs/binfmt_misc autofs rw,relatime,fd=22,pgrp=1,timeout=0,minproto=5,maxproto=5,direct 0 0
mqueue     /dev/mqueue mqueue rw,relatime 0 0
hugetlbfs  /dev/hugepages hugetlbfs rw,relatime 0 0
debugfs    /sys/kernel/debug debugfs rw,relatime 0 0
fusectl    /sys/fs/fuse/connections fusectl rw,relatime 0 0
/dev/sda8  /var ext4 rw,relatime,data=ordered 0 0
/dev/sda7  /srv ext4 rw,relatime,data=ordered 0 0
/dev/sda10 /usr/local ext4 rw,relatime,data=ordered 0 0
/dev/sda2  /boot ext4 rw,relatime,stripe=4,data=ordered 0 0
/dev/sda5  /opt ext4 rw,relatime,data=ordered 0 0
/dev/sda3  /home ext4 rw,relatime,data=ordered 0 0
cgmfs      /run/cgmanager/fs tmpfs rw,relatime,size=100k,mode=755 0 0
binfmt_misc /proc/sys/fs/binfmt_misc binfmt_misc rw,relatime 0 0
tmpfs      /run/user/1000 tmpfs rw,nosuid,nodev,relatime,size=809868k,mode=700,uid=1000,gid=1000 0 0
gvfsd-fuse /run/user/1000/gvfs fuse.gvfsd-fuse rw,nosuid,nodev,relatime,user_id=1000,group_id=1000 0 0

```
### modules
modules:当前装入内核的所有模块名称列表，可以由lsmod命令使用，也可以直接查看；如下所示，其中第一列表示模块名，第二列表示此模块占用内存空间大小，第三列表示此模块有多少实例被装入，第四列表示此模块依赖于其它哪些模块，第五列表示此模块的装载状态（Live：已经装入；Loading：正在装入；Unloading：正在卸载），第六列表示此模块在内核内存（kernel memory）中的偏移量
```
(example)
cat /proc/modules
pci_stub 16384 1 - Live 0x0000000000000000
vboxpci 24576 0 - Live 0x0000000000000000 (OE)
vboxnetadp 28672 0 - Live 0x0000000000000000 (OE)
vboxnetflt 28672 0 - Live 0x0000000000000000 (OE)
vboxdrv 454656 3 vboxpci,vboxnetadp,vboxnetflt, Live 0x0000000000000000 (OE)
binfmt_misc 20480 1 - Live 0x0000000000000000
intel_rapl 20480 0 - Live 0x0000000000000000
x86_pkg_temp_thermal 16384 0 - Live 0x0000000000000000
intel_powerclamp 16384 0 - Live 0x0000000000000000
coretemp 16384 0 - Live 0x0000000000000000
kvm_intel 167936 0 - Live 0x0000000000000000
kvm 516096 1 kvm_intel, Live 0x0000000000000000
snd_hda_codec_hdmi 49152 1 - Live 0x0000000000000000
snd_hda_codec_realtek 86016 1 - Live 0x0000000000000000
crct10dif_pclmul 16384 0 - Live 0x0000000000000000
snd_hda_codec_generic 77824 1 snd_hda_codec_realtek, Live 0x0000000000000000
crc32_pclmul 16384 0 - Live 0x0000000000000000
snd_hda_intel 36864 7 - Live 0x0000000000000000
dcdbas 16384 0 - Live 0x0000000000000000
snd_hda_codec 135168 4 snd_hda_codec_hdmi,snd_hda_codec_realtek,snd_hda_codec_generic,snd_hda_intel, Live 0x0000000000000000
snd_hda_core 65536 5 snd_hda_codec_hdmi,snd_hda_codec_realtek,snd_hda_codec_generic,snd_hda_intel,snd_hda_codec, Live 0x0000000000000000
dell_smm_hwmon 16384 0 - Live 0x0000000000000000
snd_hwdep 16384 1 snd_hda_codec, Live 0x0000000000000000
sb_edac 28672 0 - Live 0x0000000000000000
aesni_intel 167936 0 - Live 0x0000000000000000
snd_pcm 106496 5 snd_hda_codec_hdmi,snd_hda_intel,snd_hda_codec,snd_hda_core, Live 0x0000000000000000
snd_seq_midi 16384 0 - Live 0x0000000000000000
snd_seq_midi_event 16384 1 snd_seq_midi, Live 0x0000000000000000
aes_x86_64 20480 1 aesni_intel, Live 0x0000000000000000
lrw 16384 1 aesni_intel, Live 0x0000000000000000
snd_rawmidi 32768 1 snd_seq_midi, Live 0x0000000000000000
gf128mul 16384 1 lrw, Live 0x0000000000000000
snd_seq 69632 2 snd_seq_midi,snd_seq_midi_event, Live 0x0000000000000000
edac_core 53248 1 sb_edac, Live 0x0000000000000000
glue_helper 16384 1 aesni_intel, Live 0x0000000000000000
snd_seq_device 16384 3 snd_seq_midi,snd_rawmidi,snd_seq, Live 0x0000000000000000
snd_timer 32768 2 snd_pcm,snd_seq, Live 0x0000000000000000
snd 81920 24 snd_hda_codec_hdmi,snd_hda_codec_realtek,snd_hda_codec_generic,snd_hda_intel,snd_hda_codec,snd_hwdep,snd_pcm,snd_rawmidi,snd_seq,snd_seq_device,snd_timer, Live 0x0000000000000000
ablk_helper 16384 1 aesni_intel, Live 0x0000000000000000
input_leds 16384 0 - Live 0x0000000000000000
soundcore 16384 1 snd, Live 0x0000000000000000
cryptd 20480 2 aesni_intel,ablk_helper, Live 0x0000000000000000
serio_raw 16384 0 - Live 0x0000000000000000
lpc_ich 24576 0 - Live 0x0000000000000000
shpchp 36864 0 - Live 0x0000000000000000
8250_fintek 16384 0 - Live 0x0000000000000000
mei_me 36864 0 - Live 0x0000000000000000
mei 98304 1 mei_me, Live 0x0000000000000000
mac_hid 16384 0 - Live 0x0000000000000000
parport_pc 32768 0 - Live 0x0000000000000000
ppdev 20480 0 - Live 0x0000000000000000
lp 20480 0 - Live 0x0000000000000000
parport 49152 3 parport_pc,ppdev,lp, Live 0x0000000000000000
autofs4 40960 2 - Live 0x0000000000000000
hid_generic 16384 0 - Live 0x0000000000000000
usbhid 49152 0 - Live 0x0000000000000000
hid 118784 2 hid_generic,usbhid, Live 0x0000000000000000
nouveau 1388544 4 - Live 0x0000000000000000
psmouse 126976 0 - Live 0x0000000000000000
mxm_wmi 16384 1 nouveau, Live 0x0000000000000000
video 40960 1 nouveau, Live 0x0000000000000000
i2c_algo_bit 16384 1 nouveau, Live 0x0000000000000000
ttm 94208 1 nouveau, Live 0x0000000000000000
drm_kms_helper 131072 1 nouveau, Live 0x0000000000000000
e1000e 237568 0 - Live 0x0000000000000000
drm 360448 7 nouveau,ttm,drm_kms_helper, Live 0x0000000000000000
ptp 20480 1 e1000e, Live 0x0000000000000000
ahci 36864 9 - Live 0x0000000000000000
pps_core 20480 1 ptp, Live 0x0000000000000000
libahci 32768 1 ahci, Live 0x0000000000000000
wmi 20480 2 nouveau,mxm_wmi, Live 0x0000000000000000

```
