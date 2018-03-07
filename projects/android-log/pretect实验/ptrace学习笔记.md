### ptrace学习笔记

#### 1.前言

##### 1.1 什么是ptrace

ptrace系统函数是Linux提供了的一种优雅机制，使得不用使用复杂的kernel编程，就能实现对系统调用的拦截、改变系统调用的参数来愚弄你的系统kernel、使运行中

的进程暂停并且控制它等一系列在用户层拦截和修改系统调用(sys call)的操作

##### 1.2 ptrace原理
ptrace采取一种使父进程得以监视和控制其它进程的方式，它还能够改变子进程中的寄存器和内核映像，因而可以实现断点调试和系统调用的跟踪。这里把使用ptrace函

数的进程称为tracer，被控制的进程称为tracee。

##### 1.3 ptrace功能

拦截一个系统调用，然后修改它的参数

设置断点，插入代码到一个正在运行的程序中

总之就是，潜入到机器内部，偷窥和纂改进程的寄存器和数据段

##### 1.4 ptrace参数
```
long ptrace(enum __ptrace_request request,pid_t pid,void addr, void *data);
```
参数request：控制ptrace函数的行为，定义在sys/ptrace.h中

参数pid：指定tracee的进程号

以上两个参数是必须的，之后两个参数分别为地址和数据，其含义由参数request控制。

具体request参数的取值及含义可查看帮助文档（控制台输入： man ptrace）

注意返回值，man手册上的说法是返回一个字的数据大小，在32位机器上是4个字节，在64位机器上是8个字节，都对应一个long的长度。

#### 2. 基础知识

##### 2.1 什么是系统调用

系统调用(system calls)：操作系统提供的一种标准的服务（API）来让程序员实现对底层硬件和服务的控制（比如文件系统）。每个系统调用都有一个调用编号，可以

在unistd.h中查询。

##### 2.2 系统调用原理

当一个程序需要作系统调用的时候，它将相关参数放进系统调用相关的寄存器，然后调用软中断0x80，这个中断就像一个让程序得以接触到内核模式的窗口，程序将参数和

系统调用号交给内核，进入内核模式，通过内核来执行这个系统调用的代码。

##### 2.3 X86_64体系和x86体系寄存器的区别

1、在X86_64体系中，系统调用号保存在寄存器%rax中,调用参数依次保存在%rdi,%rsi,%rdx,%rcx,%r8和%r9中

比如，在以下的调用Write(2, “Hello”, 5)的汇编形式大概是这样的

```
mov rax, 1
mov rdi, message
mov rdx, 5
syscall
message:
db "Hello"
```
2、在x86体系中，系统调用号保存在寄存器%eax中，其余的参数依次保存在%ebx,%ecx,%edx,%esi中

比如，在以下的调用Write(2, “Hello”, 5)的汇编形式大概是这样的

```
movl   $4, %eax  
movl   $2, %ebx  
movl   $hello, %ecx  
movl   $5, %edx  
int    $0x80
 ```
##### 2.3 ptrace与系统调用的关系

在执行系统调用时，内核先检测一个进程是否为tracee，如果是的话内核就会暂停该进程，然后把控制权转交给tracer，之后tracer就可以查看或者修改tracee的寄

存器了。

#### 3. 示例代码

##### 3.1 获取系统调用编号

```
#include <sys/ptrace.h>
#include <sys/types.h>
#include <sys/wait.h>
#include <unistd.h>
#include <sys/reg.h>
#include <sys/user.h>
#include <stdio.h>

int main()
{
    pid_t child;
    long orig_rax;
    child = fork();             //fork创建出一个我们将要跟踪（trace）的子进程
    if(child == 0)
    {
        ptrace(PTRACE_TRACEME,0,NULL,NULL);   //子进程通过ptrace函数的PTRACE_TRACEME参数来告知内核自己将要被跟踪
        execl("/bin/ls","ls",NULL); //execl函数实际上会触发execve这个系统调用，这时内核发现0进程为tracee，然后将其暂停，
                                    //发送一个signal唤醒等待中的tracer(此程序中为主线程)。
    }
    else
    {
        wait(NULL);
        orig_rax = ptrace(PTRACE_PEEKUSER,child,8*ORIG_RAX,NULL);//当触发系统调用时，内核会将保存调用编号的rax寄存器的内容保存在
                                                                 //orig_rax中，我们可以通过ptrace的PTRACE_PEEKUSER参数来读取。
                                                                 //ORIG_RAX为寄存器编号,保存在sys/reg.h中，而在64位系统中，每个
                                                                 //寄存器有8个字节的大小，所以此处用8*ORIG_RAX来获取该寄存器地址。
        printf("the child made a system call %ld\n",orig_rax);
        ptrace(PTRACE_CONT,child,NULL,NULL);//当我们获取到系统调用编号以后，就可以通过ptrace的PTRACE_CONT参数来唤醒暂停中的子进程，
                                            //让其继续执行。
    }
    return 0;
}

//输出：the child made a system call 59
```
##### 3.2 获取系统调用编号





#### 参考资料：

[x86_64平台ptrace的使用](https://www.cnblogs.com/mmmmar/p/6040325.html)

[x86平台ptrace的使用](http://blog.csdn.net/sealyao/article/details/6710772)

[ptrace官方文档](http://man7.org/linux/man-pages/man2/ptrace.2.html)

[Linux Ptrace 详解](http://blog.csdn.net/u012417380/article/details/60470075)
