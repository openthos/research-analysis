# Kernel build note

### 1 Compile kernel in Ubuntu

#### 1.1 Prepare

##### (1) Install build-essential、kernel-package and libncurses5-dev

```shell
$ sudo apt install build-essential kernel-package libncurses5-dev
```

##### (2) Download the source code of kernel

​	There are two ways to get the code of kernel：

​	a) Download from [https://www.kernel.org/pub/linux/kernel/](https://www.kernel.org/pub/linux/kernel/)

​	b) Use git to clone from [http://git.kernel.org/cgit/linux/kernel/git/stable/linux-stable.git](http://git.kernel.org/cgit/linux/kernel/git/stable/linux-stable.git)

​	The first way is can get every sublevel, while the second way is easiler but can only get every patchlevel.

​	What‘s more, the command to decompress .tar.xz deserves to note: (x means the VERSION of kernel, y means the PATCHLEVEL of kernel, z means the SUBLEVEL of kernel)

```shell
$ tar Jfxv linux-x.y.z.tar.xz
```

##### (3) Patching your kernel

​	The older way of manually patching the kernel with：

```shell
$ patch -p1 <patchfile
```

​	This way does not create any git history, which makes it hard to revert and retry different patches. You will often have to go through several patches with a maintainer to find the right fix for a bug, so having the git history is useful.

​	So, the new way to patching the kernel is: http://blog.csdn.net/lcw_202/article/details/6106381

##### (4) Setting up your kernel configuration

​	Before you compile the kernel, you need to make a config. Two of the most useful methods to make a config are:

​	a) Use the default config. This command will use the default config of the architecture of your computer.

```shell
linux-x.y.z $ make defconfig
```

​	b) Use the graphical interface like menuconfig and nconfig.

```shell
linux-x.y.z $ make menuconfig
```

​	or :

```shell
linux-x.y.z $ make nconfig
```

##### (5) Building the kernel

​	Run

```
make

```

​	Or, if you have a multi-core processor, run 

```
make -jX

```

​	Where X is a number like 2 or 4. If you have a dual core, 2 or 3 might be good. Quad core, 4 or 6. If you are not sure, just run "make" without "-jX".

### 2 Real-Time Linux

