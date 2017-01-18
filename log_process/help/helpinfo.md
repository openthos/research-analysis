#帮助信息
##1.打开ftrace中events/sched事件追踪器
```
root@thu-Lenovo-IdeaPad-Y580:/home/thu/traceLog# source openSchedEvents.sh 
```
##2.运行测试程序
```
root@thu-Lenovo-IdeaPad-Y580:/home/thu/traceLog/bugEmu# ./sleep_bug
```
##3.等待程序结束后关闭追踪器并且保存记录
```
root@thu-Lenovo-IdeaPad-Y580:/home/thu/traceLog#source closeSchedEvents.sh sleep_bug
该命令有一个脚本参数，为运行结束的程序名，这里为sleep_bug
在脚本中会将记录保存到/home/thu/traceLog目录下，在这里可能需要做一些修改保存到合适的目录下
```
##4.处理log信息的脚本调用
```
root@thu-Lenovo-IdeaPad-Y580:/home/thu/traceLog# python logProcess.py sleep_bug.select_log sleep_bug-28831 0 10000000
该脚本的作用是统计某个特定进程的运行时间，睡眠时间，阻塞时间
logProcess.py 为python脚本名
sleep_bug.select_bug为需要分析记录的路径名称
sleep_bug-28831 为需要关注进程的进程名和pid
0：为开始时间点
10000000：为结束时间点
```
