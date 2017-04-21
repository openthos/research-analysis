# 基于framework层AppInsight的实现
## 1.基础
AppInsight论文主要针对applications层APP的二进制代码进行动态插桩，通过在APP各线程主要函数中插入log，从而实现跨异步调用边界，获取代码执行关键路径
## 2.差异
本项研究主要针对framework层的Android的源码进行静态插桩，在framework层中存在APP各线程主要函数的对应函数，找到这些函数，在其中插入恰当的log，从而实现跨异步调用边界，获取代码执行关键路径
## 3.关键
* 准确的log位置，可以精确表示函数执行的时间
* 恰当的log内容，可以明确获得线程间异步调用因果关系
## 4.测试APP代码
1. **APP1：**
  * 功能：TextView显示内容”hello world“，点击Button，更新TextView的内容为”nice to meet you“
  * 实现方法：主线程创建Handler对象，其handleMessage函数中对TextView的内容进行更新，Button的onClick函数中新建子线程，子线程中通过主线程创建的Handler对象的sendMessage函数发送更新TextView内容的Message对象
## 5.实现过程
### 1. 如何知道某条log信息是由目标进程的哪个线程打印出来的？
* **ps** 可以获得目标进程的进程id
* **ps -t 进程id** 可以获得该进程id下面的所有存活的线程信息
* **logcat -v threadtime | grep 进程id** 可以获得目标进程的log信息，并显示打印出该条log信息的进程号和线程号
### 2. 什么是APP各线程的主要函数？
* **开启新线程的onClick函数** 获取主线程处理click事件的执行时间
* **新线程的start函数** 获取从主线程到子线程的异步调用因果关系
* **新线程的run函数** 获取子线程的执行时间
* **Handler对象的sandMessage函数** 获取从子线程到主线程的异步调用因果关系
* **Handler对象的handleMessage函数** 获取主线程更新ui的执行时间
### 3.framework层中与APP各线程主要函数的对应函数在哪里？
* **开启新线程的onClick函数** 
  * frameworks/base/core/java/android/view/View.java 4798行
  * performClick()中通过li.mOnClickListener.onClick(this);调用Applications层APP的onClick函数
* **新线程的start函数** 
  * 
* **新线程的run函数** 
* **Handler对象的sandMessage函数** 
* **Handler对象的handleMessage函数** 
### 4.log应该输出什么内容？
* **开启新线程的onClick函数** 
  * 在li.mOnClickListener.onClick(this)的前后分别打log，分别输入线程的id和name
  
  ```
  Log.e("LEILOG","onClick()start-"+android.os.Process.myTid()+"-"+Thread.currentThread().getName());
  li.mOnClickListener.onClick(this);
  Log.e("LEILOG","onClick()end-"+android.os.Process.myTid()+"-"+Thread.currentThread().getName());
  ```
* **新线程的start函数** 
* **新线程的run函数** 
* **Handler对象的sandMessage函数** 
* **Handler对象的handleMessage函数** 
