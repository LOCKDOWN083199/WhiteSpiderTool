# ============================
# 此模块用于获取和转换网卡流量的各种信息
# ============================

import psutil


# 自从开机后X网卡累计接收字节数
def Bytes_Recv_From_PowerUP(Card_Name="WLAN") -> int:
    card = dict(psutil.net_io_counters(pernic=True))[f"{Card_Name}"]
    return card.bytes_recv


# 自从开机后X网卡累计发送字节数
def Bytes_Send_From_PowerUP(Card_Name="WLAN") -> int:
    card = dict(psutil.net_io_counters(pernic=True))[f"{Card_Name}"]
    return card.bytes_sent


# 自从开机后X网卡累计接收数据包数
def Packets_Recv_From_PowerUP(Card_Name="WLAN") -> int:
    card = dict(psutil.net_io_counters(pernic=True))[f"{Card_Name}"]
    return card.packets_recv


# 自从开机后X网卡累计发送数据包数
def Packets_Send_From_PowerUP(Card_Name="WLAN") -> int:
    card = dict(psutil.net_io_counters(pernic=True))[f"{Card_Name}"]
    return card.packets_sent


# 自从开机后X网卡累计错误发送数据包数
def Errout_Send_From_PowerUP(Card_Name="WLAN") -> int:
    card = dict(psutil.net_io_counters(pernic=True))[f"{Card_Name}"]
    return card.errout


# 自从开机后X网卡累计错误接收数据包数
def Errin_Recv_From_PowerUP(Card_Name="WLAN") -> int:
    card = dict(psutil.net_io_counters(pernic=True))[f"{Card_Name}"]
    return card.errin


# 自从开机后X网卡累计丢掉发送数据包数
def Dropout_Send_From_PowerUP(Card_Name="WLAN") -> int:
    card = dict(psutil.net_io_counters(pernic=True))[f"{Card_Name}"]
    return card.dropout


# 自从开机后X网卡累计丢掉接收数据包数
def Dropin_Recv_From_PowerUP(Card_Name="WLAN") -> int:
    card = dict(psutil.net_io_counters(pernic=True))[f"{Card_Name}"]
    return card.dropin


def Card_Speed(Card_Name="WLAN", Time: float = 1) -> float:
   pass


# 判断网卡是否连接
def Card_Connected(Card_Name="WLAN") -> bool:
    # 说明:禁用网卡会导致psutil无法通过网卡名获取网卡状态,所以需要先判断网卡名是否存在,如果网卡名也不存在,则可认为网卡未连接
    net_if_stats = psutil.net_if_stats() # 获取网卡状态
    if Card_Name in net_if_stats: # 如果网卡存在
        status = net_if_stats[Card_Name] # 获取网卡状态
        return status.isup # 返回网卡是否连接
    else:
        return False

# 速度转换
def format_speed(speed) -> str:

    if speed < 1024:  # < 1 KB
        return f"{speed}B/s"
    elif speed < 1024 ** 2:  # < 1 MB
        return f"{speed / 1024:.2f}KB/s"
    elif speed < 1024 ** 3:  # < 1 GB
        return f"{speed / 1024 ** 2:.2f}MB/s"
    else:  # > 1 GB
        return f"{speed / 1024 ** 3:.2f}GB/s"

# for i in range(0,10):
#     print(Packets_Recv_From_PowerUP())
#     time.sleep(1)
