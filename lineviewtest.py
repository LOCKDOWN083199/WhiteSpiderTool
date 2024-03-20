import tkinter

win=tkinter.Tk()
win.title("test")
win.geometry("300x300")
cav=tkinter.Canvas(win,width=300,height=300,bg="white")
cav.create_oval(50,50,100,100,fill="white",outline="#e83849")
cav.pack()
win.mainloop()