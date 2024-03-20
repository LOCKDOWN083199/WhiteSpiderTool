# import tkinter
#
# win=tkinter.Tk()
# win.title("test")
# win.geometry("300x300")
#
# text="abc"
# l=tkinter.Label(win,text=text,width=10,height=10,font=('Arial',12))
# l.pack()
#
#
#
# win.mainloop()

# import tkinter as tk
#
# root = tk.Tk()
# canvas = tk.Canvas(root, width=500, height=500)
# canvas.pack()
#
#
# def draw(event):
#     x, y = event.x, event.y
#     canvas.create_line((x, y, x + 1, y + 1), width=2, fill="black")
#
#
# canvas.bind("<B1-Motion>", draw)
# root.mainloop()

# import tkinter as tk
# import math
#
# # Create a root window
# root = tk.Tk()
#
# # Now, create an image
# image = tk.PhotoImage(width=800, height=600)
#
# # Draw on the image
# for i in range(100):
#     x = i * 8
#     y = 300 + 100 * math.sin(i / 10)
#     image.put("#000000", (int(x), int(y))) # Convert coordinates to integers
#
# # Create a canvas
# canvas = tk.Canvas(root, width=800, height=600)
# canvas.pack()
#
# # Copy the image to the canvas
# canvas.create_image(0, 0, image=image, anchor=tk.NW)
#
# root.mainloop()

# import tkinter as tk
#
# root = tk.Tk()
#
# var = tk.IntVar()  # 创建一个整型变量，用于存储Checkbutton的状态
#
# check_button = tk.Checkbutton(root, text="开关按钮", variable=var)
# check_button.pack()
#
# root.mainloop()
import tkinter as tk

def on_select(event):
    # 获取当前选中的选项
    selected_option = listbox.get(listbox.curselection())
    # print(f"You selected: {selected_option}")
    label.config(text=selected_option)

root = tk.Tk()

# 创建一个Scrollbar
# scrollbar = tk.Scrollbar(root)
# scrollbar.pack(side='right', fill='y')

frame=tk.Frame(root,width=200,height=200)
frame.pack()

label = tk.Label(frame, text='test')
label.pack()

# 创建一个Listbox，并与Scrollbar关联
listbox = tk.Listbox(frame)
for i in range(1, 101):
    listbox.insert('end', 'Option {}'.format(i))
listbox.pack(side='left', fill='both')

listbox.bind('<<ListboxSelect>>', on_select)

# 将Scrollbar的command设置为Listbox的yview方法
# scrollbar.config(command=listbox.yview)

root.mainloop()