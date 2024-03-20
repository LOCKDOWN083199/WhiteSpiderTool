import tkinter as tk
import queue
import if_connection
import regedit_fun
import motions


class networkview:
    def __init__(self, root, networkcard: dict = {}, cardname: str = 'network', place_set=(10, 10),
                 frame_size=(180, 300), font=('Consolas', 8)):
        # =========================公用属性部分
        self.networkcard: dict = networkcard  # 网卡信息
        self.root = root  # 上级组件
        self.place_set = place_set  # 最终位置
        # self.FactSize= (0, 0)  # 实际大小(因为有动画效果,所以本体大小会变化,因此需要记录非动画的实际大小)
        # self.FactPlace = (0, 0)  # 实际位置(因为有动画效果,所以本体位置会变化,因此需要记录非动画的实际位置)
        self.font = font  # 字体
        self.frame: tk.Frame = None  # 本级frame,使用一个frame承载所有控件
        self.frame_size = frame_size  # 本级frame大小
        self.canvas_size = (frame_size[0] * 0.9, 80)  # 画布大小
        self.RecvDataQueue = queue.Queue(maxsize=10)  # 存储10秒内收到的字节数据,1s一个数据
        self.SendDataQueue = queue.Queue(maxsize=10)  # 存储10秒内发送的字节数据
        for i in range(0, 10):
            self.RecvDataQueue.put(0)  # RecvDataQueue初始置0
        for i in range(0, 10):
            self.SendDataQueue.put(0)  # SendDataQueue初始置0

        self.RecvPacks_t1 = if_connection.Bytes_Recv_From_PowerUP()  # 第(前)1s收到的字节数据值储存
        self.SendPacks_t1 = if_connection.Bytes_Send_From_PowerUP()  # 第(前)1s发送的字节数据值储存

        self.LeftMouseClick = False  # 鼠标左键是否在frame内按下



        # =========================frame部分
        # r, g, b = 49, 181, 221  # RGB颜色值rgb(49, 181, 221)
        # frame_border_color = '#{:02x}{:02x}{:02x}'.format(r, g, b)  # 转换为十六进制颜色代码
        frame_border_color = "#1cd66c"
        self.frame = tk.Frame(self.root, highlightbackground=frame_border_color, highlightthickness=2,
                              width=self.frame_size[0],
                              height=self.frame_size[1])
        self.frame.place(anchor=tk.NW, x=self.place_set[0], y=self.place_set[1])

        # self.FactSize=(self.frame.winfo_width(),self.frame.winfo_height())
        # self.FactPlace=(self.frame.winfo_x(),self.frame.winfo_y())

        # =========================折线图部分
        self.canvas = tk.Canvas(self.frame, width=self.canvas_size[0], height=self.canvas_size[1] + 4)  # +4是为了让折线不贴着边框
        self.canvas.place(relx=0.05, rely=0.17, anchor=tk.NW, relwidth=0.9)

        # =========================上行实时速度部分
        self.SpeedSendLabel = tk.Label(self.frame, text="-" + "kb", font=self.font, width=12, height=1, fg="#0c77d6")
        self.SpeedSendLabel.place(relx=0.03, rely=0.1, anchor=tk.NW)

        # =========================下行实时速度部分
        self.SpeedRecvLabel = tk.Label(self.frame, text="-" + "kb", font=self.font, width=12, height=1, fg="green")
        self.SpeedRecvLabel.place(relx=0.53, rely=0.1, anchor=tk.NW)

        # =========================网卡名称栏
        # self.NetworkCardFrame = tk.Frame(self.frame, width=self.frame_size[0], height=20)
        # self.NetworkCardFrame.place(x=0, y=-25, anchor=tk.CENTER)
        # self.NetworkCardNameLabel=tk.Label(self.NetworkCardFrame,text=networkcard,font=self.font,width=self.frame_size[0],height=20)
        # self.NetworkCardNameLabel.place(x=self.frame_size[0]/2,y=0,anchor=tk.CENTER)
        self.NetworkCardNameLabel = tk.Label(self.frame, text=self.networkcard.keys(), font=('Consolas', 14),
                                             bg="#118945", fg="white")  # width=5,height=1,
        self.NetworkCardNameLabel.place(relx=0, rely=0, anchor=tk.NW, relwidth=1, relheight=0.1)

        # =========================拖动模块
        self.frame.bind("<Button-1>", self.LeftMouseDown)  # 绑定鼠标左键点击事件
        self.frame.bind("<ButtonRelease-1>", self.LeftMouseUp)  # 绑定鼠标左键释放事件
        self.frame.bind("<B1-Motion>", self.do_move)  # 绑定鼠标左键+移动事件

        # =========================鼠标划过反应模块
        self.frame.bind("<Enter>", self.mouse_enter)  # 绑定鼠标划入事件
        self.frame.bind("<Leave>", self.mouse_leave)  # 绑定鼠标划出事件
        self.mouse_exit = True  # 鼠标是否划出

        # =========================刷新模块/回调函数管理区
        self.flash_chart()
        # self.MoveToPoint()

    def mouse_enter(self, event):  # 鼠标划过组件响应
        self.frame.config(
            highlightbackground="#e8585f")  # , width=self.frame_size[0] + 10, height=self.frame_size[1] + 10
        # self.frame.place(x=self.frame.winfo_x()-5,y=self.frame.winfo_y()-5)
        self.mouse_exit = False
        self.mouse_motion_delay()

    def mouse_motion_delay(self):
        i = 2  # 速率系数，越大动画速度越快。建议设置为可整除的数，建议为2的倍数
        dx = i  # 每次重绘x轴移动值
        dy = (self.frame_size[1] / self.frame_size[0]) * i  # 每次重绘y轴移动值

        # 鼠标进入frame时,frame的大小逐渐增大,且frame的位置向左上角移动
        if self.frame.winfo_width() <= self.frame_size[0] + 10 and self.mouse_exit == False:
            self.frame.place(x=self.frame.winfo_x() - (dx * 0.5), y=self.frame.winfo_y() - (dy * 0.5))
            self.frame.configure(width=self.frame.winfo_width() + dx,
                                 height=self.frame.winfo_height() + dy)

            self.frame.after(30 + 5 * (i - 2), self.mouse_motion_delay)  # 延时重绘,且延时时间随速率系数增大而减小

        # 鼠标离开frame时,frame的大小逐渐减小,且frame的位置向右下角移动
        elif self.mouse_exit == True and self.frame.winfo_width() >= self.frame_size[0]:
            self.frame.place(x=self.frame.winfo_x() + (dx * 0.5), y=self.frame.winfo_y() + (dy * 0.5))
            self.frame.configure(width=self.frame.winfo_width() - dx,
                                 height=self.frame.winfo_height() - dy)
            self.frame.after(30 + 5 * (i - 2), self.mouse_motion_delay)  # 延时重绘,且延时时间随速率系数增大而减小

    def mouse_leave(self, event):  # 鼠标离开组件
        self.frame.config(highlightbackground="#1cd66c")
        self.mouse_exit = True
        self.mouse_motion_delay()

    def LeftMouseDown(self, event):  # 鼠标左键点击后拖拽
        # 记录鼠标左键点击的初始位置
        self.framex = event.x
        self.framey = event.y

        self.LeftMouseClick = True

    def LeftMouseUp(self, event):  # 停止拖拽
        # 鼠标左键释放，清除记录的位置信息
        self.framex = None
        self.framey = None

        self.LeftMouseClick = False

    def do_move(self, event):  # 拖拽运算
        # 鼠标左键移动，计算移动的距离dx, dy
        dx = event.x - self.framex  # - self.frame_size[0]-70 #如果frame设置了relx，rely，这里要减去相应的值
        dy = event.y - self.framey  # - self.frame_size[1]-50
        # 计算窗口新的位置
        x = self.frame.winfo_x() + dx
        y = self.frame.winfo_y() + dy
        # 更新窗口的位置
        self.frame.place(x=x, y=y)

    def draw_chart(self):  # canvas刷新控制函数
        # print("draw_chart")
        self.canvas.delete('all')
        self.canvas.configure(bg="#e6e6e6")

        RecvDataList = list(self.RecvDataQueue.queue)
        RecvMaxData = max(RecvDataList)
        if RecvMaxData == 0:
            RecvMaxData = 1

        SendDataList = list(self.SendDataQueue.queue)
        SendMaxData = max(SendDataList)
        if SendMaxData == 0:
            SendMaxData = 1

        self.draw_LinePoint(maxdata=RecvMaxData, datalist=RecvDataList)
        self.draw_LinePoint(maxdata=SendMaxData, datalist=SendDataList, is_Recv=False)

    def draw_LinePoint(self, is_Recv=True, maxdata=1, datalist=[]):
        normalized_data = [x / maxdata * (self.canvas_size[1]) for x in datalist]  # 按比例计算每个点的y值大小
        for i in range(1, len(normalized_data)):
            y1 = self.canvas_size[1] - normalized_data[i - 1] + 4  # +4是为了让折线不贴着边框
            y2 = self.canvas_size[1] - normalized_data[i] + 4
            x1 = (i - 1) * self.canvas.winfo_width() / 9.5
            x2 = i * self.canvas.winfo_width() / 9.5

            if is_Recv == True:
                r, g, b = 15 + 3 * i, 255 - 8 * i, 160 - i * 9  # 线条调色
                color = '#{:02x}{:02x}{:02x}'.format(r, g, b)

                self.canvas.create_line(x1, y1, x2, y2, fill=color, width=1)  # 画折线
                self.canvas.create_oval(x2 - 1, y2 - 1, x2 + 1, y2 + 1, fill=color, outline="#0a552b")  # 画数据点
            else:
                r, g, b = 70 + 7 * i, 230 - 8 * i, 255  # 线条调色
                color = '#{:02x}{:02x}{:02x}'.format(r, g, b)

                self.canvas.create_line(x1, y1, x2, y2, fill=color, width=1)  # 画折线
                self.canvas.create_oval(x2 - 1, y2 - 1, x2 + 1, y2 + 1, fill=color, outline="blue")  # 画数据点

    def update_DataQueue(self, update_queue: queue, new_data):
        if update_queue.full():
            update_queue.get()
        update_queue.put(new_data)

    # def MoveToPoint(self, x=0, y=0):
    #     speed_factor = 1  # 速率系数
    #     dx, dy = 0, 0
    #     if self.LeftMouseClick == False:
    #         dx, dy = motions.move_to(self.FactPlace[0], self.FactPlace[1], self.place_set[0], self.place_set[1], speed_factor)
    #         self.frame.place(x=self.frame.winfo_x() + dx, y=self.frame.winfo_y() + dy)
    #     self.frame.after(50, self.MoveToPoint, dx, dy)

    def flash_chart(self):
        self.update_DataQueue(update_queue=self.RecvDataQueue,
                              new_data=(if_connection.Bytes_Recv_From_PowerUP() - self.RecvPacks_t1))
        self.update_DataQueue(update_queue=self.SendDataQueue,
                              new_data=(if_connection.Bytes_Send_From_PowerUP() - self.SendPacks_t1))
        self.RecvPacks_t1 = if_connection.Bytes_Recv_From_PowerUP()
        self.SendPacks_t1 = if_connection.Bytes_Send_From_PowerUP()

        self.draw_chart()

        self.SpeedSendLabel.config(text="up:" + str(if_connection.format_speed(self.SendDataQueue.queue[-1])))
        self.SpeedRecvLabel.config(text="dw:" + str(if_connection.format_speed(self.RecvDataQueue.queue[-1])))
        self.frame.after(1000, self.flash_chart)

        # print(if_connection.Bytes_Recv_From_PowerUP())

    # def format_speed(self, speed) -> str:
    #     # 速度转换
    #     if speed < 1024:  # < 1 KB
    #         return f"{speed}B/s"
    #     elif speed < 1024 ** 2:  # < 1 MB
    #         return f"{speed / 1024:.2f}KB/s"
    #     elif speed < 1024 ** 3:  # < 1 GB
    #         return f"{speed / 1024 ** 2:.2f}MB/s"
    #     else:  # > 1 GB
    #         return f"{speed / 1024 ** 3:.2f}GB/s"


root = tk.Tk()
root.geometry("1000x600")
root.configure(bg="#dfe1e5")
wk = regedit_fun.Get_Network_Info_By_AllCard()
l = []
ii = 0
for i, v in wk.items():
    t = networkview(root, {i: v}, cardname=i, place_set=(10, 10 + 300 * len(l)))
    l.append(t)
    ii += 1
print(ii)
root.mainloop()
