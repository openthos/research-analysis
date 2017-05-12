## IntentService与Thread的区别
  - IntentService 实际上是Looper,Handler,Service 的集合体
  - IntentService是继承于Service并处理异步请求的一个类，在IntentService内有一个工作线程来处理耗时操作，启动IntentService的方式和启动传统Service一样，
  同时，当任务执行完后，IntentService会自动停止，而不需要我们去手动控制。另外，可以启动IntentService多次，而每一个耗时操作会以工作队列的方式在
  IntentService的onHandleIntent回调方法中执行，并且，每次只会执行一个工作线程，执行完第一个再执行第二个，以此类推
  - IntentService是android中开启异步线程的一种方法，程序员不需要new Thread，也不需要start和stop。程序员可以很简单的使用。IntentService可以
  自动开启一个HandleThread，并自动调用intentService中的onHandleIntent()方法来处理异步任务
 
## IntentService的源码解析
  - 首先onCreate()
```
源码地址：/frameworks/base/core/java/android/app/IntentService.java
 public void onCreate() {
        super.onCreate();
       //开启一个新的HandlerThread线程
        HandlerThread thread = new HandlerThread("IntentService[" + mName + "]");
        thread.start();
      // 调用自定义的一个内部类
        mServiceLooper = thread.getLooper();
        mServiceHandler = new ServiceHandler(mServiceLooper);
    }

```
  - 自定义的内部类：ServiceHandler
```
 private final class ServiceHandler extends Handler {
   //构造函数，ServiceHandler与Looper绑定，通过Handler向Looper发消息
   public ServiceHandler(Looper looper) {
            super(looper);
        }
   
   // 当MessageQueue有消息时，handlerMessage处理消息，并调用onHandleIntent处理任务，处理完之后stop
        @Override
        public void handleMessage(Message msg) {
            onHandleIntent((Intent)msg.obj);
            stopSelf(msg.arg1);
        }
    }
```
  - onStartCommand()
```
 public int onStartCommand(@Nullable Intent intent, int flags, int startId) {
        //调用onStart
        onStart(intent, startId);
        return mRedelivery ? START_REDELIVER_INTENT : START_NOT_STICKY;
    }
    
  
  public void onStart(@Nullable Intent intent, int startId) {
        Message msg = mServiceHandler.obtainMessage();
        msg.arg1 = startId;
        msg.obj = intent;
        //sendMessage之后，就可以HandleMessage了
        mServiceHandler.sendMessage(msg);
    }
```
  - 最主要的onHandleIntent()
```
// 抽象方法，应用层重写这个方法进行异步处理任务
protected abstract void onHandleIntent(Intent intent);
```
## 实践的问题
  - IntentService是start开启新线程，但是线程的工作并不是从native层Thread的run开启的
  - 自己写的Demo中，App打开就会开启五六个新的线程，这几个线程并不是Thread.start之后的线程;另外thread.start之后也开启了两个新的线程，他们之间的
  关系是怎样的，哪个线程是我们主要需要关注的
