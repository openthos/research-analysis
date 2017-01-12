# proc
## lkp
### interrupts
APIC：中断控制器
timer：系统时钟
i8042：控制键盘和鼠标的键盘控制器
rtc（real time clock）：CPU是不会被中断的。因为RTC存在于电子设备中，是用于追踪时间的。
ioc0：输入/输出控制寄存器
ens37：网卡 mac地址
PCI-MSI：PCI总线中，MSI中断机制是一个可选机制
vmci：VMware产品中的一个可选功能,允许虚拟机之间相互通讯
nmi：不可屏蔽中断
loc：本地定时器中断
pmi：性能监控中断
res：重安排中断
cal：函数调用中断
TLB：虚拟内存地址到物理内存地址的映射表，有软件TLB和硬件TLB， x86架构使用硬件TLB
MCP：机器检查调查
NET_TX：上行流量
NET_RX：下行流量
TASKLET：通常用于减少中断处理的时间
RCU：数据同步的一种方式
```
  "interrupts.CPU0.0:IO-APIC.2-edge.timer": 0,
  "interrupts.0:IO-APIC.2-edge.timer": 0, 
  
  "interrupts.CPU0.1:IO-APIC.1-edge.i8042": 0,
  "interrupts.CPU1.1:IO-APIC.1-edge.i8042": 0,
  "interrupts.1:IO-APIC.1-edge.i8042": 0,
  "interrupts.CPU0.12:IO-APIC.12-edge.i8042": 0,
  "interrupts.CPU1.12:IO-APIC.12-edge.i8042": 0,
  "interrupts.12:IO-APIC.12-edge.i8042": 0,

  "interrupts.CPU0.8:IO-APIC.8-edge.rtc0": 0,
  "interrupts.8:IO-APIC.8-edge.rtc0": 0,

  "interrupts.CPU0.16:IO-APIC.16-fasteoi.ehci_hcd:usb1,vmwgfx": 0,
  "interrupts.CPU1.16:IO-APIC.16-fasteoi.ehci_hcd:usb1,vmwgfx": 0,
  "interrupts.16:IO-APIC.16-fasteoi.ehci_hcd:usb1,vmwgfx": 0,   //猜测为驱动

  "interrupts.CPU0.17:IO-APIC.17-fasteoi.ioc0": 0,
  "interrupts.CPU3.17:IO-APIC.17-fasteoi.ioc0": 38,
  "interrupts.17:IO-APIC.17-fasteoi.ioc0": 38,

  "interrupts.CPU0.18:IO-APIC.18-fasteoi.uhci_hcd:usb2": 0,
  "interrupts.18:IO-APIC.18-fasteoi.uhci_hcd:usb2": 0,

  "interrupts.CPU0.19:IO-APIC.19-fasteoi.snd_ens1371,ens37": 0,
  "interrupts.CPU1.19:IO-APIC.19-fasteoi.snd_ens1371,ens37": 107,
  "interrupts.19:IO-APIC.19-fasteoi.snd_ens1371,ens37": 107,

  "interrupts.CPU0.56:PCI-MSI.1114112-edge.0000:02:04.0": 0,
  "interrupts.CPU2.56:PCI-MSI.1114112-edge.0000:02:04.0": 20,
  "interrupts.56:PCI-MSI.1114112-edge.0000:02:04.0": 20,
  "interrupts.CPU0.57:PCI-MSI.129024-edge.vmw_vmci": 0,
  "interrupts.CPU1.57:PCI-MSI.129024-edge.vmw_vmci": 0,
  "interrupts.57:PCI-MSI.129024-edge.vmw_vmci": 0,
  
  ```
