# Patch-4.4.70 手动更改适应kernel 4.12

#### 0001-ARM-smp-Move-clear_tasks_mm_cpumask-call-to-__cpu_di.patch

​	这个patch之修改了arch/arm/kernel/smp.c这一个文件，相对于kernel 4.4.70，kernel 4.12除了代码位置有6行偏移外，pr_notice()改成了pr_debug()。

```c
pr_debug("CPU%u: shutdown\n", cpu);
```

​	pr_notice()是linux/printk.h中定义的一个宏，指向printk()函数，pr_debug()是linux/printk.h中定义的另一个宏，这个宏会根据config的选择，DEBUG的开关，通过if defined的方法来动态选择指向哪个函数。



#### 0002-rtmutex-Handle-non-enqueued-waiters-gracefully.patch

​	这个patch修改了rt_mutex_start_proxy_lock()函数里的内容，相对于kernel 4.4.70，kernel 4.12消除了raw_spin_unlock()函数的重复调用，方法是增加了__rt_mutex_start_proxy_lock()函数，具体的代码内容都没变，将patch里的函数名改一下就行。