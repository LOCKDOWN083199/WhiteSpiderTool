# ============================
# Desc: Global variables
# 此模块用于存放整个程序可能会用的全局变量、样式
# ============================


# 全局线程池
# ============================
from concurrent.futures import ThreadPoolExecutor
Thread_pool = ThreadPoolExecutor(max_workers=30)  # 公共线程池
# ============================


ICMP_TIMEOUT = 1  # ICMP超时时间



# 颜色/风格统一定义区
# ============================
class STYLE:
    # 颜色  !!说明:网卡速率折线颜色是实时计算模拟渐变,因此不在此定义(在network.py.networkview.draw_data中定义)!!

    MouseEnter = "#e8585f"  # 鼠标进入view类组件边框颜色
    ViewBG = "#f0f0f0"  # 组件卡背景
    ViewBGDeepperA = "#c6c6c6"  # 组件卡背景深色
    ROOTBG = "#dfe1e5"  # 最底窗口背景


    # 按钮组件统一
    # ----------------------------
    Button_Yes_Back = "#1cd66c"  # 保存/开始按钮背景
    Button_Yes_Fore = "#16bd3b"  # 保存/开始按钮前景
    Button_Close_Back = "#ff8d93"  # 取消/停止按钮背景
    Button_Close_Fore = "#ff6464"  # 取消/停止按钮前景
    Button_Adv_Back = "#51a7f4"  # 高级按钮背景
    Button_Adv_Fore = "#0c77d6"  # 高级按钮前景
    Button_Stop_Back = "#ffbd21"  # 停止按钮背景
    Button_Stop_Fore = "#cc971a"  # 停止按钮前景
    # ----------------------------

    # 网卡区
    # ----------------------------
    PCIBorder = "#288ee9"  # 物理网卡边框
    VirtualBorder = "#1cd66c"  # 虚拟网卡边框
    NetworkCavansBG = "#e6e6e6"  # 网卡速率折线图面板背景
    NetworkCardNamePCIBG = "#0c77d6"  # 网卡简写板的背景色
    NetworkCardNameVirtualBG = "#118945"  # 网卡简写板的背景色
    DHCPEnableBG = "#31b5dd"  # DHCP启用颜色
    DHCPDisableBG = "#6a6475"  # DHCP禁用颜色
    DHCPDNSEnBG = "#f9c36a"  # DHCP DNS启用颜色
    DHCPDNSUnBG = "#6a6475"  # DHCP DNS禁用 颜色
    EntryBG = "#e6e6e6"  # 输入框背景
    NetworkAdvMouseEnter = "#ff6464"  # 鼠标进入网卡高级设置边框颜色
    DisableDark = "#9fa4a7"  # 禁用大部分控件颜色
    DisableCanvasDark = "#7f8487"  # 禁用Canvas颜色

    Font_NetworkUP = "#0c77d6"  # 网卡上行颜色
    Font_NetworkDN = "green"  # 网卡下行颜色
    # ----------------------------

    # 增加卡区
    # ----------------------------
    ADD_Border = "#7f7f7f"
    ADD_BG = "#f0f0f0"
    ADD_SubBG = "#bfbfbf"
    ADD_ADD = "#f0f0f0"
    ADD_FG = "#1b7dfa"

    ADD_ICMP_Border = "#a1df7c"
    ADD_ICMP_BG = "#57c712"
    ADD_ICMP_Font_Color = "#ffffff"

    ADD_TCPIP_Border = "#f2b6a7"
    ADD_TCPIP_BG = "#ed9745"
    ADD_TCPIP_Font_Color = "#ffffff"

    ADD_MORE_Border = "#cfcfcf"
    ADD_MORE_BG = "#bfbfbf"
    ADD_MORE_Font_Color = "#ffffff"
    # ----------------------------

    # ICMP区
    # ----------------------------
    ICMP_Border = "#7cac5f"
    ICMP_Lable = "#57c712"
    ICMP_BG = "#f0f0f0"
    ICMP_SRC_Label = "#16bd3b" # 源地址标签颜色
    ICMP_DST_Label = "#1b7dfa" # 目的地址标签颜色
    ICMP_SUCCESS_Border = "#a1df7c" # 成功颜色(当前测试未成功)
    ICMP_SUCCESS_NOW = "green" # 成功颜色(本次测试成功)
    ICMP_FAIL_Border = "#f49f9f" # 失败颜色(当前测试未失败)
    ICMP_FAIL_NOW = "#ff6464" # 失败颜色(本次测试失败)
    # ----------------------------

    # TCP/IP区
    # ----------------------------
    TCPIP_Border="#ed9745"
    TCPIP_Lable="#ed8735"
    TCPIP_SrcBG_Label="#16bd3b"
    TCPIP_DstBG_Label="#1b7dfa"
    TCPIP_Success_Border="#30c030"
    TCPIP_Fail_Border="#ff5050" ##ff6464
    TCPIP_ADV_FileSelectLabel_NULL="#ed9745"
    TCPIP_ADV_FileSelectLabel_OK="#a1df7c"
    TCPIP_ADV_FileSelectLabel_NO="#f49f9f"
    TCPIP_ADV_FileSelectButton_NULL="#ed9745"
    TCPIP_ADV_FileSelectButton_Enter="#fda755"
    TCPIP_ADV_ResetButton_NULL="#70d5d7"
    TCPIP_ADV_ResetButton_Enter="#60bac0"
    TCPIP_ADV_ADDButton_NULL="#91cf6c"
    TCPIP_ADV_ADDButton_Enter="green"
    TCPIP_ADV_DELButton_NULL="#f49f9f"
    TCPIP_ADV_DELButton_Enter="#ff6464"
    # ----------------------------

    # 字体

    DefFont = ('Consolas', 8)  # 默认字体
    DefFontBigger10 = ('Consolas', 10)
    DefFontBigger12 = ('Consolas', 12)
    DefFontBigger14 = ('Consolas', 14)
    DefFontBigger16 = ('Consolas', 16)
    MSYHFont = ('微软雅黑', 8)  # 微软雅黑字体
    MSYHFontBigger10 = ('微软雅黑', 10)
    MSYHFontBigger12 = ('微软雅黑', 12)
    MSYHFontBigger14 = ('微软雅黑', 14)
    MSYHFontBigger16 = ('微软雅黑', 16)
    MSYHFontBigger64 = ('微软雅黑', 64)  # 微软雅黑字体

