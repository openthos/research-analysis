#close trace
echo 0 > /sys/kernel/debug/tracing/tracing_on
#save record
cat /sys/kernel/debug/tracing/trace >> /home/thu/traceLog/$1.full_log
#save selected pid record
cat /sys/kernel/debug/tracing/trace | grep $1- >> /home/thu/traceLog/$1.select_log
#clean trace recode
echo 0 > /sys/kernel/debug/tracing/trace
