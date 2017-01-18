import sys
filename=sys.argv[1]
process_id=sys.argv[2]
timestamp_start=float(sys.argv[3])
timestamp_end=float(sys.argv[4])
print("filename:"+filename);
print("process_id:"+process_id);
print("time_start:"+str(timestamp_start));
print("time_end:"+str(timestamp_end));
file_object = open(filename)
stat_cost = {}
stat_timeline = []
cost_timeline = []
stat_percent ={}
raw_log = []
print("-------timeline--------");
for ftace_log in file_object.readlines():
    column = ftace_log.split(' ')
    info_list = []
    for atom in column:
        if len(atom) != 0:
            info_list.append(atom)
    timestamp = float(info_list[3].replace(':', ''))
    cur_id = info_list[0]
    if cur_id == process_id and timestamp >= timestamp_start and timestamp <= timestamp_end:
        cur_stat = info_list[4]
        if 'sched_stat_' in cur_stat:
            raw_log.append(ftace_log)
            delay_or_runtime = info_list[7]
            time_cost = float(delay_or_runtime.split('=')[1])
            stat_timeline.append(cur_stat)
            cost_timeline.append(time_cost)
            if cur_stat in stat_cost:
                stat_cost[cur_stat] += time_cost
            else:
                stat_cost[cur_stat] = time_cost
for index in range(len(cost_timeline)):
    print(stat_timeline[index],cost_timeline[index])
time_sum = 0
for key in stat_cost:
    time_sum += stat_cost[key]
for key in stat_cost:
    stat_percent[key] = stat_cost[key] / time_sum
print("-------result---------");
print(stat_cost)
print(stat_percent)
print("-------raw_log------");
for i in raw_log:
    print(i)
