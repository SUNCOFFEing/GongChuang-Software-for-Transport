from enum import Enum, IntEnum


# 小车模式选择枚举类
class Mode(Enum):
    x_distance = 1
    y_distance = 2
    rotate = 3
    qrcode = 4  # 通知下位机扫码
    x_dis_mm = 5
    y_dim_mm = 6
    grub_1 = 7  # 从原料区抓取物料块
    grub_2 = 8  # 从地面抓取物料块
    down_1 = 9  # 将物料块放到地面上
    down_2 = 10  # 精加工区，将物料块放到另一个物料块上
    adjust_height = 11  # 调整升降台到合适的位置    1.读取二维码  2.识别原料区  3.识别圆环   4.识别物料块圆心
    adjust_height_manual = 12
    mix_mode = 13  # 混动模式，一边底盘移动，一边移动升降台
    max_height = 48
    min_height = 49
    turn_front = 50
    back_home = 51
    get_qrPos = 54
    new_move = 14
    gyroscope = 18  # 我后加的陀螺仪
    reset = 17   # 陀螺仪重置

class HeightMode(Enum):
    qrPos = 1
    rawArea = 2
    circleArea = 3
    stackArea = 4


class MixMode(Enum):
    qrPos = HeightMode.qrPos.value
    rawArea = HeightMode.rawArea.value
    circleArea = HeightMode.circleArea.value
    stackArea = HeightMode.stackArea.value
    rawAreaLeave = 5
    roughAreaLeave = 6


# 二维码任务代码与颜色的对应
color_list = [0, "red", "green", "blue"]

# 粗加工颜色顺序
color_list_in_rough_area = ['blue', 'green', 'red']

# 暂存区颜色顺序
color_list_in_restore_area = ['blue', 'green', 'red']

# 精加工颜色顺序
color_list_in_fine_area = ['blue', 'green', 'red']

# 色块之间的距离
dis_between_every_circle = 0.15

pi = 3.14159

if __name__ == '__main__':
    a = [i for i in iter(HeightMode)]
    print(a[0])
