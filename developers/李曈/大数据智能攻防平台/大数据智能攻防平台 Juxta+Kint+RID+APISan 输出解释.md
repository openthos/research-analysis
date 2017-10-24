# 大数据智能攻防平台 Juxta+Kint+RID+APISan 输出解释

## 1 Juxta

![juxta_output](/Users/lt/Documents/Pictures/插图-本地图床/juxta_output.png)

​	输出包含多组compare，每组比较了一个符合POSIX接口的多个文件系统的某个函数。上图截取了两组compare，每组中：
（1）第一列Ranking：表示这个函数出错的概率在这组compare里的排序，ranking=1表示在这组compare里最有可能是bug。

（2）第二列Distan：表示这三个函数离这个接口的平均实现的“距离”，“距离”越大，越可能是bug

（3）第三列Funtion：表示出问题的函数名，冒号后面是函数参数或者返回值

（4）第四列Missing Conditions：表示缺失的条件。

​	忽略“[0m“、”[95m“之类的，这些是在cat命令里表示颜色的选项。

## 2 Kint

![kint1](/Users/lt/Documents/Pictures/插图-本地图床/kint1.png)

​	上图是Kint输出的第一部分，表示各种类型的潜在整数缺陷的数量。’umul‘中的`u`表示`unsigned`，`mul`表示乘法，’sadd‘中的`s`表示`signed`，`add`表示加法。

![kint2](/Users/lt/Documents/Pictures/插图-本地图床/kint2.png)

​	上图是Kint输出的第二部分，表示潜在整数缺陷的具体位置。

## 3 Rid

![rid](/Users/lt/Documents/Pictures/插图-本地图床/rid.png)

​	*后面的一行表示潜在问题的文件和具体的函数。

​	**后面的一行中，只需要注意最后的`dpm`，表示出问题的refcount是哪个

​	下面的每个Case表示一条执行路径，所有case的输入和输出都一样，但每个case对refcount的改变不同，买个case的第二行表示对refcount做了什么修改。

## 4 APISan

​	APISan的输出就是作者根据bug写的patch。