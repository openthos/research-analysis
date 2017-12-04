因为Oblivious store是一个client side的概念，client自己决定是否要隐藏自己的access pattern，同时client也是可信的，和我们最开始的目标其实是不一样的。
目前可以想到论文有两种写作思路：  
1. 按照secure cloud的写法，我们防御了Rollback attack。然后将oblivious store作为应用之一。   
2. 按照Oblivious store的写法，我们可以防止恶意的server。   这种写法安全性比较难写，同时我们不是传统的Oblivious store，然后我们性能好很多。

目前给的式第一种写法的第三和第四章。problem definition主要是讲清楚这篇论文主要是在做什么。Design第一个版本是按照我们有哪些措施写的，感觉不清楚。
Design2希望基于我们有哪些东西需要隐藏，为什么要隐藏，因此做了哪些事情的思路写的。
