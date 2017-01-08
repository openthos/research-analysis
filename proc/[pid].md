# proc
## [pid]
### 1. attr
目录文件，记录进程的各项属性
#### 1.1 current
#### 1.2 exec
#### 1.3 fscreate
#### 1.4 keycreate
#### 1.5 prev
#### 1.6 sockcreate

### 2. autogroup
？？？
```
#(example)
#cat /proc/1/autogroup
/autogroup-2 nice 0
```

### 3. auxv
乱码文件，？？？

### 4. cgroup
？？？
```
#(example)
#cat /proc/1/autogroup
9:memory:/init.scope
8:cpuset:/
7:pids:/init.scope
6:net_cls:/
5:freezer:/
4:blkio:/init.scope
3:cpu,cpuacct:/init.scope
2:devices:/init.scope
1:name=systemd:/init.scope
```

### 5. clear_refs
???,Invalid argument

### 6. cmdline
记录启动此进程的命令
```
#(example)
#cat /proc/cmdline
/sbin/init
```

### 7. comm
记录启动此进程的可执行文件名称
```
#(example)
#cat /proc/1/comm
systemd
```

### 8. coredump_filter
???
```
#(example)
#cat /proc/1/coredump_filter
00000033
```


### 9. cpuset
???
```
#(example)
#cat /proc/1/cpuset
/
```

### 10. cwd
软链接文件，指向了进程当前的工作目录
```
#(example)
#ls -l /proc/1/cwd
lrwxrwxrwx 1 root root 0 Jan  8 05:51 cwd -> /
```

### 11. environ
记录此进程的环境变量内容
```
#(example)
#cat /proc/1/environ
TERM=linux
```

### 12. exe
软链接文件
```

```

### 13. fd
目录文件。记录了所有进程打开的文件，每个文件以其文件描述符号码为名称的软链接表示，这些软链接指明了具体的文件 or ```socket```等的位置
```
#(example)
#ls -l /proc/1/fd
total 0
lrwx------ 1 root root 64 Jan  8 05:47 0 -> /dev/null
lrwx------ 1 root root 64 Jan  8 05:47 1 -> /dev/null
lr-x------ 1 root root 64 Jan  8 05:53 10 -> /proc/1/mountinfo
lr-x------ 1 root root 64 Jan  8 05:53 11 -> anon_inode:inotify
lr-x------ 1 root root 64 Jan  8 05:53 12 -> /proc/swaps
lrwx------ 1 root root 64 Jan  8 05:53 13 -> socket:[9910]
lrwx------ 1 root root 64 Jan  8 05:53 14 -> socket:[9912]
lrwx------ 1 root root 64 Jan  8 05:53 15 -> socket:[9914]
lrwx------ 1 root root 64 Jan  8 05:53 16 -> socket:[9915]
lrwx------ 1 root root 64 Jan  8 05:53 17 -> socket:[9916]
lrwx------ 1 root root 64 Jan  8 05:53 18 -> socket:[12800]
lrwx------ 1 root root 64 Jan  8 05:53 19 -> socket:[14469]
lrwx------ 1 root root 64 Jan  8 05:47 2 -> /dev/null
lrwx------ 1 root root 64 Jan  8 05:53 20 -> socket:[14470]
lrwx------ 1 root root 64 Jan  8 05:53 21 -> socket:[13126]
lrwx------ 1 root root 64 Jan  8 05:53 22 -> socket:[9919]
lrwx------ 1 root root 64 Jan  8 05:53 23 -> socket:[9922]
lrwx------ 1 root root 64 Jan  8 05:53 24 -> socket:[12588]
lrwx------ 1 root root 64 Jan  8 05:53 25 -> socket:[9925]
lr-x------ 1 root root 64 Jan  8 05:53 26 -> anon_inode:inotify
lrwx------ 1 root root 64 Jan  8 05:53 27 -> /run/dmeventd-server
lrwx------ 1 root root 64 Jan  8 05:53 28 -> /run/dmeventd-client
lrwx------ 1 root root 64 Jan  8 05:53 29 -> socket:[9929]
l-wx------ 1 root root 64 Jan  8 05:47 3 -> /dev/kmsg
lr-x------ 1 root root 64 Jan  8 05:53 30 -> anon_inode:inotify
lrwx------ 1 root root 64 Jan  8 05:53 31 -> socket:[9930]
lrwx------ 1 root root 64 Jan  8 05:53 32 -> /run/systemd/initctl/fifo
lrwx------ 1 root root 64 Jan  8 05:53 33 -> socket:[9935]
lrwx------ 1 root root 64 Jan  8 05:53 34 -> socket:[9938]
lrwx------ 1 root root 64 Jan  8 05:53 35 -> anon_inode:[timerfd]
lr-x------ 1 root root 64 Jan  8 05:53 36 -> /dev/autofs
lr-x------ 1 root root 64 Jan  8 05:53 37 -> pipe:[9973]
lrwx------ 1 root root 64 Jan  8 05:53 38 -> socket:[11334]
lrwx------ 1 root root 64 Jan  8 05:53 39 -> anon_inode:[timerfd]
lrwx------ 1 root root 64 Jan  8 05:53 4 -> anon_inode:[eventpoll]
lrwx------ 1 root root 64 Jan  8 05:53 40 -> socket:[11337]
lrwx------ 1 root root 64 Jan  8 05:53 41 -> socket:[11723]
lrwx------ 1 root root 64 Jan  8 05:53 42 -> socket:[11774]
lrwx------ 1 root root 64 Jan  8 05:53 43 -> socket:[11776]
lrwx------ 1 root root 64 Jan  8 05:53 44 -> socket:[12202]
lrwx------ 1 root root 64 Jan  8 05:53 45 -> /dev/rfkill
lrwx------ 1 root root 64 Jan  8 05:53 46 -> socket:[12304]
lrwx------ 1 root root 64 Jan  8 05:53 47 -> socket:[13149]
lrwx------ 1 root root 64 Jan  8 05:53 48 -> socket:[13150]
lrwx------ 1 root root 64 Jan  8 05:53 5 -> anon_inode:[signalfd]
lrwx------ 1 root root 64 Jan  8 05:53 59 -> socket:[16654]
lr-x------ 1 root root 64 Jan  8 05:53 6 -> /sys/fs/cgroup/systemd
lrwx------ 1 root root 64 Jan  8 05:53 7 -> anon_inode:[timerfd]
lrwx------ 1 root root 64 Jan  8 05:53 8 -> socket:[9908]
lrwx------ 1 root root 64 Jan  8 05:53 9 -> anon_inode:[eventpoll]

```

### 14. fdinfo
目录文件，已打开文件的对应信息，具体各参数如下：
+ pos
+ flags
+ mnt_id
```
#(example)
#ls -l /proc/1/fdinfo
total 0
-r-------- 1 root root 0 Jan  8 05:57 0
-r-------- 1 root root 0 Jan  8 05:57 1
-r-------- 1 root root 0 Jan  8 05:57 10
-r-------- 1 root root 0 Jan  8 05:57 11
-r-------- 1 root root 0 Jan  8 05:57 12
-r-------- 1 root root 0 Jan  8 05:57 13
-r-------- 1 root root 0 Jan  8 05:57 14
-r-------- 1 root root 0 Jan  8 05:57 15
-r-------- 1 root root 0 Jan  8 05:57 16
-r-------- 1 root root 0 Jan  8 05:57 17
-r-------- 1 root root 0 Jan  8 05:57 18
-r-------- 1 root root 0 Jan  8 05:57 19
-r-------- 1 root root 0 Jan  8 05:57 2
-r-------- 1 root root 0 Jan  8 05:57 20
-r-------- 1 root root 0 Jan  8 05:57 21
-r-------- 1 root root 0 Jan  8 05:57 22
-r-------- 1 root root 0 Jan  8 05:57 23
-r-------- 1 root root 0 Jan  8 05:57 24
-r-------- 1 root root 0 Jan  8 05:57 25
-r-------- 1 root root 0 Jan  8 05:57 26
-r-------- 1 root root 0 Jan  8 05:57 27
-r-------- 1 root root 0 Jan  8 05:57 28
-r-------- 1 root root 0 Jan  8 05:57 29
-r-------- 1 root root 0 Jan  8 05:57 3
-r-------- 1 root root 0 Jan  8 05:57 30
-r-------- 1 root root 0 Jan  8 05:57 31
-r-------- 1 root root 0 Jan  8 05:57 32
-r-------- 1 root root 0 Jan  8 05:57 33
-r-------- 1 root root 0 Jan  8 05:57 34
-r-------- 1 root root 0 Jan  8 05:57 35
-r-------- 1 root root 0 Jan  8 05:47 36
-r-------- 1 root root 0 Jan  8 05:47 37
-r-------- 1 root root 0 Jan  8 05:57 38
-r-------- 1 root root 0 Jan  8 05:57 39
-r-------- 1 root root 0 Jan  8 05:47 4
-r-------- 1 root root 0 Jan  8 05:57 40
-r-------- 1 root root 0 Jan  8 05:57 41
-r-------- 1 root root 0 Jan  8 05:57 42
-r-------- 1 root root 0 Jan  8 05:57 43
-r-------- 1 root root 0 Jan  8 05:57 44
-r-------- 1 root root 0 Jan  8 05:57 45
-r-------- 1 root root 0 Jan  8 05:57 46
-r-------- 1 root root 0 Jan  8 05:57 47
-r-------- 1 root root 0 Jan  8 05:57 48
-r-------- 1 root root 0 Jan  8 05:47 5
-r-------- 1 root root 0 Jan  8 05:57 59
-r-------- 1 root root 0 Jan  8 05:57 6
-r-------- 1 root root 0 Jan  8 05:57 7
-r-------- 1 root root 0 Jan  8 05:57 8
-r-------- 1 root root 0 Jan  8 05:57 9

#(example)
#cat /proc/1/fdinfo/8
pos:    0
flags:    02004002
mnt_id:    8
```

### 15. io
读写字节数目以及读写系统调用次数
```
#(example)
#cat /proc/1/io
rchar: 50720173
wchar: 2260304522
syscr: 52300
syscw: 552278
read_bytes: 109913088
write_bytes: 2237005824
cancelled_write_bytes: 6557696
```

### 16.limits
记录此进程的运行环境的各项限制值，包括硬限制、软限制等
```
#(example)
#cat /proc/1/limits
Limit(限制名称)          Soft Limit(软限制)   Hard Limit(硬限制)    Units(单位)     
Max cpu time              unlimited            unlimited            seconds   
Max file size             unlimited            unlimited            bytes     
Max data size             unlimited            unlimited            bytes     
Max stack size            8388608              unlimited            bytes     
Max core file size        unlimited            unlimited            bytes     
Max resident set          unlimited            unlimited            bytes     
Max processes             15716                15716                processes 
Max open files            65536                65536                files     
Max locked memory         65536                65536                bytes     
Max address space         unlimited            unlimited            bytes     
Max file locks            unlimited            unlimited            locks     
Max pending signals       15716                15716                signals   
Max msgqueue size         819200               819200               bytes     
Max nice priority         0                    0                    
Max realtime priority     0                    0                    
Max realtime timeout      unlimited            unlimited            us 
```

### 17. map_files
目录文件。内容为以虚拟内存地址范围命名的软链接文件，指明了可执行文件和所加载的所有库文件
```
#(example)
#ls -l /proc/1/map_files
total 0
lr-------- 1 root root 64 Jan  8 06:07 5635f4a42000-5635f4b2a000 -> /usr/lib/systemd/systemd
lr-------- 1 root root 64 Jan  8 06:07 5635f4b2b000-5635f4b50000 -> /usr/lib/systemd/systemd
lr-------- 1 root root 64 Jan  8 06:07 5635f4b50000-5635f4b51000 -> /usr/lib/systemd/systemd
lr-------- 1 root root 64 Jan  8 06:07 7fa7e9798000-7fa7e979c000 -> /usr/lib/libattr.so.1.1.0
lr-------- 1 root root 64 Jan  8 06:07 7fa7e979c000-7fa7e999b000 -> /usr/lib/libattr.so.1.1.0
lr-------- 1 root root 64 Jan  8 06:07 7fa7e999b000-7fa7e999c000 -> /usr/lib/libattr.so.1.1.0
lr-------- 1 root root 64 Jan  8 06:07 7fa7e999c000-7fa7e999d000 -> /usr/lib/libattr.so.1.1.0
lr-------- 1 root root 64 Jan  8 06:07 7fa7e999d000-7fa7e99a1000 -> /usr/lib/libuuid.so.1.3.0
lr-------- 1 root root 64 Jan  8 06:07 7fa7e99a1000-7fa7e9ba0000 -> /usr/lib/libuuid.so.1.3.0
lr-------- 1 root root 64 Jan  8 06:07 7fa7e9ba0000-7fa7e9ba1000 -> /usr/lib/libuuid.so.1.3.0
lr-------- 1 root root 64 Jan  8 06:07 7fa7e9ba1000-7fa7e9ba2000 -> /usr/lib/libuuid.so.1.3.0
lr-------- 1 root root 64 Jan  8 06:07 7fa7e9ba2000-7fa7e9be3000 -> /usr/lib/libblkid.so.1.1.0
lr-------- 1 root root 64 Jan  8 06:07 7fa7e9be3000-7fa7e9de2000 -> /usr/lib/libblkid.so.1.1.0
lr-------- 1 root root 64 Jan  8 06:07 7fa7e9de2000-7fa7e9de6000 -> /usr/lib/libblkid.so.1.1.0
lr-------- 1 root root 64 Jan  8 06:07 7fa7e9de6000-7fa7e9de7000 -> /usr/lib/libblkid.so.1.1.0
lr-------- 1 root root 64 Jan  8 06:07 7fa7e9de8000-7fa7e9dfd000 -> /usr/lib/libz.so.1.2.8
lr-------- 1 root root 64 Jan  8 06:07 7fa7e9dfd000-7fa7e9ffc000 -> /usr/lib/libz.so.1.2.8
lr-------- 1 root root 64 Jan  8 06:07 7fa7e9ffc000-7fa7e9ffd000 -> /usr/lib/libz.so.1.2.8
lr-------- 1 root root 64 Jan  8 06:07 7fa7e9ffd000-7fa7e9ffe000 -> /usr/lib/libz.so.1.2.8
lr-------- 1 root root 64 Jan  8 06:07 7fa7e9ffe000-7fa7ea000000 -> /usr/lib/libdl-2.24.so
lr-------- 1 root root 64 Jan  8 06:07 7fa7ea000000-7fa7ea200000 -> /usr/lib/libdl-2.24.so
lr-------- 1 root root 64 Jan  8 06:07 7fa7ea200000-7fa7ea201000 -> /usr/lib/libdl-2.24.so
lr-------- 1 root root 64 Jan  8 06:07 7fa7ea201000-7fa7ea202000 -> /usr/lib/libdl-2.24.so
lr-------- 1 root root 64 Jan  8 06:07 7fa7ea202000-7fa7ea234000 -> /usr/lib/libidn.so.11.6.16
lr-------- 1 root root 64 Jan  8 06:07 7fa7ea234000-7fa7ea434000 -> /usr/lib/libidn.so.11.6.16
lr-------- 1 root root 64 Jan  8 06:07 7fa7ea434000-7fa7ea435000 -> /usr/lib/libidn.so.11.6.16
lr-------- 1 root root 64 Jan  8 06:07 7fa7ea435000-7fa7ea436000 -> /usr/lib/libidn.so.11.6.16
lr-------- 1 root root 64 Jan  8 06:07 7fa7ea436000-7fa7ea43e000 -> /usr/lib/libacl.so.1.1.0
lr-------- 1 root root 64 Jan  8 06:07 7fa7ea43e000-7fa7ea63d000 -> /usr/lib/libacl.so.1.1.0
lr-------- 1 root root 64 Jan  8 06:07 7fa7ea63d000-7fa7ea63e000 -> /usr/lib/libacl.so.1.1.0
lr-------- 1 root root 64 Jan  8 06:07 7fa7ea63e000-7fa7ea63f000 -> /usr/lib/libacl.so.1.1.0
lr-------- 1 root root 64 Jan  8 06:07 7fa7ea63f000-7fa7ea652000 -> /usr/lib/libgpg-error.so.0.21.0
lr-------- 1 root root 64 Jan  8 06:07 7fa7ea652000-7fa7ea851000 -> /usr/lib/libgpg-error.so.0.21.0
lr-------- 1 root root 64 Jan  8 06:07 7fa7ea851000-7fa7ea852000 -> /usr/lib/libgpg-error.so.0.21.0
lr-------- 1 root root 64 Jan  8 06:07 7fa7ea852000-7fa7ea853000 -> /usr/lib/libgpg-error.so.0.21.0
lr-------- 1 root root 64 Jan  8 06:07 7fa7ea853000-7fa7ea95a000 -> /usr/lib/libgcrypt.so.20.1.5
lr-------- 1 root root 64 Jan  8 06:07 7fa7ea95a000-7fa7eab59000 -> /usr/lib/libgcrypt.so.20.1.5
lr-------- 1 root root 64 Jan  8 06:07 7fa7eab59000-7fa7eab5b000 -> /usr/lib/libgcrypt.so.20.1.5
lr-------- 1 root root 64 Jan  8 06:07 7fa7eab5b000-7fa7eab62000 -> /usr/lib/libgcrypt.so.20.1.5
lr-------- 1 root root 64 Jan  8 06:07 7fa7eab62000-7fa7eab73000 -> /usr/lib/liblz4.so.1.7.4
lr-------- 1 root root 64 Jan  8 06:07 7fa7eab73000-7fa7ead72000 -> /usr/lib/liblz4.so.1.7.4
lr-------- 1 root root 64 Jan  8 06:07 7fa7ead72000-7fa7ead73000 -> /usr/lib/liblz4.so.1.7.4
lr-------- 1 root root 64 Jan  8 06:07 7fa7ead73000-7fa7ead74000 -> /usr/lib/liblz4.so.1.7.4
lr-------- 1 root root 64 Jan  8 06:07 7fa7ead74000-7fa7ead99000 -> /usr/lib/liblzma.so.5.2.3
lr-------- 1 root root 64 Jan  8 06:07 7fa7ead99000-7fa7eaf98000 -> /usr/lib/liblzma.so.5.2.3
lr-------- 1 root root 64 Jan  8 06:07 7fa7eaf98000-7fa7eaf99000 -> /usr/lib/liblzma.so.5.2.3
lr-------- 1 root root 64 Jan  8 06:07 7fa7eaf99000-7fa7eaf9a000 -> /usr/lib/liblzma.so.5.2.3
lr-------- 1 root root 64 Jan  8 06:07 7fa7eaf9a000-7fa7eafae000 -> /usr/lib/libresolv-2.24.so
lr-------- 1 root root 64 Jan  8 06:07 7fa7eafae000-7fa7eb1ad000 -> /usr/lib/libresolv-2.24.so
lr-------- 1 root root 64 Jan  8 06:07 7fa7eb1ad000-7fa7eb1ae000 -> /usr/lib/libresolv-2.24.so
lr-------- 1 root root 64 Jan  8 06:07 7fa7eb1ae000-7fa7eb1af000 -> /usr/lib/libresolv-2.24.so
lr-------- 1 root root 64 Jan  8 06:07 7fa7eb1b1000-7fa7eb2b4000 -> /usr/lib/libm-2.24.so
lr-------- 1 root root 64 Jan  8 06:07 7fa7eb2b4000-7fa7eb4b3000 -> /usr/lib/libm-2.24.so
lr-------- 1 root root 64 Jan  8 06:07 7fa7eb4b3000-7fa7eb4b4000 -> /usr/lib/libm-2.24.so
lr-------- 1 root root 64 Jan  8 06:07 7fa7eb4b4000-7fa7eb4b5000 -> /usr/lib/libm-2.24.so
lr-------- 1 root root 64 Jan  8 06:07 7fa7eb4b5000-7fa7eb4b9000 -> /usr/lib/libcap.so.2.25
lr-------- 1 root root 64 Jan  8 06:07 7fa7eb4b9000-7fa7eb6b8000 -> /usr/lib/libcap.so.2.25
lr-------- 1 root root 64 Jan  8 06:07 7fa7eb6b8000-7fa7eb6b9000 -> /usr/lib/libcap.so.2.25
lr-------- 1 root root 64 Jan  8 06:07 7fa7eb6b9000-7fa7eb84e000 -> /usr/lib/libc-2.24.so
lr-------- 1 root root 64 Jan  8 06:07 7fa7eb84e000-7fa7eba4d000 -> /usr/lib/libc-2.24.so
lr-------- 1 root root 64 Jan  8 06:07 7fa7eba4d000-7fa7eba51000 -> /usr/lib/libc-2.24.so
lr-------- 1 root root 64 Jan  8 06:07 7fa7eba51000-7fa7eba53000 -> /usr/lib/libc-2.24.so
lr-------- 1 root root 64 Jan  8 06:07 7fa7eba57000-7fa7eba6f000 -> /usr/lib/libpthread-2.24.so
lr-------- 1 root root 64 Jan  8 06:07 7fa7eba6f000-7fa7ebc6e000 -> /usr/lib/libpthread-2.24.so
lr-------- 1 root root 64 Jan  8 06:07 7fa7ebc6e000-7fa7ebc6f000 -> /usr/lib/libpthread-2.24.so
lr-------- 1 root root 64 Jan  8 06:07 7fa7ebc6f000-7fa7ebc70000 -> /usr/lib/libpthread-2.24.so
lr-------- 1 root root 64 Jan  8 06:07 7fa7ebc74000-7fa7ebcbe000 -> /usr/lib/libmount.so.1.1.0
lr-------- 1 root root 64 Jan  8 06:07 7fa7ebcbe000-7fa7ebebe000 -> /usr/lib/libmount.so.1.1.0
lr-------- 1 root root 64 Jan  8 06:07 7fa7ebebe000-7fa7ebebf000 -> /usr/lib/libmount.so.1.1.0
lr-------- 1 root root 64 Jan  8 06:07 7fa7ebebf000-7fa7ebec0000 -> /usr/lib/libmount.so.1.1.0
lr-------- 1 root root 64 Jan  8 06:07 7fa7ebec2000-7fa7ebed7000 -> /usr/lib/libkmod.so.2.3.1
lr-------- 1 root root 64 Jan  8 06:07 7fa7ebed7000-7fa7ec0d6000 -> /usr/lib/libkmod.so.2.3.1
lr-------- 1 root root 64 Jan  8 06:07 7fa7ec0d6000-7fa7ec0d7000 -> /usr/lib/libkmod.so.2.3.1
lr-------- 1 root root 64 Jan  8 06:07 7fa7ec0d7000-7fa7ec0d8000 -> /usr/lib/libkmod.so.2.3.1
lr-------- 1 root root 64 Jan  8 06:07 7fa7ec0d8000-7fa7ec0e5000 -> /usr/lib/libpam.so.0.84.2
lr-------- 1 root root 64 Jan  8 06:07 7fa7ec0e5000-7fa7ec2e4000 -> /usr/lib/libpam.so.0.84.2
lr-------- 1 root root 64 Jan  8 06:07 7fa7ec2e4000-7fa7ec2e5000 -> /usr/lib/libpam.so.0.84.2
lr-------- 1 root root 64 Jan  8 06:07 7fa7ec2e5000-7fa7ec2e6000 -> /usr/lib/libpam.so.0.84.2
lr-------- 1 root root 64 Jan  8 06:07 7fa7ec2e6000-7fa7ec312000 -> /usr/lib/libseccomp.so.2.3.1
lr-------- 1 root root 64 Jan  8 06:07 7fa7ec312000-7fa7ec511000 -> /usr/lib/libseccomp.so.2.3.1
lr-------- 1 root root 64 Jan  8 06:07 7fa7ec511000-7fa7ec526000 -> /usr/lib/libseccomp.so.2.3.1
lr-------- 1 root root 64 Jan  8 06:07 7fa7ec526000-7fa7ec527000 -> /usr/lib/libseccomp.so.2.3.1
lr-------- 1 root root 64 Jan  8 06:07 7fa7ec527000-7fa7ec52e000 -> /usr/lib/librt-2.24.so
lr-------- 1 root root 64 Jan  8 06:07 7fa7ec52e000-7fa7ec72d000 -> /usr/lib/librt-2.24.so
lr-------- 1 root root 64 Jan  8 06:07 7fa7ec72d000-7fa7ec72e000 -> /usr/lib/librt-2.24.so
lr-------- 1 root root 64 Jan  8 06:07 7fa7ec72e000-7fa7ec72f000 -> /usr/lib/librt-2.24.so
lr-------- 1 root root 64 Jan  8 06:07 7fa7ec72f000-7fa7ec8bb000 -> /usr/lib/systemd/libsystemd-shared-232.so
lr-------- 1 root root 64 Jan  8 06:07 7fa7ec8bb000-7fa7ec945000 -> /usr/lib/systemd/libsystemd-shared-232.so
lr-------- 1 root root 64 Jan  8 06:07 7fa7ec945000-7fa7ec946000 -> /usr/lib/systemd/libsystemd-shared-232.so
lr-------- 1 root root 64 Jan  8 06:07 7fa7ec947000-7fa7ec96a000 -> /usr/lib/ld-2.24.so
lr-------- 1 root root 64 Jan  8 06:07 7fa7ecb69000-7fa7ecb6a000 -> /usr/lib/ld-2.24.so
lr-------- 1 root root 64 Jan  8 06:07 7fa7ecb6a000-7fa7ecb6b000 -> /usr/lib/ld-2.24.so


```

### 18. maps
以文本形式描述的进程运行内存内存图，与当前进程有关联的所有可执行文件和库文件在虚拟内存地址中的映射区域、访问权限等参数形成的列表。
具体参数如下：
+ address    
进程占用的地址空间
+ perms    
访问权限集
r=read; w=write; x=execute; s=shared; p=private（copy on write）
+ offset    
文件偏移量
+ dev    
设备号（主设备号：次设备号）
+ inode    
文件具体的inode号。
0表示没有inode关联互内存区域
```
#(example)
#cat /proc/1/maps
#address                  perms  offset  dev  inode
559235185000-55923526d000 r-xp 00000000 08:01 799480                     /usr/lib/systemd/systemd
55923526e000-559235293000 r--p 000e8000 08:01 799480                     /usr/lib/systemd/systemd
559235293000-559235294000 rw-p 0010d000 08:01 799480                     /usr/lib/systemd/systemd
559235a81000-559235b2e000 rw-p 00000000 00:00 0                          [heap]
7fc1f4000000-7fc1f4029000 rw-p 00000000 00:00 0 
7fc1f4029000-7fc1f8000000 ---p 00000000 00:00 0 
7fc1f8a18000-7fc1f8a19000 ---p 00000000 00:00 0 
7fc1f8a19000-7fc1f9219000 rw-p 00000000 00:00 0 
7fc1f9219000-7fc1f921a000 ---p 00000000 00:00 0 
7fc1f921a000-7fc1f9a1a000 rw-p 00000000 00:00 0 
7fc1f9a1a000-7fc1f9a1e000 r-xp 00000000 08:01 792978                     /usr/lib/libattr.so.1.1.0
7fc1f9a1e000-7fc1f9c1d000 ---p 00004000 08:01 792978                     /usr/lib/libattr.so.1.1.0
7fc1f9c1d000-7fc1f9c1e000 r--p 00003000 08:01 792978                     /usr/lib/libattr.so.1.1.0
7fc1f9c1e000-7fc1f9c1f000 rw-p 00004000 08:01 792978                     /usr/lib/libattr.so.1.1.0
7fc1f9c1f000-7fc1f9c23000 r-xp 00000000 08:01 797351                     /usr/lib/libuuid.so.1.3.0
7fc1f9c23000-7fc1f9e22000 ---p 00004000 08:01 797351                     /usr/lib/libuuid.so.1.3.0
7fc1f9e22000-7fc1f9e23000 r--p 00003000 08:01 797351                     /usr/lib/libuuid.so.1.3.0
7fc1f9e23000-7fc1f9e24000 rw-p 00004000 08:01 797351                     /usr/lib/libuuid.so.1.3.0
7fc1f9e24000-7fc1f9e65000 r-xp 00000000 08:01 797352                     /usr/lib/libblkid.so.1.1.0
7fc1f9e65000-7fc1fa064000 ---p 00041000 08:01 797352                     /usr/lib/libblkid.so.1.1.0
7fc1fa064000-7fc1fa068000 r--p 00040000 08:01 797352                     /usr/lib/libblkid.so.1.1.0
7fc1fa068000-7fc1fa069000 rw-p 00044000 08:01 797352                     /usr/lib/libblkid.so.1.1.0
7fc1fa069000-7fc1fa06a000 rw-p 00000000 00:00 0 
7fc1fa06a000-7fc1fa07f000 r-xp 00000000 08:01 797309                     /usr/lib/libz.so.1.2.8
7fc1fa07f000-7fc1fa27e000 ---p 00015000 08:01 797309                     /usr/lib/libz.so.1.2.8
7fc1fa27e000-7fc1fa27f000 r--p 00014000 08:01 797309                     /usr/lib/libz.so.1.2.8
7fc1fa27f000-7fc1fa280000 rw-p 00015000 08:01 797309                     /usr/lib/libz.so.1.2.8
7fc1fa280000-7fc1fa282000 r-xp 00000000 08:01 789734                     /usr/lib/libdl-2.24.so
7fc1fa282000-7fc1fa482000 ---p 00002000 08:01 789734                     /usr/lib/libdl-2.24.so
7fc1fa482000-7fc1fa483000 r--p 00002000 08:01 789734                     /usr/lib/libdl-2.24.so
7fc1fa483000-7fc1fa484000 rw-p 00003000 08:01 789734                     /usr/lib/libdl-2.24.so
7fc1fa484000-7fc1fa4b6000 r-xp 00000000 08:01 798286                     /usr/lib/libidn.so.11.6.16
7fc1fa4b6000-7fc1fa6b6000 ---p 00032000 08:01 798286                     /usr/lib/libidn.so.11.6.16
7fc1fa6b6000-7fc1fa6b7000 r--p 00032000 08:01 798286                     /usr/lib/libidn.so.11.6.16
7fc1fa6b7000-7fc1fa6b8000 rw-p 00033000 08:01 798286                     /usr/lib/libidn.so.11.6.16
7fc1fa6b8000-7fc1fa6c0000 r-xp 00000000 08:01 793044                     /usr/lib/libacl.so.1.1.0
7fc1fa6c0000-7fc1fa8bf000 ---p 00008000 08:01 793044                     /usr/lib/libacl.so.1.1.0
7fc1fa8bf000-7fc1fa8c0000 r--p 00007000 08:01 793044                     /usr/lib/libacl.so.1.1.0
7fc1fa8c0000-7fc1fa8c1000 rw-p 00008000 08:01 793044                     /usr/lib/libacl.so.1.1.0
7fc1fa8c1000-7fc1fa8d4000 r-xp 00000000 08:01 819362                     /usr/lib/libgpg-error.so.0.21.0
7fc1fa8d4000-7fc1faad3000 ---p 00013000 08:01 819362                     /usr/lib/libgpg-error.so.0.21.0
7fc1faad3000-7fc1faad4000 r--p 00012000 08:01 819362                     /usr/lib/libgpg-error.so.0.21.0
7fc1faad4000-7fc1faad5000 rw-p 00013000 08:01 819362                     /usr/lib/libgpg-error.so.0.21.0
7fc1faad5000-7fc1fabdc000 r-xp 00000000 08:01 797135                     /usr/lib/libgcrypt.so.20.1.5
7fc1fabdc000-7fc1faddb000 ---p 00107000 08:01 797135                     /usr/lib/libgcrypt.so.20.1.5
7fc1faddb000-7fc1faddd000 r--p 00106000 08:01 797135                     /usr/lib/libgcrypt.so.20.1.5
7fc1faddd000-7fc1fade4000 rw-p 00108000 08:01 797135                     /usr/lib/libgcrypt.so.20.1.5
7fc1fade4000-7fc1fadf5000 r-xp 00000000 08:01 797151                     /usr/lib/liblz4.so.1.7.4
7fc1fadf5000-7fc1faff4000 ---p 00011000 08:01 797151                     /usr/lib/liblz4.so.1.7.4
7fc1faff4000-7fc1faff5000 r--p 00010000 08:01 797151                     /usr/lib/liblz4.so.1.7.4
7fc1faff5000-7fc1faff6000 rw-p 00011000 08:01 797151                     /usr/lib/liblz4.so.1.7.4
7fc1faff6000-7fc1fb01b000 r-xp 00000000 08:01 797155                     /usr/lib/liblzma.so.5.2.3
7fc1fb01b000-7fc1fb21a000 ---p 00025000 08:01 797155                     /usr/lib/liblzma.so.5.2.3
7fc1fb21a000-7fc1fb21b000 r--p 00024000 08:01 797155                     /usr/lib/liblzma.so.5.2.3
7fc1fb21b000-7fc1fb21c000 rw-p 00025000 08:01 797155                     /usr/lib/liblzma.so.5.2.3
7fc1fb21c000-7fc1fb230000 r-xp 00000000 08:01 789737                     /usr/lib/libresolv-2.24.so
7fc1fb230000-7fc1fb42f000 ---p 00014000 08:01 789737                     /usr/lib/libresolv-2.24.so
7fc1fb42f000-7fc1fb430000 r--p 00013000 08:01 789737                     /usr/lib/libresolv-2.24.so
7fc1fb430000-7fc1fb431000 rw-p 00014000 08:01 789737                     /usr/lib/libresolv-2.24.so
7fc1fb431000-7fc1fb433000 rw-p 00000000 00:00 0 
7fc1fb433000-7fc1fb536000 r-xp 00000000 08:01 789735                     /usr/lib/libm-2.24.so
7fc1fb536000-7fc1fb735000 ---p 00103000 08:01 789735                     /usr/lib/libm-2.24.so
7fc1fb735000-7fc1fb736000 r--p 00102000 08:01 789735                     /usr/lib/libm-2.24.so
7fc1fb736000-7fc1fb737000 rw-p 00103000 08:01 789735                     /usr/lib/libm-2.24.so
7fc1fb737000-7fc1fb73b000 r-xp 00000000 08:01 793062                     /usr/lib/libcap.so.2.25
7fc1fb73b000-7fc1fb93a000 ---p 00004000 08:01 793062                     /usr/lib/libcap.so.2.25
7fc1fb93a000-7fc1fb93b000 rw-p 00003000 08:01 793062                     /usr/lib/libcap.so.2.25
7fc1fb93b000-7fc1fbad0000 r-xp 00000000 08:01 789677                     /usr/lib/libc-2.24.so
7fc1fbad0000-7fc1fbccf000 ---p 00195000 08:01 789677                     /usr/lib/libc-2.24.so
7fc1fbccf000-7fc1fbcd3000 r--p 00194000 08:01 789677                     /usr/lib/libc-2.24.so
7fc1fbcd3000-7fc1fbcd5000 rw-p 00198000 08:01 789677                     /usr/lib/libc-2.24.so
7fc1fbcd5000-7fc1fbcd9000 rw-p 00000000 00:00 0 
7fc1fbcd9000-7fc1fbcf1000 r-xp 00000000 08:01 789658                     /usr/lib/libpthread-2.24.so
7fc1fbcf1000-7fc1fbef0000 ---p 00018000 08:01 789658                     /usr/lib/libpthread-2.24.so
7fc1fbef0000-7fc1fbef1000 r--p 00017000 08:01 789658                     /usr/lib/libpthread-2.24.so
7fc1fbef1000-7fc1fbef2000 rw-p 00018000 08:01 789658                     /usr/lib/libpthread-2.24.so
7fc1fbef2000-7fc1fbef6000 rw-p 00000000 00:00 0 
7fc1fbef6000-7fc1fbf40000 r-xp 00000000 08:01 797353                     /usr/lib/libmount.so.1.1.0
7fc1fbf40000-7fc1fc140000 ---p 0004a000 08:01 797353                     /usr/lib/libmount.so.1.1.0
7fc1fc140000-7fc1fc141000 r--p 0004a000 08:01 797353                     /usr/lib/libmount.so.1.1.0
7fc1fc141000-7fc1fc142000 rw-p 0004b000 08:01 797353                     /usr/lib/libmount.so.1.1.0
7fc1fc142000-7fc1fc144000 rw-p 00000000 00:00 0 
7fc1fc144000-7fc1fc159000 r-xp 00000000 08:01 798191                     /usr/lib/libkmod.so.2.3.1
7fc1fc159000-7fc1fc358000 ---p 00015000 08:01 798191                     /usr/lib/libkmod.so.2.3.1
7fc1fc358000-7fc1fc359000 r--p 00014000 08:01 798191                     /usr/lib/libkmod.so.2.3.1
7fc1fc359000-7fc1fc35a000 rw-p 00015000 08:01 798191                     /usr/lib/libkmod.so.2.3.1
7fc1fc35a000-7fc1fc367000 r-xp 00000000 08:01 797896                     /usr/lib/libpam.so.0.84.2
7fc1fc367000-7fc1fc566000 ---p 0000d000 08:01 797896                     /usr/lib/libpam.so.0.84.2
7fc1fc566000-7fc1fc567000 r--p 0000c000 08:01 797896                     /usr/lib/libpam.so.0.84.2
7fc1fc567000-7fc1fc568000 rw-p 0000d000 08:01 797896                     /usr/lib/libpam.so.0.84.2
7fc1fc568000-7fc1fc594000 r-xp 00000000 08:01 798346                     /usr/lib/libseccomp.so.2.3.1
7fc1fc594000-7fc1fc793000 ---p 0002c000 08:01 798346                     /usr/lib/libseccomp.so.2.3.1
7fc1fc793000-7fc1fc7a8000 r--p 0002b000 08:01 798346                     /usr/lib/libseccomp.so.2.3.1
7fc1fc7a8000-7fc1fc7a9000 rw-p 00040000 08:01 798346                     /usr/lib/libseccomp.so.2.3.1
7fc1fc7a9000-7fc1fc7b0000 r-xp 00000000 08:01 789738                     /usr/lib/librt-2.24.so
7fc1fc7b0000-7fc1fc9af000 ---p 00007000 08:01 789738                     /usr/lib/librt-2.24.so
7fc1fc9af000-7fc1fc9b0000 r--p 00006000 08:01 789738                     /usr/lib/librt-2.24.so
7fc1fc9b0000-7fc1fc9b1000 rw-p 00007000 08:01 789738                     /usr/lib/librt-2.24.so
7fc1fc9b1000-7fc1fcb3d000 r-xp 00000000 08:01 799479                     /usr/lib/systemd/libsystemd-shared-232.so
7fc1fcb3d000-7fc1fcbc7000 r--p 0018b000 08:01 799479                     /usr/lib/systemd/libsystemd-shared-232.so
7fc1fcbc7000-7fc1fcbc8000 rw-p 00215000 08:01 799479                     /usr/lib/systemd/libsystemd-shared-232.so
7fc1fcbc8000-7fc1fcbc9000 rw-p 00000000 00:00 0 
7fc1fcbc9000-7fc1fcbec000 r-xp 00000000 08:01 789676                     /usr/lib/ld-2.24.so
7fc1fcdcb000-7fc1fcdd6000 rw-p 00000000 00:00 0 
7fc1fcde9000-7fc1fcdeb000 rw-p 00000000 00:00 0 
7fc1fcdeb000-7fc1fcdec000 r--p 00022000 08:01 789676                     /usr/lib/ld-2.24.so
7fc1fcdec000-7fc1fcded000 rw-p 00023000 08:01 789676                     /usr/lib/ld-2.24.so
7fc1fcded000-7fc1fcdee000 rw-p 00000000 00:00 0 
7ffc5f05c000-7ffc5f07d000 rw-p 00000000 00:00 0                          [stack]
7ffc5f148000-7ffc5f14a000 r--p 00000000 00:00 0                          [vvar]
7ffc5f14a000-7ffc5f14c000 r-xp 00000000 00:00 0                          [vdso]
ffffffffff600000-ffffffffff601000 r-xp 00000000 00:00 0                  [vsyscall]
```

### 19. mem
???
```
#(example)
#cat /proc/1/mem
Input/output error
```

### 20. mountinfo
文件系统的挂载信息
```
#(example)
#cat /proc/1/mountinfo
16 20 0:4 / /proc rw,nosuid,nodev,noexec,relatime shared:5 - proc proc rw
17 20 0:16 / /sys rw,nosuid,nodev,noexec,relatime shared:6 - sysfs sys rw
18 20 0:6 / /dev rw,nosuid,relatime shared:2 - devtmpfs dev rw,size=2011756k,nr_inodes=502939,mode=755
19 20 0:17 / /run rw,nosuid,nodev,relatime shared:11 - tmpfs run rw,mode=755
20 0 8:1 / / rw,relatime shared:1 - ext4 /dev/sda1 rw,data=ordered
21 17 0:18 / /sys/kernel/security rw,nosuid,nodev,noexec,relatime shared:7 - securityfs securityfs rw
22 18 0:19 / /dev/shm rw,nosuid,nodev shared:3 - tmpfs tmpfs rw
23 18 0:20 / /dev/pts rw,nosuid,noexec,relatime shared:4 - devpts devpts rw,gid=5,mode=620,ptmxmode=000
24 17 0:21 / /sys/fs/cgroup ro,nosuid,nodev,noexec shared:8 - tmpfs tmpfs ro,mode=755
25 24 0:22 / /sys/fs/cgroup/systemd rw,nosuid,nodev,noexec,relatime shared:9 - cgroup cgroup rw,xattr,release_agent=/usr/lib/systemd/systemd-cgroups-agent,name=systemd
26 17 0:23 / /sys/fs/pstore rw,nosuid,nodev,noexec,relatime shared:10 - pstore pstore rw
27 24 0:24 / /sys/fs/cgroup/devices rw,nosuid,nodev,noexec,relatime shared:12 - cgroup cgroup rw,devices
28 24 0:25 / /sys/fs/cgroup/cpu,cpuacct rw,nosuid,nodev,noexec,relatime shared:13 - cgroup cgroup rw,cpu,cpuacct
29 24 0:26 / /sys/fs/cgroup/blkio rw,nosuid,nodev,noexec,relatime shared:14 - cgroup cgroup rw,blkio
30 24 0:27 / /sys/fs/cgroup/freezer rw,nosuid,nodev,noexec,relatime shared:15 - cgroup cgroup rw,freezer
31 24 0:28 / /sys/fs/cgroup/net_cls rw,nosuid,nodev,noexec,relatime shared:16 - cgroup cgroup rw,net_cls
32 24 0:29 / /sys/fs/cgroup/pids rw,nosuid,nodev,noexec,relatime shared:17 - cgroup cgroup rw,pids
33 24 0:30 / /sys/fs/cgroup/cpuset rw,nosuid,nodev,noexec,relatime shared:18 - cgroup cgroup rw,cpuset
34 24 0:31 / /sys/fs/cgroup/memory rw,nosuid,nodev,noexec,relatime shared:19 - cgroup cgroup rw,memory
35 16 0:32 / /proc/sys/fs/binfmt_misc rw,relatime shared:20 - autofs systemd-1 rw,fd=28,pgrp=1,timeout=0,minproto=5,maxproto=5,direct
37 18 0:15 / /dev/mqueue rw,relatime shared:21 - mqueue mqueue rw
36 18 0:33 / /dev/hugepages rw,relatime shared:22 - hugetlbfs hugetlbfs rw
38 20 0:34 / /tmp rw,nosuid,nodev shared:23 - tmpfs tmpfs rw
39 17 0:7 / /sys/kernel/debug rw,relatime shared:24 - debugfs debugfs rw
40 17 0:35 / /sys/kernel/config rw,relatime shared:25 - configfs configfs rw
68 19 0:37 / /run/vmblock-fuse rw,nosuid,nodev,relatime shared:26 - fuse.vmware-vmblock vmware-vmblock rw,user_id=0,group_id=0,default_permissions,allow_other
70 17 0:38 / /sys/fs/fuse/connections rw,relatime shared:27 - fusectl fusectl rw
72 19 0:39 / /run/user/0 rw,nosuid,nodev,relatime shared:28 - tmpfs tmpfs rw,size=403260k,mode=700
74 20 0:40 / /mnt/hgfs rw,nosuid,nodev,relatime shared:29 - fuse.vmhgfs-fuse vmhgfs-fuse rw,user_id=0,group_id=0,allow_other
```

### 21. mounts
文件系统挂载信息
```
#(example)
#cat /proc/1/mounts
proc /proc proc rw,nosuid,nodev,noexec,relatime 0 0
sys /sys sysfs rw,nosuid,nodev,noexec,relatime 0 0
dev /dev devtmpfs rw,nosuid,relatime,size=2011756k,nr_inodes=502939,mode=755 0 0
run /run tmpfs rw,nosuid,nodev,relatime,mode=755 0 0
/dev/sda1 / ext4 rw,relatime,data=ordered 0 0
securityfs /sys/kernel/security securityfs rw,nosuid,nodev,noexec,relatime 0 0
tmpfs /dev/shm tmpfs rw,nosuid,nodev 0 0
devpts /dev/pts devpts rw,nosuid,noexec,relatime,gid=5,mode=620,ptmxmode=000 0 0
tmpfs /sys/fs/cgroup tmpfs ro,nosuid,nodev,noexec,mode=755 0 0
cgroup /sys/fs/cgroup/systemd cgroup rw,nosuid,nodev,noexec,relatime,xattr,release_agent=/usr/lib/systemd/systemd-cgroups-agent,name=systemd 0 0
pstore /sys/fs/pstore pstore rw,nosuid,nodev,noexec,relatime 0 0
cgroup /sys/fs/cgroup/devices cgroup rw,nosuid,nodev,noexec,relatime,devices 0 0
cgroup /sys/fs/cgroup/cpu,cpuacct cgroup rw,nosuid,nodev,noexec,relatime,cpu,cpuacct 0 0
cgroup /sys/fs/cgroup/blkio cgroup rw,nosuid,nodev,noexec,relatime,blkio 0 0
cgroup /sys/fs/cgroup/freezer cgroup rw,nosuid,nodev,noexec,relatime,freezer 0 0
cgroup /sys/fs/cgroup/net_cls cgroup rw,nosuid,nodev,noexec,relatime,net_cls 0 0
cgroup /sys/fs/cgroup/pids cgroup rw,nosuid,nodev,noexec,relatime,pids 0 0
cgroup /sys/fs/cgroup/cpuset cgroup rw,nosuid,nodev,noexec,relatime,cpuset 0 0
cgroup /sys/fs/cgroup/memory cgroup rw,nosuid,nodev,noexec,relatime,memory 0 0
systemd-1 /proc/sys/fs/binfmt_misc autofs rw,relatime,fd=28,pgrp=1,timeout=0,minproto=5,maxproto=5,direct 0 0
mqueue /dev/mqueue mqueue rw,relatime 0 0
hugetlbfs /dev/hugepages hugetlbfs rw,relatime 0 0
tmpfs /tmp tmpfs rw,nosuid,nodev 0 0
debugfs /sys/kernel/debug debugfs rw,relatime 0 0
configfs /sys/kernel/config configfs rw,relatime 0 0
vmware-vmblock /run/vmblock-fuse fuse.vmware-vmblock rw,nosuid,nodev,relatime,user_id=0,group_id=0,default_permissions,allow_other 0 0
fusectl /sys/fs/fuse/connections fusectl rw,relatime 0 0
tmpfs /run/user/0 tmpfs rw,nosuid,nodev,relatime,size=403260k,mode=700 0 0
vmhgfs-fuse /mnt/hgfs fuse.vmhgfs-fuse rw,nosuid,nodev,relatime,user_id=0,group_id=0,allow_other 0 0
```

### 22. mountstats
???
```
#(example)
#cat /proc/1/mountstats
device proc mounted on /proc with fstype proc
device sys mounted on /sys with fstype sysfs
device dev mounted on /dev with fstype devtmpfs
device run mounted on /run with fstype tmpfs
device /dev/sda1 mounted on / with fstype ext4
device securityfs mounted on /sys/kernel/security with fstype securityfs
device tmpfs mounted on /dev/shm with fstype tmpfs
device devpts mounted on /dev/pts with fstype devpts
device tmpfs mounted on /sys/fs/cgroup with fstype tmpfs
device cgroup mounted on /sys/fs/cgroup/systemd with fstype cgroup
device pstore mounted on /sys/fs/pstore with fstype pstore
device cgroup mounted on /sys/fs/cgroup/devices with fstype cgroup
device cgroup mounted on /sys/fs/cgroup/cpu,cpuacct with fstype cgroup
device cgroup mounted on /sys/fs/cgroup/blkio with fstype cgroup
device cgroup mounted on /sys/fs/cgroup/freezer with fstype cgroup
device cgroup mounted on /sys/fs/cgroup/net_cls with fstype cgroup
device cgroup mounted on /sys/fs/cgroup/pids with fstype cgroup
device cgroup mounted on /sys/fs/cgroup/cpuset with fstype cgroup
device cgroup mounted on /sys/fs/cgroup/memory with fstype cgroup
device systemd-1 mounted on /proc/sys/fs/binfmt_misc with fstype autofs
device mqueue mounted on /dev/mqueue with fstype mqueue
device hugetlbfs mounted on /dev/hugepages with fstype hugetlbfs
device tmpfs mounted on /tmp with fstype tmpfs
device debugfs mounted on /sys/kernel/debug with fstype debugfs
device configfs mounted on /sys/kernel/config with fstype configfs
device vmware-vmblock mounted on /run/vmblock-fuse with fstype fuse.vmware-vmblock
device fusectl mounted on /sys/fs/fuse/connections with fstype fusectl
device tmpfs mounted on /run/user/0 with fstype tmpfs
device vmhgfs-fuse mounted on /mnt/hgfs with fstype fuse.vmhgfs-fuse
```

### 23. net
目录文件。进程网络相关信息


TODO：net目录下各文件

### 24. ns
目录文件，？？？
```
#(example)
#ls -l /proc/1/ns
total 0
lrwxrwxrwx 1 root root 0 Jan  8 04:53 cgroup -> cgroup:[4026531835]
lrwxrwxrwx 1 root root 0 Jan  8 04:53 ipc -> ipc:[4026531839]
lrwxrwxrwx 1 root root 0 Jan  8 04:53 mnt -> mnt:[4026531840]
lrwxrwxrwx 1 root root 0 Jan  8 04:53 net -> net:[4026531957]
lrwxrwxrwx 1 root root 0 Jan  8 04:53 pid -> pid:[4026531836]
lrwxrwxrwx 1 root root 0 Jan  8 04:53 uts -> uts:[4026531838]
```

### 25. numa_maps
NUMA的内存映射 ???
```
#(example)
#cat /proc/1/numa_maps
559235185000 default file=/usr/lib/systemd/systemd mapped=218 mapmax=3 active=142 N0=218 kernelpagesize_kB=4
55923526e000 default file=/usr/lib/systemd/systemd anon=37 dirty=37 mapmax=2 N0=37 kernelpagesize_kB=4
559235293000 default file=/usr/lib/systemd/systemd anon=1 dirty=1 mapmax=2 N0=1 kernelpagesize_kB=4
559235a81000 default heap anon=148 dirty=148 mapmax=2 N0=148 kernelpagesize_kB=4
7fc1f4000000 default anon=3 dirty=3 N0=3 kernelpagesize_kB=4
7fc1f4029000 default
7fc1f8a18000 default
7fc1f8a19000 default anon=2 dirty=2 N0=2 kernelpagesize_kB=4
7fc1f9219000 default
7fc1f921a000 default anon=2 dirty=2 N0=2 kernelpagesize_kB=4
7fc1f9a1a000 default file=/usr/lib/libattr.so.1.1.0 mapped=4 mapmax=6 N0=4 kernelpagesize_kB=4
7fc1f9a1e000 default file=/usr/lib/libattr.so.1.1.0
7fc1f9c1d000 default file=/usr/lib/libattr.so.1.1.0 anon=1 dirty=1 mapmax=2 N0=1 kernelpagesize_kB=4
7fc1f9c1e000 default file=/usr/lib/libattr.so.1.1.0 anon=1 dirty=1 mapmax=2 N0=1 kernelpagesize_kB=4
7fc1f9c1f000 default file=/usr/lib/libuuid.so.1.3.0 mapped=4 mapmax=22 N0=4 kernelpagesize_kB=4
7fc1f9c23000 default file=/usr/lib/libuuid.so.1.3.0
7fc1f9e22000 default file=/usr/lib/libuuid.so.1.3.0 anon=1 dirty=1 mapmax=2 N0=1 kernelpagesize_kB=4
7fc1f9e23000 default file=/usr/lib/libuuid.so.1.3.0 anon=1 dirty=1 mapmax=2 N0=1 kernelpagesize_kB=4
7fc1f9e24000 default file=/usr/lib/libblkid.so.1.1.0 mapped=28 mapmax=22 N0=28 kernelpagesize_kB=4
7fc1f9e65000 default file=/usr/lib/libblkid.so.1.1.0
7fc1fa064000 default file=/usr/lib/libblkid.so.1.1.0 anon=4 dirty=4 mapmax=2 N0=4 kernelpagesize_kB=4
7fc1fa068000 default file=/usr/lib/libblkid.so.1.1.0 anon=1 dirty=1 mapmax=2 N0=1 kernelpagesize_kB=4
7fc1fa069000 default
7fc1fa06a000 default file=/usr/lib/libz.so.1.2.8 mapped=20 mapmax=28 N0=20 kernelpagesize_kB=4
7fc1fa07f000 default file=/usr/lib/libz.so.1.2.8
7fc1fa27e000 default file=/usr/lib/libz.so.1.2.8 anon=1 dirty=1 mapmax=2 N0=1 kernelpagesize_kB=4
7fc1fa27f000 default file=/usr/lib/libz.so.1.2.8 anon=1 dirty=1 mapmax=2 N0=1 kernelpagesize_kB=4
7fc1fa280000 default file=/usr/lib/libdl-2.24.so mapped=2 mapmax=34 N0=2 kernelpagesize_kB=4
7fc1fa282000 default file=/usr/lib/libdl-2.24.so
7fc1fa482000 default file=/usr/lib/libdl-2.24.so anon=1 dirty=1 mapmax=2 N0=1 kernelpagesize_kB=4
7fc1fa483000 default file=/usr/lib/libdl-2.24.so anon=1 dirty=1 N0=1 kernelpagesize_kB=4
7fc1fa484000 default file=/usr/lib/libidn.so.11.6.16 mapped=4 mapmax=5 N0=4 kernelpagesize_kB=4
7fc1fa4b6000 default file=/usr/lib/libidn.so.11.6.16
7fc1fa6b6000 default file=/usr/lib/libidn.so.11.6.16 anon=1 dirty=1 mapmax=2 N0=1 kernelpagesize_kB=4
7fc1fa6b7000 default file=/usr/lib/libidn.so.11.6.16 anon=1 dirty=1 mapmax=2 N0=1 kernelpagesize_kB=4
7fc1fa6b8000 default file=/usr/lib/libacl.so.1.1.0 mapped=8 mapmax=6 N0=8 kernelpagesize_kB=4
7fc1fa6c0000 default file=/usr/lib/libacl.so.1.1.0
7fc1fa8bf000 default file=/usr/lib/libacl.so.1.1.0 anon=1 dirty=1 mapmax=2 N0=1 kernelpagesize_kB=4
7fc1fa8c0000 default file=/usr/lib/libacl.so.1.1.0 anon=1 dirty=1 mapmax=2 N0=1 kernelpagesize_kB=4
7fc1fa8c1000 default file=/usr/lib/libgpg-error.so.0.21.0 mapped=16 mapmax=28 N0=16 kernelpagesize_kB=4
7fc1fa8d4000 default file=/usr/lib/libgpg-error.so.0.21.0
7fc1faad3000 default file=/usr/lib/libgpg-error.so.0.21.0 anon=1 dirty=1 mapmax=2 N0=1 kernelpagesize_kB=4
7fc1faad4000 default file=/usr/lib/libgpg-error.so.0.21.0 anon=1 dirty=1 mapmax=2 N0=1 kernelpagesize_kB=4
7fc1faad5000 default file=/usr/lib/libgcrypt.so.20.1.5 mapped=16 mapmax=28 N0=16 kernelpagesize_kB=4
7fc1fabdc000 default file=/usr/lib/libgcrypt.so.20.1.5
7fc1faddb000 default file=/usr/lib/libgcrypt.so.20.1.5 anon=2 dirty=2 mapmax=2 N0=2 kernelpagesize_kB=4
7fc1faddd000 default file=/usr/lib/libgcrypt.so.20.1.5 anon=7 dirty=7 mapmax=2 N0=7 kernelpagesize_kB=4
7fc1fade4000 default file=/usr/lib/liblz4.so.1.7.4 mapped=16 mapmax=27 N0=16 kernelpagesize_kB=4
7fc1fadf5000 default file=/usr/lib/liblz4.so.1.7.4
7fc1faff4000 default file=/usr/lib/liblz4.so.1.7.4 anon=1 dirty=1 mapmax=2 N0=1 kernelpagesize_kB=4
7fc1faff5000 default file=/usr/lib/liblz4.so.1.7.4 anon=1 dirty=1 mapmax=2 N0=1 kernelpagesize_kB=4
7fc1faff6000 default file=/usr/lib/liblzma.so.5.2.3 mapped=4 mapmax=29 N0=4 kernelpagesize_kB=4
7fc1fb01b000 default file=/usr/lib/liblzma.so.5.2.3
7fc1fb21a000 default file=/usr/lib/liblzma.so.5.2.3 anon=1 dirty=1 mapmax=2 N0=1 kernelpagesize_kB=4
7fc1fb21b000 default file=/usr/lib/liblzma.so.5.2.3 anon=1 dirty=1 mapmax=2 N0=1 kernelpagesize_kB=4
7fc1fb21c000 default file=/usr/lib/libresolv-2.24.so mapped=16 mapmax=30 N0=16 kernelpagesize_kB=4
7fc1fb230000 default file=/usr/lib/libresolv-2.24.so
7fc1fb42f000 default file=/usr/lib/libresolv-2.24.so anon=1 dirty=1 mapmax=2 N0=1 kernelpagesize_kB=4
7fc1fb430000 default file=/usr/lib/libresolv-2.24.so anon=1 dirty=1 mapmax=2 N0=1 kernelpagesize_kB=4
7fc1fb431000 default
7fc1fb433000 default file=/usr/lib/libm-2.24.so mapped=45 mapmax=30 N0=45 kernelpagesize_kB=4
7fc1fb536000 default file=/usr/lib/libm-2.24.so
7fc1fb735000 default file=/usr/lib/libm-2.24.so anon=1 dirty=1 mapmax=2 N0=1 kernelpagesize_kB=4
7fc1fb736000 default file=/usr/lib/libm-2.24.so anon=1 dirty=1 mapmax=2 N0=1 kernelpagesize_kB=4
7fc1fb737000 default file=/usr/lib/libcap.so.2.25 mapped=4 mapmax=29 N0=4 kernelpagesize_kB=4
7fc1fb73b000 default file=/usr/lib/libcap.so.2.25
7fc1fb93a000 default file=/usr/lib/libcap.so.2.25 anon=1 dirty=1 mapmax=2 N0=1 kernelpagesize_kB=4
7fc1fb93b000 default file=/usr/lib/libc-2.24.so mapped=333 mapmax=45 N0=333 kernelpagesize_kB=4
7fc1fbad0000 default file=/usr/lib/libc-2.24.so
7fc1fbccf000 default file=/usr/lib/libc-2.24.so anon=4 dirty=4 mapmax=2 N0=4 kernelpagesize_kB=4
7fc1fbcd3000 default file=/usr/lib/libc-2.24.so anon=2 dirty=2 N0=2 kernelpagesize_kB=4
7fc1fbcd5000 default anon=3 dirty=3 N0=3 kernelpagesize_kB=4
7fc1fbcd9000 default file=/usr/lib/libpthread-2.24.so mapped=23 mapmax=39 N0=23 kernelpagesize_kB=4
7fc1fbcf1000 default file=/usr/lib/libpthread-2.24.so
7fc1fbef0000 default file=/usr/lib/libpthread-2.24.so anon=1 dirty=1 mapmax=2 N0=1 kernelpagesize_kB=4
7fc1fbef1000 default file=/usr/lib/libpthread-2.24.so anon=1 dirty=1 N0=1 kernelpagesize_kB=4
7fc1fbef2000 default anon=1 dirty=1 N0=1 kernelpagesize_kB=4
7fc1fbef6000 default file=/usr/lib/libmount.so.1.1.0 mapped=73 mapmax=21 N0=73 kernelpagesize_kB=4
7fc1fbf40000 default file=/usr/lib/libmount.so.1.1.0
7fc1fc140000 default file=/usr/lib/libmount.so.1.1.0 anon=1 dirty=1 mapmax=2 N0=1 kernelpagesize_kB=4
7fc1fc141000 default file=/usr/lib/libmount.so.1.1.0 anon=1 dirty=1 mapmax=2 N0=1 kernelpagesize_kB=4
7fc1fc142000 default
7fc1fc144000 default file=/usr/lib/libkmod.so.2.3.1 mapped=21 mapmax=3 N0=21 kernelpagesize_kB=4
7fc1fc159000 default file=/usr/lib/libkmod.so.2.3.1
7fc1fc358000 default file=/usr/lib/libkmod.so.2.3.1 anon=1 dirty=1 mapmax=2 N0=1 kernelpagesize_kB=4
7fc1fc359000 default file=/usr/lib/libkmod.so.2.3.1 anon=1 dirty=1 mapmax=2 N0=1 kernelpagesize_kB=4
7fc1fc35a000 default file=/usr/lib/libpam.so.0.84.2 mapped=13 mapmax=3 N0=13 kernelpagesize_kB=4
7fc1fc367000 default file=/usr/lib/libpam.so.0.84.2
7fc1fc566000 default file=/usr/lib/libpam.so.0.84.2 anon=1 dirty=1 mapmax=2 N0=1 kernelpagesize_kB=4
7fc1fc567000 default file=/usr/lib/libpam.so.0.84.2 anon=1 dirty=1 N0=1 kernelpagesize_kB=4
7fc1fc568000 default file=/usr/lib/libseccomp.so.2.3.1 mapped=44 mapmax=5 N0=44 kernelpagesize_kB=4
7fc1fc594000 default file=/usr/lib/libseccomp.so.2.3.1
7fc1fc793000 default file=/usr/lib/libseccomp.so.2.3.1 anon=21 dirty=21 mapmax=2 N0=21 kernelpagesize_kB=4
7fc1fc7a8000 default file=/usr/lib/libseccomp.so.2.3.1 anon=1 dirty=1 mapmax=2 N0=1 kernelpagesize_kB=4
7fc1fc7a9000 default file=/usr/lib/librt-2.24.so mapped=7 mapmax=31 N0=7 kernelpagesize_kB=4
7fc1fc7b0000 default file=/usr/lib/librt-2.24.so
7fc1fc9af000 default file=/usr/lib/librt-2.24.so anon=1 dirty=1 mapmax=2 N0=1 kernelpagesize_kB=4
7fc1fc9b0000 default file=/usr/lib/librt-2.24.so anon=1 dirty=1 mapmax=2 N0=1 kernelpagesize_kB=4
7fc1fc9b1000 default file=/usr/lib/systemd/libsystemd-shared-232.so mapped=347 mapmax=5 N0=347 kernelpagesize_kB=4
7fc1fcb3d000 default file=/usr/lib/systemd/libsystemd-shared-232.so anon=13 dirty=13 mapmax=2 N0=13 kernelpagesize_kB=4
7fc1fcbc7000 default file=/usr/lib/systemd/libsystemd-shared-232.so anon=1 dirty=1 N0=1 kernelpagesize_kB=4
7fc1fcbc8000 default
7fc1fcbc9000 default file=/usr/lib/ld-2.24.so mapped=35 mapmax=44 N0=35 kernelpagesize_kB=4
7fc1fcdcb000 default anon=10 dirty=10 mapmax=2 N0=10 kernelpagesize_kB=4
7fc1fcde9000 default anon=2 dirty=2 N0=2 kernelpagesize_kB=4
7fc1fcdeb000 default file=/usr/lib/ld-2.24.so anon=1 dirty=1 mapmax=2 N0=1 kernelpagesize_kB=4
7fc1fcdec000 default file=/usr/lib/ld-2.24.so anon=1 dirty=1 N0=1 kernelpagesize_kB=4
7fc1fcded000 default anon=1 dirty=1 N0=1 kernelpagesize_kB=4
7ffc5f05b000 default stack anon=6 dirty=6 mapmax=2 N0=6 kernelpagesize_kB=4
7ffc5f148000 default
7ffc5f14a000 default
```

### 26. oom_adj
出现OOM时进程被kill的权值。范围为[-17,15]，越小意味着越不容易被kill。
```
#(example)
#cat /proc/1/oom_adj
0
```

### 27. oom_score
出现OOM时进程被kill的分值，就是每个进程计算出来的badness。badness越高越容易被kill
```
#(example)
#cat /proc/1/oom_score
0
```

### 28. oom_score_adj
???
```
#(example)
#cat /proc/1/oom_score_adj
0
```

### 29. pagemap
打开后长时间无反应。内存映像(二进制),类似于core


### 30. personality
???
```
#(example)
#cat /proc/1/personality
00000000
```

### 31. root
软链接文件，指向```/```

### 32. sched
进程调度信息
```
#(example)
#cat /proc/1/sched
systemd (1, #threads: 1)
-------------------------------------------------------------------
se.exec_start                                :      10641651.970868
se.vruntime                                  :           139.854055
se.sum_exec_runtime                          :          1162.274514
se.nr_migrations                             :                  206
nr_switches                                  :                 1105
nr_voluntary_switches                        :                  883
nr_involuntary_switches                      :                  222
se.load.weight                               :              1048576
se.avg.load_sum                              :               556434
se.avg.util_sum                              :               402117
se.avg.load_avg                              :                   11
se.avg.util_avg                              :                    8
se.avg.last_update_time                      :       10641651970868
policy                                       :                    0
prio                                         :                  120
clock-delta                                  :                  200
mm->numa_scan_seq                            :                    0
numa_pages_migrated                          :                    0
numa_preferred_nid                           :                   -1
total_numa_faults                            :                    0
current_node=0, numa_group_id=0
numa_faults node=0 task_private=0 task_shared=0 group_private=0 group_shared=0
```

### 33. schedstat
???
```
#(example)
#cat /proc/1/schedstat
1162274514 174247328 1105
```

### 34. smaps
记录进程内存中所有的映射情况，类似于详细信息版本的/proc/[pid]/maps
（该文件只有在开启了内核的CONFIG_MMU选项了才会产生）
```
#(example)
#cat /proc/1/smaps
559235185000-55923526d000 r-xp 00000000 08:01 799480                     /usr/lib/systemd/systemd
Size:                928 kB            /*映射区域的总大小*/
Rss:                 872 kB            /*当前驻留于内存中的大小，即实际内存的占用量。不包括已经交换出去的代码*/
Pss:                 409 kB            /*Private Rss，映射到内存的页面中仅由进程单独使用的量*/
Shared_Clean:        860 kB            /*驻留在内存中与其他内存共享部分的“干净页面”大小，*/
Shared_Dirty:          0 kB            /*驻留在内存中与其他内存共享部分的“赃页”大小*/
Private_Clean:        12 kB            /*驻留在内存中私有的“干净页面”大小*/
Private_Dirty:         0 kB            /*驻留在内存中私有的“赃页”大小*/
Referenced:          872 kB
Anonymous:             0 kB
AnonHugePages:         0 kB
ShmemPmdMapped:        0 kB
Shared_Hugetlb:        0 kB
Private_Hugetlb:       0 kB
Swap:                  0 kB
SwapPss:               0 kB
KernelPageSize:        4 kB
MMUPageSize:           4 kB
Locked:                0 kB
VmFlags: rd ex mr mw me dw 
55923526e000-559235293000 r--p 000e8000 08:01 799480                     /usr/lib/systemd/systemd
Size:                148 kB
Rss:                 148 kB
Pss:                  74 kB
Shared_Clean:          0 kB
Shared_Dirty:        148 kB
Private_Clean:         0 kB
Private_Dirty:         0 kB
Referenced:          148 kB
Anonymous:           148 kB
AnonHugePages:         0 kB
ShmemPmdMapped:        0 kB
Shared_Hugetlb:        0 kB
Private_Hugetlb:       0 kB
Swap:                  0 kB
SwapPss:               0 kB
KernelPageSize:        4 kB
MMUPageSize:           4 kB
Locked:                0 kB
VmFlags: rd mr mw me dw ac 
559235293000-559235294000 rw-p 0010d000 08:01 799480                     /usr/lib/systemd/systemd
Size:                  4 kB
Rss:                   4 kB
Pss:                   2 kB
Shared_Clean:          0 kB
Shared_Dirty:          4 kB
Private_Clean:         0 kB
Private_Dirty:         0 kB
Referenced:            4 kB
Anonymous:             4 kB
AnonHugePages:         0 kB
ShmemPmdMapped:        0 kB
Shared_Hugetlb:        0 kB
Private_Hugetlb:       0 kB
Swap:                  0 kB
SwapPss:               0 kB
KernelPageSize:        4 kB
MMUPageSize:           4 kB
Locked:                0 kB
VmFlags: rd wr mr mw me dw ac 
559235a81000-559235b2e000 rw-p 00000000 00:00 0                          [heap]
Size:                692 kB
Rss:                 592 kB
Pss:                 510 kB
Shared_Clean:          0 kB
Shared_Dirty:        164 kB
Private_Clean:         0 kB
Private_Dirty:       428 kB
Referenced:          592 kB
Anonymous:           592 kB
AnonHugePages:         0 kB
ShmemPmdMapped:        0 kB
Shared_Hugetlb:        0 kB
Private_Hugetlb:       0 kB
Swap:                  0 kB
SwapPss:               0 kB
KernelPageSize:        4 kB
MMUPageSize:           4 kB
Locked:                0 kB
VmFlags: rd wr mr mw me ac 
```

### 35. stack
???
```
#(example)
#cat /proc/1/stack
[<ffffffff81252f2b>] ep_poll+0x27b/0x350
[<ffffffff8125443e>] SyS_epoll_wait+0xce/0xf0
[<ffffffff815f8032>] entry_SYSCALL_64_fastpath+0x1a/0xa4
[<ffffffffffffffff>] 0xffffffffffffffff
```

### 36. stat
当前进程的状态信息
```
#(example)
#cat /proc/1/stat
1 (systemd) S 0 1 1 0 -1 4194560 2837 215477 66 637 8 107 1641 3161 20 0 1 0 5 138170368 1607 18446744073709551615 94086444371968 94086445321800 140721902830496 140721902828608 140471127129555 0 671173123 4096 1260 1 0 0 17 1 0 0 113 0 0 94086445329472 94086445478188 94086453792768 140721902833623 140721902833634 140721902833634 140721902833645 0
```

### 37. statm
记录内存使用方面的信息，具体各项参数信息如下：
+ size (same as VmSize in /proc/[pid]/status）    
程序内存总大小
+ resident (same as VmRSS in /proc/[pid]/status)    
实际使用物理内存大小
+ share (from shared mappings)    
共享页面数量
+ text (code)    
代码段大小
+ lib (library)    
库文件大小
+ data (data + stack)    
数据段与堆栈段大小总和
+ dt (dirty pages)     
“脏页”数量
```
#(example)
#cat /proc/1/statm
#size resident share text lib data dt
33733 1607 1302 232 0 4403 0
```

### 38. status
进程运行系统状态
```
#(example)
#cat /proc/1/status
Name:    systemd        /*产生此进程的命令*/
Umask:    0000
State:    S (sleeping)        /*进程的当前状态*/
Tgid:    1        /*进程组id号*/
Ngid:    0
Pid:    1        /*进程id号*/
PPid:    0
TracerPid:    0
Uid:    0    0    0    0
Gid:    0    0    0    0
FDSize:    64        /*目前已分配文件描述符个数*/
Groups:
NStgid:    1
NSpid:    1
NSpgid:    1
NSsid:    1
VmPeak:      200468 kB        /*虚拟内存峰值*/
VmSize:      134932 kB        /*虚拟内存大小*/
VmLck:           0 kB        /*已锁虚拟内存大小*/
VmPin:           0 kB
VmHWM:        6428 kB        /*实际使用物理内存峰值（即进程的“高水位”）*/
VmRSS:        6428 kB        /*实际使用物理内存大小*/
RssAnon:        1220 kB
RssFile:        5208 kB
RssShmem:           0 kB
VmData:       17476 kB        /*数据段大小*/
VmStk:         136 kB        /*堆栈段大小*/
VmExe:         928 kB        /*文本段大小*/
VmLib:        7176 kB        /*共享库大小*/
VmPTE:         124 kB        /*页表项大小*/
VmPMD:          12 kB
VmSwap:           0 kB
HugetlbPages:           0 kB
Threads:    1        /*进程中所含线程数量*/
SigQ:    0/15716
SigPnd:    0000000000000000
ShdPnd:    0000000000000000
SigBlk:    7be3c0fe28014a03
SigIgn:    0000000000001000
SigCgt:    00000001800004ec
CapInh:    0000000000000000
CapPrm:    0000003fffffffff
CapEff:    0000003fffffffff
CapBnd:    0000003fffffffff
CapAmb:    0000000000000000
Seccomp:    0
Cpus_allowed:    ffffffff,ffffffff,ffffffff,ffffffff
Cpus_allowed_list:    0-127
Mems_allowed:    00000000,00000001
Mems_allowed_list:    0
voluntary_ctxt_switches:    885
nonvoluntary_ctxt_switches:    222
```

### 39. syscall
???
```
#(example)
#cat /proc/1/syscall
232 0x4 0x7ffc5f07bc50 0x36 0xffffffff 0x431bde82d7b634db 0xc60 0x7ffc5f07bc40 0x7fc1fba23dd3
```

### 40. task
目录文件。进程包含的线程，其内容为各个目录文件，以线程的ID命名，代表各个线程

### 41. timerslack_ns
???
```
#(example)
#cat /proc/1/timerslack_ns
50000
```

### 42. wchan
???
```
#(example)
#cat /proc/1/wchan
ep_poll
```
