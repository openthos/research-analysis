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



#### 0002-rtmutex-Handle-non-enqueued-waiters-gracefully.patch

```shell
diff --git a/kernel/locking/rtmutex.c b/kernel/locking/rtmutex.c
index b066724d7a5b..e10cd0ec66fe 100644
--- a/kernel/locking/rtmutex.c
+++ b/kernel/locking/rtmutex.c
@@ -1681,7 +1681,7 @@ int rt_mutex_start_proxy_lock(struct rt_mutex *lock,
                ret = 0;
        }

-       if (unlikely(ret))
+       if (ret && rt_mutex_has_waiters(lock))
                remove_waiter(lock, waiter);

        raw_spin_unlock(&lock->wait_lock);
-- 
```

​	首先理清一下rtmutex是啥。mutex是linux同步中的互斥量，出自POSIX线程标准，用来保证一个对象的在任意时刻，最多只有一个线程能访问它。RT-mutex采用优先级继承(PI, Priority Inheritance) 的机制来解决优先级反转问题，详见Documentation/locking/rt-mutex-design.txt

​	在这个Patch中，unlikely是一个宏，这个宏在此处的用法是：

```C
#define unlikely(cond) (cond)
```

​	语义上来说这个宏相当于没用，修改之后，除了通过ret判断这个锁当前是否有线程占用，还要判断等待队列里是否有线程。

















































