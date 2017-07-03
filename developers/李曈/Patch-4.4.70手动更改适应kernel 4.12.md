# Patch-4.4.70 手动更改适应kernel 4.12

#### 0001-ARM-smp-Move-clear_tasks_mm_cpumask-call-to-__cpu_di.patch

​	这个patch之修改了arch/arm/kernel/smp.c这一个文件，相对于kernel 4.4.70，kernel 4.11.8除了代码位置有6行偏移外，pr_notice()改成了pr_debug()。

```c
pr_debug("CPU%u: shutdown\n", cpu);
```

​	pr_notice()是linux/printk.h中定义的一个宏，指向printk()函数，pr_debug()是linux/printk.h中定义的另一个宏，这个宏会根据config的选择，DEBUG的开关，通过if defined的方法来动态选择指向哪个函数。

