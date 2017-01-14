# 给定log文件
file_object = open("ping_sched.txt")
# 查看进程名
process_id = "ping-10105"
# 查看时间段
timestamp_start = 48479.058831
timestamp_end = 48479.951749
# 统计耗时
statistics = {'sched_stat_runtime': 0, 'sched_stat_sleep': 0, 'sched_stat_wait': 0}
# 百分比
percentage = {'sched_stat_runtime': 0, 'sched_stat_sleep': 0, 'sched_stat_wait': 0}

for ftace_log in file_object.readlines():
    # print(ftace_log,end="")
    column =ftace_log.split(" ")
    # remove blank component, get pure log data
    list = []
    for atom in column:
        if len(atom)!=0:
            list.append(atom)
    # find target process id and get time cost
    timestamp = float(list[3].replace(':',''))
    if list[0] == process_id and timestamp >= timestamp_start and timestamp <= timestamp_end:
        # print(list)
        if list[4] == 'sched_stat_runtime:':
            # print(list)
            runtime = list[7].split('=')
            statistics['sched_stat_runtime'] += int( runtime[1])
        elif list[4] == 'sched_stat_sleep:':
            # print(list)
            sleep = list[7].split('=')
            statistics['sched_stat_sleep'] += int(sleep[1])
        elif list[4] == 'sched_stat_wait:':
            # print(list)
            wait = list[7].split('=')
            statistics['sched_stat_wait'] += int(wait[1])
        else:
            pass
print(statistics)
# get percentage of each schedule state
time_sum = 0
for key in statistics:
    time_sum += statistics[key]
percentage['sched_stat_runtime'] = statistics['sched_stat_runtime']/time_sum
percentage['sched_stat_sleep'] = statistics['sched_stat_sleep'] / time_sum
percentage['sched_stat_wait'] = statistics['sched_stat_wait'] / time_sum
print(percentage)
