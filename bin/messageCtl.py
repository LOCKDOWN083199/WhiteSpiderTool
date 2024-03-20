# ============================
# 此模块的代码负责程序弹出消息提示
# ============================

import queue
import tkinter as tk
from bin.globals import STYLE  # 引入样式

# 消息队列
# ============================
MSG_QUEUE = queue.Queue()
# ============================

# ============================
# 初步设置7色进行提示分类
# 红 出现错误/报错
# 橙 出现警告/信息提示
# 黄 未分配
# 绿 出现成功
# 青 未分配
# 蓝 未分配
# 紫 未分配
# ============================

class MSG_TYPE:  # 消息类型
    ERR = 1
    WARN = 2
    SUC = 4

    # 颜色和消息类型对应
    ERR_STR = "red"
    WARN_STR = "orange"
    SUC_STR = "green"


# ============================

def msgtype2str(msgtype):  # 消息类型转颜色
    if msgtype == MSG_TYPE.ERR:
        return MSG_TYPE.ERR_STR
    elif msgtype == MSG_TYPE.WARN:
        return MSG_TYPE.WARN_STR
    elif msgtype == MSG_TYPE.SUC:
        return MSG_TYPE.SUC_STR
    else:
        return "white"


def Pop_Top_message(root, type=MSG_TYPE.SUC, msgstr: str = "test msg", TTL=3000):  # 弹出消息提示
    # global MSG_QUEUE

    MessageFrame = tk.Frame(root, width=150, height=30, bg=msgtype2str(type))
    MessageLabel = tk.Label(MessageFrame, text=msgstr, bg="white", fg="black", font=STYLE.MSYHFontBigger10)
    # MSG_QUEUE.put(MessageFrame)

    MessageLabel.place(x=2, y=2)

    MessageFrame.update()
    MessageLabel.update()

    MessageFrame.configure(width=MessageLabel.winfo_width() + 4, height=MessageLabel.winfo_height() + 4)
    # 根据消息队列调整消息框y轴位置

    MessageFrame.place(relx=0.5, anchor=tk.CENTER, y=30)
    MessageFrame.lift()

    MessageFrame.after(TTL, MSG_QUEUE.get().destroy)
