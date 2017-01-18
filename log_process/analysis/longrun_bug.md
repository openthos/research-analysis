#关于longrun_bug分析
##1.模拟代码
```c
#include<stdio.h>
int main(){
 long long time = 1000000000;
 printf("the program start...");
 while(time--){}
 printf("the program end...");
 return 0;
}
```

##2.结果分析
###2.1 从log中发现了两个特殊的状态
```
     longrun_bug-4071  [000] d...2..  6843.548802: sched_waking: comm=migration/0 pid=14 prio=0 target_cpu=000
     longrun_bug-4071  [000] dN..3..  6843.548803: sched_wakeup: comm=migration/0 pid=14 prio=0 target_cpu=000
     longrun_bug-4071  [000] dN..2..  6843.548804: sched_stat_runtime: comm=bash pid=4071 runtime=146815 [ns] vruntime=81029643 [ns]
     longrun_bug-4071  [000] d...2..  6843.548804: sched_switch: prev_comm=bash prev_pid=4071 prev_prio=120 prev_state=R+ ==> next_comm=migration/0 next_pid=14 next_prio=0
     longrun_bug-4071  [003] .......  6843.548980: sched_process_exec: filename=./longrun_bug pid=4071 old_pid=4071
```
注意其中一个很特殊的状态**sched_process_exec**,该状态在源码中的解释为:**Tracepoint for exec**
```
     longrun_bug-4071  [002] .......  6845.863185: sched_process_exit: comm=longrun_bug pid=4071 prio=120
     longrun_bug-4071  [002] d...113  6845.863196: sched_waking: comm=bash pid=4001 prio=120 target_cpu=006
     longrun_bug-4071  [002] d...213  6845.863197: sched_stat_sleep: comm=bash pid=4001 delay=2314462136 [ns]
     longrun_bug-4071  [002] d...213  6845.863198: sched_wake_idle_without_ipi: cpu=6
     longrun_bug-4071  [002] d...213  6845.863198: sched_wakeup: comm=bash pid=4001 prio=120 target_cpu=006
     longrun_bug-4071  [002] d...2..  6845.863199: sched_stat_runtime: comm=longrun_bug pid=4071 runtime=1330457 [ns] vruntime=1537721569 [ns]
     longrun_bug-4071  [002] d...2..  6845.863200: sched_switch: prev_comm=longrun_bug prev_pid=4071 prev_prio=120 prev_state=x ==> next_comm=swapper/2 next_pid=0 next_prio=120
```
注意其中一个很特殊的状态**sched_process_exit**,该状态在源码中的解释为:**Tracepoint for a task exiting** 

那么我们针对该类程序是否可以以这两个点为开始点和结束点？这样开始和结束就可以进行标记.当然很多进程是一直处于运行状态中的，可能不存在这两个状态。
###2.2关于统计结果的分析
```
{'sched_stat_runtime:': 2309590353.0, 'sched_stat_sleep:': 6807835264.0}
{'sched_stat_runtime:': 0.2533160620135608, 'sched_stat_sleep:': 0.7466839379864392}
```
从统计结果来看,这里的sleep占比是非常高的(并不完全符合我们的期望,我们的期望是runtime的时间占比比较高的).但是从记录上看，状态位于runtime的log条数是远远多于sleep的log条数，这意味着每次sleep的时间都相对较长，另外一点是sleep时间比较集中在某几个数值上：
```
('sched_stat_sleep:', 3992433.0)
('sched_stat_runtime:', 3645.0)
('sched_stat_runtime:', 2726869.0)
('sched_stat_runtime:', 1261302.0)
('sched_stat_sleep:', 3993695.0)
('sched_stat_runtime:', 3978.0)
('sched_stat_runtime:', 2079179.0)
('sched_stat_runtime:', 1090582.0)
('sched_stat_runtime:', 22624.0)
('sched_stat_runtime:', 65658.0)
('sched_stat_runtime:', 508876.0)
('sched_stat_runtime:', 179870.0)
('sched_stat_sleep:', 3992249.0)
('sched_stat_runtime:', 3753.0)
('sched_stat_runtime:', 3518299.0)
('sched_stat_runtime:', 146236.0)
('sched_stat_runtime:', 307084.0)
('sched_stat_sleep:', 3992843.0)
```
从这一小段记录来看，sleep的时间都比较接近**3992433**这一数值(从整个log上来看，sleep的时间也比较接近某几个数值)，此外我们也可以注意到log记录的条数中sleep的条目数也远小于runtime的条目数。

实际上**sleep**是一个很奇怪的状态：根据在源码中的解释**Tracepoint for accounting sleep time (time the task is not runnable,including iowait, see below)**.从给的定义来看,**sleep**好像是**runtime**的对立(包括了iowait这些状态)?
这同我们理解的**sleep**是程序自身主动调用**sleep()**是有差别的。
