# 给定log文件
file_object = open('trace.txt')
# 查看进程名,最好输入的文件即为该进程的全部ftrace（|grep process）
process_id = "irq/27-i915-263"
# 查看时间段
timestamp_start = 0
timestamp_end = 50000
# 统计耗时
# statistics = {'sched_stat_runtime': 0, 'sched_stat_sleep': 0, 'sched_stat_wait': 0,
#               'sched_stat_blocked':0,'sched_stat_iowait':0}
stat_cost = {}
# 百分比
# percentage = {'sched_stat_runtime': 0, 'sched_stat_sleep': 0, 'sched_stat_wait': 0}
stat_percent ={}

for ftace_log in file_object.readlines():
    # print(ftace_log,end="")
    column =ftace_log.split(" ")
    # remove blank component, get pure log data
    info_list = []
    for atom in column:
        if len(atom)!=0:
            info_list.append(atom)
    # find target process id and get time cost
    # print(info_list)
    # timestamp has bug（有一行在timestamp处打印的是“buffer”），在grep 下无问题
    # timestamp = float(info_list[3].replace(':',''))
    timestamp = 1
    if info_list[0] == process_id and timestamp >= timestamp_start and timestamp <= timestamp_end:
        if 'sched_stat' in info_list[4]:
            time_cost = float(info_list[7].split('=')[1])
            if info_list[4] in stat_cost:
                stat_cost[info_list[4]] += time_cost
            else:
                stat_cost[info_list[4]] = time_cost
# get percentage of each schedule state
time_sum = 0
for key in stat_cost:
    time_sum += stat_cost[key]
for key in stat_cost:
    stat_percent[key] = stat_cost[key] / time_sum
# output
print(stat_cost)
print( stat_percent)
