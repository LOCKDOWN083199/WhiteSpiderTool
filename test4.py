# import tkinter as tk
#
# class DraggableFrame:
#     def __init__(self, root):
#         self.root = root  # 主窗口
#         self.frame = tk.Frame(root, width=100, height=100, bg='red')  # 创建一个Frame
#         self.frame.pack()
#
#         # 绑定鼠标左键点击事件
#         self.frame.bind("<Button-1>", self.start_move)
#         # 绑定鼠标左键释放事件
#         self.frame.bind("<ButtonRelease-1>", self.stop_move)
#         # 绑定鼠标左键移动事件
#         self.frame.bind("<B1-Motion>", self.do_move)
#
#     def start_move(self, event):
#         # 记录鼠标左键点击的初始位置
#         self.x = event.x
#         self.y = event.y
#
#     def stop_move(self, event):
#         # 鼠标左键释放，清除记录的位置信息
#         self.x = None
#         self.y = None
#
#     def do_move(self, event):
#         # 鼠标左键移动，计算移动的距离dx, dy
#         dx = event.x - self.x
#         dy = event.y - self.y
#         # 计算窗口新的位置
#         x = self.root.winfo_x() + dx
#         y = self.root.winfo_y() + dy
#         # 更新窗口的位置
#         self.root.geometry(f"+{x}+{y}")
#
# root = tk.Tk()
# df = DraggableFrame(root)
# root.mainloop()

# import tkinter as tk
#
# class HoverFrame:
#     def __init__(self, root):
#         self.root = root
#         self.frame = tk.Frame(root, bg="black", width=100, height=100)
#         self.frame.pack()
#
#         # 绑定鼠标进入事件
#         self.frame.bind("<Enter>", self.on_enter)
#         self.frame.bind("<Leave>", self.on_leave)
#
#     def on_enter(self, event):
#         # 鼠标进入frame，逐渐增大frame的大小
#         self.expand_frame()
#
#     def on_leave(self, event):
#         # 鼠标离开frame，恢复frame的大小
#         self.frame.config(width=100, height=100)
#
#     def expand_frame(self):
#         # 获取当前frame的大小
#         width = self.frame.winfo_width()
#         height = self.frame.winfo_height()
#
#         # 如果frame的大小小于200，那么增大frame的大小
#         if width < 200 and height < 200:
#             self.frame.config(width=width+10, height=height+10)
#             # 100毫秒后再次调用expand_frame函数
#             self.frame.after(100, self.expand_frame)
#
# root = tk.Tk()
# root.geometry("500x500")
# hf = HoverFrame(root)
# root.mainloop()

# import tkinter as tk
#
# root = tk.Tk()
#
# # 创建顶级菜单
# menu = tk.Menu(root)
#
# # 创建第一级菜单
# filemenu = tk.Menu(menu, tearoff=0)
# menu.add_cascade(label="文件", menu=filemenu)
#
# # 在第一级菜单中创建第二级菜单
# submenu = tk.Menu(filemenu, tearoff=0)
# filemenu.add_cascade(label="子菜单", menu=submenu)
#
# # 在第二级菜单中添加命令，这将是第三级选项
# submenu.add_command(label="选项1", command=None)
# submenu.add_command(label="选项2", command=None)
#
# root.config(menu=menu)
# root.mainloop()
# import tkinter as tk
#
# # 创建主窗口
# root = tk.Tk()
#
# # 创建一个Canvas
# canvas = tk.Canvas(root)
# canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
#
# # 创建一个滚动条，并关联到Canvas
# scrollbar = tk.Scrollbar(root, command=canvas.yview)
# scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
#
# # 将Canvas的滚动设置为滚动条的移动
# canvas.configure(yscrollcommand=scrollbar.set)
#
# # 创建一个Frame，并放入Canvas
# frame = tk.Frame(canvas)
# canvas.create_window((0,0), window=frame, anchor='nw')
#
# # 在Frame中创建多个可编辑的Text组件
# for i in range(100):
#     text = tk.Text(frame, height=1, width=20)
#     text.insert(tk.END, str(i))
#     text.pack()
#
# # 更新滚动区域的大小
# frame.update_idletasks()
# canvas.config(scrollregion=canvas.bbox('all'))
#
# root.mainloop()

from bin import networkCtl
import json

# 在networkCtl传来的字典中将'以太网'键值对筛选出来,并将其写入json文件
def write_json(data, filename='tmp3.json'):
    with open(filename, 'w') as f:
        json.dump(data, f, indent=4)

def main():
    network_info = networkCtl.Get_Network_Info_By_AllCard()
    eth_info = {}
    for k, v in network_info.items():
        if '以太网' == k:
            eth_info[k] = v
    write_json(eth_info)

if __name__ == '__main__':
    main()
