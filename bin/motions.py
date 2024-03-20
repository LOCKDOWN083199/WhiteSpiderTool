############################
# 此文件用于定义运动动画函数的算法
############################

import math

# 用于计算两点之间的距离
def distance(x1, y1, x2, y2):
    return math.sqrt(abs((x1-x2))**2+abs((y1-y2))**2)

# 用于计算两点之间的角度
def angle(x1, y1, x2, y2):
    return math.atan2(y2-y1, x2-x1)

# 由快到慢的匀减速运动，参数为起始点坐标，目标点坐标，速度系数，返回下一帧移动变化量
def move_to(x1, y1, x2, y2, speed):
    if distance(x1, y1, x2, y2) > 0:
        return int((x2-x1)**2)*speed, int((y2-y1)**2)*speed
    else:
        return 0, 0

