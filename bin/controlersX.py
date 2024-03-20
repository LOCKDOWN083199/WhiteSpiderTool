# ============================
# 此模块是各种自定义控件和组件的实现
# ============================

import tkinter as tk
import queue
import threading
import time
import re
import copy
import json
from tkinter import filedialog
from bin import messageCtl
from bin import networkCtl
from bin import frames
from bin import protocols
from bin import if_connection

from bin.globals import Thread_pool, STYLE, ICMP_TIMEOUT  # 引入公共线程池


class BASE_FRAME(threading.Thread):  # 基础frame类,作为每个卡组件的父类(底板)
    def __init__(self, root, frame_size=(180, 280), font=STYLE.DefFont, place_set=(10, 10)):
        super().__init__()
        self.root = root  # 上级组件
        self.frame: tk.Frame = tk.Frame(self.root, highlightthickness=2)  # 本级frame,使用一个frame承载所有控件
        self.frame_size = frame_size  # 本级frame大小
        self.frame_border_color = "#ffffff"  # 边框颜色
        self.place_set = place_set  # 位置
        self.font = font  # 字体

        self.KillSelfDone = False  # 是否已执行del self (可能会用到的标志属性)

        # 事件绑定区
        # =============================================
        # 鼠标划过组件反应模块
        # -------------------------
        self.frame.bind("<Enter>", self.mouse_enter)  # 绑定鼠标划入事件
        self.frame.bind("<Leave>", self.mouse_leave)  # 绑定鼠标划出事件
        self.mouse_exit = True  # 鼠标是否划出
        # -------------------------

        # 拖动组件模块 (禁用)
        # -------------------------
        # self.frame.bind("<Button-1>", self.LeftMouseDown)  # 绑定鼠标左键点击事件
        # self.frame.bind("<ButtonRelease-1>", self.LeftMouseUp)  # 绑定鼠标左键释放事件
        # self.frame.bind("<B1-Motion>", self.do_move)  # 绑定鼠标左键+移动事件
        # -------------------------

        # =============================================

    # 拖拽功能现已禁用 2024.1.17
    # ==============================================================================================================
    # def LeftMouseDown(self, event):  # 鼠标左键点击frame后拖拽
    #     # 记录鼠标左键点击的初始位置
    #     self.framex = event.x
    #     self.framey = event.y
    #
    #     self.IPAddressEntry.select_clear()
    #
    #     self.AdvancedFrame.place_forget()  # !!!如果高级面板存在,则隐藏(将来可能要删除此功能)!!!
    #     self.AdvancedButtonClicked = False
    #     self.AdvancedFrameExsit = False
    #
    #     self.LeftMouseClick = True
    #
    # def LeftMouseUp(self, event):  # 停止拖拽
    #     # 鼠标左键释放，清除记录的位置信息
    #     self.framex = None
    #     self.framey = None
    #
    #     self.LeftMouseClick = False
    #
    #     self.place_set = (self.frame.winfo_x(), self.frame.winfo_y())  # !!!注意:关闭拖拽功能后这里可能要删除!!!
    #
    # def do_move(self, event):  # 拖拽运算
    #     # 鼠标左键移动，计算移动的距离dx, dy
    #     dx = event.x - self.framex  # - self.frame_size[0]-70 #如果frame设置了relx，rely，这里要减去相应的值
    #     dy = event.y - self.framey  # - self.frame_size[1]-50
    #     # 计算窗口新的位置
    #     x = self.frame.winfo_x() + dx
    #     y = self.frame.winfo_y() + dy
    #     # 更新窗口的位置
    #     self.frame.place(x=x, y=y)
    # ==============================================================================================================

    def mouse_enter(self, event):  # 鼠标划过frame组件响应
        self.frame.config(
            highlightbackground=STYLE.MouseEnter)
        self.mouse_exit = False
        self.mouse_motion_delay()
        # self.frame.config(cursor="hand2") # 鼠标划过frame组件时,鼠标变为手型

    def mouse_motion_delay(self):
        i = 2  # 速率系数，越大动画速度越快。建议设置为可整除的数，建议为2的倍数
        dx = i  # 每次重绘x轴移动值
        dy = (self.frame_size[1] / self.frame_size[0]) * i / 2  # 每次重绘y轴移动值

        # 鼠标进入frame时,frame的大小逐渐增大,且frame的位置向左上角移动
        if self.frame.winfo_width() <= self.frame_size[0] + 10 and self.mouse_exit == False:
            self.frame.place(x=self.frame.winfo_x() - (dx * 0.5), y=self.frame.winfo_y() - (dy * 0.5))
            self.frame.configure(width=self.frame.winfo_width() + dx,
                                 height=self.frame.winfo_height() + dy)
            self.frame.after(30, self.mouse_motion_delay)  # 延时重绘

        # 鼠标离开frame时,frame的大小逐渐减小,且frame的位置向右下角移动
        elif self.mouse_exit == True and self.frame.winfo_width() >= self.frame_size[0]:
            self.frame.place(x=self.frame.winfo_x() + (dx * 0.5), y=self.frame.winfo_y() + (dy * 0.5))
            self.frame.configure(width=self.frame.winfo_width() - dx,
                                 height=self.frame.winfo_height() - dy)
            self.frame.after(30, self.mouse_motion_delay)  # 延时重绘

    def mouse_leave(self, event):  # 鼠标离开frame组件
        self.frame.config(highlightbackground=self.frame_border_color)
        self.mouse_exit = True
        self.mouse_motion_delay()
        self.frame.config(cursor="arrow")


class SECOND_FRAME:  # 二级面板基类,比如高级面板
    def __init__(self, root, frame_size=(180, 280), place_set=(10, 10), frame_border_color="#ffffff", bg=STYLE.ViewBG):
        self.root = root
        self.frame: tk.Frame = tk.Frame(self.root)
        self.frame_size = frame_size
        self.frame_border_color = frame_border_color
        self.place_set = place_set

        self.frame.configure(highlightbackground=self.frame_border_color, highlightthickness=2,
                             width=self.frame_size[0], bg=STYLE.ViewBG, height=self.frame_size[1])

        self.isClosed = True  # 是否关闭

        # 事件绑定区
        # ---------------------------------------------
        self.frame.bind("<Enter>", self.mouse_enter_SECOND_FRAME)  # 绑定鼠标划入事件
        self.frame.bind("<Leave>", self.mouse_leave_SECOND_FRAME)  # 绑定鼠标划出事件
        self.frame.bind("<Button-1>", self.click_SECOND_FRAME)  # 绑定鼠标左键点击事件

    def mouse_enter_SECOND_FRAME(self, event):
        self.isClosed = False
        self.frame.config(highlightbackground=STYLE.MouseEnter)
        # self.frame.config(cursor="hand2")

    def mouse_leave_SECOND_FRAME(self, event):
        self.isClosed = True
        self.frame.place_forget()
        self.frame.config(highlightbackground=self.frame_border_color)
        # self.frame.config(cursor="arrow")

    def click_SECOND_FRAME(self, event):  # 点击frame
        pass


class LableButton:  # 标签按钮类
    def __init__(self, root, text="标签按钮", font=STYLE.MSYHFont, place_set=(10, 10),
                 frame_size=(40, 20), bg=STYLE.ViewBG, fg="black", border_color="#ffffff", ):
        self.root = root
        self.frame_size = frame_size
        self.BaseFrame = tk.Frame(self.root)
        self.text = text
        self.font = font
        self.border_color = border_color
        self.bg = bg
        self.fg = fg
        self.place_set = place_set
        self.Label = tk.Label(self.BaseFrame, text=self.text, font=self.font, bg=STYLE.ViewBG)

        self.BaseFrame.configure(bg=self.border_color)
        self.Label.configure(bg=self.bg, fg=self.fg)
        self.Label.place(relx=0.5, rely=0.5, anchor=tk.CENTER, relwidth=0.95, relheight=0.9)

        # 事件绑定区
        # ---------------------------------------------
        self.BaseFrame.bind("<Enter>", self.mouse_enter_frame)  # 绑定鼠标划入事件
        self.BaseFrame.bind("<Leave>", self.mouse_leave_frame)  # 绑定鼠标划出事件
        self.BaseFrame.bind("<Button-1>", self.click)  # 绑定鼠标左键点击事件
        self.Label.bind("<Button-1>", self.click)  # 绑定鼠标左键点击事件

    def mouse_enter_frame(self, event):
        self.BaseFrame.config(bg=STYLE.MouseEnter)
        self.BaseFrame.config(cursor="hand2")

    def mouse_leave_frame(self, event):
        self.BaseFrame.config(bg=self.border_color)
        self.BaseFrame.config(cursor="arrow")

    def click(self, event):
        pass


# 列表组件
class ListFrame:  # 带可设置边框的列表组件(frame+listbox)
    def __init__(self, root, frame_size=(0.4, 0.4), border_color="#ffffff", bg=STYLE.ViewBG,
                 place_set=(0.1, 0.1)):
        self.root = root
        self.frame_size = frame_size
        self.border_color = border_color
        self.bg = bg
        self.place_set = place_set

        self.BaseFrame = tk.Frame(self.root, bg=self.border_color, highlightbackground=self.border_color,
                                  highlightthickness=2)
        self.ListBox = tk.Listbox(self.BaseFrame, bg=self.bg, font=STYLE.MSYHFont)
        self.ListBox.place(relx=0, rely=0, anchor=tk.NW, relwidth=1, relheight=1)
        self.BaseFrame.place(relx=self.place_set[0], rely=self.place_set[1], anchor=tk.NW, relwidth=self.frame_size[0],
                             relheight=self.frame_size[1])

        # 事件绑定区
        # ---------------------------------------------
        # listbox绑定鼠标左键点击事件
        self.ListBox.bind("<Button-1>", self.click)
        # listbox绑定选中事件
        self.ListBox.bind("<<ListboxSelect>>", self.SelectItem)

    def click(self, event):
        pass

    def SelectItem(self, event):
        pass

    # 增加listbox里的选项
    def AddItem(self, item):
        self.ListBox.insert("end", item)

    # 删除listbox里的选项
    def DelItem(self, item):
        self.ListBox.delete(item)


class NetworkView(BASE_FRAME):
    def __init__(self, root, networkcard: dict = {}, cardname: str = 'network', place_set=(10, 10),
                 frame_size=(180, 280), font=STYLE.DefFont, NetX=0, NetY=0,
                 quote=None):  # quote用于存储网卡菜单的引用,拿来管理三级菜单中的网卡
        # =========================线程类继承初始化
        super().__init__(root, frame_size=frame_size, font=font, place_set=place_set)
        # =========================公用属性部分
        self.networkcard: dict = networkcard  # 网卡信息
        self.NetworkCardName = cardname  # 网卡名称
        # self.FactSize = (0, 0)  # 实际大小(因为有动画效果,所以本体大小会变化,因此需要记录非动画的实际大小)   #弃用
        # self.FactPlace = (0, 0)  # 实际位置(因为有动画效果,所以本体位置会变化,因此需要记录非动画的实际位置)  #弃用
        # self.NetX = NetX  # 网卡在frame.py中的管理位置  #弃用
        # self.NetY = NetY  # 网卡在frame.py中的管理位置  #弃用

        self.canvas_size = (frame_size[0] * 0.9, 80)  # 折线图画布大小
        self.RecvDataQueue = queue.Queue(maxsize=10)  # 存储10秒内收到的字节数据,1s更新一个数据
        self.SendDataQueue = queue.Queue(maxsize=10)  # 存储10秒内发送的字节数据
        for i in range(0, 10):
            self.RecvDataQueue.put(0)  # RecvDataQueue初始置0
        for i in range(0, 10):
            self.SendDataQueue.put(0)  # SendDataQueue初始置0

        self.RecvPacks_t1 = if_connection.Bytes_Recv_From_PowerUP()  # 第(前)1s收到的字节数据值储存
        self.SendPacks_t1 = if_connection.Bytes_Send_From_PowerUP()  # 第(前)1s发送的字节数据值储存

        self.LeftMouseClick = False  # 鼠标左键是否在frame内按下

        self.DhcpEnable = 2  # 是否启用DHCP,0未启用,1启用,2未知
        if "EnableDHCP" in self.networkcard[cardname]["cfg"]:
            if self.networkcard[cardname]["cfg"]["EnableDHCP"] == 1:
                self.DhcpEnable = 1
            elif self.networkcard[cardname]["cfg"]["EnableDHCP"] == 0:
                self.DhcpEnable = 0

        self.is_physical = False  # 是否是物理网卡

        self.after_id = None  # 用于存储after的id,用于取消after

        self.networkmenuquote = quote  # 用于存储网卡菜单的引用(为了动态管理可添加网卡的三级菜单,需要传入三级菜单的引用)

        self.MoreIP = False  # 是否有多个IP地址
        self.MoreGateWay = False  # 是否有多个网关
        self.MoreDNS = False  # 是否有多个DNS

        # 最终统一化处理
        self.IpAddrs = []
        self.NetMasks = []
        self.GateWays = []
        self.DNSs = []

        self.result = []  # 保存配置的操作结果
        self.msgout = False  # 用于判断是否有消息输出
        self.msgdata = ""  # 用于保存消息输出
        self.msgnum = 0  # 用于消息计时

        self.only_one_select = 0  # 可能由于tkinter的谜之特性,会导致select事件重复触发,此属性用于判断只有一个listbox被选中

        # 将ip地址和掩码从dhcp配置或静态配置梳理后加入IpAddrs和NetMasks
        if self.DhcpEnable == 0:
            if "IPAddress" in self.networkcard[self.NetworkCardName]["cfg"]:
                self.IpAddrs = self.networkcard[self.NetworkCardName]["cfg"]["IPAddress"]
                self.NetMasks = self.networkcard[self.NetworkCardName]["cfg"]["SubnetMask"]
        elif self.DhcpEnable == 1:
            if "DhcpIPAddress" in self.networkcard[self.NetworkCardName]["cfg"]:
                self.IpAddrs.append(self.networkcard[self.NetworkCardName]["cfg"]["DhcpIPAddress"])
                self.NetMasks.append(self.networkcard[self.NetworkCardName]["cfg"]["DhcpSubnetMask"])
        else:
            if "IPAddress" in self.networkcard[self.NetworkCardName]["cfg"]:
                self.IpAddrs = self.networkcard[self.NetworkCardName]["cfg"]["IPAddress"]
                self.NetMasks = self.networkcard[self.NetworkCardName]["cfg"]["SubnetMask"]
            messageCtl.Pop_Top_message(messageCtl.MSG_TYPE.ERR,
                                       f"{self.NetworkCardName}\n未知的DHCP状态,网卡可能有异常!", TTL=5000)

        # 将网关和DNS从dhcp配置或静态配置梳理后加入GateWays和DNSs
        if self.DhcpEnable == 0:
            if "DefaultGateway" in self.networkcard[self.NetworkCardName]["cfg"]:
                self.GateWays = self.networkcard[self.NetworkCardName]["cfg"]["DefaultGateway"]
            if "NameServer" in self.networkcard[self.NetworkCardName]["cfg"]:
                # 说明:注册表内存储方式可能如下"NameServer": "114.114.114.114,114.114.114.115",所以需要分割
                self.DNSs = self.networkcard[self.NetworkCardName]["cfg"]["NameServer"].split(",")
        elif self.DhcpEnable == 1:
            if "DhcpDefaultGateway" in self.networkcard[self.NetworkCardName]["cfg"]:
                self.GateWays.append(self.networkcard[self.NetworkCardName]["cfg"]["DhcpDefaultGateway"])
            if "DhcpNameServer" in self.networkcard[self.NetworkCardName]["cfg"]:
                # 说明:注册表内存储方式可能如下"DhcpNameServer": "192.168.1.1 192.168.0.1",所以需要分割
                self.DNSs = self.networkcard[self.NetworkCardName]["cfg"]["DhcpNameServer"].split(" ")
        else:
            # 未知的DHCP状态,可以添加其他异常处理
            if "DefaultGateway" in self.networkcard[self.NetworkCardName]["cfg"]:
                self.GateWays = self.networkcard[self.NetworkCardName]["cfg"]["DefaultGateway"]
            if "NameServer" in self.networkcard[self.NetworkCardName]["cfg"]:
                # 说明:注册表内存储方式可能如下"NameServer": "114.114.114.114,114.114.114.115",所以需要分割
                self.DNSs = self.networkcard[self.NetworkCardName]["cfg"]["NameServer"].split(",")

        # =========================线程管理
        self.daemon = True  # 设置为守护线程

        # =========================frame部分
        if "PnPInstanceId" in self.networkcard[self.NetworkCardName]:  # 根据(物理/虚拟)网卡类型设置边框颜色
            if self.networkcard[self.NetworkCardName]["PnPInstanceId"].find("PCI") != -1:
                self.frame_border_color = STYLE.PCIBorder
                self.is_physical = True
            else:
                self.frame_border_color = STYLE.VirtualBorder
                self.is_physical = False

        self.frame.configure(highlightbackground=self.frame_border_color, highlightthickness=2,
                             width=self.frame_size[0], bg=STYLE.ViewBG, height=self.frame_size[1])
        self.frame.place(anchor=tk.NW, x=self.place_set[0], y=self.place_set[1])

        # =========================折线图部分
        self.canvas = tk.Canvas(self.frame, width=self.canvas_size[0], height=self.canvas_size[1] + 4)  # +4是为了让折线不贴着边框
        self.canvas.place(relx=0.05, rely=0.17, anchor=tk.NW, relwidth=0.9)
        self.canvas.configure(bg=STYLE.NetworkCavansBG)

        # =========================上行实时速度部分
        self.SpeedSendLabel = tk.Label(self.frame, text="-" + "kb", font=self.font, width=12, height=1,
                                       fg=STYLE.Font_NetworkUP)
        self.SpeedSendLabel.place(relx=0.03, rely=0.1, anchor=tk.NW)

        # =========================下行实时速度部分
        self.SpeedRecvLabel = tk.Label(self.frame, text="-" + "kb", font=self.font, width=12, height=1,
                                       fg=STYLE.Font_NetworkDN)
        self.SpeedRecvLabel.place(relx=0.53, rely=0.1, anchor=tk.NW)

        # =========================网卡名称栏
        if len(cardname) <= 10:
            NetworkCardNameLess = cardname
        else:
            NetworkCardNameLess = cardname[0:7] + "..." + cardname[-4::1]
        if "PnPInstanceId" in self.networkcard[self.NetworkCardName]:
            if self.is_physical:
                self.NetworkCardNameLabel = tk.Label(self.frame, text=NetworkCardNameLess, font=STYLE.DefFontBigger14,
                                                     bg=STYLE.NetworkCardNamePCIBG, fg="white")
            else:
                self.NetworkCardNameLabel = tk.Label(self.frame, text=NetworkCardNameLess, font=STYLE.DefFontBigger14,
                                                     bg=STYLE.NetworkCardNameVirtualBG, fg="white")
        self.NetworkCardNameLabel.place(relx=0, rely=0, anchor=tk.NW, relwidth=1, relheight=0.1)

        # =========================ip地址栏
        self.DhcpEnableLabel = tk.Label(self.frame, text="D", font=self.font, fg="white")
        if self.DhcpEnable == 0 or self.DhcpEnable == 2:
            self.DhcpEnableLabel.config(bg=STYLE.DHCPDisableBG)
        elif self.DhcpEnable == 1:
            self.DhcpEnableLabel.config(bg=STYLE.DHCPEnableBG)
        self.DhcpEnableLabel.place(relx=0.05, rely=0.53, anchor=tk.NW)
        self.IPAddressLabel = tk.Label(self.frame, text="IP:", font=self.font, fg="black")
        self.IPAddressLabel.place(relx=0.15, rely=0.53, anchor=tk.NW)
        self.IPAddressEntry = tk.Entry(self.frame, font=self.font, bg=STYLE.EntryBG, fg="black", justify=tk.CENTER)
        self.IPAddressEntry.place(relx=0.28, rely=0.53, anchor=tk.NW, relwidth=0.64, relheight=0.07)

        # 设置DHCP启用状态标签颜色
        if self.DhcpEnable == 0 or self.DhcpEnable == 2:
            self.DhcpEnableLabel.config(bg=STYLE.DHCPDisableBG)
        elif self.DhcpEnable == 1:
            self.DhcpEnableLabel.config(bg=STYLE.DHCPEnableBG)

        if len(self.IpAddrs) > 1:  # 多个IP地址
            self.IPAddressEntry.insert(0, self.IpAddrs[0])
            self.MoreIP = True
        elif len(self.IpAddrs) == 1:  # 单个IP地址
            self.IPAddressEntry.insert(0, self.IpAddrs[0])
        else:
            self.IPAddressEntry.insert(0, "NULL")

        # =========================网关地址栏
        self.GatewayAddressLabel = tk.Label(self.frame, text="GW:", font=self.font, fg="black")
        self.GatewayAddressLabel.place(relx=0.15, rely=0.63, anchor=tk.NW)
        self.GatewayAddressEntry = tk.Entry(self.frame, font=self.font, bg=STYLE.EntryBG, fg="black", justify=tk.CENTER)
        self.GatewayAddressEntry.place(relx=0.28, rely=0.63, anchor=tk.NW, relwidth=0.64, relheight=0.07)
        # if "DefaultGateway" in self.networkcard[self.NetworkCardName]["cfg"]:
        #     self.GatewayAddressEntry.insert(0, self.networkcard[self.NetworkCardName]["cfg"]["DefaultGateway"])
        # elif "DhcpDefaultGateway" in self.networkcard[self.NetworkCardName]["cfg"]:
        #     self.GatewayAddressEntry.insert(0, self.networkcard[self.NetworkCardName]["cfg"]["DhcpDefaultGateway"])
        # else:
        #     self.GatewayAddressEntry.insert(0, "NULL")

        if len(self.GateWays) > 1:  # 多个网关地址
            self.GatewayAddressEntry.insert(0, self.GateWays[0])
            self.MoreGateWay = True
        elif len(self.GateWays) == 1:  # 单个网关地址
            self.GatewayAddressEntry.insert(0, self.GateWays[0])
        else:
            self.GatewayAddressEntry.insert(0, "NULL")

        # =========================DNS地址栏
        self.DNSServerTypeLabel = tk.Label(self.frame, text="D", font=self.font, fg="white", bg="#f9c36a")
        self.DNSServerTypeLabel.place(relx=0.05, rely=0.73, anchor=tk.NW)
        self.DNSAddressLabel = tk.Label(self.frame, text="DNS:", font=self.font, fg="black")
        self.DNSAddressLabel.place(relx=0.12, rely=0.73, anchor=tk.NW)
        self.DNSAddressEntry = tk.Entry(self.frame, font=self.font, bg=STYLE.EntryBG, fg="black", justify=tk.CENTER)
        self.DNSAddressEntry.place(relx=0.28, rely=0.73, anchor=tk.NW, relwidth=0.64, relheight=0.07)

        # 设置DHCP启用状态标签颜色
        if self.DhcpEnable == 0 or self.DhcpEnable == 2:
            self.DNSServerTypeLabel.config(bg=STYLE.DHCPDNSUnBG)
        elif self.DhcpEnable == 1:
            self.DNSServerTypeLabel.config(bg=STYLE.DHCPDNSEnBG)

        if len(self.DNSs) > 1:  # 多个DNS地址
            self.DNSAddressEntry.insert(0, self.DNSs[0])
            self.MoreDNS = True
        elif len(self.DNSs) == 1:  # 单个DNS地址
            self.DNSAddressEntry.insert(0, self.DNSs[0])
        else:
            self.DNSAddressEntry.insert(0, "NULL")

        # =========================保存按钮
        self.SaveButton = tk.Button(self.frame, text="保存", font=STYLE.MSYHFontBigger10, fg="white",
                                    bg=STYLE.Button_Yes_Back,
                                    relief=tk.GROOVE)
        self.SaveButton.place(relx=0.05, rely=0.86, anchor=tk.NW, relwidth=0.28, relheight=0.1)

        # =========================删除控件按钮
        self.DeleteButton = tk.Button(self.frame, text="关闭", font=STYLE.MSYHFontBigger10, fg="white",
                                      bg=STYLE.Button_Close_Back,
                                      relief=tk.GROOVE)
        self.DeleteButton.place(relx=0.36, rely=0.86, anchor=tk.NW, relwidth=0.28, relheight=0.1)

        # =========================高级按钮
        self.AdvancedButton = tk.Button(self.frame, text="高级", font=STYLE.MSYHFontBigger10, fg="white",
                                        bg=STYLE.Button_Adv_Back,
                                        relief=tk.GROOVE)
        self.AdvancedButton.place(relx=0.67, rely=0.86, anchor=tk.NW, relwidth=0.28, relheight=0.1)
        self.AdvancedButtonClicked = False

        # =========================高级管理面板
        self.AdvancedFrameSize = (self.frame_size[0] * 2, self.frame_size[1])
        self.AdvancedFrame = tk.Frame(self.root, bg=STYLE.ViewBG, width=self.AdvancedFrameSize[0],
                                      height=self.AdvancedFrameSize[1],
                                      highlightbackground=self.frame_border_color, highlightthickness=2)
        self.AdvancedFrameExsit = False  # 高级面板是否存在
        self.AdvancedFrameOutOfWindow = False  # 高级面板是否超出窗口
        # +++++++++++++++++ frame初始化后需要更新数值
        self.frame.update()
        # +++++++++++++++++
        self.AdvancedFrame_OutOfWindow()
        # -------------------------高级管理面板-网卡全称
        if self.is_physical:
            self.AdvancedCardNameLabel = tk.Label(self.AdvancedFrame, text="[物理]" + self.NetworkCardName,
                                                  font=STYLE.DefFontBigger12, fg="white", bg=STYLE.NetworkCardNamePCIBG)
        else:
            self.AdvancedCardNameLabel = tk.Label(self.AdvancedFrame, text="[虚拟]" + self.NetworkCardName,
                                                  font=STYLE.DefFontBigger12, fg="white",
                                                  bg=STYLE.NetworkCardNameVirtualBG)
        self.AdvancedCardNameLabel.place(relx=0, rely=0, anchor=tk.NW, relwidth=1)

        # -------------------------高级管理面板-所有地址
        self.Multi_IPMask_Label = tk.Label(self.AdvancedFrame, text="多地址:", font=self.font, fg="black")
        self.Multi_IPMask_Label.place(relx=0.02, rely=0.14, anchor=tk.NW)

        self.Multi_IPMask_ListFrame = ListFrame(self.AdvancedFrame, frame_size=(0.44, 0.22), place_set=(0.02, 0.21),
                                                border_color=self.frame_border_color)
        for i in range(0, len(self.IpAddrs)):  # 将IP地址和掩码加入多地址列表
            num = networkCtl.MaskToNum(self.NetMasks[i])
            self.Multi_IPMask_ListFrame.AddItem(f"{self.IpAddrs[i]}/{num}")

        # 新地址输入框
        self.New_IPMask_Entry = tk.Entry(self.AdvancedFrame, font=self.font, bg=STYLE.EntryBG, fg="black",
                                         justify=tk.LEFT)
        self.New_IPMask_Entry.place(relx=0.02, rely=0.45, anchor=tk.NW, relwidth=0.32, relheight=0.07)

        # 新地址添加按钮
        self.New_IPMask_AddButton = tk.Button(self.AdvancedFrame, text="+", font=STYLE.MSYHFont, fg="white",
                                              bg=STYLE.Button_Yes_Back, relief=tk.GROOVE)
        self.New_IPMask_AddButton.place(relx=0.35, rely=0.45, anchor=tk.NW, relheight=0.07)

        # 所选地址删除按钮
        self.IPMask_DelButton = tk.Button(self.AdvancedFrame, text="-", font=STYLE.MSYHFont, fg="white",
                                          bg=STYLE.Button_Close_Back, relief=tk.GROOVE)
        self.IPMask_DelButton.place(relx=0.42, rely=0.45, anchor=tk.NW, relheight=0.07)
        self.IPMask_DelButton.config(state="disabled")  # 初始时禁用删除按钮
        # ---------------------------------------------

        # -------------------------高级管理面板-多网关
        self.Multi_Gateway_Label = tk.Label(self.AdvancedFrame, text="多网关:", font=self.font, fg="black")
        self.Multi_Gateway_Label.place(relx=0.54, rely=0.14, anchor=tk.NW)

        self.Multi_Gateway_ListFrame = ListFrame(self.AdvancedFrame, frame_size=(0.44, 0.22), place_set=(0.54, 0.21),
                                                 border_color=self.frame_border_color)
        for i in range(0, len(self.GateWays)):  # 将网关加入多网关列表
            self.Multi_Gateway_ListFrame.AddItem(self.GateWays[i])

        # 新网关输入框
        self.New_Gateway_Entry = tk.Entry(self.AdvancedFrame, font=self.font, bg=STYLE.EntryBG, fg="black",
                                          justify=tk.LEFT)
        self.New_Gateway_Entry.place(relx=0.54, rely=0.45, anchor=tk.NW, relwidth=0.32, relheight=0.07)

        # 新网关添加按钮
        self.New_Gateway_AddButton = tk.Button(self.AdvancedFrame, text="+", font=STYLE.MSYHFont, fg="white",
                                               bg=STYLE.Button_Yes_Back, relief=tk.GROOVE)
        self.New_Gateway_AddButton.place(relx=0.87, rely=0.45, anchor=tk.NW, relheight=0.07)

        # 所选网关删除按钮
        self.Gateway_DelButton = tk.Button(self.AdvancedFrame, text="-", font=STYLE.MSYHFont, fg="white",
                                           bg=STYLE.Button_Close_Back, relief=tk.GROOVE)
        self.Gateway_DelButton.place(relx=0.94, rely=0.45, anchor=tk.NW, relheight=0.07)
        self.Gateway_DelButton.config(state="disabled")  # 初始时禁用删除按钮
        # ---------------------------------------------

        # -------------------------高级管理面板-多DNS
        self.Multi_DNS_Label = tk.Label(self.AdvancedFrame, text="多DNS:", font=self.font, fg="black")
        self.Multi_DNS_Label.place(relx=0.02, rely=0.57, anchor=tk.NW)

        self.Multi_DNS_ListFrame = ListFrame(self.AdvancedFrame, frame_size=(0.32, 0.23), place_set=(0.02, 0.64),
                                             border_color=self.frame_border_color)
        for i in range(0, len(self.DNSs)):  # 将DNS加入多DNS列表
            self.Multi_DNS_ListFrame.AddItem(self.DNSs[i])

        # 新DNS输入框
        self.New_DNS_Entry = tk.Entry(self.AdvancedFrame, font=self.font, bg=STYLE.EntryBG, fg="black", justify=tk.LEFT)
        self.New_DNS_Entry.place(relx=0.02, rely=0.89, anchor=tk.NW, relwidth=0.32, relheight=0.07)

        # 新DNS添加按钮
        self.New_DNS_AddButton = tk.Button(self.AdvancedFrame, text="+", font=STYLE.MSYHFont, fg="white",
                                           bg=STYLE.Button_Yes_Back, relief=tk.GROOVE)
        self.New_DNS_AddButton.place(relx=0.35, rely=0.89, anchor=tk.NW, relheight=0.07)

        # 所选DNS删除按钮
        self.DNS_DelButton = tk.Button(self.AdvancedFrame, text="-", font=STYLE.MSYHFont, fg="white",
                                       bg=STYLE.Button_Close_Back, relief=tk.GROOVE)
        self.DNS_DelButton.place(relx=0.42, rely=0.89, anchor=tk.NW, relheight=0.07)
        self.DNS_DelButton.config(state="disabled")  # 初始时禁用删除按钮

        # 所选DNS优先级上升按钮
        self.DNS_UpButton = tk.Button(self.AdvancedFrame, text="上升", font=STYLE.MSYHFont, fg="white",
                                      bg=STYLE.Button_Yes_Back, relief=tk.GROOVE)
        self.DNS_UpButton.place(relx=0.35, rely=0.66, anchor=tk.NW, relwidth=0.12, relheight=0.08)
        self.DNS_UpButton.config(state="disabled")  # 初始时禁用上升按钮

        # 所选DNS优先级下降按钮
        self.DNS_DownButton = tk.Button(self.AdvancedFrame, text="下降", font=STYLE.MSYHFont, fg="white",
                                        bg=STYLE.Button_Yes_Back, relief=tk.GROOVE)
        self.DNS_DownButton.place(relx=0.35, rely=0.76, anchor=tk.NW, relwidth=0.12, relheight=0.08)
        self.DNS_DownButton.config(state="disabled")  # 初始时禁用下降按钮
        # ---------------------------------------------

        # -------------------------高级管理面板-其他设置label
        self.OtherSettingLabel = tk.Label(self.AdvancedFrame, text="其他设置:", font=self.font, fg="black")
        self.OtherSettingLabel.place(relx=0.54, rely=0.59, anchor=tk.NW)

        # -------------------------高级管理面板-DHCP启用勾选框
        self.DHCPVar = tk.IntVar()  # 说明:Checkbutton的variable参数需要一个IntVar类型才能保证实例勾选是独立的
        self.DHCPEnableCheckButton = tk.Checkbutton(self.AdvancedFrame, text="DHCP", font=self.font, fg="black",
                                                    variable=self.DHCPVar)
        if self.DhcpEnable == 1:
            self.DHCPEnableCheckButton.select()
        else:
            self.DHCPEnableCheckButton.deselect()
        self.DHCPEnableCheckButton.place(relx=0.54, rely=0.66, anchor=tk.NW)
        # ---------------------------------------------

        # -------------------------高级管理面板-重置为上一次保存的设置按钮
        self.ResetButton = tk.Button(self.AdvancedFrame, text="重置更改", font=STYLE.MSYHFontBigger10, fg="white",
                                     bg=STYLE.Button_Adv_Back,
                                     relief=tk.GROOVE)
        self.ResetButton.place(relx=0.54, rely=0.88, anchor=tk.NW, relwidth=0.43, relheight=0.08)

        # -------------------------提示网卡未连接的Label
        self.ConDownLabel = tk.Label(self.frame, text="网卡未连接或禁用", font=STYLE.DefFontBigger12, fg="red",
                                     bg="white", borderwidth=1, relief=tk.SOLID)
        self.ConDownLabel.place_forget()

        # -------------------------提示配置中的Label
        self.ConfigingLabel = tk.Label(self.frame, text="配置中...", font=STYLE.MSYHFontBigger10, fg="black",
                                       bg="white", borderwidth=1, relief=tk.SOLID)

        # =========================保存按钮事件绑定
        self.SaveButton.bind("<Enter>", self.mouse_enter_save)  # 绑定鼠标划入事件
        self.SaveButton.bind("<Leave>", self.mouse_leave_save)  # 绑定鼠标划出事件
        self.SaveButton.bind("<Button-1>", self.save_card)  # 绑定鼠标左键点击事件

        # =========================关闭按钮事件绑定
        self.DeleteButton.bind("<Enter>", self.mouse_enter_del)  # 绑定鼠标划入事件
        self.DeleteButton.bind("<Leave>", self.mouse_leave_del)  # 绑定鼠标划出事件
        self.DeleteButton.bind("<Button-1>", self.delete_card)  # 绑定鼠标左键点击事件

        # =========================高级按钮事件绑定
        self.AdvancedButton.bind("<Enter>", self.mouse_enter_adv)  # 绑定鼠标划入事件
        self.AdvancedButton.bind("<Leave>", self.mouse_leave_adv)  # 绑定鼠标划出事件
        self.AdvancedButton.bind("<Button-1>", self.advanced_card)  # 绑定鼠标左键点击事件

        # =========================高级面板事件绑定
        self.AdvancedFrame.bind("<Enter>", self.mouse_enter_AdvancedFrame)  # 绑定鼠标划入事件
        self.AdvancedFrame.bind("<Leave>", self.mouse_leave_AdvancedFrame)  # 绑定鼠标划出事件
        self.AdvancedFrame.bind("<Button-1>", self.click_AdvancedFrame)  # 绑定鼠标左键点击事件

        # =========================高级面板-多地址事件绑定
        self.Multi_IPMask_ListFrame.ListBox.bind("<Button-1>", self.Multi_IPMask_ListFrame_Click)
        self.Multi_IPMask_ListFrame.ListBox.bind("<<ListboxSelect>>", self.Multi_IPMask_ListFrame_Select)  # 绑定选择事件
        self.Multi_IPMask_ListFrame.ListBox.bind("<FocusOut>", self.Multi_IPMask_ListFrame_FocusOut)  # 绑定失去焦点事件
        self.New_IPMask_AddButton.bind("<Button-1>", self.New_IPMask_Add)
        self.IPMask_DelButton.bind("<Button-1>", self.IPMask_Del)

        # =========================高级面板-多网关事件绑定
        self.Multi_Gateway_ListFrame.ListBox.bind("<Button-1>", self.Multi_Gateway_ListFrame_Click)
        self.Multi_Gateway_ListFrame.ListBox.bind("<<ListboxSelect>>", self.Multi_Gateway_ListFrame_Select)
        self.Multi_Gateway_ListFrame.ListBox.bind("<FocusOut>", self.Multi_Gateway_ListFrame_FocusOut)
        self.New_Gateway_AddButton.bind("<Button-1>", self.New_Gateway_Add)
        self.Gateway_DelButton.bind("<Button-1>", self.Gateway_Del)

        # =========================高级面板-多DNS事件绑定
        self.Multi_DNS_ListFrame.ListBox.bind("<Button-1>", self.Multi_DNS_ListFrame_Click)
        self.Multi_DNS_ListFrame.ListBox.bind("<<ListboxSelect>>", self.Multi_DNS_ListFrame_Select)
        self.Multi_DNS_ListFrame.ListBox.bind("<FocusOut>", self.Multi_DNS_ListFrame_FocusOut)
        self.New_DNS_AddButton.bind("<Button-1>", self.New_DNS_Add)
        self.DNS_DelButton.bind("<Button-1>", self.DNS_Del)
        self.DNS_UpButton.bind("<Button-1>", self.DNS_Up)
        self.DNS_DownButton.bind("<Button-1>", self.DNS_Down)

        # =========================高级面板-重置按钮事件绑定
        self.ResetButton.bind("<Button-1>", self.reset_click)  # 绑定鼠标左键点击事件
        self.ResetButton.bind("<Enter>", self.reset_enter)  # 绑定鼠标划入事件
        self.ResetButton.bind("<Leave>", self.reset_leave)  # 绑定鼠标划出事件

        # =========================刷新模块/回调函数管理区
        self.flash_chart()  # 刷新折线图
        self.start()  # 获取网卡流量信息线程启动

    def run(self):  # 线程运行,每秒获取一次网卡流量信息
        while True:
            if if_connection.Card_Connected(self.NetworkCardName):
                self.update_DataQueue(update_queue=self.RecvDataQueue,
                                      new_data=(if_connection.Bytes_Recv_From_PowerUP(
                                          self.NetworkCardName) - self.RecvPacks_t1))
                self.update_DataQueue(update_queue=self.SendDataQueue,
                                      new_data=(if_connection.Bytes_Send_From_PowerUP(
                                          self.NetworkCardName) - self.SendPacks_t1))
                self.RecvPacks_t1 = if_connection.Bytes_Recv_From_PowerUP(self.NetworkCardName)
                self.SendPacks_t1 = if_connection.Bytes_Send_From_PowerUP(self.NetworkCardName)

            if self.msgout and self.msgnum < 5:
                self.ConfigingLabel.config(text=self.msgdata)
                self.ConfigingLabel.place(relx=0.5, rely=0.33, anchor=tk.CENTER)
                self.msgnum += 1
            elif self.msgnum >= 5:
                self.ConfigingLabel.place_forget()
                self.ConfigingLabel.config(text="配置中...")
                self.msgout = False
                self.msgnum = 0
            elif self.msgout == False:
                pass

            time.sleep(1)  # 暂停1秒

    def mouse_enter_save(self, event):  # 鼠标划过保存组件响应
        self.SaveButton.config(bg=STYLE.Button_Yes_Fore)

    def mouse_leave_save(self, event):  # 鼠标离开保存组件响应
        self.SaveButton.config(bg=STYLE.Button_Yes_Back)

    def save_card(self, event):  # 保存网卡配置信息
        self.ConfigingLabel.place(relx=0.5, rely=0.33, anchor=tk.CENTER, relheight=0.1)
        # 保存线程
        r = Thread_pool.submit(self.save_config)
        # self.save_config()

        self.SaveButton.config(state=tk.NORMAL)
        # self.ConfigingLabel.place_forget() # 隐藏"配置中"标签
        self.frame.after(1500, self.reset_click, 1)
        self.frame.after(1550, self.ConfigingLabel.place_forget)
        # self.frame.after(1600, self.save_config_result)

    def save_config(self):  # 保存配置
        print("保存开始执行")
        if self.DhcpEnable == 1 and self.DHCPVar.get() == 0:
            networkCtl.Set_DHCP_Netsh(self.NetworkCardName)
        elif self.DhcpEnable == 1:  # 如果是DHCP模式,则不保存
            print("DHCP无法保存")
            # messageCtl.Pop_Top_message(self.root, type=messageCtl.MSG_TYPE.ERR, msgstr="DHCP无法保存")
            return
        else:
            networkCtl.Set_DHCP_Netsh(self.NetworkCardName)

        networkCtl.Set_IP_Netsh(self.NetworkCardName, self.IpAddrs, self.NetMasks, self.GateWays)
        networkCtl.Set_DNS_Netsh(self.NetworkCardName, self.DNSs)

        print("保存执行完成")

        messageCtl.Pop_Top_message(self.root, type=messageCtl.MSG_TYPE.SUC, msgstr="成功", TTL=3000)

        # self.result = []
        # if self.DhcpEnable == 1 and self.DHCPVar.get() == 0:
        #     self.result.append(True)  # 变更
        # elif self.DhcpEnable == 1:  # 如果是DHCP模式,则不保存
        #     # messageCtl.Pop_Top_message(self.root, type=messageCtl.MSG_TYPE.ERR, msgstr="DHCP无法保存")
        #     # self.ConfigingLabel.place_forget() # 隐藏"配置中"标签
        #     self.result.append(False)
        #     return
        # else:
        #     self.result.append(True)
        #
        # # 获取dhcp钩选框状态
        # if self.DHCPVar.get() == 1:
        #     self.result.append(networkCtl.Set_DHCP_Netsh(self.NetworkCardName))
        # else:
        #     self.result.append(networkCtl.Set_DHCP_WMI(self.networkcard[self.NetworkCardName]["Description"], False))
        #
        # if networkCtl.Set_IP_WMI(self.networkcard[self.NetworkCardName]["Description"], self.IpAddrs, self.NetMasks,
        #                          self.GateWays) == False:
        #     # messageCtl.Pop_Top_message(self.root, type=messageCtl.MSG_TYPE.ERR, msgstr="IP或网关设置失败")
        #     # self.reset_click(1)
        #     # self.ConfigingLabel.place_forget() # 隐藏"配置中"标签
        #
        #     self.result.append(False)
        # else:
        #     self.result.append(True)
        #
        # # 深拷贝DNSs,因为DNSs可能会被多次修改
        # DNSs = copy.deepcopy(self.DNSs)
        # r = networkCtl.Set_DNS_WMI(self.networkcard[self.NetworkCardName]["Description"], DNSs)
        # self.result.append(r)
        # if r[0] == 84:
        #     messageCtl.Pop_Top_message(self.root, type=messageCtl.MSG_TYPE.WARN,
        #                                msgstr="DNS警告:WMI返回值84\n根据微软说明,网络未连接时调试DNS配置会失败",
        #                                TTL=5000)
        # elif r[0] == False:
        #     messageCtl.Pop_Top_message(self.root, type=messageCtl.MSG_TYPE.ERR, msgstr=f"DNS设置失败\n{r[1]}", TTL=5000)
        # self.reset_click(1)
        # self.ConfigingLabel.place_forget() # 隐藏"配置中"标签

        # messageCtl.Pop_Top_message(self.root, type=messageCtl.MSG_TYPE.SUC, msgstr="成功\n[testting]")

    # 根据save_config返回的结果,弹出提示框(原本使用wmi控制配置时设计使用，现弃用)
    def save_config_result(self):
        # print(self.result)
        self.msgout = True
        sdata = ""  # 成功
        fdata = ""  # 失败
        wdata = ""  # 警告
        if self.result[0] == False:
            fdata = "DHCP无法保存\n请尝试先关闭DHCP\n"
        if len(self.result) <= 1:
            sdata = "成功:" + sdata
            fdata = "失败:" + fdata
            wdata = "警告:" + wdata

            self.msgdata = sdata + "\n" + fdata + "\n" + wdata
            return

        if self.result[1] == False:
            fdata += "DHCP;"
        else:
            sdata += "DHCP;"
        if self.result[2] == False:
            fdata += "IP或网关;"
        else:
            sdata += "IP或网关;"
        if self.result[3][0] == 84:
            wdata += "DNS(84)"
        elif self.result[3][0] == False:
            fdata += "DNS;"
        else:
            sdata += "DNS;"

        sdata = "成功:" + sdata
        fdata = "失败:" + fdata
        wdata = "警告:" + wdata

        self.msgdata = sdata + "\n" + fdata + "\n" + wdata

    def mouse_enter_del(self, event):  # 鼠标划过删除组件响应
        self.DeleteButton.config(bg=STYLE.Button_Close_Fore)

    def mouse_leave_del(self, event):  # 鼠标离开删除组件响应
        self.DeleteButton.config(bg=STYLE.Button_Close_Back)

    def delete_card(self, event):  # 删除整个组件
        # self.frame.after_cancel(self.after_id)
        if self.AdvancedFrameExsit == True:
            self.AdvancedFrame.destroy()
        frames.DeleteNetworkFromNetFrame(self.NetworkCardName, RootMenu=self.networkmenuquote)
        self.frame.destroy()
        del self

    def mouse_enter_adv(self, event):  # 鼠标划过高级组件响应
        self.AdvancedButton.config(bg=STYLE.Button_Adv_Fore)

    def mouse_leave_adv(self, event):  # 鼠标离开高级组件响应
        self.AdvancedButton.config(bg=STYLE.Button_Adv_Back)

    def advanced_card(self, event):  # 高级设置
        self.AdvancedFrame_OutOfWindow()
        self.AdvancedButtonClicked = not self.AdvancedButtonClicked
        if self.AdvancedButtonClicked == True:
            if self.AdvancedFrameOutOfWindow == False:
                self.AdvancedFrame.place(anchor=tk.NW, x=self.frame.winfo_x() + self.frame.winfo_width() + 5,
                                         y=self.place_set[1])
            else:
                self.AdvancedFrame.place(anchor=tk.NW, x=self.frame.winfo_x() - self.AdvancedFrameSize[0] - 5,
                                         y=self.place_set[1])
            self.AdvancedFrameExsit = True
            self.AdvancedFrame.lift()
        else:
            self.AdvancedFrame.place_forget()
            self.AdvancedFrameExsit = False

    def AdvancedFrame_OutOfWindow(self):  # 判断高级面板是否超出窗口
        if self.frame.winfo_x() + self.AdvancedFrameSize[0] + self.frame.winfo_width() + 10 > self.root.winfo_width():
            self.AdvancedFrameOutOfWindow = True

        else:
            self.AdvancedFrameOutOfWindow = False

    def mouse_motion_delay(self):  # 由于存在高级面板需要变化，所以重写了父类的鼠标动画函数，增加了高级面板的动画调用
        i = 2  # 速率系数，越大动画速度越快。建议设置为可整除的数，建议为2的倍数
        dx = i  # 每次重绘x轴移动值
        dy = (self.frame_size[1] / self.frame_size[0]) * i / 2  # 每次重绘y轴移动值

        # 鼠标进入frame时,frame的大小逐渐增大,且frame的位置向左上角移动
        if self.frame.winfo_width() <= self.frame_size[0] + 10 and self.mouse_exit == False:
            self.frame.place(x=self.frame.winfo_x() - (dx * 0.5), y=self.frame.winfo_y() - (dy * 0.5))
            self.frame.configure(width=self.frame.winfo_width() + dx,
                                 height=self.frame.winfo_height() + dy)

            self.frame.after(30, self.mouse_motion_delay)  # 延时重绘

            self.AdvancedFrame_motion(is_expand=True, i=i / 2)  # 与父类相比，增加高级面板动画

        # 鼠标离开frame时,frame的大小逐渐减小,且frame的位置向右下角移动
        elif self.mouse_exit == True and self.frame.winfo_width() >= self.frame_size[0]:
            self.frame.place(x=self.frame.winfo_x() + (dx * 0.5), y=self.frame.winfo_y() + (dy * 0.5))
            self.frame.configure(width=self.frame.winfo_width() - dx,
                                 height=self.frame.winfo_height() - dy)
            self.frame.after(30, self.mouse_motion_delay)  # 延时重绘

            self.AdvancedFrame_motion(is_expand=False, i=i / 2)  # 与父类相比，增加高级面板动画

    def AdvancedFrame_motion(self, is_expand=False, i=2):  # 高级面板运动
        if self.AdvancedFrameExsit == True:  # 判断高级面板是否存在
            if self.AdvancedFrameOutOfWindow == False:  # 判断高级面板是否超出窗口，如超出窗口运动时向左
                if is_expand == True:  # 判断frame是否在扩大
                    self.AdvancedFrame.place(anchor=tk.NW, x=self.AdvancedFrame.winfo_x() + i,
                                             y=self.place_set[1])
                else:  # 判断frame在缩小
                    self.AdvancedFrame.place(anchor=tk.NW, x=self.AdvancedFrame.winfo_x() - i,
                                             y=self.place_set[1])
            else:
                if is_expand == True:
                    self.AdvancedFrame.place(anchor=tk.NW, x=self.AdvancedFrame.winfo_x() - i,
                                             y=self.place_set[1])
                else:
                    self.AdvancedFrame.place(anchor=tk.NW, x=self.AdvancedFrame.winfo_x() + i,
                                             y=self.place_set[1])

    def mouse_enter_AdvancedFrame(self, event):  # 鼠标划过高级面板组件响应
        self.AdvancedFrame.config(
            highlightbackground=STYLE.NetworkAdvMouseEnter)

    def mouse_leave_AdvancedFrame(self, event):  # 鼠标离开高级面板组件响应
        self.AdvancedFrame.config(
            highlightbackground=self.frame_border_color)

    def click_AdvancedFrame(self, event):  # 鼠标左键点击高级面板组件响应
        self.AdvancedFrame.lift()

    def draw_chart(self):  # 绘制折线图
        self.canvas.delete('all')

        RecvDataList = list(self.RecvDataQueue.queue)  # 获取队列中的数据
        RecvMaxData = max(RecvDataList)  # 获取最大值
        if RecvMaxData == 0:  # 如果最大值为0,则将最大值置为1,防止除0错误
            RecvMaxData = 1

        SendDataList = list(self.SendDataQueue.queue)
        SendMaxData = max(SendDataList)  # 获取最大值
        if SendMaxData == 0:  # 如果最大值为0,则将最大值置为1,防止除0错误
            SendMaxData = 1

        self.draw_data(RecvMaxData, RecvDataList, True)
        self.draw_data(SendMaxData, SendDataList, False)

    def draw_data(self, maxdata, datalist, is_Recv):
        normalized_data = [x / maxdata * (self.canvas_size[1]) for x in datalist]
        for i in range(1, len(normalized_data)):
            y1 = self.canvas_size[1] - normalized_data[i - 1] + 4
            y2 = self.canvas_size[1] - normalized_data[i] + 4
            x1 = (i - 1) * self.canvas.winfo_width() / 9.5
            x2 = i * self.canvas.winfo_width() / 9.5

            if is_Recv:
                color = '#{:02x}{:02x}{:02x}'.format(15 + 3 * i, 255 - 8 * i, 160 - i * 9)
                outline = "#0a552b"
            else:
                color = '#{:02x}{:02x}{:02x}'.format(70 + 7 * i, 230 - 8 * i, 255)
                outline = "blue"

            self.canvas.create_line(x1, y1, x2, y2, fill=color, width=1)
            self.canvas.create_oval(x2 - 1, y2 - 1, x2 + 1, y2 + 1, fill=color, outline=outline)

    def update_DataQueue(self, update_queue: queue, new_data):  # 更新流量速率数据队列
        if update_queue.full():
            update_queue.get()
        update_queue.put(new_data)

    # 将所有组件的颜色变暗,用于提示网卡未连接
    def set_all_widget_color_dark(self):
        self.canvas.configure(bg=STYLE.DisableCanvasDark)
        self.frame.config(bg=STYLE.DisableDark)
        self.SpeedSendLabel.config(bg=STYLE.DisableDark)
        self.SpeedRecvLabel.config(bg=STYLE.DisableDark)
        self.IPAddressLabel.config(bg=STYLE.DisableDark)
        # self.IPAddressEntry.config(bg=STYLE.DisableDark)
        # self.GatewayAddressEntry.config(bg=STYLE.DisableDark)
        self.GatewayAddressLabel.config(bg=STYLE.DisableDark)
        # self.DNSAddressEntry.config(bg=STYLE.DisableDark)
        self.DNSAddressLabel.config(bg=STYLE.DisableDark)

    # 所有组件恢复原来的颜色
    def set_all_widget_color_normal(self):
        self.canvas.configure(bg=STYLE.NetworkCavansBG)
        self.frame.config(bg=STYLE.ViewBG)
        self.SpeedSendLabel.config(bg=STYLE.ViewBG)
        self.SpeedRecvLabel.config(bg=STYLE.ViewBG)
        self.IPAddressLabel.config(bg=STYLE.ViewBG)
        # self.IPAddressEntry.config(bg="#e6e6e6")
        # self.GatewayAddressEntry.config(bg="#e6e6e6")
        self.GatewayAddressLabel.config(bg=STYLE.ViewBG)
        # self.DNSAddressEntry.config(bg="#e6e6e6")
        self.DNSAddressLabel.config(bg=STYLE.ViewBG)

    # 隐藏save按钮和advanced按钮
    def hide_save_and_advanced_button(self):
        self.SaveButton.place_forget()
        self.AdvancedButton.place_forget()

    # 显示save按钮和advanced按钮
    def show_save_and_advanced_button(self):
        self.SaveButton.place(relx=0.05, rely=0.86, anchor=tk.NW, relwidth=0.25)
        self.AdvancedButton.place(relx=0.69, rely=0.86, anchor=tk.NW, relwidth=0.25)

    def flash_chart(self):  # 刷新折线图

        if if_connection.Card_Connected(self.NetworkCardName):  # 如果网卡连接状态发生变化
            if not Thread_pool._shutdown:  # 如果线程池没有关闭
                Thread_pool.submit(self.draw_chart)  # 提交线程池

            self.SpeedSendLabel.config(
                text="up:" + str(if_connection.format_speed(self.SendDataQueue.queue[-1])))  # 更新上行速率
            self.SpeedRecvLabel.config(
                text="dw:" + str(if_connection.format_speed(self.RecvDataQueue.queue[-1])))  # 更新下行速率

            self.set_all_widget_color_normal()
            self.ConDownLabel.place_forget()
            # self.show_save_and_advanced_button()
        else:
            self.set_all_widget_color_dark()
            self.ConDownLabel.place(relx=0.5, rely=0.33, anchor=tk.CENTER)
            # self.hide_save_and_advanced_button()

        self.after_id = self.frame.after(1000, self.flash_chart)  # 1s后再次刷新折线图

    # 高级面板里的事件绑定
    # 多地址
    def Multi_IPMask_ListFrame_Click(self, event):
        self.only_one_select = 1
        # print("Multi_IPMask_ListFrame_Click")

    def Multi_IPMask_ListFrame_Select(self, event):
        if self.only_one_select != 1:
            return
        self.IPMask_DelButton.config(state="normal")
        # print("Multi_IPMask_ListFrame_Select!")

    def Multi_IPMask_ListFrame_FocusOut(self, event):
        self.IPMask_DelButton.config(state="disabled")
        # print("Multi_IPMask_ListFrame_FocusOut!!")

    def New_IPMask_Add(self, event):
        # 从输入框获取新地址
        new_addr = self.New_IPMask_Entry.get()

        # 正则表达式验证地址合法性
        if re.match(r"^(?:[0-9]{1,3}\.){3}[0-9]{1,3}/[0-9]{1,2}$", new_addr):
            self.Multi_IPMask_ListFrame.AddItem(new_addr)
            self.New_IPMask_Entry.delete(0, "end")
        else:
            messageCtl.Pop_Top_message(self.root, type=messageCtl.MSG_TYPE.ERR,
                                       msgstr="地址格式错误\n应该如192.168.1.1/24")
            self.New_IPMask_Entry.delete(0, "end")
            return

        # 将新地址保存入列表
        self.IpAddrs.append(new_addr.split("/")[0])
        self.NetMasks.append(networkCtl.NumToMask(int(new_addr.split("/")[1])))

    def IPMask_Del(self, event):
        # 获取所选地址的索引
        index = self.Multi_IPMask_ListFrame.ListBox.curselection()

        # 删除所选地址
        self.Multi_IPMask_ListFrame.DelItem(index[0])
        self.IpAddrs.pop(index[0])
        self.NetMasks.pop(index[0])

        # 禁用删除按钮
        self.IPMask_DelButton.config(state="disabled")
        # print("IPMask_Del!!!")

    def Multi_Gateway_ListFrame_Click(self, event):
        self.only_one_select = 2
        # print("Multi_Gateway_ListFrame_Click")

    def Multi_Gateway_ListFrame_Select(self, event):
        if self.only_one_select != 2:
            return
        self.Gateway_DelButton.config(state="normal")
        # print("Multi_Gateway_ListFrame_Select!")

    def Multi_Gateway_ListFrame_FocusOut(self, event):
        self.Gateway_DelButton.config(state="disabled")
        # print("Multi_Gateway_ListFrame_FocusOut!!")

    def New_Gateway_Add(self, event):
        # 从输入框获取新网关
        new_gateway = self.New_Gateway_Entry.get()

        # 正则表达式验证网关合法性
        if re.match(r"^(?:[0-9]{1,3}\.){3}[0-9]{1,3}$", new_gateway):
            self.Multi_Gateway_ListFrame.AddItem(new_gateway)
            self.New_Gateway_Entry.delete(0, "end")
        else:
            messageCtl.Pop_Top_message(self.root, type=messageCtl.MSG_TYPE.ERR,
                                       msgstr="网关格式错误\n应该如192.168.1.1")
            self.New_Gateway_Entry.delete(0, "end")
            return

        # 将新网关保存入列表
        self.GateWays.append(new_gateway)

    def Gateway_Del(self, event):
        # 获取所选网关的索引
        index = self.Multi_Gateway_ListFrame.ListBox.curselection()

        # 删除所选网关
        self.Multi_Gateway_ListFrame.DelItem(index[0])
        self.GateWays.pop(index[0])

        # 禁用删除按钮
        self.Gateway_DelButton.config(state="disabled")
        # print("Gateway_Del!!!")

    def Multi_DNS_ListFrame_Click(self, event):
        self.only_one_select = 3
        # print("Multi_DNS_ListFrame_Click")

    def Multi_DNS_ListFrame_Select(self, event):
        if self.only_one_select != 3:
            return
        self.DNS_DelButton.config(state="normal")
        self.DNS_UpButton.config(state="normal")
        self.DNS_DownButton.config(state="normal")
        # print("Multi_DNS_ListFrame_Select!")

    def Multi_DNS_ListFrame_FocusOut(self, event):
        self.DNS_DelButton.config(state="disabled")
        self.DNS_UpButton.config(state="disabled")
        self.DNS_DownButton.config(state="disabled")
        # print("Multi_DNS_ListFrame_FocusOut!!")

    def New_DNS_Add(self, event):
        # 从输入框获取新DNS
        new_dns = self.New_DNS_Entry.get()

        # 正则表达式验证DNS合法性
        if re.match(r"^(?:[0-9]{1,3}\.){3}[0-9]{1,3}$", new_dns):
            self.Multi_DNS_ListFrame.AddItem(new_dns)
            self.New_DNS_Entry.delete(0, "end")
        else:
            messageCtl.Pop_Top_message(self.root, type=messageCtl.MSG_TYPE.ERR,
                                       msgstr="DNS格式错误\n应该如114.114.114.114")
            self.New_DNS_Entry.delete(0, "end")
            return

        # 将新DNS保存入列表
        self.DNSs.append(new_dns)

    def DNS_Del(self, event):
        # 获取所选DNS的索引
        index = self.Multi_DNS_ListFrame.ListBox.curselection()

        # 删除所选DNS
        self.Multi_DNS_ListFrame.DelItem(index[0])
        self.DNSs.pop(index[0])

        # 禁用删除按钮
        self.DNS_DelButton.config(state="disabled")
        self.DNS_UpButton.config(state="disabled")
        self.DNS_DownButton.config(state="disabled")
        # print("DNS_Del!!!")

    def DNS_Up(self, event):
        # print("-----\n",self.DNSs,end=" ") # 打印调试信息

        # 获取所选DNS的索引
        index = self.Multi_DNS_ListFrame.ListBox.curselection()
        if index[0] == 0:
            return

        # print(self.DNSs[index[0]]) # 打印调试信息

        tmp = self.DNSs[index[0]]
        self.DNSs[index[0]] = self.DNSs[index[0] - 1]
        self.DNSs[index[0] - 1] = tmp

        self.Multi_DNS_ListFrame.ListBox.delete(index[0] - 1)
        self.Multi_DNS_ListFrame.ListBox.insert(index[0], self.DNSs[index[0]])
        self.Multi_DNS_ListFrame.ListBox.select_set(index[0] - 1)

        # print("",self.DNSs,self.DNSs[index[0]],"\n-----") # 打印调试信息

    def DNS_Down(self, event):
        # print("-----\n",self.DNSs,end=" ") # 打印调试信息

        # 获取所选DNS的索引
        index = self.Multi_DNS_ListFrame.ListBox.curselection()
        if index[0] == len(self.DNSs) - 1:
            return

        # print(self.DNSs[index[0]]) # 打印调试信息

        tmp = self.DNSs[index[0]]
        self.DNSs[index[0]] = self.DNSs[index[0] + 1]
        self.DNSs[index[0] + 1] = tmp
        self.Multi_DNS_ListFrame.ListBox.delete(index[0] + 1)
        self.Multi_DNS_ListFrame.ListBox.insert(index[0], self.DNSs[index[0]])
        self.Multi_DNS_ListFrame.ListBox.select_set(index[0] + 1)

        # print("",self.DNSs,self.DNSs[index[0]],"\n-----") # 打印调试信息

    def reset_click(self, event):
        NetData = networkCtl.Get_Network_Info_By_AllCard()
        NetData = NetData[self.NetworkCardName]
        self.networkcard[self.NetworkCardName] = NetData
        self.Update_all()

    # 全量更新与重置,当前用于重置未保存的修改(类似构造函数里的操作),基于self.networkcard重置
    def Update_all(self):

        self.IpAddrs = []
        self.NetMasks = []
        self.GateWays = []
        self.DNSs = []

        # 重置DHCP信息
        self.DhcpEnable = 2  # 是否启用DHCP,0未启用,1启用,2未知
        if "EnableDHCP" in self.networkcard[self.NetworkCardName]["cfg"]:
            if self.networkcard[self.NetworkCardName]["cfg"]["EnableDHCP"] == 1:
                self.DhcpEnable = 1
            elif self.networkcard[self.NetworkCardName]["cfg"]["EnableDHCP"] == 0:
                self.DhcpEnable = 0

        # 将ip地址和掩码从dhcp配置或静态配置梳理后加入IpAddrs和NetMasks
        if self.DhcpEnable == 0:
            if "IPAddress" in self.networkcard[self.NetworkCardName]["cfg"]:
                self.IpAddrs = self.networkcard[self.NetworkCardName]["cfg"]["IPAddress"]
                self.NetMasks = self.networkcard[self.NetworkCardName]["cfg"]["SubnetMask"]
        elif self.DhcpEnable == 1:
            if "DhcpIPAddress" in self.networkcard[self.NetworkCardName]["cfg"]:
                self.IpAddrs.append(self.networkcard[self.NetworkCardName]["cfg"]["DhcpIPAddress"])
                self.NetMasks.append(self.networkcard[self.NetworkCardName]["cfg"]["DhcpSubnetMask"])
        else:
            if "IPAddress" in self.networkcard[self.NetworkCardName]["cfg"]:
                self.IpAddrs = self.networkcard[self.NetworkCardName]["cfg"]["IPAddress"]
                self.NetMasks = self.networkcard[self.NetworkCardName]["cfg"]["SubnetMask"]
            messageCtl.Pop_Top_message(messageCtl.MSG_TYPE.ERR,
                                       f"{self.NetworkCardName}\n未知的DHCP状态,网卡可能有异常!", TTL=5000)

        # 将网关和DNS从dhcp配置或静态配置梳理后加入GateWays和DNSs
        if self.DhcpEnable == 0:
            if "DefaultGateway" in self.networkcard[self.NetworkCardName]["cfg"]:
                self.GateWays = self.networkcard[self.NetworkCardName]["cfg"]["DefaultGateway"]
            if "NameServer" in self.networkcard[self.NetworkCardName]["cfg"]:
                # 说明:注册表内存储方式可能如下"NameServer": "114.114.114.114,114.114.114.115",所以需要分割
                self.DNSs = self.networkcard[self.NetworkCardName]["cfg"]["NameServer"].split(",")
        elif self.DhcpEnable == 1:
            if "DhcpDefaultGateway" in self.networkcard[self.NetworkCardName]["cfg"]:
                self.GateWays.append(self.networkcard[self.NetworkCardName]["cfg"]["DhcpDefaultGateway"])
            if "DhcpNameServer" in self.networkcard[self.NetworkCardName]["cfg"]:
                # 说明:注册表内存储方式可能如下"DhcpNameServer": "192.168.1.1 192.168.0.1",所以需要分割
                self.DNSs = self.networkcard[self.NetworkCardName]["cfg"]["DhcpNameServer"].split(" ")
        else:
            # 未知的DHCP状态,可以添加其他异常处理
            if "DefaultGateway" in self.networkcard[self.NetworkCardName]["cfg"]:
                self.GateWays = self.networkcard[self.NetworkCardName]["cfg"]["DefaultGateway"]
            if "NameServer" in self.networkcard[self.NetworkCardName]["cfg"]:
                # 说明:注册表内存储方式可能如下"NameServer": "114.114.114.114,114.114.114.115",所以需要分割
                self.DNSs = self.networkcard[self.NetworkCardName]["cfg"]["NameServer"].split(",")

        # 更新所有组件
        self.IPAddressEntry.delete(0, "end")
        if len(self.IpAddrs) > 0:
            self.IPAddressEntry.insert(0, self.IpAddrs[0])
        else:
            self.IPAddressEntry.insert(0, "null")
        self.GatewayAddressEntry.delete(0, "end")
        if len(self.GateWays) > 0:
            self.GatewayAddressEntry.insert(0, self.GateWays[0])
        else:
            self.GatewayAddressEntry.insert(0, "null")
        self.DNSAddressEntry.delete(0, "end")
        if len(self.DNSs) > 0:
            self.DNSAddressEntry.insert(0, self.DNSs[0])
        else:
            self.DNSAddressEntry.insert(0, "null")

        self.Multi_IPMask_ListFrame.ListBox.delete(0, "end")
        for i in range(0, len(self.IpAddrs)):
            self.Multi_IPMask_ListFrame.AddItem(self.IpAddrs[i] + "/" + str(networkCtl.MaskToNum(self.NetMasks[i])))

        self.Multi_Gateway_ListFrame.ListBox.delete(0, "end")
        for i in range(0, len(self.GateWays)):
            self.Multi_Gateway_ListFrame.AddItem(self.GateWays[i])

        self.Multi_DNS_ListFrame.ListBox.delete(0, "end")
        for i in range(0, len(self.DNSs)):
            self.Multi_DNS_ListFrame.AddItem(self.DNSs[i])

        # 更新DHCP状态
        if self.DhcpEnable == 1:
            self.DHCPEnableCheckButton.select()
        else:
            self.DHCPEnableCheckButton.deselect()

    def reset_enter(self, event):
        self.ResetButton.config(bg=STYLE.Button_Adv_Fore)

    def reset_leave(self, event):
        self.ResetButton.config(bg=STYLE.Button_Adv_Back)


class AddCardView(BASE_FRAME):  # 添加选项卡组件(目前只有测试面板使用/2024.1.21)
    def __init__(self, root, place_set=(10, 10), frame_size=(180, 280)):
        super().__init__(root, frame_size=frame_size, place_set=place_set)

        # -------------------------frame配置
        self.frame.configure(highlightbackground=STYLE.ADD_Border, bg=STYLE.ADD_BG, width=self.frame_size[0],
                             height=self.frame_size[1], highlightthickness=2)
        self.frame_border_color = STYLE.ADD_Border
        self.frame.place(anchor=tk.NW, x=self.place_set[0], y=self.place_set[1])
        # -------------------------

        # -------------------------二级frame
        self.SubFrame = tk.Frame(self.frame, bg=STYLE.ADD_SubBG, width=self.frame_size[0] - 10,
                                 height=self.frame_size[1] - 10)
        self.SubFrame.place(anchor=tk.NW, relx=0.04, rely=0.03, relwidth=0.92, relheight=0.94)

        # -------------------------"添加"标签
        self.AddLabel = tk.Label(self.SubFrame, text="+", font=STYLE.MSYHFontBigger64, fg=STYLE.ADD_FG,
                                 bg=STYLE.ADD_SubBG)
        self.AddLabel.place(relx=0.5, rely=0.4, anchor=tk.CENTER)

        # 事件绑定区
        # -------------------------鼠标点击事件
        self.AddLabel.bind("<Button-1>", self.click_add)
        self.SubFrame.bind("<Button-1>", self.click_add)
        self.frame.bind("<Button-1>", self.click_add)

    def click_add(self, event):  # 鼠标点击事件,由子类重写具体实现
        pass


class TAddCardView(AddCardView):  # 测试面板的添加选项卡组件
    def __init__(self, root, place_set=(10, 10), frame_size=(180, 280)):
        super().__init__(root, place_set=place_set, frame_size=frame_size)

        # 公用属性-------------------------<# 选择功能面板
        self.SelctetFrame = SECOND_FRAME(root, place_set=(self.frame.winfo_x() + self.frame.winfo_width() + 5, 10),
                                         frame_size=(180, 280), frame_border_color=STYLE.ADD_Border)
        self.SelctetFrameExsit = False
        self.SelctetFrameOutOfWindow = False
        self.SelctetFrameSize = (self.frame_size[0], self.frame_size[1])

        self.ICMPButton = LableButton(self.SelctetFrame.frame, text="ICMP", font=STYLE.MSYHFontBigger16,
                                      bg=STYLE.ADD_ICMP_BG, fg=STYLE.ADD_ICMP_Font_Color,
                                      border_color=STYLE.ADD_ICMP_Border)
        self.TCPIPButton = LableButton(self.SelctetFrame.frame, text="TCP/IP", font=STYLE.MSYHFontBigger16,
                                       bg=STYLE.ADD_TCPIP_BG, fg=STYLE.ADD_TCPIP_Font_Color,
                                       border_color=STYLE.ADD_TCPIP_Border)
        self.MOREButton = LableButton(self.SelctetFrame.frame, text="MORE", font=STYLE.MSYHFontBigger16,
                                      bg=STYLE.ADD_MORE_BG, fg=STYLE.ADD_MORE_Font_Color,
                                      border_color=STYLE.ADD_MORE_Border)

        self.ICMPButton.BaseFrame.place(relx=0.04, rely=0.03, anchor=tk.NW, relwidth=0.92, relheight=0.3)
        self.TCPIPButton.BaseFrame.place(relx=0.04, rely=0.35, anchor=tk.NW, relwidth=0.92, relheight=0.3)
        self.MOREButton.BaseFrame.place(relx=0.04, rely=0.67, anchor=tk.NW, relwidth=0.92, relheight=0.3)

        # 按钮事件绑定区
        # -------------------------
        self.ICMPButton.BaseFrame.bind("<Button-1>", self.click_ICMPButton)
        self.ICMPButton.Label.bind("<Button-1>", self.click_ICMPButton)
        self.TCPIPButton.BaseFrame.bind("<Button-1>", self.click_TCPIPButton)
        self.TCPIPButton.Label.bind("<Button-1>", self.click_TCPIPButton)
        # self.MOREButton.BaseFrame.bind("<Button-1>", self.click_MOREButton)

    # 检测SelctetFrame是否超出窗口
    def SelctetFrame_OutOfWindow(self) -> None:
        if self.frame.winfo_x() + self.SelctetFrameSize[0] + self.frame.winfo_width() + 10 > self.root.winfo_width():
            self.SelctetFrameOutOfWindow = True

        else:
            self.SelctetFrameOutOfWindow = False

    # 打开SelctetFrame(当前版本是当鼠标离开selctetFrame时自动关闭,因此此处只需实现单击开关selctetFrame和超出窗口自动关闭)
    def click_add(self, event):

        if self.SelctetFrame.isClosed == False:  # 如果selctetFrame没有关闭,则关闭selctetFrame
            self.SelctetFrame.frame.place_forget()
            self.SelctetFrame.isClosed = True
            return

        self.SelctetFrame.isClosed = False
        self.SelctetFrame_OutOfWindow()  # 检测SelctetFrame是否超出窗口
        if self.SelctetFrameOutOfWindow == False:  # 如果没有超出窗口
            self.SelctetFrame.frame.place(anchor=tk.NW, x=self.frame.winfo_x() + self.frame.winfo_width() + 5,
                                          y=self.place_set[1])
        else:  # 如果超出窗口
            self.SelctetFrame.frame.place(anchor=tk.NW, x=self.frame.winfo_x() - self.SelctetFrameSize[0] - 5,
                                          y=self.place_set[1])
        self.SelctetFrame.frame.lift()

    # selctetFrame随着父类frame的动画而动画
    def mouse_motion_delay(self):  # 由于存在二级面板需要变化，所以重写了父类的鼠标动画函数，增加了高级面板的动画调用
        i = 2  # 速率系数，越大动画速度越快。建议设置为可整除的数，建议为2的倍数
        dx = i  # 每次重绘x轴移动值
        dy = (self.frame_size[1] / self.frame_size[0]) * i / 2  # 每次重绘y轴移动值

        if self.frame.winfo_width() <= self.frame_size[0] + 10 and self.mouse_exit == False:
            self.frame.place(x=self.frame.winfo_x() - (dx * 0.5), y=self.frame.winfo_y() - (dy * 0.5))
            self.frame.configure(width=self.frame.winfo_width() + dx,
                                 height=self.frame.winfo_height() + dy)

            self.frame.after(30, self.mouse_motion_delay)

            if self.SelctetFrame.isClosed == False:  # 如果selctetFrame没有关闭
                self.SelctetFrame_motion(is_expand=True, i=i / 2)

        elif self.mouse_exit == True and self.frame.winfo_width() >= self.frame_size[0]:
            self.frame.place(x=self.frame.winfo_x() + (dx * 0.5), y=self.frame.winfo_y() + (dy * 0.5))
            self.frame.configure(width=self.frame.winfo_width() - dx,
                                 height=self.frame.winfo_height() - dy)
            self.frame.after(30, self.mouse_motion_delay)

            if self.SelctetFrame.isClosed == False:  # 如果selctetFrame没有关闭
                self.SelctetFrame_motion(is_expand=False, i=i / 2)

    # selctetFrame随着父类frame的动画而动画
    def SelctetFrame_motion(self, is_expand=False, i=2):
        if self.SelctetFrame.isClosed == False:  # 如果selctetFrame没有关闭
            if self.SelctetFrameOutOfWindow == False:
                if is_expand == True:
                    self.SelctetFrame.frame.place(anchor=tk.NW, x=self.SelctetFrame.frame.winfo_x() + i,
                                                  y=self.place_set[1])
                else:
                    self.SelctetFrame.frame.place(anchor=tk.NW, x=self.SelctetFrame.frame.winfo_x() - i,
                                                  y=self.place_set[1])
            else:
                if is_expand == True:
                    self.SelctetFrame.frame.place(anchor=tk.NW, x=self.SelctetFrame.frame.winfo_x() - i,
                                                  y=self.place_set[1])
                else:
                    self.SelctetFrame.frame.place(anchor=tk.NW, x=self.SelctetFrame.frame.winfo_x() + i,
                                                  y=self.place_set[1])

    def mouse_enter(self, event):  # 鼠标划过frame组件响应
        self.frame.config(
            highlightbackground=STYLE.MouseEnter)
        self.mouse_exit = False
        self.mouse_motion_delay()
        self.frame.config(cursor="hand2")  # 鼠标划过frame组件时,鼠标变为手型

    def click_ICMPButton(self, event):
        self.KillSelfDone = True
        frames.AddICMPViewToDetectFrame(OLDx=self.frame.winfo_x(), OLDy=self.frame.winfo_y())

        # 销毁整个实例
        self.frame.destroy()
        del self

    def click_TCPIPButton(self, event):
        self.KillSelfDone = True
        frames.AddTCPIPViewToDetectFrame(OLDx=self.frame.winfo_x(), OLDy=self.frame.winfo_y())

        # 销毁自己
        self.frame.destroy()
        del self


class ICMPView(BASE_FRAME):  # 网络检测组件
    def __init__(self, root, place_set=(0, 0), frame_size=(180, 280)):
        super().__init__(root, frame_size=frame_size, place_set=place_set)

        # =========================公共属性
        self.frame_border_color = STYLE.ICMP_Border
        self.frame.configure(highlightbackground=self.frame_border_color, bg=STYLE.ICMP_BG, width=self.frame_size[0],
                             height=self.frame_size[1], highlightthickness=2)
        self.frame.place(anchor=tk.NW, x=self.place_set[0], y=self.place_set[1])

        self.src_ip = ""
        self.dst_ip = ""
        self.count = ""
        self.TimeOut = None  # 预留
        self.PingData = b"This is a PING test!"  # 自定义ping的数据

        self.SUCSum = 0  # 成功次数
        self.FAILSum = 0  # 失败次数

        self.IsStop = False  # 是否停止ping

        # =========================控件布局
        # -------------------------顶部标签
        self.TopLable = tk.Label(self.frame, text="ICMP", font=STYLE.DefFontBigger14, fg="white",
                                 bg=STYLE.ICMP_Lable)
        self.TopLable.place(relx=0, rely=0, anchor=tk.NW, relwidth=1, relheight=0.1)

        # -------------------------源地址标签
        self.SRCLabel = tk.Label(self.frame, text="源", font=STYLE.MSYHFontBigger10, fg="white",
                                 bg=STYLE.ICMP_SRC_Label)
        self.SRCLabel.place(relx=0.05, rely=0.15, anchor=tk.NW)

        # -------------------------源地址输入框
        self.SRCEnter = tk.Entry(self.frame, font=STYLE.MSYHFont, fg="black", bg=STYLE.EntryBG,
                                 justify=tk.CENTER)
        self.SRCEnter.insert(0, "Default")
        self.SRCEnter.place(relx=0.2, rely=0.16, anchor=tk.NW, relwidth=0.75, relheight=0.07)

        # -------------------------目标地址标签
        self.DSTLabel = tk.Label(self.frame, text="目", font=STYLE.MSYHFontBigger10, fg="white",
                                 bg=STYLE.ICMP_DST_Label)
        self.DSTLabel.place(relx=0.05, rely=0.27, anchor=tk.NW)

        # -------------------------目标地址输入框
        self.DSTEnter = tk.Entry(self.frame, font=STYLE.MSYHFont, fg="black", bg=STYLE.EntryBG,
                                 justify=tk.CENTER)
        self.DSTEnter.place(relx=0.2, rely=0.28, anchor=tk.NW, relwidth=0.75, relheight=0.07)

        # -------------------------指定次数标签
        self.CountLabel = tk.Label(self.frame, text="次", font=STYLE.MSYHFontBigger10, fg="black"
                                   )  # bg=STYLE.ICMP_Count_Label
        self.CountLabel.place(relx=0.05, rely=0.39, anchor=tk.NW)

        # -------------------------指定次数输入框
        self.CountEnter = tk.Entry(self.frame, font=STYLE.MSYHFont, fg="black", bg=STYLE.EntryBG,
                                   justify=tk.CENTER)
        self.CountEnter.insert(0, "4")
        self.CountEnter.place(relx=0.2, rely=0.4, anchor=tk.NW, relwidth=0.3, relheight=0.07)

        # -------------------------是否长ping的钩选框
        self.LongPingVar = tk.IntVar()
        self.LongPingVar.set(0)
        self.LongPingCheckButton = tk.Checkbutton(self.frame, text="长ping", font=STYLE.MSYHFontBigger10, fg="black",
                                                  variable=self.LongPingVar)
        self.LongPingCheckButton.place(relx=0.55, rely=0.4, anchor=tk.NW, relwidth=0.4, relheight=0.07)

        # -------------------------自定义报文内容大输入框
        self.CustomPacketEnter = tk.Text(self.frame, font=STYLE.MSYHFont, fg="black", bg=STYLE.EntryBG)
        self.CustomPacketEnter.insert(chars=self.PingData, index=tk.END)
        self.CustomPacketEnter.place(relx=0.05, rely=0.52, anchor=tk.NW, relwidth=0.9, relheight=0.2)

        # -------------------------实时统计成功次数
        self.SucCountLabel = tk.Label(self.frame, text="OK:null", font=STYLE.MSYHFontBigger10, fg="white",
                                      bg=STYLE.ICMP_SUCCESS_Border)
        self.SucCountLabel.place(relx=0.05, rely=0.75, anchor=tk.NW, relwidth=0.4, relheight=0.08)

        # -------------------------实时统计失败次数
        self.FailCountLabel = tk.Label(self.frame, text="NO:null", font=STYLE.MSYHFontBigger10, fg="white",
                                       bg=STYLE.ICMP_FAIL_Border)
        self.FailCountLabel.place(relx=0.55, rely=0.75, anchor=tk.NW, relwidth=0.4, relheight=0.08)

        # -------------------------开始按钮
        self.StartButton = tk.Button(self.frame, text="开始", font=STYLE.MSYHFontBigger10, fg="white",
                                     bg=STYLE.Button_Yes_Back, relief=tk.GROOVE)
        self.StartButton.place(relx=0.05, rely=0.86, anchor=tk.NW, relwidth=0.28, relheight=0.1)

        # -------------------------中断按钮
        self.StopButton = tk.Button(self.frame, text="中断", font=STYLE.MSYHFontBigger10, fg="white",
                                    bg=STYLE.Button_Stop_Back, relief=tk.GROOVE)
        self.StopButton.place(relx=0.36, rely=0.86, anchor=tk.NW, relwidth=0.28, relheight=0.1)
        self.StopButton.config(state=tk.DISABLED)

        # -------------------------关闭按钮
        self.CloseButton = tk.Button(self.frame, text="关闭", font=STYLE.MSYHFontBigger10, fg="white",
                                     bg=STYLE.Button_Close_Back, relief=tk.GROOVE)
        self.CloseButton.place(relx=0.66, rely=0.86, anchor=tk.NW, relwidth=0.28, relheight=0.1)

        # =========================事件绑定
        # -------------------------开始按钮事件绑定
        self.StartButton.bind("<Enter>", self.mouse_enter_start)
        self.StartButton.bind("<Leave>", self.mouse_leave_start)
        self.StartButton.bind("<Button-1>", self.click_start)

        # -------------------------中断按钮事件绑定
        self.StopButton.bind("<Enter>", self.mouse_enter_stop)
        self.StopButton.bind("<Leave>", self.mouse_leave_stop)
        self.StopButton.bind("<Button-1>", self.click_stop)

        # -------------------------关闭按钮事件绑定
        self.CloseButton.bind("<Enter>", self.mouse_enter_close)
        self.CloseButton.bind("<Leave>", self.mouse_leave_close)
        self.CloseButton.bind("<Button-1>", self.click_close)

    def runner(self):  # ping任务
        self.SucCountLabel.config(text="OK:0")
        self.FailCountLabel.config(text="NO:0")
        self.SUCSum = 0
        self.FAILSum = 0
        for i in range(int(self.count)):
            if self.IsStop == True:
                self.StartButton.config(state=tk.NORMAL)
                break
            JobOK, ACKOK = protocols.ping(src_addr=self.src_ip, dest_addr=self.dst_ip, ping_data=self.PingData, seq=i)
            if JobOK == False:
                messageCtl.Pop_Top_message(root=self.root, type=messageCtl.MSG_TYPE.ERR, msgstr="线程错误")
                return False
            if ACKOK == True:
                self.SUCSum += 1
                self.SucCountLabel.config(text="OK:" + str(self.SUCSum))
            else:
                self.FAILSum += 1
                self.FailCountLabel.config(text="NO:" + str(self.FAILSum))
            self.CountLabel_Change_Color(ACKOK)

            # 线程休眠1秒
            time.sleep(1)

        # ping任务结束后恢复按钮
        self.StartButton.config(state=tk.NORMAL)
        self.StopButton.config(state=tk.DISABLED)
        self.CountLabel_Restore_Color()

    # =========================事件响应
    # -------------------------开始按钮事件响应
    def mouse_enter_start(self, event):
        self.StartButton.config(bg=STYLE.Button_Yes_Fore)

    def mouse_leave_start(self, event):
        self.StartButton.config(bg=STYLE.Button_Yes_Back)

    def click_start(self, event):
        self.src_ip = self.SRCEnter.get()
        self.dst_ip = self.DSTEnter.get()
        self.count = self.CountEnter.get()
        self.TimeOut = None  # 预留
        self.PingData = self.CustomPacketEnter.get("1.0", tk.END)

        # 判断count是否为数字或字符
        if self.count.isdigit():
            self.count = int(self.count)
        else:
            messageCtl.Pop_Top_message(root=self.root, type=messageCtl.MSG_TYPE.ERR, msgstr="次数格式错误")
            return False

        if self.count < 1 and self.count > 100000:
            messageCtl.Pop_Top_message(root=self.root, type=messageCtl.MSG_TYPE.ERR, msgstr="次数超出范围")
            return False

        if self.src_ip == "Default" or self.src_ip == "":
            self.src_ip = ""
        elif protocols.check_ip(self.src_ip):  # 源地址正则匹配IP地址
            pass
        else:
            messageCtl.Pop_Top_message(root=self.root, type=messageCtl.MSG_TYPE.ERR, msgstr="源IP地址格式错误")
            return False

        if protocols.check_ip(self.dst_ip) and self.dst_ip != "":  # 目的地址正则匹配IP地址
            pass
        else:
            messageCtl.Pop_Top_message(root=self.root, type=messageCtl.MSG_TYPE.ERR, msgstr="目的IP地址格式错误")
            return False

        self.StartButton.config(state=tk.DISABLED)  # 禁用开始按钮
        if self.LongPingVar.get() == 1:  # 如果选择长ping
            self.count = 100000000
        self.IsStop = False
        self.StopButton.config(state=tk.NORMAL)

        # 使用公共线程池创建线程ping任务
        Thread_pool.submit(self.runner)

    # -------------------------中断按钮事件响应
    def mouse_enter_stop(self, event):
        self.StopButton.config(bg=STYLE.Button_Stop_Fore)

    def mouse_leave_stop(self, event):
        self.StopButton.config(bg=STYLE.Button_Stop_Back)

    def click_stop(self, event):
        self.IsStop = True
        self.CountLabel_Restore_Color()

    # -------------------------关闭按钮事件响应
    def mouse_enter_close(self, event):
        self.CloseButton.config(bg=STYLE.Button_Close_Fore)

    def mouse_leave_close(self, event):
        self.CloseButton.config(bg=STYLE.Button_Close_Back)

    def click_close(self, event):
        frames.DeleteDetectView(self)
        self.frame.destroy()
        del self

    # -------------------------成功和失败label变色
    def CountLabel_Change_Color(self, IsOK: bool):
        if IsOK == True:
            self.SucCountLabel.config(bg=STYLE.ICMP_SUCCESS_NOW)
            self.FailCountLabel.config(bg=STYLE.ICMP_FAIL_Border)
        else:
            self.SucCountLabel.config(bg=STYLE.ICMP_SUCCESS_Border)
            self.FailCountLabel.config(bg=STYLE.ICMP_FAIL_NOW)

    # -------------------------成功和失败label恢复默认颜色
    def CountLabel_Restore_Color(self):
        self.SucCountLabel.config(bg=STYLE.ICMP_SUCCESS_Border)
        self.FailCountLabel.config(bg=STYLE.ICMP_FAIL_Border)


class TCPIPView(BASE_FRAME):  # TCP/IP组件
    def __init__(self, root, place_set=(0, 0), frame_size=(180, 280)):
        super().__init__(root, frame_size=frame_size, place_set=place_set)

        # =========================公共属性
        self.src_ip = ""
        self.dst_ip = ""
        self.dst_port = ""
        self.add_port = ""
        self.TimeOut = None  # 预留

        self.frame_border_color = STYLE.TCPIP_Border
        self.frame.configure(highlightbackground=self.frame_border_color, bg=STYLE.ViewBG, width=self.frame_size[0],
                             height=self.frame_size[1], highlightthickness=2)
        self.frame.place(anchor=tk.NW, x=self.place_set[0], y=self.place_set[1])

        self.PortDict = {}  # 准备测试的端口列表(会整合所有需要测试的端口)
        self.SucPortDict = {}  # 成功的端口列表
        self.FailPortDict = {}  # 失败的端口列表
        self.LoadPortDict = {}  # 从文件加载的端口列表

        self.StopFlag=False  # 是否停止测试

        # =========================控件布局
        # -------------------------顶部标签
        self.TopLable = tk.Label(self.frame, text="TCP/IP", font=STYLE.DefFontBigger14, fg="white",
                                 bg=STYLE.TCPIP_Lable)
        self.TopLable.place(relx=0, rely=0, anchor=tk.NW, relwidth=1, relheight=0.1)

        # -------------------------源地址标签
        self.SRCLabel = tk.Label(self.frame, text="源", font=STYLE.MSYHFontBigger10, fg="white",
                                 bg=STYLE.TCPIP_SrcBG_Label)
        self.SRCLabel.place(relx=0.05, rely=0.15, anchor=tk.NW)

        # -------------------------源地址输入框
        self.SRCEnter = tk.Entry(self.frame, font=STYLE.MSYHFont, fg="black", bg=STYLE.EntryBG,
                                 justify=tk.CENTER)
        self.SRCEnter.insert(0, "Default")
        self.SRCEnter.place(relx=0.2, rely=0.16, anchor=tk.NW, relwidth=0.75, relheight=0.07)

        # -------------------------目标地址标签
        self.DSTLabel = tk.Label(self.frame, text="目", font=STYLE.MSYHFontBigger10, fg="white",
                                 bg=STYLE.TCPIP_DstBG_Label)
        self.DSTLabel.place(relx=0.05, rely=0.27, anchor=tk.NW)

        # -------------------------目标地址输入框
        self.DSTEnter = tk.Entry(self.frame, font=STYLE.MSYHFont, fg="black", bg=STYLE.EntryBG,
                                 justify=tk.CENTER)
        self.DSTEnter.place(relx=0.2, rely=0.28, anchor=tk.NW, relwidth=0.75, relheight=0.07)

        # -------------------------目标端口标签
        self.DSTPortLabel = tk.Label(self.frame, text="端口", font=STYLE.MSYHFontBigger10, fg="black")
        self.DSTPortLabel.place(relx=0.05, rely=0.39, anchor=tk.NW)

        # -------------------------目标端口输入框
        self.DSTPortEnter = tk.Entry(self.frame, font=STYLE.MSYHFont, fg="black", bg=STYLE.EntryBG,
                                     justify=tk.CENTER)
        self.DSTPortEnter.place(relx=0.3, rely=0.4, anchor=tk.NW, relwidth=0.4, relheight=0.07)

        # -------------------------高级设置按钮
        self.AdvancedButton = tk.Button(self.frame, text="...", font=STYLE.MSYHFontBigger10, fg="black",
                                        relief=tk.GROOVE)
        self.AdvancedButton.place(relx=0.75, rely=0.4, anchor=tk.NW, relwidth=0.17, relheight=0.07)

        # -------------------------成功端口列表
        self.SucPortList = ListFrame(self.frame, place_set=(0.05, 0.52), frame_size=(0.42, 0.3),
                                     border_color=STYLE.TCPIP_Success_Border)
        # listbox居中显示
        self.SucPortList.ListBox.config(justify=tk.CENTER)

        # -------------------------失败端口列表
        self.FailPortList = ListFrame(self.frame, place_set=(0.52, 0.52), frame_size=(0.42, 0.3),
                                      border_color=STYLE.TCPIP_Fail_Border)
        # listbox居中显示
        self.FailPortList.ListBox.config(justify=tk.CENTER)

        # -------------------------开始按钮
        self.StartButton = tk.Button(self.frame, text="开始", font=STYLE.MSYHFontBigger10, fg="white",
                                     bg=STYLE.Button_Yes_Back, relief=tk.GROOVE)
        self.StartButton.place(relx=0.05, rely=0.86, anchor=tk.NW, relwidth=0.28, relheight=0.1)

        # -------------------------中断按钮
        self.StopButton = tk.Button(self.frame, text="中断", font=STYLE.MSYHFontBigger10, fg="white",
                                    bg=STYLE.Button_Stop_Back, relief=tk.GROOVE)
        self.StopButton.place(relx=0.36, rely=0.86, anchor=tk.NW, relwidth=0.28, relheight=0.1)
        self.StopButton.config(state=tk.DISABLED)

        # -------------------------关闭按钮
        self.CloseButton = tk.Button(self.frame, text="关闭", font=STYLE.MSYHFontBigger10, fg="white",
                                     bg=STYLE.Button_Close_Back, relief=tk.GROOVE)
        self.CloseButton.place(relx=0.66, rely=0.86, anchor=tk.NW, relwidth=0.28, relheight=0.1)

        # -------------------------高级设置界面
        self.AdvancedFrame = SECOND_FRAME(root, place_set=(self.frame.winfo_x() + self.frame.winfo_width() + 5, 10),
                                          frame_size=(180, 280), frame_border_color=STYLE.TCPIP_Border)
        self.AdvancedFrameOutOfWindow = False  # 高级设置界面是否超出窗口

        # - - - - - - - - - - - - -高级设置界面->选择文件标签
        self.SelectFileNameLabel = tk.Label(self.AdvancedFrame.frame, text="选择的json文件",
                                            font=STYLE.MSYHFont,
                                            fg="black",
                                            bg=STYLE.ViewBGDeepperA)
        self.SelectFileNameLabel.place(relx=0.05, rely=0.02, anchor=tk.NW, relwidth=0.9, relheight=0.1)

        # - - - - - - - - - - - - -高级设置界面->选择文件按钮
        self.SelectFileButton = tk.Button(self.AdvancedFrame.frame, text="选择文件", font=STYLE.MSYHFontBigger10,
                                          fg="white", relief=tk.GROOVE, bg=STYLE.TCPIP_ADV_FileSelectButton_NULL)
        self.SelectFileButton.place(relx=0.05, rely=0.15, anchor=tk.NW, relwidth=0.45, relheight=0.08)

        # - - - - - - - - - - - - -高级设置界面->重置按钮
        self.ResetButton = tk.Button(self.AdvancedFrame.frame, text="重置", font=STYLE.MSYHFontBigger10,
                                     fg="white", relief=tk.GROOVE, bg=STYLE.TCPIP_ADV_ResetButton_NULL)
        self.ResetButton.place(relx=0.55, rely=0.15, anchor=tk.NW, relwidth=0.4, relheight=0.08)

        # - - - - - - - - - - - - -高级设置界面->单个端口输入框
        self.SinglePortEnter = tk.Entry(self.AdvancedFrame.frame, font=STYLE.MSYHFont, fg="black", bg=STYLE.EntryBG,
                                        justify=tk.CENTER)
        self.SinglePortEnter.place(relx=0.05, rely=0.32, anchor=tk.NW, relwidth=0.45)

        # - - - - - - - - - - - - -高级设置界面->添加单个端口按钮
        self.AddSinglePortButton = tk.Button(self.AdvancedFrame.frame, text="添加", font=STYLE.MSYHFont,
                                             fg="white", relief=tk.GROOVE, bg=STYLE.TCPIP_ADV_ADDButton_NULL)
        self.AddSinglePortButton.place(relx=0.55, rely=0.31, anchor=tk.NW, relheight=0.08)

        # - - - - - - - - - - - - -高级设置界面->删除所选端口按钮
        self.DelSelectPortButton = tk.Button(self.AdvancedFrame.frame, text="删除", font=STYLE.MSYHFont,
                                             fg="white", relief=tk.GROOVE, bg=STYLE.TCPIP_ADV_DELButton_NULL)
        self.DelSelectPortButton.place(relx=0.77, rely=0.31, anchor=tk.NW, relheight=0.08)

        # - - - - - - - - - - - - -高级设置界面->端口列表组件(ListFrame)
        self.PortList = ListFrame(self.AdvancedFrame.frame, place_set=(0.05, 0.42), frame_size=(0.9, 0.55),
                                  border_color=STYLE.TCPIP_Border)
        # listbox居中显示
        self.PortList.ListBox.config(justify=tk.CENTER,font=STYLE.MSYHFontBigger10)

        # =========================事件绑定
        # -------------------------开始按钮事件绑定
        self.StartButton.bind("<Enter>", self.mouse_enter_start)
        self.StartButton.bind("<Leave>", self.mouse_leave_start)
        self.StartButton.bind("<Button-1>", self.click_start)

        # -------------------------中断按钮事件绑定
        self.StopButton.bind("<Enter>", self.mouse_enter_stop)
        self.StopButton.bind("<Leave>", self.mouse_leave_stop)
        self.StopButton.bind("<Button-1>", self.click_stop)

        # -------------------------关闭按钮事件绑定
        self.CloseButton.bind("<Enter>", self.mouse_enter_close)
        self.CloseButton.bind("<Leave>", self.mouse_leave_close)
        self.CloseButton.bind("<Button-1>", self.click_close)

        # -------------------------高级设置按钮事件绑定
        self.AdvancedButton.bind("<Button-1>", self.click_advanced)

        self.AdvancedFrame.frame.unbind("<Leave>")  # [单独解绑再绑定 鼠标离开高级设置不会导致关闭]解除高级设置界面的鼠标离开事件绑定
        self.AdvancedFrame.frame.bind("<Leave>", self.mouse_leave_AdvFrame)  # 鼠标离开高级设置界面时关闭高级设置界面

        # -------------------------高级设置界面->选择文件按钮事件绑定
        self.SelectFileButton.bind("<Enter>", self.mouse_enter_selectfile)
        self.SelectFileButton.bind("<Leave>", self.mouse_leave_selectfile)
        self.SelectFileButton.bind("<Button-1>", self.click_selectfile)

        # -------------------------高级设置界面->重置按钮事件绑定
        self.ResetButton.bind("<Enter>", self.mouse_enter_reset)
        self.ResetButton.bind("<Leave>", self.mouse_leave_reset)
        self.ResetButton.bind("<Button-1>", self.click_reset)

        # -------------------------高级设置界面->添加单个端口按钮事件绑定
        self.AddSinglePortButton.bind("<Enter>", self.mouse_enter_addsingleport)
        self.AddSinglePortButton.bind("<Leave>", self.mouse_leave_addsingleport)
        self.AddSinglePortButton.bind("<Button-1>", self.click_addsingleport)

        # -------------------------高级设置界面->删除所选端口按钮事件绑定
        self.DelSelectPortButton.bind("<Enter>", self.mouse_enter_delselectport)
        self.DelSelectPortButton.bind("<Leave>", self.mouse_leave_delselectport)
        self.DelSelectPortButton.bind("<Button-1>", self.click_delselectport)

    # =========================事件响应
    # -------------------------开始按钮事件响应
    def mouse_enter_start(self, event):
        self.StartButton.config(bg=STYLE.Button_Yes_Fore)

    def mouse_leave_start(self, event):
        self.StartButton.config(bg=STYLE.Button_Yes_Back)

    def click_start(self, event):
        self.SucPortList.ListBox.delete(0, tk.END)
        self.FailPortList.ListBox.delete(0, tk.END)

        self.src_ip=self.SRCEnter.get()
        self.dst_ip=self.DSTEnter.get()
        self.dst_port=self.DSTPortEnter.get()

        if self.src_ip == "Default" or self.src_ip == "":
            self.src_ip = ""
        elif protocols.check_ip(self.src_ip):  # 源地址正则匹配IP地址
            pass
        else:
            print("TCPIP SRC ERR")
            # messageCtl.Pop_Top_message(root=self.root, type=messageCtl.MSG_TYPE.ERR, msgstr="源IP地址格式错误")
            return False

        if protocols.check_ip(self.dst_ip):  # 目的地址正则匹配IP地址
            pass
        else:
            print("TCPIP DST ERR")
            # messageCtl.Pop_Top_message(root=self.root, type=messageCtl.MSG_TYPE.ERR, msgstr="目的IP地址格式错误")
            return False

        if self.dst_port.isdigit():
            self.dst_port = int(self.dst_port)
        elif self.LoadPortDict!={}:
            pass
        else:
            print("TCPIP PORT ERR")
            # messageCtl.Pop_Top_message(root=self.root, type=messageCtl.MSG_TYPE.ERR, msgstr="端口书写错误")
            return False

        self.StartButton.config(state=tk.DISABLED)  # 禁用开始按钮
        self.StopButton.config(state=tk.NORMAL)  # 启用中断按钮

        self.PortDict = {}
        if self.DSTPortEnter.get() != "":
            self.PortDict[self.DSTPortEnter.get()] = ""

        for port, func in self.LoadPortDict.items():
            self.PortDict[port] = func

        Thread_pool.submit(self.runner)

    def runner(self):
        t = 0
        for port in self.PortDict.keys():
            # 判断是否停止
            if self.StopFlag==True:
                self.StopFlag=False
                break

            # 对port进行字符串转数字
            if port.isdigit():
                port = int(port)

            Thread_pool.submit(self.tcpip_runner(port))

            # 每批3个端口
            t += 1
            if t >= 3:
                time.sleep(1)
                t = 0
        self.StartButton.config(state=tk.NORMAL)
        self.StopButton.config(state=tk.DISABLED)

    def tcpip_runner(self, port):
        RunOK, ConOK = protocols.tcp_port_test(src_addr=self.src_ip, dest_addr=self.dst_ip, port=port)
        func = self.PortDict[str(port)]

        if RunOK and ConOK:
            self.SucPortList.ListBox.insert(tk.END, str(port)+":"+func)
            # print(f"[ok]"+str(port)+":"+func)
        elif RunOK and ConOK!=True:
            self.FailPortList.ListBox.insert(tk.END,str(port)+":"+func)
            # print(f"[fail]"+str(port)+":"+func)
        else:
            pass # 连接失败


    # -------------------------中断按钮事件响应
    def mouse_enter_stop(self, event):
        self.StopButton.config(bg=STYLE.Button_Stop_Fore)

    def mouse_leave_stop(self, event):
        self.StopButton.config(bg=STYLE.Button_Stop_Back)

    def click_stop(self, event):
        self.StopFlag=True

    # -------------------------关闭按钮事件响应
    def mouse_enter_close(self, event):
        self.CloseButton.config(bg=STYLE.Button_Close_Fore)

    def mouse_leave_close(self, event):
        self.CloseButton.config(bg=STYLE.Button_Close_Back)

    def click_close(self, event):
        frames.DeleteDetectView(self)
        self.AdvancedFrame.frame.destroy()
        self.frame.destroy()
        del self

    # -------------------------高级设置按钮事件响应
    def click_advanced(self, event):
        # 判断高级设置界面是否超出窗口，并打开或关闭高级设置界面
        if self.AdvancedFrame.isClosed == False:  # 如果高级设置界面没有关闭,则关闭高级设置界面
            self.AdvancedFrame.frame.place_forget()
            self.AdvancedFrame.isClosed = True
            return

        self.AdvancedFrame.isClosed = False
        self.AdvancedFrame_OutOfWindow()  # 检测高级设置界面是否超出窗口

        if self.AdvancedFrameOutOfWindow == False:  # 如果没有超出窗口
            self.AdvancedFrame.frame.place(anchor=tk.NW, x=self.frame.winfo_x() + self.frame.winfo_width() + 5,
                                           y=self.place_set[1])

        else:  # 如果超出窗口
            self.AdvancedFrame.frame.place(anchor=tk.NW, x=self.frame.winfo_x() - self.AdvancedFrameSize[0] - 5,
                                           y=self.place_set[1])
        self.AdvancedFrame.frame.lift()

    # -------------------------高级设置界面->选择文件按钮事件响应
    def mouse_enter_selectfile(self, event):
        self.SelectFileButton.config(bg=STYLE.TCPIP_ADV_FileSelectButton_Enter)

    def mouse_leave_selectfile(self, event):
        self.SelectFileButton.config(bg=STYLE.TCPIP_ADV_FileSelectButton_NULL)

    def click_selectfile(self, event):
        JsonFile=filedialog.askopenfilename()
        self.SelectFileButton.config(state=tk.DISABLED) # 这两步用于刷新按钮ui
        self.SelectFileButton.config(state=tk.NORMAL) # 这两步用于刷新按钮ui
        if JsonFile=="":
            return
        self.SelectFileNameLabel.config(text=JsonFile.split("/")[-1])
        self.LoadPortDict = json.load(open(JsonFile, "r",encoding="utf-8"))
        # print(self.LoadPortDict,"hhh")

        self.PortList.ListBox.delete(0, tk.END)
        for port, func in self.LoadPortDict.items():
            self.PortList.ListBox.insert(tk.END, str(port) + ":" + func)


    # -------------------------高级设置界面->重置按钮事件响应
    def mouse_enter_reset(self, event):
        self.ResetButton.config(bg=STYLE.TCPIP_ADV_ResetButton_Enter)

    def mouse_leave_reset(self, event):
        self.ResetButton.config(bg=STYLE.TCPIP_ADV_ResetButton_NULL)

    def click_reset(self, event):
        self.SelectFileNameLabel.config(text="选择的json文件")
        self.LoadPortDict = {}
        self.PortList.ListBox.delete(0, tk.END)

    # -------------------------高级设置界面->添加单个端口按钮事件响应
    def mouse_enter_addsingleport(self, event):
        self.AddSinglePortButton.config(bg=STYLE.TCPIP_ADV_ADDButton_Enter)

    def mouse_leave_addsingleport(self, event):
        self.AddSinglePortButton.config(bg=STYLE.TCPIP_ADV_ADDButton_NULL)

    def click_addsingleport(self, event):
        sport = self.SinglePortEnter.get() # signal port
        if sport.isdigit():
            self.LoadPortDict[sport] = ""
            self.PortList.ListBox.insert(tk.END, sport)
        else:
            pass # 端口号非法处理
        self.SinglePortEnter.delete(0, tk.END)

    # -------------------------高级设置界面->删除所选端口按钮事件响应
    def mouse_enter_delselectport(self, event):
        self.DelSelectPortButton.config(bg=STYLE.TCPIP_ADV_DELButton_Enter)

    def mouse_leave_delselectport(self, event):
        self.DelSelectPortButton.config(bg=STYLE.TCPIP_ADV_DELButton_NULL)

    def click_delselectport(self, event):
        for i in self.PortList.ListBox.curselection():
            del self.LoadPortDict[str(self.PortList.ListBox.get(i)).split(":")[0]]
            self.PortList.ListBox.delete(i)

    # 检测高级设置界面是否超出窗口
    def AdvancedFrame_OutOfWindow(self) -> None:
        if self.frame.winfo_x() + self.AdvancedFrame.frame.winfo_width() + self.frame.winfo_width() + 10 > self.root.winfo_width():
            self.AdvancedFrameOutOfWindow = True
        else:
            self.AdvancedFrameOutOfWindow = False

    # 动画
    def mouse_motion_delay(self):
        i = 2
        dx = i
        dy = (self.frame_size[1] / self.frame_size[0]) * i / 2

        if self.frame.winfo_width() <= self.frame_size[0] + 10 and self.mouse_exit == False:
            self.frame.place(x=self.frame.winfo_x() - (dx * 0.5), y=self.frame.winfo_y() - (dy * 0.5))
            self.frame.configure(width=self.frame.winfo_width() + dx,
                                 height=self.frame.winfo_height() + dy)

            self.frame.after(30, self.mouse_motion_delay)

            if self.AdvancedFrame.isClosed == False:
                self.AdvancedFrame_motion(is_expand=True, i=i / 2)

        elif self.mouse_exit == True and self.frame.winfo_width() >= self.frame_size[0]:
            self.frame.place(x=self.frame.winfo_x() + (dx * 0.5), y=self.frame.winfo_y() + (dy * 0.5))
            self.frame.configure(width=self.frame.winfo_width() - dx,
                                 height=self.frame.winfo_height() - dy)
            self.frame.after(30, self.mouse_motion_delay)

            if self.AdvancedFrame.isClosed == False:
                self.AdvancedFrame_motion(is_expand=False, i=i / 2)

    def AdvancedFrame_motion(self, is_expand=False, i=2):
        if self.AdvancedFrame.isClosed == False:
            if self.AdvancedFrameOutOfWindow == False:
                if is_expand == True:
                    self.AdvancedFrame.frame.place(anchor=tk.NW, x=self.AdvancedFrame.frame.winfo_x() + i,
                                                   y=self.place_set[1])
                else:
                    self.AdvancedFrame.frame.place(anchor=tk.NW, x=self.AdvancedFrame.frame.winfo_x() - i,
                                                   y=self.place_set[1])
            else:
                if is_expand == True:
                    self.AdvancedFrame.frame.place(anchor=tk.NW, x=self.AdvancedFrame.frame.winfo_x() - i,
                                                   y=self.place_set[1])
                else:
                    self.AdvancedFrame.frame.place(anchor=tk.NW, x=self.AdvancedFrame.frame.winfo_x() + i,
                                                   y=self.place_set[1])

    def mouse_leave_AdvFrame(self, event):
        self.AdvancedFrame.frame.config(highlightbackground=STYLE.TCPIP_Border)

# 测试代码，现注释掉，转由main.py主控
#
# Thread_pool = ThreadPoolExecutor(max_workers=10)
#
# root = tk.Tk()
# root.geometry("1000x630")
# root.maxsize(1000, 630)
# root.minsize(1000, 630)
# root.title("白蛛")
# root.configure(bg="#3c3f41")
# wk = regedit_fun.Get_Network_Info_By_AllCard()
# print(len(regedit_fun.Get_Network_Info_By_AllCard()))
#
# MainFrame = tk.Frame(root, bg="#3c3f41", width=1000, height=630)
# MainFrame.place(x=0, y=0)
# MainFrame.update()
#
# xx=900/4
# l = []
# ii = 0
# jj = 0
# t=None
# for i, v in wk.items():
#     if ii >= 4:
#         ii = 0
#         jj += 1
#     if v["PnPInstanceId"].find("PCI") != -1:
#         t = networkview(MainFrame, {i: v}, cardname=i, place_set=(50 + xx* ii, 15 + 300 * jj))
#         ii += 1
#         l.append(t)
#
#
# root.mainloop()
# Thread_pool.shutdown(wait=False, cancel_futures=True)
# print("DONE")
