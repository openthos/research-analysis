# 2017.03.03~2017.03.08

## 1 本周目标：
搞懂ActivityManagerService服务运行的详细过程，然后研究一个调用方案，实现在Linux中启动该Service，并且能够与Android中的ActivityManagerService服务相交互。

## 2 研究过程：

现在的短期思路是：

搞清楚Service启动时，应用需要通过Intent发送哪些数据给系统，系统才能找到Service并启动。

题外话：想到一种更简易的修改方式，借鉴插件化开发的思想，使用代理Activity等形式，达到间接与Linux上的程序交互。

参考：http://gityuan.com/2016/03/06/start-service/

启动初始化重点在ActivityThread.java 里的 15. AT.handleCreateService 这里面loadClass，然后创建了context和application，调用service.onCreate() 

现在研究，发送一个启动Service的Intent需要哪些数据，并把这些数据通过Binder发送给ActivityManagerService。

分析这过程中包含的进程和对象。

|整个过程参与的进程|作用|
| ------------- |------------- |
|Process A进程                |    发送Intent的进程
|system_server进程            |   ActivityManagerService服务所在进程
|Zygote进程                   |      创建新进程的进程

比如Process A进程 里的Activity对象执行startService()方法，Activity继承了ContextWrapper类，在ContextWrapper类中，有一个成员变量mBase，它是一个ContextImpl实例。ContextWrapper类的startService函数最终过调用ContextImpl类的startService函数来实现。

即 Process A进程 执行startService()方法

Activity extends ContextWrapper

执行 startService() -> ContextImpl里的startService()

在ContextImpl类的startService类，最终又调用了ActivityManagerNative里的ActivityManagerProxy类的startService来实现启动服务的操作。

abstract class ActivityManagerNative extends Binder implements IActivityManager

ActivityManagerProxy 是 ActivityManagerNative 的内部类

class ActivityManagerProxy implements IActivityManager
``` java
public ComponentName startService(IApplicationThread caller, Intent service,
        String resolvedType, String callingPackage, int userId) throws RemoteException
{
    Parcel data = Parcel.obtain();
    Parcel reply = Parcel.obtain();
    data.writeInterfaceToken(IActivityManager.descriptor);
    data.writeStrongBinder(caller != null ? caller.asBinder() : null);
    service.writeToParcel(data, 0);
    data.writeString(resolvedType);
    data.writeString(callingPackage);
    data.writeInt(userId);
    mRemote.transact(START_SERVICE_TRANSACTION, data, reply, 0);
    reply.readException();
    ComponentName res = ComponentName.readFromParcel(reply);
    data.recycle();
    reply.recycle();
    return res;
}
```

可以看到data存储了以下内容

|变量|内容作用|
| ------------- |------------- |
|IActivityManager.descriptor    | String descriptor = "android.app.IActivityManager";
|IApplicationThread caller| 辅助？
|Intent service                 | 里面指定了要启动的服务的名称
|String resolvedType           | 表示service这个Intent的MIME类型，它是在解析Intent时用到的
|String callingPackage| 调用者的包名
|int userId   | 调用者的用户ID

action 标识为 `START_SERVICE_TRANSACTION`

ActivityManagerProxy类的startService函数把这三个参数写入到data本地变量去，接着通过mRemote.transact函数进入到Binder驱动程序，然后Binder驱动程序唤醒正在等待Client请求的ActivityManagerService进程，最后进入到ActivityManagerService的startService函数中。

然后进入之前看到的20步的 ActivityManagerService的startService函数的处理流程

在 startServiceLocked 里 通过 retrieveServiceLocked 解析intent里需要的Service

retrieveServiceLocked : 通过intent 和PackageManagerService 获得ServiceRecord

参考 http://3dobe.com/archives/30/

ServiceRecord，我们可以称之服务记录，也可以叫服务描述符，每一个运行中的服务都会在 AMS 的 HashMap<ComponentName, ServiceRecord> mServices 字段中存储一份自己的 ServiceRecord，该类记录了一个 Service 的状态信息。

查找源有二：AMS 中的 mServices（正在运行中的服务）和 PMS 中的 mServices（已经安装服务的解析类）

对于Linux上的程序启动Android上的Service这种情况，我们暂时不考虑Service的注册问题。我们可以模拟Android上的程序将IActivityManager.descriptor、caller等五个信息通过Binder发送给AMS。并通过将userID设置为0之类的手段，暂时屏蔽掉AMS的调用者权限检测，应该能够成功实现调用。

但是对于在Linux上运行Service这种情况，首先需要在PMS里注册Service。在Android里注册后，启动Service时，ActivityManagerService会调用Zogote进程创建新进程。

但是，Linux中的程序应该是自主运行的，运行的进程不受Android上的ActivityManagerService控制。

应该如何修改ActivityManagerService机制？


## 3 本周结果：

通过 ActivityManagerService 服务发送启动Service的Intent、并启动Service的部分已经看完。

对于情景： **Linux上的程序启动Android上的Service** 已经比较清楚。

这种情景，我们暂时不需要考虑Service的注册问题。

我们可以模拟Android上的程序将IActivityManager.descriptor、caller等五个信息通过Binder发送给AMS。并通过将userID设置为0之类的手段，暂时屏蔽掉AMS的调用者权限检测，应该能够成功实现调用。

对于情景：**Android上的APP调用Linux上运行Service** 不太清楚。

这种情况，首先需要在 PackageManagerService 里注册该 Service 。在Android里注册后，启动Service时，ActivityManagerService会调用Zogote进程创建新进程。但是，Linux中的程序应该是自主运行的，运行的进程不受Android上的ActivityManagerService控制。

如果是这样，如何修改ActivityManagerService的机制，来实现Linux上的Service自主启动，不使用Zogote进程，并连接上ActivityManagerService。

## 4 下载计划：

# 2017.02.25~2017.03.02

## 1 本周目标：

上周与陈渝老师进行远程会议后，定下本周计划是做一个简单的例子，如下：

尝试在Linux中运行一个简单的Service（如：只有简单的计算功能），然后在Android中的APP可以调用该Service。

第一步：了解 Binder 如何启动新的Service

第二步：了解如何在 Binder 中注册新的Service

第三步：移植相关代码测试

如果这个例子不能够简单的完成，则说明本课题不是我想象中的那么简单，是有研究价值的。

## 2 研究过程：

通过几天的努力，我现在能够在Linux上编译Android中的Service类，但是该Service并不能够运行。

由于我现在还没有完全弄清楚Android中的APP启动机制，所以先说一说已经研究的部分。

参考罗升阳的博客： Android系统在新进程中启动自定义服务过程（startService）的原理分析

http://blog.csdn.net/luoshengyang/article/details/6677029

将ActivityManagerService的startService函数的处理流程记录下，共20步。如果自己找的话，中间很多是通过父类调用子类方法、Socket、Binder通信等方式，无法直接找出下一步跳到哪，所以罗升阳的这篇博客有很大阅读价值。
```
Step 1. ActivityManagerService.startService
Step 2. ActivityManagerService.startServiceLocked
Step 3. ActivityManagerService.bringUpServiceLocked
Step 4. ActivityManagerService.startProcessLocked
Step 5. Process.start
Step 6. ActivityThread.main
Step 7. ActivityThread.attach
Step 8. ActivityManagerProxy.attachApplication
Step 9. ActivityManagerService.attachApplication
Step 10. ActivityManagerService.attachApplicationLocked
Step 11. ActivityManagerService.realStartServiceLocked
Step 12. ApplicationThreadProxy.scheduleCreateService
Step 13. ApplicationThread.scheduleCreateService
Step 14. ActivityThread.queueOrSendMessage
Step 15. H.sendMessage
Step 16. H.handleMessage
Step 17. ActivityThread.handleCreateService
Step 18. ClassLoader.loadClass
Step 19. Obtain Service
Step 20. Service.onCreate
```
这样，Android系统在新进程中启动服务的过程就分析完成了，虽然很复杂，但是条理很清晰。它通过三次Binder进程间通信完成了服务的启动过程，分别是：

  一. Step 1至Step 7，从主进程调用到ActivityManagerService进程中，完成新进程的创建；
  
  二. Step 8至Step 11，从新进程调用到ActivityManagerService进程中，获取要在新进程启动的服务的相关信息；
  
  三. Step 12至Step 20，从ActivityManagerService进程又回到新进程中，最终将服务启动起来。

参考

以Binder视角来看Service启动 http://blog.csdn.net/omnispace/article/details/52732442

startService启动过程分析 http://gityuan.com/2016/03/06/start-service/

![调用图](http://ww3.sinaimg.cn/large/0060lm7Tgy1fd8urgqdx8j30j9054aae.jpg)

1 - ActivityManagerService通过Socket通信方式向Zygote进程请求生成(fork)用于承载服务的进程ActivityThread。此处讲述启动远程服务的过程，即服务运行于单独的进程中，对于运行本地服务则不需要启动服务的过程。ActivityThread是应用程序的主线程；

2 - Zygote通过fork的方法，将zygote进程复制生成新的进程，并将ActivityThread相关的资源加载到新进程；

3 - ActivityManagerService向新生成的ActivityThread进程，通过Binder方式发送生成服务的请求；

4 - ActivityThread启动运行服务，这便于服务启动的简易过程，真正流程远比这服务复杂；

我自己再查看 ActivityManagerService.java 源码

在Step 4  startProcessLocked中
```
Process.ProcessStartResult startResult = Process.start(entryPoint,
                    app.processName, uid, uid, gids, debugFlags, mountExternal,
                    app.info.targetSdkVersion, app.info.seinfo, requiredAbi, instructionSet,
                    app.info.dataDir, entryPointArgs);
```
进入Step 5 Process.start()
```
return startViaZygote(processClass, niceName, uid, gid, gids,
  debugFlags, mountExternal, targetSdkVersion, seInfo,
  abi, instructionSet, appDataDir, zygoteArgs);
```
进入 startViaZygote()
return zygoteSendArgsAndGetResult(openZygoteSocketIfNeeded(abi), argsForZygote);

可以看到，程序通过 zygoteState.writer 将命令写入Socket

另外查找源码看到 public static ZygoteState connect(String socketAddress) throws IOException {

可以看到在connect里创建了socket连接

另外，通过查资料看到，这个Socket就是 /dev/socket/zygote

后面的暂时不用不看了，已经大致过了一遍Service的启动流程。

## 3 本周结果：

通过发现上图 1 Socket 过程，看到ActivityManagerService启动Service是通过Socket的方式连接Zygote进程，让它来fork出新的进程，然后ClassLoader.loadClass，之后ActivityManagerService通过Binder与新进程交互，完成启动。
所以Service的运行并不是像我之前想象的一样：是一个进程fork之后，自己通过Binder连接系统服务完成初始化。Service的整个初始化过程受到Zygote控制，它并没有一个main函数主动执行所有逻辑，全是被调用。
我之前完全没有意识到这个概念，太天真了。并且Android系统中的程序在ART虚拟机中运行，这就造成谁来启动Service的问题：

1. Android中的Service在ART虚拟机中运行，而我在Linux中不能这样干，因为我要和Linux中的程序结合，必然要在Linux中启动，比如：Linux中的JAVA程序在JVM中运行。

2. 需要一个服务程序主动调用Service中的函数，完成Service的生命周期。

所以现在将android.jar（APP层依赖库）复制过来，在Linux中编译程序

javac -Djava.ext.dirs=. com/example/bboxh/testipcapplication/MyService.java

虽然能够编译，但是没有程序能够调用。。。

## 4 下周计划：

搞懂ActivityManagerService服务运行的详细过程，然后研究一个调用方案，实现在Linux中启动该Service，并且能够与Android中的ActivityManagerService服务相交互。

目前想到这里面有一些细节有待解决：

1. Linux中的Service的注册问题

2. Linux中的Service的生命周期同步问题
