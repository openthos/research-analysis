# event-stream代码分析
## 1、kernel log 解析
1. m

    * 编译event-decompressor.c minilzo/minilzo.c生成目标文件event-decompressor

    * 编译event-decoder.c生成目标文件event-decoder

1. event-read-sorted

    * 运行event-read，排序？？？

1. event-read

    * 依次运行event-decompressor、event-decoder、event-printer

1. 使用流程
    * ./m  警告不用去管它
    * cat ../EventLoggingServer/bin/5284047f4ffb4e04824a2fd1d1f0cd62/kernel/1505200252970778 | ./event-read-sorted

1. event-fork-extracter

    * 输入：标准输入，多个文件名
    
    * 输出：标准输出
    
1. event-merger-splitter

    * 输入：标准输入，多个文件名
    
    * 输出：通过path参数指定
    
1. event-timestamp-fixer
1. events.h
1. events.py
1. kernel_analysis.py
## 2、user log 解析
1. panappticon-tools/event-stream/user_space_traces/user_trace_process/parse.c

    * 解析user二进制文件

1. 使用流程
    * gcc -o parse parse.c    编译parse.c生成目标文件parse
    * cat ../../../EventLoggingServer/bin/5284047f4ffb4e04824a2fd1d1f0cd62/user/1505199593553371 | ./parse

## 3、关键路径构建
1. ComputeDependencies.py
```
import sys
import Event
from EventHandlerMap import event_handler_map
            from EventHandlers import *
from Global import Global
from EventReordering import ReorderEvents

cat ../EventLoggingServer/bin/5284047f4ffb4e04824a2fd1d1f0cd62/kernel/1505200252970778 | python kernel_analysis.py
ImportError: No module named numpy
首先python2.7：sudo apt-get install python-numpy

其次python3.4：sudo apt-get install python3-numpy

然后分别进入各版本的shell 测试import numpy是否成功。

ImportError: No module named matplotlib.pyplot


    sudo apt-get install python-matplotlib  

cat ../EventLoggingServer/bin/5284047f4ffb4e04824a2fd1d1f0cd62/kernel/1505200252970778 | ./event-read-sorted|./event-timestamp-fixer

```
