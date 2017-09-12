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

## 2、user log 解析
## 3、关键路径构建
