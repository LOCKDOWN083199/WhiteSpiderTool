import tkinter as tk
import winreg


def set_dns(dns_server):
    try:
        # 打开注册表项
        with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, "SYSTEM\\CurrentControlSet\\Services\\Tcpip\\Parameters", 0,
                            winreg.KEY_SET_VALUE) as key:
            # 设置DNS服务器
            winreg.SetValueEx(key, "DNS Server", 0, winreg.REG_SZ, dns_server)
            # 重置TCP/IP堆栈
            winreg.SetValueEx(key, "Reset TCPIP", 0, winreg.REG_SZ, "1")
            winreg.SetValueEx(key, "Force Reset", 0, winreg.REG_SZ, "1")
            # 重启计算机以使更改生效
        import os
        os.system("shutdown /r /t 1")
    except Exception as e:
        print(f"Error: {e}")


def change_dns():
    # 获取输入的DNS服务器地址
    dns_server = entry.get()
    # 设置DNS服务器
    set_dns(dns_server)


# 创建GUI窗口
window = tk.Tk()
window.title("DNS设置工具")
window.geometry("300x200")

# 添加输入框和按钮
label = tk.Label(window, text="请输入DNS服务器地址：")
label.pack(pady=10)
entry = tk.Entry(window)
entry.pack()
button = tk.Button(window, text="设置DNS", command=change_dns)
button.pack()

# 运行GUI窗口
window.mainloop()