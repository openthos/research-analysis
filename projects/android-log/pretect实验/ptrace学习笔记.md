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
参数request：控制ptrace函数的行为，定义在sys/ptrace.h中，可取的值有:
```
       PTRACE_ME

       PTRACE_PEEKTEXT

       PTRACE_PEEKDATA

       PTRACE_PEEKUSER 查看USER区域的内容，例如查看寄存器的值。USER区域为一个结构体（定义在sys/user.h中的user结构体）。

                       内核将寄存器的值储存在该结构体中，便于tracer通过ptrace函数查看

       PTRACE_POKETEXT

       PTRACE_POKEDATA

       PTRACE_POKEUSER

       PTRACE_GETREGS

       PTRACE_GETFPREGS,

       PTRACE_SETREGS

       PTRACE_SETFPREGS

       PTRACE_CONT

       PTRACE_SYSCALL 使tracee在触发系统调用或者结束系统调用时暂停，同时向tracer发送signal

       PTRACE_SINGLESTEP

       PTRACE_DETACH
```
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

##### 3.1 拦截系统调用，获取系统调用编号

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
##### 3.2 读取系统调用参数 查看write系统调用（由ls命令向控制台打印文字触发）的参数
```
#include <sys/ptrace.h>
#include <sys/types.h>
#include <sys/wait.h>
#include <sys/reg.h>
#include <sys/user.h>
#include <sys/syscall.h>
#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>

int main()
{
    pid_t child;
    long orig_rax,rax;
    long params[3]={0};
    int status;        //status变量时用来检测是否tracee已经执行结束，是否需要继续等待tracee执行
    int insyscall = 0;
    child = fork();    //fork创建出一个我们将要跟踪（trace）的子进程
    if(child == 0)
    {
        ptrace(PTRACE_TRACEME,0,NULL,NULL);  //子进程通过ptrace函数的PTRACE_TRACEME参数来告知内核自己将要被跟踪
        execl("/bin/ls","ls",NULL); //execl函数实际上会触发execve这个系统调用，这时内核发现0进程为tracee，然后将其暂停，
                                    //发送一个signal唤醒等待中的tracer(此程序中为主线程)。
    }
    else
    {    
        while(1)
        {
            wait(&status);
            if(WIFEXITED(status))
                break;
            orig_rax = ptrace(PTRACE_PEEKUSER,child,8*ORIG_RAX,NULL);//当触发系统调用时，内核会将保存调用编号的rax寄存器的内容保存在
                                                                     //orig_rax中，我们可以通过ptrace的PTRACE_PEEKUSER参数来读取。
                                                                     //ORIG_RAX为寄存器编号,保存在sys/reg.h中，而在64位系统中，每个
                                                                     //寄存器有8个字节的大小，所以此处用8*ORIG_RAX来获取该寄存器地址。
            //printf("the child made a system call %ld\n",orig_rax);
            if(orig_rax == SYS_write) //过滤write系统调用
            {
                if(insyscall == 0)
                {
                    insyscall = 1;
                    params[0] = ptrace(PTRACE_PEEKUSER,child,8*RDI,NULL);//使用PTRACE_PEEKUSER参数来查看系统调用的参数
                    params[1] = ptrace(PTRACE_PEEKUSER,child,8*RSI,NULL);//使用PTRACE_PEEKUSER参数来查看系统调用的参数
                    params[2] = ptrace(PTRACE_PEEKUSER,child,8*RDX,NULL);//使用PTRACE_PEEKUSER参数来查看系统调用的参数
                    printf("write called with %ld, %ld, %ld\n",params[0],params[1],params[2]);
                }
                else
                {
                    rax = ptrace(PTRACE_PEEKUSER,child,8*RAX,NULL);//使用PTRACE_PEEKUSER参数来查看保存在RAX寄存器中的系统调用返回值
                    printf("write returned with %ld\n",rax);
                    insyscall = 0;
                }
            }
            ptrace(PTRACE_SYSCALL,child,NULL,NULL); //使tracee在触发系统调用或者结束系统调用时暂停，同时向tracer发送signal
        }
    }
    return 0;

}
```
##### 3.3 读取所有寄存器的值
```
#include <sys/ptrace.h>
#include <sys/types.h>
#include <sys/wait.h>
#include <sys/user.h>
#include <sys/reg.h>
#include <sys/syscall.h>
#include <unistd.h>
#include <stdio.h>

int main()
{
    pid_t child;
    long orig_rax ,rax;
    long params[3] = {0};
    int status = 0;
    int insyscall = 0;
    struct user_regs_struct regs;
    child = fork();
    if(child == 0)
    {
        ptrace(PTRACE_TRACEME,0,NULL,NULL);
        execl("/bin/ls","ls",NULL);
    }
    else
    {
        while(1)
        {
            wait(&status);
            if(WIFEXITED(status))
                break;
            orig_rax = ptrace(PTRACE_PEEKUSER,child,8*ORIG_RAX,NULL);
            if(orig_rax == SYS_write)
            {
                if(insyscall == 0)
                {
                    insyscall = 1;
                    ptrace(PTRACE_GETREGS,child,NULL,&regs); //通过PTRACE_GETREGS参数获取了所有的寄存器值。
                                                             //结构体user_regs_struct定义在sys/user.h中
                    printf("write called with %llu, %llu, %llu\n",regs.rdi,regs.rsi,regs.rdx);
                }
                else
                {
                    ptrace(PTRACE_GETREGS,child,NULL,&regs);
                    printf("write returned with %ld\n",regs.rax);
                    insyscall = 0;
                }
            }
            ptrace(PTRACE_SYSCALL,child,NULL,NULL);
        }
    }
    return 0;
}
```

##### 3.4 修改系统调用的参数
```
#include <sys/ptrace.h>
#include <sys/user.h>
#include <sys/reg.h>
#include <sys/wait.h>
#include <sys/syscall.h>
#include <unistd.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>


#define LONG_SIZE 8
//获取参数
char* getdata(pid_t child,unsigned long addr,unsigned long len)
{
    char *str =(char*) malloc(len + 1);
    memset(str,0,len +1);
    union u{
        long int val;
        char chars[LONG_SIZE];
    }word;
    int i, j;    
    for(i = 0,j = len/LONG_SIZE; i<j; ++i)
    {
        word.val = ptrace(PTRACE_PEEKDATA,child,addr + i*LONG_SIZE,NULL);
        if(word.val == -1)
            perror("trace get data error");
        memcpy(str+i*LONG_SIZE,word.chars,LONG_SIZE);
    }
    j = len % LONG_SIZE;
    if(j != 0)
    {
        word.val = ptrace(PTRACE_PEEKDATA,child,addr + i*LONG_SIZE,NULL);
        if(word.val == -1)
            perror("trace get data error");
        memcpy(str+i*LONG_SIZE,word.chars,j);
    }
    return str;
}
//提交参数
void putdata(pid_t child,unsigned long  addr,unsigned long len, char *newstr)
{
    union u
    {
        long val;
        char chars[LONG_SIZE];
    }word;
    int i,j;
    for(i = 0, j = len/LONG_SIZE; i<j ; ++i)
    {
        memcpy(word.chars,newstr+i*LONG_SIZE,LONG_SIZE);
        if(ptrace(PTRACE_POKEDATA, child, addr+i*LONG_SIZE,word.val) == -1)  //使用了ptrace的PTRACE_POKEDATA参数来修改系统调用的参数值
            perror("trace error");

    }
    j = len % LONG_SIZE;
    if(j !=0 )
    {
        memcpy(word.chars,newstr+i*LONG_SIZE,j);
        ptrace(PTRACE_POKEDATA, child, addr+i*LONG_SIZE,word.val);
    }
}

//修改参数
void reserve(char *str,unsigned int len)
{
    int i,j;
    char tmp;
    for(i=0,j=len-2; i<=j; ++i,--j )
    {
        tmp = str[i];
        str[i] = str[j];
        str[j] = tmp;
    }
}

int main()
{
    pid_t child;
    child = fork();
    if(child == 0)
    {
        ptrace(PTRACE_TRACEME,0,NULL,NULL);
        execl("/bin/ls","ls",NULL);
    }
    else
    {
        struct user_regs_struct regs;
        int status = 0;
        int toggle = 0;
        while(1)
        {
            wait(&status);
            if(WIFEXITED(status))
                break;
            memset(&regs,0,sizeof(struct user_regs_struct));
            if(ptrace(PTRACE_GETREGS,child,NULL,&regs) == -1)
            {
                perror("trace error");
            }
            
            if(regs.orig_rax == SYS_write)
            {
                if(toggle == 0)
                {
                    toggle = 1;
                    //in x86_64 system call ,pass params with %rdi, %rsi, %rdx, %rcx, %r8, %r9
                    //no system call has over six params 
                    printf("make write call params %llu, %llu, %llu\n",regs.rdi,regs.rsi,regs.rdx);
                    char  *str = getdata(child,regs.rsi,regs.rdx);
                    printf("old str,len %lu:\n%s",strlen(str),str);
                    reserve(str,regs.rdx);
                    printf("hook str,len %lu:\n%s",strlen(str),str);
                    putdata(child,regs.rsi,regs.rdx,str);
                    free(str);
                }
                else
                {
                    toggle = 0;
                }
            }
            ptrace(PTRACE_SYSCALL,child,NULL,NULL);
        }
    }
    return 0;
}
```

##### 3.5 单步调试
```
#include <sys/ptrace.h>
#include <sys/types.h>
#include <sys/user.h>
#include <sys/reg.h>
#include <sys/syscall.h>
#include <sys/wait.h>
#include <stdio.h>
#include <unistd.h>

#define LONG_SIZE 8

void main()
{
    pid_t chid;
    chid = fork();
    if(chid == 0)
    {
        ptrace(PTRACE_TRACEME,0,NULL,NULL);
　　　　 //这里的test是一个输出hello world的小程序
        execl("./test","test",NULL);
    }
    else
    {
        int status = 0;
        struct user_regs_struct regs;
        int start = 0;
        long ins;
        while(1)
        {
            wait(&status);
            if(WIFEXITED(status))
                break;
            ptrace(PTRACE_GETREGS,chid,NULL,&regs);
            if(start == 1)
            {
                ins = ptrace(PTRACE_PEEKTEXT,chid,regs.rip,NULL); //通过rip寄存器的值来获取下一条要执行指令的地址
                                                                  //最后用PTRACE_PEEKTEXT读取
                printf("EIP:%llx Instuction executed:%lx\n",regs.rip,ins);
            }
            if(regs.orig_rax == SYS_write)
            {
                start = 1;
                ptrace(PTRACE_SINGLESTEP,chid,NULL,NULL);
            }else{
                ptrace(PTRACE_SYSCALL,chid,NULL,NULL);
            }
        }
    }
}
```
##### 3.6 进程附加
在之前的文章中，我们都是trace自己程序fork出来的子进程，现在我们来看一下如何trace一个正在运行的进程。
trace一个正在运行的进程称为进程附加（attach）。使用的是ptrace函数的PTRACE_ATTACH参数。当一个进程成功附加到一个正在运行的进程时，此进程会成为被
附加进程的父进程，同时向被附加的进程发送一个SIGSTOP信号，让其停止，这时我们就可以对其进行操纵。当我们完成对tracee的操作后就可以使用ptrace的PTRACE_DETACH参数停止附加。

我们用一个循环来模拟一个正在运行的进程，下边称此程序为hello
```
int main()
{   int i;
    for(i = 0;i < 10; ++i) {
        printf("My counter: %d\n", i);
        sleep(2);
    }
    return 0;
}
```
在其运行之后我们可以使用 ps -h 命令查看其进程号（pid），以便我们通过进程号对其附加。
接下来看一个简单的进程附加的例子
```
#include <sys/types.h>
#include <sys/reg.h>
#include <sys/user.h>
#include <sys/wait.h>
#include <sys/ptrace.h>
#include <stdio.h>
#include <unistd.h>
#include <stdlib.h>

int main(int argc, char *argv[])
{
    pid_t traced_process;
    struct user_regs_struct regs;
    long ins;
    if(argc != 2)
    {
        puts("no pid input");
        exit(1);
    }
    traced_process = atoi(argv[1]);
    printf("try to trace pid :%u\n",traced_process);
    if(ptrace(PTRACE_ATTACH,traced_process,NULL,NULL)==-1)
    {
        perror("trace error:");
    }
    wait(NULL);
    if(ptrace(PTRACE_GETREGS,traced_process,NULL,&regs)==-1)
    {
        perror("trace error:");
    }
    ins = ptrace(PTRACE_PEEKTEXT,traced_process,regs.rip,NULL);
    if(ins == -1)
    {
        perror("trace error:");
    }
    printf("EIP:%llx Instruction executed: %lx\n",regs.rip,ins);
    if(ptrace(PTRACE_DETACH,traced_process,NULL,NULL)==-1)
    {
        perror("trace error:");
    }
    return 0;
}
```
对hello进行了附加，等其停下来以后，读取hello要运行的下一条指令的内容（地址存在rip中）。读取之后停止附加，让hello继续运行。

在x64机器上需要进行修改，改成<sys/user.h>
在x64机器上我们看到
其实最终访问的文件是/usr/include/x86_64-linux-gnu/sys/user.h 

#### 参考资料：

[x86_64平台ptrace的使用](https://www.cnblogs.com/mmmmar/p/6040325.html)

[x86平台ptrace的使用](http://blog.csdn.net/sealyao/article/details/6710772)

[ptrace官方文档](http://man7.org/linux/man-pages/man2/ptrace.2.html)

[Linux Ptrace 详解](http://blog.csdn.net/u012417380/article/details/60470075)
