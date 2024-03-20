# ============================
# 此模块用于操作注册表
# ============================

# ----------------------------
# 开发说明:据观察,wmi貌似并不能根据网络适配器筛选网卡,因此使用注册表查找、筛选并整理网卡数据;wmi用于修改网卡配置
# ----------------------------

import winreg
import wmi
import re
import os
from bin import if_connection


# 遍历注册表网卡参数
# 返回值说明：
# {
#     '注册表路径':{
#                     'ip属性':值,
#                     '掩码属性':值,
#                     ...
#                 },
#     ...
# }
def Get_All_Networks_Info(key_path=r"SYSTEM\CurrentControlSet\Services\Tcpip\Parameters\Interfaces") -> dict:
    key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, key_path)
    result = {}

    for i in range(0, winreg.QueryInfoKey(key)[0]):
        sub_key_path = key_path + "\\" + winreg.EnumKey(key, i)
        sub_key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, sub_key_path)
        result[f"{sub_key_path}"] = {}

        for j in range(0, winreg.QueryInfoKey(sub_key)[1]):
            ttuple = winreg.EnumValue(sub_key, j)
            if ttuple[0] == 'DhcpInterfaceOptions':
                continue

            # 将bytes类型转换成str
            if type(ttuple[1]) == bytes:
                result[f"{sub_key_path}"][f"{ttuple[0]}"] = str(ttuple[1])
            else:
                result[f"{sub_key_path}"][f"{ttuple[0]}"] = ttuple[1]

        Get_All_Networks_Info(sub_key_path)
        winreg.CloseKey(sub_key)

    winreg.CloseKey(key)
    return result


# print(Get_All_Networks_Info()) #测试函数
# print(len(Get_All_Networks_Info()))


# 将网卡名和注册表查到的信息绑定
# 返回值说明:
# {
#     '网卡名':{
#                 'ip属性':值,
#                 '掩码属性':值,
#                 ...
#             },
#     ...
# }
def Get_Network_Info_By_CardName(key_path=r'SOFTWARE\Microsoft\Windows NT\CurrentVersion\NetworkCards') -> dict:
    ifcfgs = Get_All_Networks_Info()
    iflist = {}
    tlist = {}

    key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, key_path)
    for i in range(0, winreg.QueryInfoKey(key)[0]):
        sub_key_path = key_path + "\\" + winreg.EnumKey(key, i)

        tlist[str(i)] = {}

        sub_key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, sub_key_path)
        for j in range(0, winreg.QueryInfoKey(sub_key)[1]):
            ttuple = winreg.EnumValue(sub_key, j)
            tlist[str(i)][ttuple[0]] = ttuple[1]

        # Get_Network_Info_By_CardName(sub_key_path)
        winreg.CloseKey(sub_key)
    winreg.CloseKey(key)
    for i in range(0, len(tlist)):
        for j in ifcfgs:
            if j.find(tlist[str(i)]["ServiceName"].lower()) != -1:
                iflist[f"{tlist[str(i)]['Description']}"] = ifcfgs[j].values()

    return iflist


# Get_Network_Info_By_CardName() # 测试函数


# 获得所有已知网卡的信息(物理网卡和虚拟网卡)
# 返回值说明:
# {
#     '网卡名称':{
#                     'cfg':{
#                                 (网卡配置信息)
#                                 'ip信息':"xxx",
#                                 '掩码信息':"xxx",
#                                 ...
#                           },
#                     'GUID':'值', #GUID标识符
#                     'MediaSubType':'eth' | 'wifi' | 'other', #初步判定是无线还是有线
#                     'PnPInstanceId':'值' #此值用于简单判定是否为虚拟网卡
#               },
#     ...
# }
def Get_Network_Info_By_AllCard(
        key_path=r'SYSTEM\CurrentControlSet\Control\Network\{4D36E972-E325-11CE-BFC1-08002BE10318}') -> dict:
    ifcfg = Get_All_Networks_Info()
    iflist = {}  # 用于储存所有网卡的所有信息

    # 此部分循环用于获取所有网卡的网卡名和GUID存入iflist,并把硬件id,网卡类型等信息存入iflist
    # ====================================================================================================
    key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, key_path)
    for i in range(0, winreg.QueryInfoKey(key)[0]):  # i代表 表里的第i张网卡
        if winreg.EnumKey(key, i)[0] == "{":
            sub_key_path = key_path + "\\" + winreg.EnumKey(key, i) + "\\Connection"
        else:
            continue

        try:
            winreg.CloseKey(sub_key)
        except Exception as e:  # 以后可以加报错日志点
            # print(e)
            pass

        sub_key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, sub_key_path)

        for j in range(0, winreg.QueryInfoKey(sub_key)[1]):  # j代表表的第j个键

            # 取网卡名和GUID绑定
            if winreg.EnumValue(sub_key, j)[0] == "Name":
                iflist[f"{winreg.EnumValue(sub_key, j)[1]}"] = {}
                iflist[f"{winreg.EnumValue(sub_key, j)[1]}"]["GUID"] = winreg.EnumKey(key, i).lower()

                for k in range(0, winreg.QueryInfoKey(sub_key)[1]):

                    # 判断无线/有线网卡
                    if winreg.EnumValue(sub_key, k)[0] == "MediaSubType":
                        # 有线网卡
                        if winreg.EnumValue(sub_key, k)[1] == 1:
                            iflist[f"{winreg.EnumValue(sub_key, j)[1]}"]["Type"] = "eth"
                        # 无线网卡
                        elif winreg.EnumValue(sub_key, k)[1] == 2:
                            iflist[f"{winreg.EnumValue(sub_key, j)[1]}"]["Type"] = "wifi"
                        # 其他类型
                        else:
                            iflist[f"{winreg.EnumValue(sub_key, j)[1]}"]["Type"] = "other"

                    # 取机器ID,用于简单判断物理卡和虚拟卡
                    elif winreg.EnumValue(sub_key, k)[0] == "PnPInstanceId":
                        iflist[f"{winreg.EnumValue(sub_key, j)[1]}"]["PnPInstanceId"] = winreg.EnumValue(sub_key, k)[1]
            else:
                continue

    # 此部分将配置信息和网卡信息绑定
    # ====================================================================================================
    CfgExsit = False  # 用于判断是否有配置信息,即是否有ifcfg[k]是否有值
    tiflist = iflist.copy()  # 用于遍历iflist
    for i, v in tiflist.items():  # i是iflist储存的网卡名; v储存非配置信息(包括GUID),需要GUID来绑定网卡名和网卡配置信息
        for k in ifcfg:  # k是regedit表绝对路径
            if k.find(v["GUID"].lower()) != -1:  # 通过GUID绑定网卡名和网卡配置信息
                iflist[i]["cfg"] = ifcfg[k]  # 将配置信息绑定在iflist["网卡名"]["cfg"]中
                ifcfg.pop(k)  # 避免重复绑定
                CfgExsit = True  # ifcfg有配置信息
                break
        if CfgExsit == False:  # ifcfg中没有配置信息
            iflist.pop(i)  # 则视为无用网卡,删除
        else:
            CfgExsit = False

    tiflist = iflist.copy()  # 用于临时遍历iflist
    for i in tiflist.keys():
        try:  # 用于判断网卡是否连接(是否能监测流量)
            if_connection.Bytes_Recv_From_PowerUP(i)
        except KeyError:  # 无法监测流量,则视为无用网卡,删除
            iflist.pop(i)

    # 用wmi和注册表，将网卡的Description属性加入iflist
    # ====================================================================================================
    c = wmi.WMI()
    for interface in c.Win32_NetworkAdapterConfiguration():  # 遍历所有网卡
        for i in iflist.keys():
            # 查找是否存在子串
            if str(interface.SettingID).lower().find(iflist[i]["GUID"]) != -1:
                iflist[i]["Description"] = interface.Description
                break

    # winreg.CloseKey(sub_key)
    winreg.CloseKey(key)
    return iflist


# print( Get_Network_Info_By_AllCard())  # 测试函数
# print(len(Get_Network_Info_By_AllCard()))
Get_Network_Info_By_AllCard()


# [变更]通过wmi修改IP地址
def Set_IP_WMI(cardname: str = "", ip=[], mask=[], gateway=[]) -> bool:
    c = wmi.WMI()
    for interface in c.Win32_NetworkAdapterConfiguration():  # 遍历所有网卡
        # print(interface.NetConnectionID, cardname, interface.NetConnectionID == cardname)
        if interface.Description == cardname:
            try:
                interface.EnableStatic(IPAddress=ip, SubnetMask=mask)
                interface.SetGateways(DefaultIPGateway=gateway, GatewayCostMetric=[9999] * len(gateway))
                return True
            except Exception as e:
                print(e)
                return False
    return False


# [变更]修改dns
def Set_DNS_WMI(cardname: str = "", dns=[]) -> tuple:
    c = wmi.WMI()
    for interface in c.Win32_NetworkAdapterConfiguration():  # 遍历所有网卡
        if interface.Description == cardname:
            try:
                r = interface.SetDNSServerSearchOrder(DNSServerSearchOrder=dns)
                # print(type(r[0]))
                return r
            except Exception as e:
                print(e)
                return False, e
    return False, "NULL False"


# [变更]根据传入的status变更dhcp状态
def Set_DHCP_WMI(cardname: str = "", status=True):
    c = wmi.WMI()
    for interface in c.Win32_NetworkAdapterConfiguration():  # 遍历所有网卡
        if interface.Description == cardname:
            try:
                if status:
                    print(interface.EnableDHCP())
                else:
                    print(interface.DisableDHCP())
                return True
            except Exception as e:
                print(e)
                return False
    return False


# 将子网掩码值转换为数字值,如255.255.255.0转换成24
def MaskToNum(mask: str) -> int:
    # 验证输入是否合法
    if not re.match(r"(\d{1,3}\.){3}\d{1,3}", mask):
        return -1  # 输入不合法

    mask = mask.split(".")
    mask = [int(i) for i in mask]
    mask = sum([bin(i).count("1") for i in mask])
    return mask


# 将数字值转换为子网掩码,如24转换成255.255.255.0
def NumToMask(num: int) -> str:
    # 验证输入是否合法
    if num < 0 or num > 32:
        return "ERR"  # 输入不合法

    mask = [0, 0, 0, 0]
    for i in range(0, num):
        mask[i // 8] = mask[i // 8] + (1 << (7 - i % 8))
    return ".".join([str(i) for i in mask])


# 将"192.168.1.1/24"转换成"192.168.1.1"和"24"
def IPWithMaskToIPAndMask(ipwithmask: str) -> tuple:
    # 验证输入是否合法
    if not re.match(r"(\d{1,3}\.){3}\d{1,3}/\d{1,2}", ipwithmask):
        return "ERR", -1  # 输入不合法

    ipwithmask = ipwithmask.split("/")
    return ipwithmask[0], int(ipwithmask[1])


# 将"192.168.1.1"和"24"转换成"192.168.1.1/24"
def IPAndMaskToIPWithMask(ip: str, mask: int) -> str:
    # 验证输入是否合法
    if not re.match(r"(\d{1,3}\.){3}\d{1,3}", ip) or mask < 0 or mask > 32:
        return "ERR"  # 输入不合法

    return f"{ip}/{mask}"


def Set_IP_Netsh(cardname: str = "", ip=[], mask=[], gateway=[]) -> bool:
    # 清除原有IP
    try:
        os.system(f"netsh interface ip set address name=\"{cardname}\" source=dhcp")
    except Exception as e:
        print(e, "清除原有IP失败")
        return False

    # # 清除原有网关
    # try:
    #     os.system(f"netsh interface ip delete address name=\"{cardname}\" gateway=all")
    # except Exception as e:
    #     print(e, "清除原有网关失败")
    #     return False

    # 设置新IP
    # os.system(f"netsh interface ip set address name=\"{cardname}\" source=static")
    try:
        for i in range(0, len(ip)):
            os.system(f"netsh interface ip add address name=\"{cardname}\" addr={ip[i]} mask={mask[i]}")
        # os.system(f"netsh interface ip set address name=\"{cardname}\" source=static addr={ip} mask={mask} gateway={gateway} gwmetric=1")
    except Exception as e:
        print(e, "设置IP失败")
        return False

    # 设置新网关
    try:
        for i in range(0, len(gateway)):
            os.system(f"netsh interface ip add address name=\"{cardname}\" gateway={gateway[i]} gwmetric=9999")
        return True
    except Exception as e:
        print(e, "设置网关失败")
        return False


def Set_DHCP_Netsh(cardname: str = "") -> bool:
    try:
        os.system(f"netsh interface ip set address name=\"{cardname}\" source=dhcp")
        return True
    except Exception as e:
        print(e, "设置DHCP失败")
        return False


def Set_DNS_Netsh(cardname: str = "", dns=[]) -> bool:
    # 清除原有DNS
    try:
        os.system(f"netsh interface ip delete dns name=\"{cardname}\" all")
    except Exception as e:
        print(e, "清除原有DNS失败")
        return False

    # 设置新DNS
    try:
        for i in range(0, len(dns)):
            os.system(f"netsh interface ip add dns name=\"{cardname}\" addr={dns[i]} index={i + 1}")
        return True
    except Exception as e:
        print(e, "设置DNS失败")
        return False


# command = 'netsh interface ip add address name="以太网" addr=192.168.1.2 mask=255.255.255.0'
# result = os.popen(command).read()
# print(result)

# print(Set_IP_Netsh("以太网", ["192.168.100.100", "192.168.100.200","192.168.1.1"], ["255.255.255.0", "255.255.255.0","255.255.255.0"], ["192.168.100.1","192.168.100.2"]))
# Set_DNS_Netsh("以太网", ["1.1.1.1","2.2.2.2","3.3.3.3","4.4.4.4","5.5.5.5"])