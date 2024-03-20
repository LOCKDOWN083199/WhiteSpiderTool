# ============================
# 此模块用于各主面板和菜单UI控制
# ============================


import copy
import tkinter as tk

from bin.controlersX import NetworkView, TAddCardView, ICMPView, AddCardView,TCPIPView
from bin import networkCtl
from main import ShowNetworkCardlistInThirdMune  # 引入网卡三级菜单刷新函数

# 大面板
# ====================
NetworkFrame: tk.Frame = None  # 网卡面板(页)
DetectFrame: tk.Frame = None  # 监测面板(页)
# ====================


# 网卡面板使用的变量
# -------------------------------------
# NetworkMatrix = [[0 for i in range(4)] for j in range(2)]  # 默认2行4列  ###24.1.6弃用
NetX = 0  # 存储生成下一个控件的x编号，注意x是列
NetY = 0  # 存储生成下一个控件的y编号，注意y是行
Ndx = 900 / 4  # 用于计算下一个控件的变化x位置(列间距)
Ndy = 300  # 用于计算下一个控件变化的y位置(行间距)

MAXCOL = 4  # 最大列数
MAXROW = 2  # 最大行数

NetworkList = {}  # 用于存储所有网卡
NetworkListExist = {}  # 用于存储未显示的网卡
NetworkListUnExist = {}  # 用于存储已显示的网卡,实现每一个网卡动态增删

NetworkViews = {}  # 用于存储网卡实例


# -------------------------------------


# 一些大家都用得到的基本函数
# ===================================================================<

# ===================================================================<


# 网卡面板使用的函数
# ===================================================================<

def NetworkFrameOnTop():  # 网卡面板置于最前面 # 未实现的预留参数NetMenu,TestMenu
    global NetworkFrame
    NetworkFrame.lift()

    # 其他面板未使用时禁用其他面板选项
    # ===============================================未实现
    # StartN = 1 # 网卡二级菜单启用的起始项
    # print("开始调用index", NetMenu.menu.index("end"))
    # EndN = NetMenu.menu.index("end") + 1
    # for i in range(StartN, EndN):
    #     NetMenu.menu.entryconfig(i, state="normal") # 启用二级菜单各项
    #
    # StartN = 1 # 测试二级菜单禁用的起始项
    # EndN = TestMenu.menu.index("end") + 1
    # for i in range(StartN, EndN):
    #     TestMenu.menu.entryconfig(i, state="disabled") # 禁用测试二级菜单各项
    # ======================================================


def CreateNetworkFrame(root, NetListMenu):  # 网卡面板,罗列网卡,默认只显示物理网卡
    global NetworkFrame, NetworkList, NetX, NetY, Ndx, Ndy, NetworkListExist, NetworkListUnExist, NetworkViews  # 全局变量

    NetworkFrame = tk.Frame(root, bg="#dfe1e5", width=1000, height=630)
    NetworkFrame.place(x=0, y=0)
    NetworkFrame.update()

    wk = networkCtl.Get_Network_Info_By_AllCard()
    NetworkList = copy.deepcopy(wk)
    NetworkListExist = copy.deepcopy(wk)

    NetX = 0
    NetY = 0
    for i, v in wk.items():
        if v["PnPInstanceId"].find("PCI") != -1:  # 只显示物理网卡
            NetworkViews[i] = NetworkView(NetworkFrame, {i: v}, cardname=i,
                                          place_set=(50 + Ndx * NetX, 15 + Ndy * NetY),
                                          NetX=NetX, NetY=NetY, quote=NetListMenu)
            NetworkListUnExist[i] = NetworkListExist.pop(i)
            NetX += 1
            # addcardview(NetworkFrame, place_set=(50 + Ndx * NetX, 15 + Ndy * NetY))
            # NetX += 1

        if NetX >= MAXCOL:  # y行 x 4列...(窗口正常显示下,预计最多2x4)
            NetX = 0
            NetY += 1


def AddNetworkToNetFrame(cardname: str, RootMenu: tk.Menu):  # 添加网卡到网卡面板
    global NetworkFrame, NetworkList, NetX, NetY, Ndx, Ndy, NetworkListExist, NetworkListUnExist, NetworkViews  # 全局变量
    if cardname in NetworkListExist.keys():
        NetworkViews[cardname] = NetworkView(NetworkFrame, {cardname: NetworkListExist[cardname]}, cardname=cardname,
                                             place_set=(50 + Ndx * NetX, 15 + Ndy * NetY), NetX=NetX, NetY=NetY,
                                             quote=RootMenu)
        NetworkListUnExist[cardname] = NetworkListExist.pop(cardname)
        NetX += 1
        if NetX >= MAXCOL:
            NetX = 0
            NetY += 1

        ShowNetworkCardlistInThirdMune(RootMenu)

        return True


def DeleteNetworkFromNetFrame(cardname: str, RootMenu: tk.Menu):  # 从网卡面板删除网卡
    global NetworkFrame, NetworkList, NetX, NetY, Ndx, Ndy, NetworkListExist, NetworkListUnExist, NetworkViews  # 全局变量
    if cardname in NetworkList.keys():
        NetworkListExist[cardname] = NetworkListUnExist.pop(cardname)
        NetworkViews.pop(cardname)
        ReDrawNetworkFrame()
        NetX -= 1
        if NetX < 0:
            NetX = MAXCOL - 1
            if NetY > 0:
                NetY -= 1

        ShowNetworkCardlistInThirdMune(RootMenu)
        return True


# 重绘各个组件位置
def ReDrawNetworkFrame():  # 删减网卡后重绘网卡面板
    global NetworkFrame, NetworkList, NetX, NetY, Ndx, Ndy, NetworkListExist, NetworkListUnExist, NetworkViews  # 全局变量

    x, y = 0, 0  # 用于计算行列号

    for i in NetworkViews.values():  # 遍历所有网卡组件实例,i是本轮循环的网卡组件实例
        i.frame.place(x=50 + Ndx * x, y=15 + Ndy * y)
        i.place_set = (50 + Ndx * x, 15 + Ndy * y)
        if i.AdvancedFrameExsit:  # 如果网卡高级面板存在,则隐藏高级面板
            i.AdvancedFrameExsit = False
            i.AdvancedFrame.place_forget()

        # 用于计算行列号
        x += 1
        if x >= MAXCOL:
            x = 0
            y += 1

    NetworkFrame.update()


# ===================================================================<


# 增加项目面板
# ===================================================================<

def CreateAddFrame(Root):  # 添加到面板
    global NetX, NetY, Ndx, Ndy  # 全局变量

    C = AddCardView(Root, place_set=(50 + Ndx * NetX, 15 + Ndy * NetY))

    NetX += 1
    if NetX >= MAXCOL:
        NetX = 0
        NetY += 1

    return True


# 调试面板使用的变量
# -------------------------------------
DetX = 0  # 存储生成下一个控件的x编号，注意x是列
DetY = 0  # 存储生成下一个控件的y编号，注意y是行
Detdx = 900 / 4  # 用于计算下一个控件的变化x位置(列间距)
Detdy = 300  # 用于计算下一个控件变化的y位置(行间距)

DetectViewList = []  # 用于存储所有测试选项卡和增加选项卡


# -------------------------------------

# 调试面板使用的函数
# ===================================================================<
def DetectFrameOnTop():  # 调试面板置于最前面
    global DetectFrame
    DetectFrame.lift()

    # 其他面板未使用时禁用其他面板选项
    # ===============================================未实现
    # StartN = 1 # 网卡的二级菜单禁用的起始项
    # EndN = len(main.NetMenu.menu.index("end") + 1)
    # for i in range(StartN, EndN):
    #     main.NetMenu.menu.entryconfig(i, state="disabled") # 禁用二级菜单各项
    #
    # StartN = 1 # 测试的二级菜单启用的起始项
    # EndN = len(main.TestMenu.menu.index("end") + 1)
    # for i in range(StartN, EndN):
    #     main.TestMenu.menu.entryconfig(i, state="normal") # 启用测试二级菜单各项
    # ======================================================


def CreateDetectFrame(root):  # 调试面板
    global DetectFrame
    DetectFrame = tk.Frame(root, bg="#dfe1e5", width=1000, height=630)
    DetectFrame.place(x=0, y=0)
    DetectFrame.update()

    AddAddCardToDetectFrame()


def AddAddCardToDetectFrame():  # 添加AddCard到调试面板
    global DetectFrame, DetX, DetY, Detdx, Detdy  # 全局变量

    if DetY >= MAXROW:
        print("调试面板已满")
        return

    T = TAddCardView(DetectFrame, place_set=(50 + Detdx * DetX, 15 + Detdy * DetY))
    DetectViewList.append(T)

    DetX += 1
    if DetX >= MAXCOL:
        DetX = 0
        DetY += 1


def AddICMPViewToDetectFrame(OLDx=0, OLDy=0):  # 添加ICMPView到调试面板
    global DetectFrame, DetX, DetY, Detdx, Detdy, DetectViewList  # 全局变量

    DetectListFlash()

    T = ICMPView(DetectFrame, place_set=(OLDx, OLDy))
    DetectViewList.append(T)
    DetectFrameReDraw()
    DetectListFlash()

    AddAddCardToDetectFrame()


def DetectListFlash():  # 列表重新整理
    global DetectFrame, DetectViewList  # 全局变量
    TList = []
    for i in range(0, len(DetectViewList)):
        if DetectViewList[i].KillSelfDone == False:
            TList.append(DetectViewList[i])
    DetectViewList = TList


def DetectFrameReDraw():  # 重绘调试面板
    global DetectFrame, DetectViewList, Detdx, Detdy  # 全局变量

    x, y = 0, 0  # 用于计算行列号

    for i in DetectViewList:  # 遍历所有测试组件实例,i是本轮循环的测试组件实例
        i.frame.place(x=50 + Detdx * x, y=15 + Detdy * y)
        i.place_set = (50 + Detdx * x, 15 + Detdy * y)

        # 用于计算行列号
        x += 1
        if x >= MAXCOL:
            x = 0
            y += 1

    DetectFrame.update()


# 删除一个测试面板
def DeleteDetectView(DetectView):  # 从调试面板删除一个测试面板
    global DetectFrame, DetectViewList, DetX, DetY, Detdx, Detdy  # 全局变量

    DetectViewList.remove(DetectView) # 从列表中删除
    DetectFrameReDraw()

    DetX -= 1
    if DetX < 0:
        DetX = MAXCOL - 1
        if DetY > 0:
            DetY -= 1


def AddTCPIPViewToDetectFrame(OLDx=0, OLDy=0):  # 添加TCPIPView到调试面板
    global DetectFrame, DetX, DetY, Detdx, Detdy, DetectViewList  # 全局变量

    DetectListFlash()

    T = TCPIPView(DetectFrame, place_set=(OLDx, OLDy))
    DetectViewList.append(T)
    DetectFrameReDraw()
    DetectListFlash()

    AddAddCardToDetectFrame()

# ===================================================================<
