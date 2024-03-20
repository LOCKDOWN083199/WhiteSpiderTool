import winreg


def traverse_registry_folder(key_path):
    key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, key_path)

    for i in range(0, winreg.QueryInfoKey(key)[0]): #winreg.QueryInfoKey(key) 返回：1.子键数量 2.当前key值 3.修改时间
        try:
            sub_key = winreg.EnumKey(key, i)
            new_path=key_path+"\\"+sub_key
            print(f"{key_path}\\{sub_key}={winreg.QueryValue(winreg.HKEY_LOCAL_MACHINE,new_path)}")
            tkey=winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE,new_path)
            for j in range(0,winreg.QueryInfoKey(tkey)[0]):
                infokey = winreg.EnumKey(tkey,j)
                print(f"{infokey}:{winreg.QueryValueEx(winreg.HKEY_LOCAL_MACHINE,infokey)}")

            sub_key_handle = winreg.OpenKey(key, sub_key)
            traverse_registry_folder(f"{key_path}\\{sub_key}")
            winreg.CloseKey(sub_key_handle)
        except WindowsError as we:
            print(we)
            pass

    winreg.CloseKey(key)


# 调用遍历函数，开始遍历注册表文件夹
traverse_registry_folder("SYSTEM\CurrentControlSet\Services\Tcpip\Parameters\Interfaces")