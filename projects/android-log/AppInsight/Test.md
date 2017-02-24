### 目标
- 复现论文的工作
 + 一个apk的Demo
 + 手动添加Log
 + 手动生成Decour库
 
### 工作进展

- 一个Demo，实现简单的异步调用UI更新
- 手动在回调的地方添加Log
- apk源码如下：
```
public class MainActivity extends Activity {

    private TextView tv;
    private Button button;
    private Thread newThread;


    Handler handler = null;
    public ActionBarDrawerToggle.Delegate updateUI;

    void updateUI(){
        Log.v("LogUpcallStart","21");

        this.handler = new Handler()
    {
        public void handleMessage(android.os.Message msg) {
            if(msg.what==0x123)
            {
                tv.setText("更新后的TextView");
            }
        };
    };

        Log.v("LogUpcallEnd","21");
    }

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_main);
        tv = (TextView) findViewById(R.id.text);
        button = (Button) findViewById(R.id.button);
        button.setOnClickListener(new View.OnClickListener() {
            public ActionBarDrawerToggle.Delegate upcall;

            @Override
            public void onClick(View view) {
                Log.v("LogUpcallStart","5");
                //upcall();

                Log.v("LogCallStart","7");
                Detour dt = DetourFactory.GetDetour(upcall, 7);
                dt.Cb1();




                Log.v("LogCallEnd","7");
                Log.v("LogUpcallEnd","5");
            }
        });

    }

   void upcall(){
       Log.v("LogUpcallStart","19");
       newThread = new Thread() {
           @Override
           public void run() {
               //延迟两秒更新
               try {
                   Thread.sleep(1000);
               } catch (InterruptedException e) {
                   // TODO Auto-generated catch block
                   e.printStackTrace();
               }
               handler.sendEmptyMessage(0x123);
           }
       };
       newThread.start();

       Log.v("LogUpcallStart", "13");
       Detour dt = DetourFactory.GetDetour(updateUI, 13);
       dt.Cb2();
       Log.v("LogUpcallEnd", "13");
      // updateUI();

       Log.v("LogUpcallEnd","19");
   }
}
```
- 手动生成Decour库，可以对回调函数进行绕行，源码如下：
```
public class DetourFactory {

    public static Detour GetDetour(ActionBarDrawerToggle.Delegate d, int callId) {
        Random rand = new Random();
        int matchId =rand.nextInt(100);

        String match = String.valueOf(matchId);
        String  call= String.valueOf(callId);

        Log.v(call,match);

        return new Detour(d,matchId);
    }
}



public class Detour {
    int matchId;
    ActionBarDrawerToggle.Delegate originalCb;
    public Detour(ActionBarDrawerToggle.Delegate d, int matchId) {
        this.originalCb = d;
        this.matchId = matchId;
    }

    public void Cb1() {
        String match = String.valueOf(matchId);
        Log.v("LOgcallbackStart",match);
        new MainActivity().upcall();
    }

    public void Cb2() {
        String match = String.valueOf(matchId);
        Log.v("LOgcallbackStart",match);
        new MainActivity().updateUI();
    }
}
```
- 打印结果的Log如下：
```
02-15 07:02:19.831 3050-3050/com.example.root.papertext V/LogUpcallStart: 5
02-15 07:02:19.832 3050-3050/com.example.root.papertext V/LogCallStart: 7
02-15 07:02:19.971 3050-3050/com.example.root.papertext V/7: 7
02-15 07:02:19.997 3050-3057/com.example.root.papertext W/art: Suspending all threads took: 17.904ms
02-15 07:02:20.002 3050-3050/com.example.root.papertext V/LOgcallbackStart: 7
02-15 07:02:20.004 3050-3050/com.example.root.papertext V/LogUpcallStart: 19
02-15 07:02:20.037 3050-3050/com.example.root.papertext V/LogUpcallStart: 13
02-15 07:02:20.038 3050-3050/com.example.root.papertext V/13: 80
02-15 07:02:20.038 3050-3050/com.example.root.papertext V/LOgcallbackStart: 80
02-15 07:02:20.038 3050-3050/com.example.root.papertext V/LogUpcallStart: 21
02-15 07:02:20.053 3050-3050/com.example.root.papertext V/LogUpcallEnd: 21
02-15 07:02:20.053 3050-3050/com.example.root.papertext V/LogUpcallEnd: 13
02-15 07:02:20.053 3050-3050/com.example.root.papertext V/LogUpcallEnd: 19
02-15 07:02:20.053 3050-3050/com.example.root.papertext V/LogCallEnd: 7
02-15 07:02:20.053 3050-3050/com.example.root.papertext V/LogUpcallEnd: 5
```

### 存在的问题
- Log打印的结果并不是异步调用应有的结果
- Android程序编码规则不像论文中那么好找到回调的点，并绕行
