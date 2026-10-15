import time
from loguru import logger

from models.Detection import Detection
from models.MoveControl import MoveControl
from models.config import (
    color_list,
    color_list_in_rough_area,
    color_list_in_restore_area,
    dis_between_every_circle,
    HeightMode,
    MixMode,
)



class ComRun:
    def __init__(self, _stm32_port: str, _stm32_baudrate: int, qr_cam_index: int, downward_cam_index: int) -> None:
        self.stm32_port = _stm32_port
        self.stm32_baudrate = _stm32_baudrate
        self.qr_cam = qr_cam_index
        self.downward_cam = downward_cam_index

        self.moveControl = MoveControl(self.stm32_port, self.stm32_baudrate)
        self.downward_detection = None
        self.qr_detection = Detection(self.qr_cam)
        #self.downward_detection = Detection(self.downward_cam)
        self.log('串口和摄像头初始化完成')

    # 获取二维码信息
    @staticmethod
    def get_taskinfo(qr_result: str) -> tuple[list[str], list[str]]:
        if len(qr_result) != 7:
            raise ValueError

        task1_num = [int(task_str) for task_str in qr_result[:3]]
        task2_num = [int(task_str) for task_str in qr_result[4:]]

        task1_colors = [color_list[i] for i in task1_num]
        task2_colors = [color_list[i] for i in task2_num]

        return task1_colors, task2_colors

    # 根据圆心调整小车X，Y位置
    def adjustCircle(self, thresh=0.02, dis_max=80, timeout=30):
        t1 = time.time()
        while True:
            d_x, d_y = self.downward_detection.get_circle_center()
            print(d_x, d_y)
            if abs(d_x) > thresh:
                self.moveControl.move_in_mm(x=-d_x * 80)
                
            if abs(d_y) > thresh:
                self.moveControl.move_in_mm(y=d_y * dis_max)
            if abs(d_x) < thresh and abs(d_y) < thresh:
                break
            if time.time() - t1 > timeout:
                break
        self.moveControl.move_in_mm(y=-11)
        self.moveControl.move_in_mm(x=-8)

    def adjustColorCircle(self, thresh=0.02, dis_max=60, timeout=30, color='blue'):
        t1 = time.time()
        while True:
            d_x, d_y = self.downward_detection.get_colored_circle_center(color, min_r=50)
            print(d_x, d_y)
            if abs(d_x) > thresh:
                self.moveControl.move_in_mm(x=-d_x * dis_max)
                
            if abs(d_y) > thresh:
                self.moveControl.move_in_mm(y=d_y * dis_max * 0.75)
            if abs(d_x) < thresh and abs(d_y) < thresh:
                break
            if time.time() - t1 > timeout:
                break
        self.moveControl.move_in_mm(y=-11)
        self.moveControl.move_in_mm(x=-8)
            #if abs(d_x) > thresh:
            #    self.moveControl.move_in_mm(y=-d_x * dis_max)
            #    continue
            #if abs(d_y) > thresh:
            #    self.moveControl.move_in_mm(x=-d_y * dis_max * 0.75)
            #if abs(d_x) < thresh and abs(d_y) < thresh:
            #    break
            #if time.time() - t1 > timeout:
            #    break
        #self.moveControl.move_in_mm(y=8)
        #self.moveControl.move_in_mm(x=10)

    @staticmethod
    def continueOrNot():
        x = input('是否继续程序:')
        if x == 'y' or x == 'Y':
            pass
        else:
            exit(0)

    @staticmethod
    def log(msg: str) -> None:
        logger.info(msg)

    def run(self):
        
        #self.moveControl.set_distance(x=0.18)
        #exit(0)
        
        
        
        
        #self.moveControl.move_while_adjusting_height(mix_mode=MixMode.qrPos, move_dis=0)
        #self.moveControl.move_while_adjusting_height(mix_mode=MixMode.circleArea, move_dis=0)
        #print("begin to adjust circles")
        #self.adjustCircle()
        #print("finish")
        #self.moveControl.putBlockToCircle()
        
        #exit(0)
        
        
        
        #del self.qr_detection
        #self.downward_detection = Detection(self.downward_cam)
        #self.moveControl.move_while_adjusting_height(mix_mode=MixMode.qrPos, move_dis=0)
        #self.moveControl.adjustHeight(HeightMode.circleArea)
        #self.adjustCircle()
        #print("finish")
        #self.moveControl.putBlockToCircle()
        #self.moveControl.grubBlockFromGround()
        
        #self.moveControl.putBlockToCircle()
        #self.moveControl.putBlockToAnotherBlock()
        #exit(0)
      
        
       
      
        
        
        #self.moveControl.move_while_adjusting_height(mix_mode=MixMode.qrPos, move_dis=0)
        #self.moveControl.notice_qr_info()
        #color="green"
        #self.moveControl.adjustHeight(target_height=HeightMode.rawArea)
        #self.downward_detection.detect_color(color)
        #self.moveControl.adjustHeight(HeightMode.circleArea)
        #self.moveControl.adjustHeight(target_height=HeightMode.rawArea)
        #self.moveControl.grubBlockFromGround()
        #self.moveControl.grubBlockFromRawArea()
        #exit(0)
        #i=1
        #self.moveControl.grubBlockFromRawArea()
        #self.moveControl.grubBlockFromGround()
        #self.moveControl.move_while_adjusting_height(mix_mode=MixMode.qrPos, move_dis=0)
        
       
       
        
 
        
        
        #self.moveControl.move_while_adjusting_height(mix_mode=MixMode.rawArea, move_dis=0.85)
        #self.moveControl.set_distance(y=-0.02)
        #self.moveControl.set_distance(x=0.4)
        #self.moveControl.turn_left()
        #self.moveControl.set_distance(x=1.85)
        #self.moveControl.turn_left()
        #self.moveControl.set_distance(x=0.95)
        #exit(0)
        
        
        
        #self.moveControl.wait_for_start_cmd()
        #self.moveControl.move_in_mm()
        #self.moveControl.adjustHeight(target_height=HeightMode.qrPos)
        #self.moveControl.move_while_adjusting_height(mix_mode=MixMode.qrPos, move_dis=0.20)
        #exit(0)

        # ---------------------------------------------------------------------------------------- #
        # 前置任务：                                                                               #
        #         1. 机器人移动到二维码区，识别二维码信息，从而获取两次拿取物料块的顺序             # 
        # -----------------------------------------------------------------------------------------#

        self.log(f'------------- 小车运行前置任务，移动到二维码并扫描二维码信息 -------------------')
        # ----------------------------------- 1.读取二维码信息 ----------------------------------- #
        # 前往二维码
        self.log(f'前往二维码')
        self.moveControl.set_distance(y=0.15)
        # self.moveControl.set_distance(x=0.5)
        # self.moveControl.adjustHeight(target_height=HeightMode.qrPos)
        self.moveControl.move_while_adjusting_height(mix_mode=MixMode.qrPos, move_dis=0)
        self.moveControl.set_distance(x=1.4)
        # 在二维码区识别二维码
        self.log(f'调用摄像头识别二维码')

        qr_info = self.qr_detection.get_qr_info()
        self.moveControl.send_qr_info(qr_info)
        task1_color, task2_color = self.get_taskinfo(qr_info)
        self.log(f'二维码识别结果为，任务1: {task1_color}, 任务2: {task2_color}')
        del self.qr_detection
        self.downward_detection = Detection(self.downward_cam)
        # ---------------------------------------------------------------------------------------  #
        # 第一圈任务：                                                                             #
        #           1.前往暂存区，抓取物料块
        #           2.前往精加工区，放料块
        #           3.将放到精加工的物块再放到小车上
        #           4.前往成品，将物料块放到成品区的地面
        #           5.回到原料区，准备任务二
        # ---------------------------------------------------------------------------------------- #
        self.log(f'-------------- 小车运行第一圈的任务 --------------')
        # ----------------------------------  1.到原料区抓取物块 ---------------------------------- #
        self.log(f'第一圈任务：1.前往暂存区，抓取物料块')
        # 前往暂存区
        self.moveControl.move_while_adjusting_height(mix_mode=MixMode.rawArea, move_dis=-0.4)
        self.moveControl.set_distance(x=-0.89)
        self.moveControl.turn_right()
        self.moveControl.set_distance(x=-0.89)
        # 调整高度，识别颜色，抓取物块
        for i, color in enumerate(task1_color):

            self.moveControl.adjustHeight(target_height=HeightMode.rawArea)
            self.downward_detection.detect_color(color)
            if i != 2:
                self.moveControl.grubBlockFromRawArea()
            else:
                self.moveControl.grubBlockFromRawArea()
                # self.moveControl.set_distance(x=-0.4)
                self.moveControl.move_while_adjusting_height(mix_mode=MixMode.rawArea, move_dis=-0)

        # ----------------------------------  2.到粗加工区放料块 ---------------------------------- #
        self.log(f'第一圈任务：2.前往精加工区，放料块')
        # 前往精加工区
        self.moveControl.turn_left()
        self.moveControl.set_distance(y=-0.05)
        self.moveControl.set_distance(x=1.68)
        self.moveControl.turn_left()
        # 根据任务一的顺序移动小车，并摆放物料块
        current_color = color_list_in_rough_area[1]  # 小车现在应该处于中间色块
        #self.moveControl.turn_left()
        self.moveControl.gyroscope()
        # 此时车头朝向粗加工区蓝色物料块方向，车尾朝向红色物料块方向
        for color in task1_color:
            current_index = color_list_in_rough_area.index(current_color)
            next_index = color_list_in_rough_area.index(color)
            if current_index == next_index:
                self.moveControl.adjustHeight(HeightMode.circleArea)
            else:
                dis2move = -(next_index - current_index) * dis_between_every_circle
                self.moveControl.move_while_adjusting_height(mix_mode=MixMode.circleArea, move_dis=dis2move)
            print("begin to adjust circles")
            self.adjustCircle()
            print("finish")
            self.moveControl.putBlockToCircle()

            current_color = color
        # exit(0)
        # ---------------------------------- 3.把放到粗加工区的物料块拿回小车 ---------------------------------- #
        self.log(f'第一圈任务：3.将放到粗加工的物块再放到小车上')

        # 按任务一的顺序，将粗加工的物料搬到小车上
        for i, color in enumerate(task1_color):
            current_index = color_list_in_rough_area.index(current_color)
            next_index = color_list_in_rough_area.index(color)

            if current_index == next_index:
                self.moveControl.adjustHeight(HeightMode.circleArea)
            else:
                dis2move = -(next_index - current_index) * dis_between_every_circle
                self.moveControl.move_while_adjusting_height(mix_mode=MixMode.qrPos, move_dis=dis2move)
            # self.adjustCircle()
            if i == 2:
                # 计算从当前位置到粗加工红色物料块的距离
                dis2red = dis_between_every_circle * (2 - color_list_in_rough_area.index(current_color))
                red2corner = 0.55
                # 前往粗加工和暂存区之间的拐角
                self.moveControl.grubBlockFromGround()
                self.moveControl.move_while_adjusting_height(mix_mode=MixMode.circleArea,
                                                             move_dis=(dis_between_every_circle * 2+0.85-dis2red))
                break
            self.moveControl.grubBlockFromGround()
            current_color = color

        # ---------------------------------- 4.前往暂存区，将物料块放到暂存区的地面 ---------------------------------- #
        self.log(f'第一圈任务：4.前往暂存区，将物料块放到暂存区的地面')

        # -------- 前往暂存区 ----------- #
        dis2blue = 0.7 + dis_between_every_circle * 2 # 拐角到暂存区蓝色物料块圆环的距离
        dis2first_block = dis_between_every_circle * color_list_in_rough_area.index(task1_color[0])
        self.moveControl.turn_left()
        self.moveControl.set_distance(x=(dis2blue - dis2first_block))
        self.moveControl.gyroscope()
        current_color = task1_color[0]
        for i, color in enumerate(task1_color):
            current_index = color_list_in_restore_area.index(current_color)
            next_index = color_list_in_restore_area.index(color)
            if current_index == next_index:
                self.moveControl.adjustHeight(HeightMode.circleArea)
            else:
                dis2move = -(next_index - current_index) * dis_between_every_circle
                self.moveControl.move_while_adjusting_height(mix_mode=MixMode.circleArea, move_dis=dis2move)
            self.adjustCircle()
            self.moveControl.putBlockToCircle()
            current_color = color

        # exit(0)
        # ---------------------------------- 5.离开暂存区，前往原料区 ------------------#
        self.log(f'第一圈任务：5.回到暂存区，准备任务二')
        # 计算从当前位置到暂存区最右边物料块（红色）的距离
        # 计算从当前位置到暂存区最右边物料块（红色）的距离
        dis2restore_red = dis_between_every_circle * (2 - color_list_in_restore_area.index(current_color))
        dis2corner2 = 0.73
        self.moveControl.set_distance(x=(dis_between_every_circle * 2-dis2restore_red)+dis2corner2)
        self.moveControl.turn_left()
        self.moveControl.move_while_adjusting_height(mix_mode=MixMode.rawArea, move_dis=0.85)  # 从拐角到原料区的距离
        # self.moveControl.set_distance(x=-0.4)
        # -------------------------------------------------------------------------------------- #
        # 任务二：
        #       1.在原料区按任务二顺序取物料块
        #       2.将物料块搬运到粗加工
        #       3.将物料块搬运到暂存区
        #       4.将物料块搬运到粗加工并进行码垛
        # -------------------------------------------------------------------------------------- #

        self.log(f'-------------- 小车运行第二圈的任务 --------------')
        # ----------------------------------  1.在原料区抓取物块 ---------------------------------- #
        self.log(f'第二圈任务：1.在原料区抓取物块')
        # 调整高度，识别颜色，抓取物块
        for i, color in enumerate(task2_color):
            self.moveControl.adjustHeight(target_height=HeightMode.rawArea)
            self.downward_detection.detect_color(color)
            if i != 2:
                self.moveControl.grubBlockFromRawArea()
            else:
                self.moveControl.grubBlockFromRawArea()
                self.moveControl.move_while_adjusting_height(mix_mode=MixMode.rawArea, move_dis=-0)

        # ----------------------------------  2.将物料块放到粗加工区 ---------------------------------- #
        self.log(f'第一圈任务：2.前往精加工区，放料块')
        # 前往精加工区
        self.moveControl.turn_left()
        self.moveControl.set_distance(y=-0.05)
        self.moveControl.set_distance(x=1.68)
        self.moveControl.turn_left()
        # 根据任务一的顺序移动小车，并摆放物料块
        current_color = color_list_in_rough_area[1]  # 小车现在应该处于中间色块
        #self.moveControl.turn_left()
        self.moveControl.gyroscope()
        # 此时车头朝向粗加工区蓝色物料块方向，车尾朝向红色物料块方向
        for color in task2_color:
            current_index = color_list_in_rough_area.index(current_color)
            next_index = color_list_in_rough_area.index(color)
            if current_index == next_index:
                self.moveControl.adjustHeight(HeightMode.circleArea)
            else:
                dis2move = -(next_index - current_index) * dis_between_every_circle
                self.moveControl.move_while_adjusting_height(mix_mode=MixMode.circleArea, move_dis=dis2move)
            print("begin to adjust circles")
            self.adjustCircle()
            print("finish")
            self.moveControl.putBlockToCircle()

            current_color = color
        # exit(0)
        # ---------------------------------- 3.把放到粗加工区的物料块拿回小车 ---------------------------------- #
        self.log(f'第一圈任务：3.将放到粗加工的物块再放到小车上')

        # 按任务一的顺序，将粗加工的物料搬到小车上
        for i, color in enumerate(task2_color):
            current_index = color_list_in_rough_area.index(current_color)
            next_index = color_list_in_rough_area.index(color)

            if current_index == next_index:
                self.moveControl.adjustHeight(HeightMode.circleArea)
            else:
                dis2move = -(next_index - current_index) * dis_between_every_circle
                self.moveControl.move_while_adjusting_height(mix_mode=MixMode.qrPos, move_dis=dis2move)
            # self.adjustCircle()
            if i == 2:
                # 计算从当前位置到粗加工红色物料块的距离
                dis2red = dis_between_every_circle * (2 - color_list_in_rough_area.index(current_color))
                red2corner = 0.55
                # 前往粗加工和暂存区之间的拐角
                self.moveControl.grubBlockFromGround()
                self.moveControl.move_while_adjusting_height(mix_mode=MixMode.circleArea,
                                                             move_dis=(dis_between_every_circle * 2 + 0.45 - dis2red))
                break
            self.moveControl.grubBlockFromGround()
            current_color = color

        # ---------------------------------- 4.前往成品区，将物料块放到暂存区的地面 ---------------------------------- #
        self.log(f'第一圈任务：4.前往暂存区，将物料块放到暂存区的地面')

        # -------- 前往暂存区 ----------- #
        dis2blue = 0.7 + dis_between_every_circle * 2  # 拐角到暂存区蓝色物料块圆环的距离
        dis2first_block = dis_between_every_circle * color_list_in_rough_area.index(task1_color[0])
        self.moveControl.turn_left()
        self.moveControl.set_distance(x=(dis2blue - dis2first_block))
        self.moveControl.gyroscope()
        
        current_color = task2_color[0]
        for i, color in enumerate(task2_color):
            current_index = color_list_in_restore_area.index(current_color)
            next_index = color_list_in_restore_area.index(color)
            if current_index == next_index:
                self.moveControl.adjustHeight(HeightMode.stackArea)
                # pass
            else:
                dis2move = -(next_index - current_index) * dis_between_every_circle
                self.moveControl.move_while_adjusting_height(mix_mode=MixMode.stackArea, move_dis=dis2move)
            # self.moveControl.adjustHeight(HeightMode.stackArea)
            self.adjustColorCircle(color=color)
            print("begin to adjustcircle")
            self.moveControl.putBlockToAnotherBlock()
            print("finish")
            current_color = color

        # exit(0)
        # ---------------------------------- 5.离开暂存区，前往原料区 ------------------#
        self.log(f'第一圈任务：5.回到暂存区，准备任务二')
        # 计算从当前位置到暂存区最右边物料块（红色）的距离
        # 计算从当前位置到暂存区最右边物料块（红色）的距离
        dis2restore_red = dis_between_every_circle * (2 - color_list_in_restore_area.index(current_color))
        dis2corner2 = 0.75
        self.moveControl.set_distance(x=(dis_between_every_circle * 2 - dis2restore_red) + dis2corner2)
        self.moveControl.turn_left()
        self.moveControl.move_while_adjusting_height(mix_mode=MixMode.rawArea, move_dis=1.25)
        self.moveControl.set_distance(x=0.70)
          # 从拐角到原料区的距离
        # self.moveControl.set_distance(x=-0.4)
        self.moveControl.turn_left()
        self.moveControl.back()
        self.moveControl.set_distance(x=-0.10)
        self.moveControl.set_distance(y=-0.15)














if __name__ == "__main__":
    # stm32_port = "COM4"
    stm32_port = "/dev/ttyUSB0"
    stm32_baudrate = 115200
    qr_cam_name = 0
    downward_cam_name = 2

    com = ComRun(stm32_port, stm32_baudrate, qr_cam_name, downward_cam_name)
    com.run()
