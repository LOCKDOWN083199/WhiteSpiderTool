# ============================
# 网络协议实现
# 规划的协议:icmp,tcp端口检测协议
# ============================

import time
import select
import socket
import struct
import re
from bin import messageCtl
from bin.globals import ICMP_TIMEOUT


# 计算校验和
def checksum(data):
    s = 0
    n = len(data) % 2
    for i in range(0, len(data) - n, 2):
        s += (data[i]) + ((data[i + 1]) << 8)
    if n:
        s += (data[i + 1])
    while (s >> 16):
        s = (s & 0xFFFF) + (s >> 16)
    s = ~s & 0xFFFF
    return s


# ip地址格式检查
def check_ip(ip):
    if re.match(r"(\d{1,3}\.){3}\d{1,3}", ip):  # 正则匹配IP地址
        return True
    else:
        return False


# ping功能
# 返回值:是否执行成功,是否收到回复
def ping(src_addr="Default", dest_addr=None, timeout=ICMP_TIMEOUT, seq=0, ping_data=b"This is a PING test!"):
    # print(src_addr, dest_addr)
    icmp = socket.getprotobyname('icmp')
    s = None
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_RAW, icmp)
        s.bind((src_addr, 0))
    except socket.error as e:
        if e.errno == 1:
            # messageCtl.Pop_Top_message(messageCtl.MSG_TYPE.ERR, "创建socket异常")
            print("ICMP messages can only be sent from processes running as root.")
            s.close()
            return False, None
    send_ping(s, dest_addr, seq, ping_data)
    result = receive_pong(s, dest_addr, timeout)
    s.close()
    return True, result


# 发送ICMP echo请求
def send_ping(s, dest_addr, seq, ping_data=b"This is a PING test!"):
    # ping_data转换为bytes类型
    if type(ping_data) == str:
        ping_data = ping_data.encode()
    # 去除data末尾可能存在的换行符
    if ping_data[-1] == 10:
        ping_data = ping_data[:-1]

    DataLen = str(len(ping_data))

    # 报头:type (8), code (8), checksum (16), id (16), sequence (16)
    packet = struct.pack('<BBHHH' + DataLen + 's', 8, 0, 0, 1, seq, ping_data)  # <表示小端模式
    packet1 = struct.pack('>BBHHH' + DataLen + 's', 8, 0, 0, 1, seq, ping_data)  # >表示大端模式
    # Checksum ICMP packet
    chksum = checksum(packet)
    packet = struct.pack('<BBHHH' + DataLen + 's', 8, 0, chksum, 1, seq, ping_data)
    packet1 = struct.pack('>BBHHH' + DataLen + 's', 8, 0, chksum, 1, seq, ping_data)
    s.sendto(packet, (dest_addr, 1))
    s.sendto(packet1, (dest_addr, 1))


# 接收ICMP echo响应
def receive_pong(s, dest_addr, timeout):
    time_remaining = timeout  # 剩余时间
    while True:  # 循环接收
        start_time = time.time()  # 开始时间
        readable = select.select([s], [], [], time_remaining)  # 阻塞函数,等待s可读,超时时间为time_remaining
        time_spent = (time.time() - start_time)  # 已经消耗的时间
        if readable[0] == []:  # Timeout
            print("Request timed out.", dest_addr)
            return False
        time_received = time.time()  # 接收到数据的时间
        packet, addr = s.recvfrom(1024)  # 接收数据
        # print(addr)
        icmp_header = packet[20:28]  # 提取ICMP头部
        type, code, checksum, packet_id, sequence = struct.unpack('!BBHHH', icmp_header)
        if type == 0 and sequence >= 0:  # 0表示回显应答
            print('ping reply received',addr, packet_id, sequence)
            return True
        time_remaining = time_remaining - time_spent
        if time_remaining <= 0:  # 超时
            # print("Request timed out.")
            return False


# print("ping test")
# ping(dest_addr="192.168.31.1")  # , src_addr="192.168.31.14"
# print(ping(dest_addr="192.168.31.1"))

# TCP端口检测
# 返回值:是否执行成功,是否端口开放
def tcp_port_test(src_addr="Default", dest_addr=None, port=80, timeout=ICMP_TIMEOUT):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.settimeout(timeout)
    try:
        s.bind((src_addr, 0))
        s.connect((dest_addr, port))
        return True, True
    except socket.timeout:
        return True, False
    except Exception as e:
        print(e)
        return False, False
    finally:
        s.close()


# print( tcp_port_test(src_addr="", dest_addr="127.0.0.1", port=7861))

class PortInfo:
    def __init__(self, port, func="", other=None):
        # 保证port是整数
        self.port = int(port)
        self.func = func
        self.other = other

    def __str__(self):
        return "Port: " + str(self.port) + " Func: " + self.func + " Other: " + str(self.other)

    def GetInfo(self):
        return f"{self.port} ({self.func})"

    def GetKeyAndValue(self):
        return self.port, self.func

def PortInfoStr2KeyAndValue(portinfostr):
    port = int(portinfostr.split(":")[0])
    func = portinfostr.split(":")[1]
    return port, func

def PortAndFunc2PortInfo(port, func):
    return str(port) + ":" + func

# 端口监听测试
# import psutil
#
# def get_listening_ports():
#     connections = psutil.net_connections()
#     listening_ports = [conn.laddr.port for conn in connections if conn.status == 'LISTEN']
#     return listening_ports
#
# print(get_listening_ports())