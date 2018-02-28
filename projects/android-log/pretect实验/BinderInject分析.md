### BinderInject分析
#### 论文原文摘录
It is worth noting that we rely on a dynamic instrumentation mechanism to keep Pretect compatible with most Android
versions and devices. The mechanism requires no changes to the target app per se. It also does not require us to recompile
the underlying OS and the Android framework. Moreover, the tool requires little human effort to install and apply.

We intercept Android framework methods in both Java and C. This approach is more light-weight and easier to implement
than tracking the functions at the OS level, which typically requires heavy-weighted and sophisticated tools for kernel
instrumentation. More importantly, we can rely on an Android-specific feature to conveniently track the relevant methods.

For our C method interception, we note that the Android OS is based on the Linux kernel. A well-known Linux system
tool named ptrace, which is commonly used in debugging tools (e.g., gdb), is also available on Android. Ptrace makes
it possible to inspect the child process of the parent process.Ptrace enables the parent process to read and replace the
value of the register of the child process. We can utilize ptrace to attach code to a target process (with a known
process ID pid). Then, we are able to take over the execution of the target process. By analyzing the elf-format library files
of the target process, we can locate the memory addresses of the methods with the relevant names and invoke them
accordingly. Therefore, it is feasible to invoke the dlopen, dlsym library-related system calls of the target process. We
implement the idea by adopting a tool called LibInject [25].

Libinject – c/c++ code injection library. [Online]. Available: http://blog.csdn.net/jinzhuojun/article/details/9900105

#### Android native层动态链接库注入扫盲

Libinject注入代码是基于shellcode实现，这里称要被注入的进程为目标进程，大致的实现思路是：

1.让目标进程调用其mmap函数在其进程内存中申请一段内存空间，用来写shellcode和参数

2.将要注入的so库的名称字符串和so库中要调用的函数名称字符串写入到目标进程的内存（上面申请的内存）中

3.将编写好的ShellCode汇编代码写入到到目标进程的内存（上面申请的内存）中，shellcode会调用dlopen来载入我们的library

4.修改目标进程的PC寄存器的值，让其跳到注入的ShellCode代码中执行，实现so库的注入，然后调用注入的so库中的函数。

Android的so库注入代码的头文件inject.h：
```
#pragma once

#include <sys/types.h>

#ifdef __cplusplus
extern "C"
{
#endif
//远程进程注入
int inject_remote_process( pid_t target_pid, const char *library_path, const char *function_name, 
                                                       void *param, size_t param_size );
//根据进程的名字获取进程的PID
int find_pid_of( const char *process_name );
//获取进程加载的模块的基址
void* get_module_base( pid_t pid, const char* module_name );

#ifdef __cplusplus
}
#endif

//进程注入的参数-根据Hook的函数需要自定义该结构体
struct inject_param_t
{
	pid_t from_pid;
} ;
```

Android的so库注入代码的实现文件inject.c：

```
/*
 ============================================================================
 Name        : libinject.c
 Author      :  
 Version     :
 Copyright   : 
 Description : Android shared library inject helper
 ============================================================================
 */

#include <stdio.h>
#include <stdlib.h>
#include <asm/ptrace.h>
#include <asm/user.h>
#include <asm/ptrace.h>
#include <sys/wait.h>
#include <sys/mman.h>
#include <dlfcn.h>
#include <dirent.h>
#include <unistd.h>
#include <string.h>
#include <utils/Log.h>



#define ENABLE_DEBUG 1

#define PTRACE_PEEKTEXT 1
#define PTRACE_POKETEXT 4
#define PTRACE_ATTACH	16
#define PTRACE_CONT 	7
#define PTRACE_DETACH   17
#define PTRACE_SYSCALL	24
#define CPSR_T_MASK		( 1u << 5 )

#define  MAX_PATH 0x100
//本地ShellCode的指令或者数据的内存地址到远程目标进程的内存地址的重定位映射
#define REMOTE_ADDR( addr, local_base, remote_base ) ( (uint32_t)(addr) + (uint32_t)(remote_base) - (uint32_t)(local_base) )
//系统调用函数mmap所在的模块  
const char *libc_path = "/system/lib/libc.so";
//系统调用函数dlopn、dlsym、dlclose所在的模块 
const char *linker_path = "/system/bin/linker";

//显示调试的信息
#if ENABLE_DEBUG
	#define DEBUG_PRINT(format,args...) \
		LOGD(format, ##args)
#else
	#define DEBUG_PRINT(format,args...)
#endif

××××××××××××××××××××××××××××××××××××××××××××××××××××××××××××××××××××××××××××××××××××××××××××××××××××××××××××××××××××××

//读取被附加调试目标进程内存中的数据  
//读取的数据保存在buf缓冲区中
int ptrace_readdata( pid_t pid,  uint8_t *src, uint8_t *buf, size_t size )
{
	uint32_t i, j, remain;
	uint8_t *laddr;

  //联合体
	union u {
		long val;
		char chars[sizeof(long)];
	} d;

  //4字节的整数倍
	j = size / 4;
  
  //剩余的字节数 
	remain = size % 4;
  
  //src为要读取数据的目标进程的内存地址  
  //buf保存读取到目标进程中的数据
	laddr = buf;

  //在目标进程中读取4字节的整数倍的数据
	for ( i = 0; i < j; i ++ )
	{
     //在目标进程中读取数据
		 d.val = ptrace( PTRACE_PEEKTEXT, pid, src, 0 );
     
     //拷贝读取的数据到临时缓冲区中
		 memcpy( laddr, d.chars, 4 );
		 src += 4;
		 laddr += 4;
	}

  //在目标进程中读取剩余的数据
	if ( remain > 0 )
	{
    //在目标进程中读取数据
		d.val = ptrace( PTRACE_PEEKTEXT, pid, src, 0 );
    
    //拷贝读取的数据到临时缓冲区中
		memcpy( laddr, d.chars, remain );
	}

	return 0;

}


××××××××××××××××××××××××××××××××××××××××××××××××××××××××××××××××××××××××××××××××××××××××××××××××××××××××××××××××××××××

//向附加调试的目标进程内存中写入数据
int ptrace_writedata( pid_t pid, uint8_t *dest, uint8_t *data, size_t size )
{
	uint32_t i, j, remain;
	uint8_t *laddr;

  //联合体 
	union u {
		long val;
		char chars[sizeof(long)];
	} d;

  //4字节整数倍
	j = size / 4;
  
  //剩余的字节数
	remain = size % 4;
	
  //data中存放的是要写入目标进程的数据
	laddr = data;
	
  //向目标进程中写入4字节的整数倍的数据 
	for ( i = 0; i < j; i ++ )
	{
		memcpy( d.chars, laddr, 4 );
    
    //向目标中写入1个字的数据
		ptrace( PTRACE_POKETEXT, pid, dest, d.val );
	
		dest  += 4;
		laddr += 4;
	}

  //向目标进程中写入剩余的数据
	if ( remain > 0 )
	{
		d.val = ptrace( PTRACE_PEEKTEXT, pid, dest, 0 ); //原来的代码中有，感觉是多余的 
		for ( i = 0; i < remain; i ++ )
		{
			d.chars[i] = *laddr ++;
		}

    //向目标进程中写入剩余的数据
		ptrace( PTRACE_POKETEXT, pid, dest, d.val );
		
	}

	return 0;
}


××××××××××××××××××××××××××××××××××××××××××××××××××××××××××××××××××××××××××××××××××××××××××××××××××××××××××××××××××××××

//向附加调试的目标进程内存中写入字符串数据
int ptrace_writestring( pid_t pid, uint8_t *dest, char *str  )
{
  //调用函数向附加目标进程内存中写入数据
	return ptrace_writedata( pid, dest, str, strlen(str)+1 );
}

××××××××××××××××××××××××××××××××××××××××××××××××××××××××××××××××××××××××××××××××××××××××××××××××××××××××××××××××××××××

/* 
 * 在其他进程（远程目标进程）中调用系统函数mmap申请内存空间 
 * void* mmap(void* start, size_t length, int prot, int flags, int fd, off_t offset);  
 * params是已经格式化的mmap函数的参数，num_params是mmap函数的参数的个数 
 * regs是远程目标进程的寄存器的数据，addr为远程目标进程中函数mmap的调用地址  
 */ 
int ptrace_call( pid_t pid, uint32_t addr, long *params, uint32_t num_params, struct pt_regs* regs )
{
	uint32_t i;

  /* 
    struct user_regs_struct 
    { 
      long int ebx; 
      long int ecx; 
      long int edx; 
      long int esi; 
      long int edi; 
      long int ebp; 
      long int eax; 
      long int xds; 
      long int xes; 
      long int xfs; 
      long int xgs; 
      long int orig_eax; 
      long int eip; 
      long int xcs; 
      long int eflags; 
      long int esp; 
      long int xss; 
    }; 
    */  
   
  //ARM中函数mmap的前4个参数通过r0-r3来传入  
	for ( i = 0; i < num_params && i < 4; i ++ )
	{
		regs->uregs[i] = params[i];
	}

	//
	// push remained params onto stack
	//
  //ARM中函数mmap的剩余2个参数通过栈来传入 
	if ( i < num_params )
	{
    //在目标进程的ARM栈中为剩余的2个参数申请内存空间
		regs->ARM_sp -= (num_params - i) * sizeof(long) ;
    //向目标进程的ARM栈中写入剩余的2个参数的数据
		ptrace_writedata( pid, (void *)regs->ARM_sp, (uint8_t *)&params[i], (num_params - i) * sizeof(long) );
	}

  //设置远程目标进程的的PC寄存器的值（修改目标进程的执行）
	regs->ARM_pc = addr;//addr为远程目标进程中函数mmap的调用地址  
  
  //根据远程目标进程的运行模式，设置目标进程的CPSR寄存器的值  
	if ( regs->ARM_pc & 1 )
	{
		/* thumb */
    //thumb模式
		regs->ARM_pc &= (~1u);
		regs->ARM_cpsr |= CPSR_T_MASK;
	}
	else
	{
		/* arm */
    //arm模式
		regs->ARM_cpsr &= ~CPSR_T_MASK;
	}

  //设置远程目标进程的LR寄存器的值为0，触发地址0异常回到当前进程中 
	regs->ARM_lr = 0;	

  //设置远程目标进程各寄存器的值然后在远程目标进程中调用mmap函数申请内存空间
	if ( ptrace_setregs( pid, regs ) == -1 
		|| ptrace_continue( pid ) == -1 )
	{
		return -1;
	}

  //等待在远程目标进程中申请内存空间操作的完成  
  //申请到的内存空间的地址保存在返回值寄存器r0中
	waitpid( pid, NULL, WUNTRACED );

	return 0;
}


××××××××××××××××××××××××××××××××××××××××××××××××××××××××××××××××××××××××××××××××××××××××××××××××××××××××××××××××××××××

//获取被附加调试进程的寄存器的值 
int ptrace_getregs( pid_t pid, struct pt_regs* regs )
{
	if ( ptrace( PTRACE_GETREGS, pid, NULL, regs ) < 0 )
	{
		perror( "ptrace_getregs: Can not get register values" );
		return -1;
	}

	return 0;
}

××××××××××××××××××××××××××××××××××××××××××××××××××××××××××××××××××××××××××××××××××××××××××××××××××××××××××××××××××××××

//设置被附加调试进程的寄存器的值 
int ptrace_setregs( pid_t pid, struct pt_regs* regs )
{
	if ( ptrace( PTRACE_SETREGS, pid, NULL, regs ) < 0 )
	{
		perror( "ptrace_setregs: Can not set register values" );
		return -1;
	}

	return 0;
}


××××××××××××××××××××××××××××××××××××××××××××××××××××××××××××××××××××××××××××××××××××××××××××××××××××××××××××××××××××××


//附加的目标进程继续执行
int ptrace_continue( pid_t pid )
{
	if ( ptrace( PTRACE_CONT, pid, NULL, 0 ) < 0 )
		{
			perror( "ptrace_cont" );
			return -1;
		}

		return 0;
}

××××××××××××××××××××××××××××××××××××××××××××××××××××××××××××××××××××××××××××××××××××××××××××××××××××××××××××××××××××××

//附加目标进程
int ptrace_attach( pid_t pid )
{
  //附加目标进程
	if ( ptrace( PTRACE_ATTACH, pid, NULL, 0  ) < 0 )
	{
		perror( "ptrace_attach" );
		return -1;
	}

  //等待目标进程附加完成
	waitpid( pid, NULL, WUNTRACED );

	//DEBUG_PRINT("attached\n");

  //目标进程继续执行，让目标进程在下次进/出系统调用时被调试 
	if ( ptrace( PTRACE_SYSCALL, pid, NULL, 0  ) < 0 )
	{
		perror( "ptrace_syscall" );
		return -1;
	}


  //等待目标进程的此设置的完成
	waitpid( pid, NULL, WUNTRACED );

	return 0;
}

××××××××××××××××××××××××××××××××××××××××××××××××××××××××××××××××××××××××××××××××××××××××××××××××××××××××××××××××××××××

//结束目标进程的附加
int ptrace_detach( pid_t pid )
{
	if ( ptrace( PTRACE_DETACH, pid, NULL, 0 ) < 0 )
		{
			perror( "ptrace_detach" );
			return -1;
		}

		return 0;
}

××××××××××××××××××××××××××××××××××××××××××××××××××××××××××××××××××××××××××××××××××××××××××××××××××××××××××××××××××××××

//获取进程加载模块的基址
void* get_module_base( pid_t pid, const char* module_name )
{
	FILE *fp;
	long addr = 0;
	char *pch;
  
  //保存模块的名称
	char filename[32];
  
  //保存读取的信息  
	char line[1024];

	if ( pid < 0 )
	{
		/* self process */
    //获取当前进程的模块的基址
		snprintf( filename, sizeof(filename), "/proc/self/maps", pid );
	}
	else
	{
    //获取其他进程的模块的基址
		snprintf( filename, sizeof(filename), "/proc/%d/maps", pid );
	}
  
  //打开"/proc/pid/maps"文件
	fp = fopen( filename, "r" );

	if ( fp != NULL )
	{
    //循环读取"/proc/pid/maps"文件的信息，每次一行
		while ( fgets( line, sizeof(line), fp ) )
		{
      //判断读取的信息line中是否包含要查找的模块名称
			if ( strstr( line, module_name ) )
			{
        //以"-"为标记拆分字符串 
				pch = strtok( line, "-" );
        
        //字符串转无符号长整型的模块基址
				addr = strtoul( pch, NULL, 16 );

        //排除特殊情况
				if ( addr == 0x8000 )
					addr = 0;

				break;
			}
		}

				fclose( fp ) ;
	}
  
  //返回获取到的模块的基址
	return (void *)addr;
}

××××××××××××××××××××××××××××××××××××××××××××××××××××××××××××××××××××××××××××××××××××××××××××××××××××××××××××××××××××××

//获取其他进程的某加载模块中某系统函数的调用地址
/* 
 * Once we know the base address of a given library both in our process and in the target process,  
 * what we can do to resolve the remote function address is: 
 *      REMOTE_ADDRESS = LOCAL_ADDRESS + (REMOTE_BASE - LOCAL_BASE) 
 *  
 */  
void* get_remote_addr( pid_t target_pid, const char* module_name, void* local_addr )
{
	void* local_handle, *remote_handle;

  //获取某系统模块在当前进程中的加载基址 
	local_handle = get_module_base( -1, module_name );
  
  //获取其他进程（目标进程）中某系统模块的加载基址
	remote_handle = get_module_base( target_pid, module_name );

	DEBUG_PRINT( "[+] get_remote_addr: local[%x], remote[%x]\n", local_handle, remote_handle );

  //REMOTE_ADDRESS = LOCAL_ADDRESS + (REMOTE_BASE - LOCAL_BASE)  
  //获取其他进程（目标进程）某系统模块中某系统函数的调用地址并返回  
	return (void *)( (uint32_t)local_addr + (uint32_t)remote_handle - (uint32_t)local_handle );
}

××××××××××××××××××××××××××××××××××××××××××××××××××××××××××××××××××××××××××××××××××××××××××××××××××××××××××××××××××××××

//查找要注入的目标进程的PID  
//process_name为要查找的进程名字
int find_pid_of( const char *process_name )
{
	int id;
        //保存进程的PID 
	pid_t pid = -1;
	DIR* dir;
	FILE *fp;
  //保存进程的名称
	char filename[32];
  //保存运行进程的命令行
	char cmdline[256];

	struct dirent * entry;

  //进程的名字不能为NULL 
	if ( process_name == NULL )
		return -1;

  //打开文件目录"/proc"
	dir = opendir( "/proc" );

  //文件目录"/proc"的句柄不能为NULL 
	if ( dir == NULL )
		return -1;

    /* 
     * 函数struct dirent* readdir(DIR* dir_handle);  //读取目录（循环遍历） 
     * struct dirent 
     * { 
     *  long d_ino;                          //inode number 索引节点号  
     *  off_t d_off;                         //offset to this dirent 在目录文件中的偏移  
     *  unsigned short d_reclen;             //length of this d_name 文件名长  
     *  unsigned char d_type;                //the type of d_name 文件类型  
     *  char d_name [NAME_MAX+1];            //file name (null-terminated) 文件名，最长255字符  
     * } 
     */  

  //循环读取文件目录"/proc"里的文件  
	while( (entry = readdir( dir )) != NULL )
	{
    //将文件名字符串转整型得到进程的PID
		id = atoi( entry->d_name );
		if ( id != 0 )
		{
      //格式化字符串得到"/proc/pid/cmdline" 
			sprintf( filename, "/proc/%d/cmdline", id );
      //打开文件"/proc/pid/cmdline"
			fp = fopen( filename, "r" );
			if ( fp )
			{
        //读取运行进程的命令行中的arg[0]即进程的名称 
				fgets( cmdline, sizeof(cmdline), fp );
				fclose( fp );
             
        //判断获取到进程的名字是否与要查找的目标进程名字process_name相等
				if ( strcmp( process_name, cmdline ) == 0 )
				{
					/* process found */
          //保存目标进程的PID
					pid = id;
					break;
				}
			}
		}
	}

	closedir( dir );
        
  //返回查找到目标进程的PID
	return pid;
}

××××××××××××××××××××××××××××××××××××××××××××××××××××××××××××××××××××××××××××××××××××××××××××××××××××××××××××××××××××××

/* 
 * 对远程目标进程进行LibInject和函数的Hook 
 * library_path------------------自定义的Hook函数所在的模块（libHook.so库）的路径 
 * function_name-----------------Hook函数在libHook.so库中名称Hook_Api 
 * param-------------------------Hook函数调用所需要的参数 
 * param_size--------------------Hook函数调用所需要的参数的大小 
 */

int inject_remote_process( pid_t target_pid, const char *library_path, const char *function_name, void *param, 
                                                                                               size_t param_size )
{
	int ret = -1;
	void *mmap_addr, *dlopen_addr, *dlsym_addr, *dlclose_addr;
	void *local_handle, *remote_handle, *dlhandle;
	uint8_t *map_base;
	uint8_t *dlopen_param1_ptr, *dlsym_param2_ptr, *saved_r0_pc_ptr, *inject_param_ptr, *remote_code_ptr, *local_code_ptr;


	struct pt_regs regs, original_regs;

  //导出全局变量
	extern uint32_t _dlopen_addr_s, _dlopen_param1_s, _dlopen_param2_s, _dlsym_addr_s, \
			_dlsym_param2_s, _dlclose_addr_s, _inject_start_s, _inject_end_s, _inject_function_param_s, \
			_saved_cpsr_s, _saved_r0_pc_s;

	uint32_t code_length;


	long parameters[10];



	DEBUG_PRINT( "[+] Injecting process: %d\n", target_pid );

  //附加远程目标进程
	if ( ptrace_attach( target_pid ) == -1 )
		return EXIT_SUCCESS;

  //获取附加远程目标进程此时寄存器的状态值
	if ( ptrace_getregs( target_pid, &regs ) == -1 )
		goto exit;

	/* save original registers */
  //保存获取到的附加远程目标进程的寄存器的状态值 
	memcpy( &original_regs, &regs, sizeof(regs) );

  //获取附加远程目标进程"/system/lib/libc.so"模块中函数mmap的调用地址
	mmap_addr = get_remote_addr( target_pid, "/system/lib/libc.so", (void *)mmap );

	DEBUG_PRINT( "[+] Remote mmap address: %x\n", mmap_addr );

	/* call mmap */
  //格式化函数mmap的调用参数
	parameters[0] = 0;	// addr
	parameters[1] = 0x4000; // size  申请内存空间的大小
	parameters[2] = PROT_READ | PROT_WRITE | PROT_EXEC;  // prot  可读可写可执行
	parameters[3] =  MAP_ANONYMOUS | MAP_PRIVATE; // flags
	parameters[4] = 0; //fd
	parameters[5] = 0; //offset

	DEBUG_PRINT( "[+] Calling mmap in target process.\n" );

  //在附加远程目标进程中调用函数mmmap申请内存空间
	if ( ptrace_call( target_pid, (uint32_t)mmap_addr, parameters, 6, &regs ) == -1 )
		goto exit;


  //读取附加远程目标进程中此时寄存器的状态值，获取函数mmap调用返回的申请内存空间的地址
	if ( ptrace_getregs( target_pid, &regs ) == -1 )
		goto exit;


	DEBUG_PRINT( "[+] Target process returned from mmap, return value=%x, pc=%x \n", regs.ARM_r0, regs.ARM_pc );

  //保存在附加远程目标进程中申请到内存空间的地址map_base = r0  
	map_base = (uint8_t *)regs.ARM_r0;

  //获取附加远程目标进程中函数dlopen的调用地址
	dlopen_addr = get_remote_addr( target_pid, linker_path, (void *)dlopen );

  //获取附加远程目标进程中函数dlsym的调用地址 
	dlsym_addr = get_remote_addr( target_pid, linker_path, (void *)dlsym );

  //获取附加远程目标进程中函数dlclose的调用地址 
	dlclose_addr = get_remote_addr( target_pid, linker_path, (void *)dlclose );

	DEBUG_PRINT( "[+] Get imports: dlopen: %x, dlsym: %x, dlclose: %x\n", dlopen_addr, dlsym_addr, dlclose_addr );

  //附加远程目标进程注入代码ShellCode的起始地址，并预留0x3C00的内存空间空间
	remote_code_ptr = map_base + 0x3C00;

  //注入ShellCode的本地起始地址
	local_code_ptr = (uint8_t *)&_inject_start_s;
        
  //保存函数dlopen的调用地址到全局变量_dlopen_addr_s中  
	_dlopen_addr_s = (uint32_t)dlopen_addr;
        
  //保存函数dlsym的调用地址到全局变量_dlsym_addr_s中 
	_dlsym_addr_s = (uint32_t)dlsym_addr;

  //保存函数dlclose的调用地址到全局变量_dlclose_addr_s中
	_dlclose_addr_s = (uint32_t)dlclose_addr;

	DEBUG_PRINT( "[+] Inject code start: %x, end: %x\n", local_code_ptr, &_inject_end_s );
  
  //获取注入ShellCode代码指令的长度
	code_length = (uint32_t)&_inject_end_s - (uint32_t)&_inject_start_s;
  
  //本地为函数dlopen的第1个参数pathname变量申请内存空间  
  //void * dlopen(const char* pathname, int mode);
	dlopen_param1_ptr = local_code_ptr + code_length + 0x20;
  
  //本地为函数dlsym的第2个参数symbol变量申请内存空间  
  //void*dlsym(void* handle, constchar* symbol); 
	dlsym_param2_ptr = dlopen_param1_ptr + MAX_PATH;
  
  //本地为附加远程目标进程的寄存器状态值r0-r15(pc)的保存申请内存空间
	saved_r0_pc_ptr = dlsym_param2_ptr + MAX_PATH;
  
  //本地为附加远程目标进程的Hook函数的参数inject_param_ptr申请内存空间
	inject_param_ptr = saved_r0_pc_ptr + MAX_PATH;


	/* dlopen parameter 1: library name */
  //拷贝函数dlopen的第1个参数到本地内存空间dlopen_param1_ptr中  
  //函数dlopen的第1个参数也就是附加远程目标中要调用的Hook函数所在的模块
	strcpy( dlopen_param1_ptr, library_path );
  
  //获取函数dlopen的第1个参数从本地内存地址到附加远程目标进程内存映射的重定位地址 
	_dlopen_param1_s = REMOTE_ADDR( dlopen_param1_ptr, local_code_ptr, remote_code_ptr );
	DEBUG_PRINT( "[+] _dlopen_param1_s: %x\n", _dlopen_param1_s );

	/* dlsym parameter 2: function name */
  //拷贝函数dlsym的第2个参数到本地内存空间dlsym_param2_ptr中  
  //函数dlsym的第2个参数也就是附加远程目标中要调用的Hook函数的名称 
	strcpy( dlsym_param2_ptr, function_name );
  
  //获取函数dlsym的第2个参数从本地内存地址到附加远程目标进程内存映射的重定位地址 
	_dlsym_param2_s = REMOTE_ADDR( dlsym_param2_ptr, local_code_ptr, remote_code_ptr );
	DEBUG_PRINT( "[+] _dlsym_param2_s: %x\n", _dlsym_param2_s );

	/* saved cpsr */
  //保存附加远程目标进程的cpsr寄存器的值（cpsr寄存器在ARM的模式切换的时候会使用）
	_saved_cpsr_s = original_regs.ARM_cpsr;

	/* saved r0-pc */
  //保存附加远程目标进程的寄存器r0-r15(pc)的状态值  
	memcpy( saved_r0_pc_ptr, &(original_regs.ARM_r0), 16 * 4 ); // r0 ~ r15
  
  //获取附加远程目标进程的寄存器r0-r15(pc)的状态值从本地内存保存地址到附加远程目标进程内存映射的重定位地址
	_saved_r0_pc_s = REMOTE_ADDR( saved_r0_pc_ptr, local_code_ptr, remote_code_ptr );
	DEBUG_PRINT( "[+] _saved_r0_pc_s: %x\n", _saved_r0_pc_s );

	/* Inject function parameter */
  //拷贝附加远程目标进程的Hook函数的参数到本地内存空间inject_param_ptr中  
	memcpy( inject_param_ptr, param, param_size );
  
  //获取附加远程目标进程的Hook函数的参数从本地内存地址到附加远程目标进程内存映射的重定位地址
	_inject_function_param_s = REMOTE_ADDR( inject_param_ptr, local_code_ptr, remote_code_ptr );
	DEBUG_PRINT( "[+] _inject_function_param_s: %x\n", _inject_function_param_s );

  //显示附加远程目标进程的ShellCode注入的内存地址
	DEBUG_PRINT( "[+] Remote shellcode address: %x\n", remote_code_ptr );
  
  //向附加远程目标进程的内存空间中写入0x400大小的本地ShellCode指令代码
	ptrace_writedata( target_pid, remote_code_ptr, local_code_ptr, 0x400 );

  //拷贝附加远程目标进程被附加时寄存器的状态值到临时变量regs中
	memcpy( &regs, &original_regs, sizeof(regs) );
  
  //修改附加远程目标进程的sp寄存器的值为ShellCode的注入地址
	regs.ARM_sp = (long)remote_code_ptr;
  
  //修改附加远程目标进程的pc寄存器的值为ShellCode的注入地址
	regs.ARM_pc = (long)remote_code_ptr;
  
  //设置附加远程目标进程的寄存器的状态值即让附加远程目标进程执行注入的ShellCode指令代码
	ptrace_setregs( target_pid, &regs );
  
  //结束目标进程的附加
	ptrace_detach( target_pid );

	// inject succeeded
  //进程注入成功
	ret = 0;

exit:
	return ret;
}

××××××××××××××××××××××××××××××××××××××××××××××××××××××××××××××××××××××××××××××××××××××××××××××××××××××××××××××××××××××

//main函数
int main(int argc, char** argv) {

  //要注入的进程的PID
	pid_t target_pid;
  
  //查找要注入的目标进程"/system/bin/servicemanager"的PID 
	target_pid = find_pid_of("/system/bin/servicemanager");
  //对目标进程servicemanager进行LibInject和函数的Hook  
  //"/data/local/tmp/libhookdll.so"为要注入到目标进程中的so库  
  //"hook_entry"为注入要调用的so库中的函数
	inject_remote_process( target_pid, "/dev/yuki/payload.so", "hook_entry", "I'm parameter!", strlen("I'm parameter!") );
}
```
Android的so库注入代码的SellCode代码shellcode.s的编写：
这个文件是用来干什么的？？？？？？？？？？？？？？？？？？？？？？？？？？？？？？？？？？？？？？？？？？？？？？
```
    .global _dlopen_addr_s             @全局变量_dlopen_addr_s保存dlopen函数的调用地址  
    .global _dlopen_param1_s           @全局变量_dlopen_param1_s保存函数dlopen的第一个参数-加载库文件的路径  
    .global _dlopen_param2_s           @全局变量_dlopen_param2_s保存函数dlopen的第二个参数-库文件的打开模式  
      
    .global _dlsym_addr_s              @全局变量_dlsym_addr_s保存函数dlsym的调用地址    
    .global _dlsym_param2_s            @全局变量_dlsym_param2_s保存函数dlsym的第二个参数-获取调用地址的函数的名称  
      
    .global _dlclose_addr_s            @全局变量_dlclose_addr_s保存函数dlclose的调用地址  
      
    .global _inject_start_s            @全局变量_inject_start_s保存注入代码的起始地址  
    .global _inject_end_s              @全局变量_inject_end_s保存注入代码的结束地址  
      
    .global _inject_function_param_s   @全局变量_inject_function_param_s保存Hook函数的参数  
      
    .global _saved_cpsr_s              @全局变量_saved_cpsr_s保存当前程序状态寄存器CPSR的值  
    .global _saved_r0_pc_s             @全局变量_saved_r0_pc_s保存寄存器环境R0-R15(PC)的值起始地址  
      
    @定义数据段.data   
    .data                                
      
    @注入代码的起始地址  
    _inject_start_s:  
        @ debug loop  
    3:  
        @sub r1, r1, #0  
        @B 3b  
      
        @调用dlopen函数  
        ldr r1, _dlopen_param2_s    @库文件的打开模式  
        ldr r0, _dlopen_param1_s    @加载库文件的路径字符串即Hook函数所在的模块  
        ldr r3, _dlopen_addr_s      @dlopen函数的调用地址  
        blx r3                      @调用函数dlopen加载并打开动态库文件  
        subs r4, r0, #0             @判断函数返回值r0-是否打开动态库文件成功  
        beq 2f                  @打开动态库文件失败跳转标签2的地方执行  
                        @r0保存加载库的引用pHandle  
                          
        @调用dlsym函数  
        ldr r1, _dlsym_param2_s     @获取调用的地址的函数名称字符串   
        ldr r3, _dlsym_addr_s       @dlsym函数的调用地址  
        blx r3                      @调用函数dlsym获取目标函数的调用地址  
        subs r3, r0, #0             @判断函数的返回值r0  
        beq 1f                      @不成功跳转到标签1的地方执行  
                                        @r3保存获取到的函数的调用地址  
      
        @调用Hook_Api函数  
        ldr r0, _inject_function_param_s   @给Hook函数传入参数r0  
        blx r3                             @调用Hook函数Hook远程目标进程的某系统调用函数  
        subs r0, r0, #0                    @判断函数的返回值r0  
        beq 2f                             @r0=0跳转到标签2的地方执行 ??  
      
    1:  
        @调用dlclose函数  
        mov r0, r4                         @参数r0动态库的应用  
        ldr r3, _dlclose_addr_s            @赋值r3为dlclose函数的调用地址  
        blx r3                             @调用dlclose函数关闭库文件的引用pHandle            
      
    2:  
        @恢复目标进程的原来状态  
        ldr r1, _saved_cpsr_s  
        msr cpsr_cf, r1                    @恢复目标进程寄存器CPSR的值  
      
        ldr sp, _saved_r0_pc_s          
        ldmfd sp, {r0-pc}                  @恢复目标进程寄存器环境R0-R15(PC)的值且sp不改变     
      
    _dlopen_addr_s:  
    .word 0x11111111                           @初始化word型全局变量_dlopen_addr_s  
      
    _dlopen_param1_s:  
    .word 0x11111111                           @初始化word型全局变量_dlopen_param1_s  
      
    _dlopen_param2_s:                          @初始化word型全局变量_dlopen_param2_s = 0x2  
    .word 0x2  
      
    _dlsym_addr_s:  
    .word 0x11111111                           @初始化word型全局变量_dlsym_addr_s  
      
    _dlsym_param2_s:  
    .word 0x11111111                           @初始化word型全局变量_dlsym_param2_s  
      
    _dlclose_addr_s:                            
    .word 0x11111111                           @初始化word型全局变量_dlclose_addr_s  
      
    _inject_function_param_s:   
    .word 0x11111111                           @初始化word型全局变量_inject_function_param_s  
      
    _saved_cpsr_s:  
    .word 0x11111111                           @初始化word型全局变量_saved_cpsr_s  
      
    _saved_r0_pc_s:  
    .word 0x11111111                           @初始化word型全局变量_saved_r0_pc_s  
      
    @注入代码的结束地址  
    _inject_end_s:                               
      
    .space 0x400, 0                            @申请的代码段内存空间大小  
      
    @数据段.data的结束位置   
    .end  
```
Android的so库注入代码的Android.mk文件的编写： 
```
LOCAL_PATH := $(call my-dir)    
    
#  
#注入程序LibInject  
#  
  
#清除变量  
include $(CLEAR_VARS)    
  
#生成的模块的名称LibInject  
LOCAL_MODULE := LibInject     
  
#需要编译的源码并包含注入的shellcode代码  
LOCAL_SRC_FILES := inject.c shellcode.s    
  
#使用Android的Log日志系统  
LOCAL_LDLIBS += -L$(SYSROOT)/usr/lib -llog    
    
#LOCAL_FORCE_STATIC_EXECUTABLE := true    
  
#编译生成可执行程序  
include $(BUILD_EXECUTABLE) 
```

Android的so库注入代码的Application.mk文件的编写： 

```
#最终编译运行支持的平台  
APP_ABI := armeabi armeabi-v7a  
```
```
@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
```

Android的so库的注入工具LibInject已经写好了。下面就可以开始编写注入到Android目标进程中的so库的代码了。

#### 参考资料
Libinject  https://bbs.pediy.com/thread-141355.htm

Libinject代码分析   http://blog.csdn.net/qq1084283172/article/details/46859931
