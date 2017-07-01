# Patch-4.4.70-rt83 分析

#### 0001-ARM-smp-Move-clear_tasks_mm_cpumask-call-to-__cpu_di.patch

```shell
diff --git a/arch/arm/kernel/smp.c b/arch/arm/kernel/smp.c
index b26361355dae..e5754e3b03c4 100644
--- a/arch/arm/kernel/smp.c
+++ b/arch/arm/kernel/smp.c
@@ -230,8 +230,6 @@ int __cpu_disable(void)
        flush_cache_louis();
        local_flush_tlb_all();

-       clear_tasks_mm_cpumask(cpu);
-
        return 0;
 }

@@ -247,6 +245,9 @@ void __cpu_die(unsigned int cpu)
                pr_err("CPU%u: cpu didn't die\n", cpu);
                return;
        }
+
+       clear_tasks_mm_cpumask(cpu);
+
        pr_notice("CPU%u: shutdown\n", cpu);

        /*
-- 
```

​	修改了smp中关于cpu的操作，将clear_tasks_mm_cpumask()的位置从\_\_cpu\_disable()函数中移到了\_\_cpu\_die()函数中。在多核arm架构、RT-kernel的机器中，将机器挂起到内存时，disable cpu时会卡住，原因是clear_tasks_mm_cpumask()函数在遍历锁的时候，使用的是一种比较松弛的调度，task_lock()函数使用spin_lock，在保持锁的过程中执行了sleep，导致死锁。在clear_tasks_mm_cpumask()函数的注释中也明确写了，只适用于已经处于offline状态的cpu。