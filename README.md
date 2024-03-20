# WhiteSpiderTool
 get network card info and test network tool by Tkinter
 本程序逻辑使用python编写，ui使用Tkinter编写。开发初衷是为了更方便地调试网络，同时可以方便地监控网卡，同时程序小巧灵活，能快速在windows系统上使用。

 开发测试硬件：i7-10870K  DDR4-32G

 核心功能实现：
  1.系统的信息通过获取是筛选注册表实现的
  2.网络配置的变更是由netsh实现的(注：在测试过程中发现启动程序后点击"保存"后仅能做一次更改，查阅文献猜测是微软或网卡厂商的原因，因此建议变更仍使用网络适配器更改)
  3.网络测试方面目前实现了icmp探测主机存活和tcp端口检测，可以多线程ping和同时探测端口是否在线，用于快速检查某设备服务(如http80是否开启)；端口探测支持导入json，方便批量探测

目前只开发了上述功能，可能存在一些bug，看时间和心情再去修了ヾ(•ω•`)o

网卡检测面板
![image](https://github.com/LOCKDOWN083199/WhiteSpiderTool/assets/133126018/02293449-35b8-4acc-8c92-76b9466ca4b1)

网络调试面板
![image](https://github.com/LOCKDOWN083199/WhiteSpiderTool/assets/133126018/5cc5581c-efee-487e-b2c9-ba44c74a0915)


