# =====================================================================
# Description: Main file for the project
# 主程序入口
# Author: zouyuhang
# Start: 2023.10
# =====================================================================

import tkinter as tk
from bin import frames
from bin.globals import Thread_pool, STYLE  # 引入公共线程池
from functools import partial


# ============================
# 在三级菜单罗列网卡
def ShowNetworkCardlistInThirdMune(RootMenu: tk.Menu):
    CardList = frames.NetworkListExist
    RootMenu.delete(0, "end")
    for i in CardList.keys():
        command = partial(frames.AddNetworkToNetFrame, i, RootMenu)
        RootMenu.add_command(label=i, command=command)


# class MenuCtrl:  # 菜单控制类(保存菜单引用)
#     def __init__(self, menu: tk.Menu = None):
#         self.menu = menu
#
#     def SetMenu(self, menu: tk.Menu):
#         self.menu = menu
#
# NetMenu = MenuCtrl()  # 网卡二级菜单引用
# TestMenu = MenuCtrl()  # 测试二级菜单引用


def DisableSubMuneSwich(mune: tk.Menu):  # 轮换禁用子菜单(控制非当前面板禁用菜单里的选项) # 未实现
    pass


def main():
    root = tk.Tk()
    root.resizable(False, False)
    root.geometry("1000x630")
    root.maxsize(1000, 630)
    root.minsize(1000, 630)
    root.title("白蛛")
    root.configure(bg=STYLE.ROOTBG)

    # 菜单栏生成部分
    # ============================
    menu = tk.Menu(root)
    filemenu = tk.Menu(menu, tearoff=0)

    filemenu.add_command(label="保存", command=None)
    filemenu.add_separator()
    filemenu.add_command(label="退出", command=root.quit)
    menu.add_cascade(label="文件", menu=filemenu)

    networkmenu = tk.Menu(menu, tearoff=0)
    networks = tk.Menu(networkmenu, tearoff=0)
    com1 = partial(frames.NetworkFrameOnTop)  # 后面可添加拓展
    networkmenu.add_command(label="面板", command=com1)
    networkmenu.add_separator()
    networkmenu.add_cascade(label="添加监测网卡", menu=networks)
    menu.add_cascade(label="网卡", menu=networkmenu)

    testmenu = tk.Menu(menu, tearoff=0)
    com2 = partial(frames.DetectFrameOnTop)  # 后面可添加拓展
    testmenu.add_command(label="面板", command=com2)
    # testmenu.add_separator()
    # testmenu.add_command(label="添加测试项", command=None)
    # testmenu.entryconfig("添加测试项", state="disabled")
    menu.add_cascade(label="调试与测试", menu=testmenu)

    root.config(menu=menu)
    # 菜单栏生成部分结束
    # ============================

    frames.CreateNetworkFrame(root, networks)  # 创建各个物理网卡面板,为了动态管理可添加网卡的三级菜单,需要传入三级菜单的引用
    frames.CreateDetectFrame(root)  # 创建监测面板
    frames.NetworkFrameOnTop()
    ShowNetworkCardlistInThirdMune(networks)  # 为了动态管理可添加网卡的三级菜单,需要传入三级菜单的引用
    # frames.NetworkFrameOnTop() # 网卡面板置于最前面,同时禁用测试二级菜单的功能项

    root.mainloop()
    Thread_pool.shutdown(wait=False, cancel_futures=True)
    print("DONE")


if __name__ == '__main__':
    main()

# 以下是复杂逻辑实现的梳理(以防以后忘了看不懂代码):

# =====================================================================
# 1.三级菜单动态刷新可添加网卡逻辑:
#   创建菜单的静态项目后 -> 执行一次ShowNetworkCardlistInThirdMune?(将可添加网卡动态刷到三级菜单)
#   在ShowNetworkCardlistInThirdMune中将frame里的AddNetworkToNetFrame绑定在三级菜单点击事件上
#   点击三级菜单后,调用AddNetworkToNetFrame,将网卡添加到frame中,同时把三级菜单引用传入AddNetworkToNetFrame
#   在AddNetworkToNetFrame中,使用networkview生成实例时,把三级菜单引用一并传入networkview,并在networkview中绑定删除网卡事件

# 2.测试添加卡实现逻辑:
#   默认创建测试面板时就创建一个添加选项卡(./bin/controlersX中的TAddCardFrame)
#   添加选项卡的功能被点击后调用frames中的生成功能组件函数,完成后再原位销毁添加选项卡,此时功能选项卡就留在界面
