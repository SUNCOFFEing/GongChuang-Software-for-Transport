# _*_ coding:utf-8 _*_
from typing import Tuple, List
import time

from models.Detection import Detection
from models.MoveControl import MoveControl
from models.config import (
    pi,
    color_list,
    color_list_in_fine_area,
    color_list_in_rough_area,
    dis_between_every_circle,
    HeightMode,
    MixMode
)


# 整体流程类，控制小车的路径
class LogisticsCom(object):
    def __init__(self, stm32_port: str, stm32_baudrate: int, qr_cam: int, downward_cam: int):
        self.stm32_port = stm32_port
        self.stm32_baudrate = stm32_baudrate
        self.qr_cam = qr_cam
        self.downward_cam = downward_cam

        self.moveControl = MoveControl(self.stm32_port, self.stm32_baudrate)
        self.qr_detection = Detection(self.qr_cam)
        self.downward_detection = None

    # 从二维码扫描结果中，获取两次的任务
    def get_taskinfo(self, task_info: str) -> Tuple[List[int], List[int]]:
        task1_num = [int(task_str) for task_str in task_info[:3]]
        task2_num = [int(task_str) for task_str in task_info[4:]]

        task1_colors = [color_list[i] for i in task1_num]
        task2_colors = [color_list[i] for i in task2_num]


        return task1_colors, task2_colors

    # 根据直线调整小车角度以及距离
    def adjustLine(self, angel_thresh=0.015, dis_thresh=0.05, 
                   max_dis=72, max_angel=90, timeout=20, error_k=-0.02):
        t1 = time.time()
        while True:
            k, dy = self.downward_detection.get_line_info()
            k = k - error_k
            if abs(k) > angel_thresh:
                self.moveControl.rotate(int((k / pi * 2) * max_angel))
                continue
            if abs(dy) > dis_thresh:
                self.moveControl.move_in_mm(y=-dy * max_dis * 0.75)
            if abs(k) < angel_thresh and abs(dy) < dis_thresh:
                break
            if time.time() - t1 > timeout:
                break

    # 根据圆心调整小车X，Y位置
    def adjustCircle(self, thresh=0.02, dis_max=127, timeout=30):
        t1 = time.time()
        while True:
            d_x, d_y = self.downward_detection.get_circle_center()
            if abs(d_x) > thresh:
                self.moveControl.move_in_mm(y=-d_x * dis_max)
                continue
            if abs(d_y) > thresh:
                self.moveControl.move_in_mm(x=-d_y * dis_max * 0.75)
            if abs(d_x) < thresh and abs(d_y) < thresh:
                break
            if time.time() - t1 > timeout:
                break
        self.moveControl.move_in_mm(y = 8)
        self.moveControl.move_in_mm(x = 10)


    # 精加工区域码垛，根据物料块圆心位置，调整小车的X、Y位置
    def adjustColorCircle(self, thresh=0.02, dis_max=60, timeout=30, color='blue'):
        t1 = time.time()
        while True:
            d_x, d_y = self.downward_detection.get_colored_circle_center(color)
            if abs(d_x) > thresh:
                self.moveControl.move_in_mm(y=-d_x * dis_max)
                continue
            if abs(d_y) > thresh:
                self.moveControl.move_in_mm(x=-d_y * dis_max * 0.75)
            if abs(d_x) < thresh and abs(d_y) < thresh:
                break
            if time.time() - t1 > timeout:
                break
        self.moveControl.move_in_mm(y = 8)
        self.moveControl.move_in_mm(x = 10)

    def continueOrNot(self):
        x = input('是否继续程序:')
        if x == 'y' or x == 'Y':
            pass
        else:
            exit(0)
        
    def run_com(self) -> bool:
        # self.moveControl.wait_for_start_cmd()

        # 初始化,机械臂回中
        # --------------------------------------------------
        #               第一圈
        # --------------------------------------------------
        # 离开启停区
        
        self.moveControl.set_distance(y=0.11)

        # 前往二维码
        # self.moveControl.set_distance(x=0.5)
        # self.moveControl.adjustHeight(target_height=HeightMode.qrPos)
        self.moveControl.move_while_adjusting_height(mix_mode=MixMode.qrPos, move_dis=0.5)

        # 二维码区 识别二维码
        qr_info = self.qr_detection.get_qr_info()
        task1_color, task2_color = self.get_taskinfo(qr_info)
        print(task1_color, task2_color)
        del self.qr_detection
        self.downward_detection = Detection(self.downward_cam)

        # 二维码区到原料区
        # self.moveControl.adjustHeight(target_height=HeightMode.rawArea)
        # self.moveControl.set_distance(x=0.95)
        self.moveControl.move_while_adjusting_height(mix_mode=MixMode.rawArea, move_dis=0.95)

        # 到达原料区，调整高度，识别颜色，抓取物块
        for i, color in enumerate(task1_color):
            self.moveControl.adjustHeight(target_height=HeightMode.rawArea)
            self.downward_detection.detect_color(color)
            if i != 2:
                self.moveControl.grubBlockFromRawArea()
            else:
                self.moveControl.move_while_adjusting_height(mix_mode=MixMode.rawAreaLeave, move_dis=0.45)

        # 从原料区到粗加工的拐角
        # self.moveControl.set_distance(x=0.45)
        self.moveControl.turn_left()

        # 拐角到三个圆环最右端的距离
        dis_temp = 0.80
        # self.moveControl.set_distance(x=0.75)

        # 计算最右端圆环到第一个圆环的距离
        current_color = color_list_in_rough_area[-1]
        next_color = task1_color[0]
        count_num = color_list_in_rough_area.index(next_color) - color_list_in_rough_area.index(current_color)
        dis = count_num * dis_between_every_circle

        # 移动过去并调整高度
        # self.moveControl.set_distance(x=-dis + dis_temp)
        # self.moveControl.adjustHeight(target_height=HeightMode.circleArea)
        self.moveControl.move_while_adjusting_height(mix_mode=MixMode.circleArea, move_dis=dis_temp - dis)
        current_color = next_color

        # 校准圆心，并放下物块
        self.adjustCircle()
        self.moveControl.putBlockToCircle()

        # 继续完成粗加工区剩余的两个任务
        for color in task1_color[1:]:
            next_color = color
            count_num = color_list_in_rough_area.index(next_color) - color_list_in_rough_area.index(current_color)
            dis = count_num * dis_between_every_circle
            self.moveControl.set_distance(x=-dis)

            # self.moveControl.adjustHeight(target_height=HeightMode.circleArea)
            # self.adjustCircle()
            self.moveControl.putBlockToCircle()

            current_color = next_color

        # 再把物块抓取起来
        for i, color in enumerate(task1_color):
            next_color = color
            count_num = color_list_in_rough_area.index(next_color) - color_list_in_rough_area.index(current_color)
            dis = count_num * dis_between_every_circle
            if i == 2:
                self.moveControl.set_distance(x=-dis)
                current_color = next_color
                # 计算最后一个任务圆环距离最左端圆环的距离
                dis_count = 0 - color_list_in_rough_area.index(current_color)
                dis = dis_count * dis_between_every_circle
                dis_temp = dis
                self.moveControl.move_while_adjusting_height(mix_mode=MixMode.roughAreaLeave, move_dis=0.58 - dis)
            else:
                self.moveControl.set_distance(x=-dis)
                self.moveControl.grubBlockFromGround()

            current_color = next_color

        # 计算最后一个任务圆环距离最左端圆环的距离
        # dis_count = 0 - color_list_in_rough_area.index(current_color)
        # dis = dis_count * dis_between_every_circle
        # dis_temp = dis


        # 从最后一个任务圆环，去往精加工的拐角
        # self.moveControl.set_distance(x=0.58 - dis)
        self.moveControl.turn_left()

        # 精加工区右边拐角到精加工区最右端圆心的距离
        dis_temp = 0.78

        # 精加工最右端圆心到第一个任务圆心的距离
        current_color = color_list_in_fine_area[-1]
        next_color = task1_color[0]
        count_num = color_list_in_fine_area.index(next_color) - color_list_in_fine_area.index(current_color)
        dis = count_num * dis_between_every_circle
        current_color = next_color

        # 前往第一个任务点，并同时调整升降台
        # self.moveControl.set_distance(x=dis_temp - dis)
        # self.moveControl.adjustHeight(target_height=HeightMode.circleArea)
        self.moveControl.move_while_adjusting_height(mix_mode=MixMode.circleArea,
                                                     move_dis=dis_temp - dis)

        # 校准圆心，并放下物块
        self.adjustCircle()
        self.moveControl.putBlockToCircle()

        # 精加工区
        for color in task1_color[1:]:
            # 前往剩余的两个任务点
            next_color = color
            count_num = color_list_in_fine_area.index(next_color) - color_list_in_fine_area.index(current_color)
            dis = count_num * dis_between_every_circle
            self.moveControl.set_distance(x=-dis)

            # 调整圆心并放下物块
            # self.moveControl.adjustHeight(target_height=HeightMode.circleArea)
            # self.adjustCircle()
            self.moveControl.putBlockToCircle()

            current_color = next_color


        # 计算精加工区，当前任务圆环与最右端圆环之间的距离
        dis_count = 2 - color_list_in_fine_area.index(current_color)
        dis = dis_count * dis_between_every_circle
        dis_temp = dis

        # 从当前圆心，前往精加工拐角
        self.moveControl.move_while_adjusting_height(move_dis=-0.78 - dis_temp, mix_mode=MixMode.rawArea)
        self.moveControl.turn_right()

        # 到粗加工与原料区的拐弯
        self.moveControl.set_distance(x=-1.70)
        self.moveControl.turn_right()

        # 到原料区
        # self.moveControl.adjustHeight(HeightMode.rawArea)
        self.moveControl.set_distance(x=-0.50)
        # self.moveControl.move_while_adjusting_height(mix_mode=MixMode.rawArea, move_dis=-0.45)

        # --------------------------------------------------
        #                 第二圈
        # --------------------------------------------------

        # 到达原料区，调整高度，识别颜色，抓取物块
        for i, color in enumerate(task2_color):
            self.moveControl.adjustHeight(target_height=HeightMode.rawArea)
            self.downward_detection.detect_color(color)
            if i != 2:
                self.moveControl.grubBlockFromRawArea()
            else:
                self.moveControl.move_while_adjusting_height(mix_mode=MixMode.rawAreaLeave, move_dis=0.45)

        # 从原料区到粗加工的拐角
        # self.moveControl.set_distance(x=0.45)
        self.moveControl.turn_left()

        # 拐角到三个圆环最右端的距离
        dis_temp = 0.78
        # self.moveControl.set_distance(x=0.75)

        # 计算最右端圆环到第一个圆环的距离
        current_color = color_list_in_rough_area[-1]
        next_color = task2_color[0]
        count_num = color_list_in_rough_area.index(next_color) - color_list_in_rough_area.index(current_color)
        dis = count_num * dis_between_every_circle

        # 移动过去并调整高度
        # self.moveControl.set_distance(x=-dis + dis_temp)
        # self.moveControl.adjustHeight(target_height=HeightMode.circleArea)
        self.moveControl.move_while_adjusting_height(mix_mode=MixMode.circleArea, move_dis=dis_temp - dis)
        current_color = next_color

        # 校准圆心，并放下物块
        self.adjustCircle()
        self.moveControl.putBlockToCircle()

        # 继续完成粗加工区剩余的两个任务
        for color in task2_color[1:]:
            next_color = color
            count_num = color_list_in_rough_area.index(next_color) - color_list_in_rough_area.index(current_color)
            dis = count_num * dis_between_every_circle
            self.moveControl.set_distance(x=-dis)

            # self.moveControl.adjustHeight(target_height=HeightMode.circleArea)
            # self.adjustCircle()
            self.moveControl.putBlockToCircle()

            current_color = next_color

        # 再把物块抓取起来
        for i, color in enumerate(task2_color):
            next_color = color
            count_num = color_list_in_rough_area.index(next_color) - color_list_in_rough_area.index(current_color)
            dis = count_num * dis_between_every_circle
            if i == 2:
                self.moveControl.set_distance(x=-dis)
                current_color = next_color
                # 计算最后一个任务圆环距离最左端圆环的距离
                dis_count = 0 - color_list_in_rough_area.index(current_color)
                dis = dis_count * dis_between_every_circle
                dis_temp = dis
                self.moveControl.move_while_adjusting_height(mix_mode=MixMode.roughAreaLeave, move_dis=0.58 - dis)
            else:
                self.moveControl.set_distance(x=-dis)
                self.moveControl.grubBlockFromGround()

            current_color = next_color

        # 计算最后一个任务圆环距离最左端圆环的距离
        # dis_count = 0 - color_list_in_rough_area.index(current_color)
        # dis = dis_count * dis_between_every_circle
        # dis_temp = dis


        # 从最后一个任务圆环，去往精加工的拐角
        # self.moveControl.set_distance(x=0.58 - dis)
        self.moveControl.turn_left()

        # 精加工区右边拐角到精加工区最右端圆心的距离
        dis_temp = 0.75

        # 精加工最右端圆心到第一个任务圆心的距离
        current_color = color_list_in_fine_area[-1]
        next_color = task2_color[0]
        count_num = color_list_in_fine_area.index(next_color) - color_list_in_fine_area.index(current_color)
        dis = count_num * dis_between_every_circle
        current_color = next_color

        # 前往第一个任务点，并同时调整升降台
        # self.moveControl.set_distance(x=dis_temp - dis)
        # self.moveControl.adjustHeight(target_height=HeightMode.circleArea)
        self.moveControl.move_while_adjusting_height(mix_mode=MixMode.stackArea,
                                                     move_dis=dis_temp - dis)

        # 校准圆心，并放下物块
        self.adjustCircle()
        self.moveControl.putBlockToAnotherBlock()

        # 精加工区
        for color in task2_color[1:]:
            # 前往剩余的两个任务点
            next_color = color
            count_num = color_list_in_fine_area.index(next_color) - color_list_in_fine_area.index(current_color)
            dis = count_num * dis_between_every_circle
            self.moveControl.set_distance(x=-dis)

            # 调整圆心并放下物块
            # self.moveControl.adjustHeight(target_height=HeightMode.circleArea)
            # self.adjustCircle()
            self.moveControl.putBlockToAnotherBlock()

            current_color = next_color

        # 计算精加工区，最后一个任务的圆环，距离最左边圆环之间的距离
        dis_count = 0 - color_list_in_fine_area.index(current_color)
        dis = dis_count * dis_between_every_circle
        dis_temp = dis

        # 从精加工区最后一个物块，前往精加工区左边的拐角
        self.moveControl.set_distance(x=0.88 - dis)
        self.moveControl.turn_left()

        # 到达拐角后，继续前往出发点
        self.moveControl.set_distance(x=1.80)
        self.moveControl.turn_left()

    def test(self):
        del self.qr_detection
        self.downward_detection = Detection(2)
        self.moveControl.adjustHeight(target_height=HeightMode.circleArea)
        self.adjustCircle()


if __name__ == "__main__":
    stm32_port = "/dev/ttyUSB0"
    stm32_baudrate = 115200
    qr_cam_name = 0
    downward_cam_name = 2

    com = LogisticsCom(stm32_port, stm32_baudrate, qr_cam_name, downward_cam_name)
    com.run_com()
