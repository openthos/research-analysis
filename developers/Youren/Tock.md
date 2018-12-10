Tock的故事背景：
在嵌入式系统中，IOT环境下的很多处理器都是microcontroller，没有MMU，只有物理地址，但是可以提供一个MPU(Memory protection unit)，这个MPU可以提供内存的简单隔离（类似于段机制），可以将内存划分8个区域（或更多）。
那么在这种环境下，内存的大小通常也很小，只有64KB。但是还是需要有嵌入式操作系统。

作者定义了几种嵌入式系统的特性：
每种特性都可以分为有用，不好做两个部分
1. Dependability
 嵌入式系统经常没有人参与维护，只有有限制的用户接口，因此可靠性非常的重要，因为机器一旦无法工作，没有人会去修复机器。因此，许多的嵌入式系统通过静态分配内存，或者在compile-time确定内存需求等方法来确保可靠性。
2. Concurrency
在嵌入式系统中，许多的应用都有能耗的需求，如果能够引入Concurrency，那么CPU的处理可以和IO操作重叠，可以提高系统的能耗。有些系统通过提供协助的run-to-complete 模型来简化stack 管理，长时间的操作会消耗完CPU资源。为了防止这个，有些系统采用抢占式调度。
3. Efficiency
Efficiency主要是指内存的有效，即分配出去的内存有多少真的在使用。最有效的当然是使用动态分配内存，但是这和dependability 冲突。或者通过设计可以静态决定使用多少内存的方式达到最大的利用率。有一些操作系统的静态分配的浪费率达到80%。
4. Fault Isolation
将用户程序互相隔离开，一个用户程序无法影响另一个程序的运行，在嵌入式系统中支持多线程运行很重要。到最近microcontroller都没有提供 硬件的保护机制，因此嵌入式的操作系统都没有提供硬件隔离。 有一些通过bytecode interpreter，有一些通过API设计和guardregion 保证。
5. loadable applicaiton
应用程序是否可动态加载，即是否支持动态创建程序。

作者设计的TOCK系统希望可以同时满足上面的五点，TOCK的基本架构如下
TOCK分为内核态和用户态，内核态以rust 写的Capsules为基本单位，用户态的process 可以是任意语言编写的。
Capsules通过语言在compile-time实现隔离，同时process 通过MPU实现硬件辅助的隔离。

在TOCK 的系统中， threat model 通过系统中的4个角色确定：
1. Board integrators
Board Integrators 是负责将主板和主板上的驱动以及部分的应用程序组合在一起的人。其负责分发kernel components，对古剑和系统有着绝对的控制权限。
2. Kernel component developers
内核模块开发者负责写大部分的内核的功能，包括总线驱动和通信协议等，以capsule的形式写。board integrators会对kernel component developers编写的内核模块进行审查，但是tock不认为board integrators 可以将所有的bug 都找出来。Tock 可以限制错误的capsule 代码造成的错误。一个capsule可能会耗尽CPU的资源，但是无法越界访问不属于自己的资源。
3. Application developes
用户程序的开发者是不可信的，他们可能想要阻止系统运行，破坏别的application。 同时application 的代码并不是 硬件交付的时候就全部部署了——可以是后期通过终端用户来动态安装。
4. End-User
通常是没有编程背景的普通用户，不了解安全相关的知识。

Tock 的kernel 是由叫做capsule 的kernel component编写的。 capsule 是由rust 写的，一个capsule 是一个rust 的结构体的实例。kernel cooperative 的调度capsule，capsule 共享一个栈。
Capsule 分了一些类型，最基础的划分方式是，有些capsule 是负责管理资源的，这些capsule 通常都认为不是十分可信的。 另一些capsule 是负责直接操作硬件的，这些capsule通常需要被更严格的要求。Capsule 的隔离是通过Rust 的type system 和module system 实现的，这样就让隔离是在compile time 实现，而不会增加run-time overhead。
Rust 的语言机制可以提供很强的安全保证，一个不可信的capsule 只可以访问显式赋给他的资源。
Capsule 之间的concurrency如何支持呢？
Kernel 调度 capsule 是event-driven的，同时也是cooperative 的（cooperative 意思是一直运行直到主动放弃CPU）。
Event 只有可能是
1. Hardware interrupt
2. Application syscall
而Capsule 之间是不会有event 产生的，capsule 之间使用正常的控制流转化（call/jump）

Processes则是Tock 的用户进程的组织，其可以是使用任意语言写的，使用MPU进行硬件隔离。
另外Process 之间的IPC通过MPU划分一个多个process能够同时访问的内存来实现。

Tock 中另一个很重要的概念是Grants。
想象一下Tock 中：
如果capsule 是静态分配内存的，那么一个process 可以像这个capsule发送多个请求导致这个capsule 无法响应别的process 的请求。
如果capsule 是动态分配内存的，那么如果有多个process 请求同一个 capsule 的服务，那么这个capsule 为了处理这些服务，需要分配内存，很可能很快就分配完了，其他的capsule 无法响应服务。
两者都会导致dependability受损。
为了解决这个问题，Tock中采用了取巧的办法：在每个process 中预留一块内存，一旦需要请求某个capsule的服务，那么这个capsule 就会在这个process 预留内存中分配一块给自己使用。这样就保证一个process 请求的服务太多，只会影响自己。

capsule 对grants的访问都是通过rust 的类型系统的，因此一个capsule 不会访问到别的capsule的grant。同时Tock使用mpu保护grants，让process 无法访问grant，保证 grant的类型安全。
另一方面，为了保证capsule 每一次访问grants时，这个grants都是有效的（包括这个process还存活），tock 采用了两种方法：
1. 每个process 只能同时允许一个capsule操作。因此一个capsule如果释放了这个process（或者grant），capsule自己是知道的。
2. 对grant的访问都通过几个有限的API，保证在访问每一个grant之前，都确保这个process 是有效的。

因为grants集中在process中，因此对grants的分配和释放都比较方便。

我们可以对比观察，Tock 的process 是满足之前的五个条件的。

对于MPU的管理，可以多说一句：
每个MPU都有一组寄存器可以用来管理MPU。当运行在kernel态时，将MPU disable。当运行在某个process时，将MPU设置为这个process 的代码段，数据段等，但不包括grants。并不是MPU支持几个region，就最多支持多少个process。
