# 给定log文件
file_object = open('ping_sched.txt')
# 查看进程名
process_id = 'ping-10105'
# 查看时间段
timestamp_start = 0
timestamp_end = 50000
# 统计耗时
stat_cost = {}
# 初始化时间线上的状态与耗时统计
stat_timeline = []
cost_timeline = []
# 百分比
stat_percent ={}
# 原始数据
raw_log = []

# 逐行读取
for ftace_log in file_object.readlines():
    column = ftace_log.split(' ')
    # 过滤无效信息
    info_list = []
    for atom in column:
        if len(atom) != 0:
            info_list.append(atom)
    # 获取本行时间戳
    timestamp = float(info_list[3].replace(':', ''))
    # 本行进程名
    cur_id = info_list[0]
    if cur_id == process_id and timestamp >= timestamp_start and timestamp <= timestamp_end:
        # 本行调度状态
        cur_stat = info_list[4]
        if 'sched_stat_' in cur_stat:
            raw_log.append(ftace_log)
            delay_or_runtime = info_list[7]
            time_cost = float(delay_or_runtime.split('=')[1])
            stat_timeline.append(cur_stat)
            cost_timeline.append(time_cost)
            # 汇总。dict(map)中没有就添加上，有就累加
            if cur_stat in stat_cost:
                stat_cost[cur_stat] += time_cost
            else:
                stat_cost[cur_stat] = time_cost
# 输出时间线调度状态信息
for index in range(len(cost_timeline)):
    print(stat_timeline[index],cost_timeline[index])
# 获取各状态耗时占比
time_sum = 0
for key in stat_cost:
    time_sum += stat_cost[key]
for key in stat_cost:
    stat_percent[key] = stat_cost[key] / time_sum
# 汇总数据输出
print(stat_cost)
print(stat_percent)
# 原始数据输出
for i in raw_log:
    print(i)
