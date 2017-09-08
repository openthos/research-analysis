EventLogging代码分析

1、StartupReceiver.java

监听手机的开机广播，一旦接受到，开启ServerService服务

2、ServerService.java   TAG = "ServerService"

创建UserSpaceServer实例mUserServer并调用start()方法开启
创建KernelEventServer实例mKernelServer并调用start()方法开启

创建Writer实例mWriter并初始化
创建BufferQueue实例mBufferQueue并初始化

创建ConfigChange实例mConfigChange并调用start()方法开启
  
给NetworkListenerRegistered赋值为false
  
动态注册一个batterybroadcastIntentReceiver，如果手机处于充电或者满电的状态，就动态注册一个networkbroadcastReceiver，并将
NetworkListenerRegistered赋值为true，如果手机不处于充电状态，并且注册了networkbroadcastReceiver，就撤销注册，并将
NetworkListenerRegistered赋值为false

当收到网络已连接的广播，networkbroadcastReceiver创建SendFiles实例mSender，如果mSender.shouldUpload()为true，将mSender作为参数传入Thread
构造方法中创建Thread实例，并调用start（）开启线程

3、UserSpaceServer.java
UserSpaceServer继承于Thread，创建一个1234端口，
while((mActive) && (!interrupted())){
			Socket connectionSocket;			
			try {
				Log.d(TAG,"accepting...");
				connectionSocket = mySocket.accept();
				ServerWorker myWorker = new ServerWorker(connectionSocket);
				Thread workerThread = new Thread(myWorker);
				workerThread.start();
			} catch (ClosedByInterruptException e){
				//Thread has been interrupted, close
			}catch (IOException e) {
				// TODO Fill in the right handling
			}	
}
4、KernelEventServer.java
KernelEventServer继承于Thread，从/proc/event_logging下读取kernel log
5、Writer.java
File UserDirectory = new File("/sdcard/user/");
UserDirectory.mkdir();
File KernelDirectory = new File("/sdcard/kernel/");
KernelDirectory.mkdir();
