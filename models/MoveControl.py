import serial
from .config import Mode, HeightMode, MixMode
import time
from loguru import logger


# 输入一个十进制的[-128, 127]范围内的整数，获取它补码的十进制
def get_int8(num: float) -> int:
    assert 127 >= num >= -128, print("int8类型范围为[-128, 127]")
    if num >= 0:
        return int(num)
    else:
        return int(255 + num + 1)


# 运动控制类，包含小车的距离控制，以及旋转控制
class MoveControl(object):
    def __init__(self, port: str, baudrate: int) -> None:
        self.port = port
        self.baudrate = baudrate
        try:
            self.serial = serial.Serial(port, baudrate)
        except serial.SerialException as e:
            logger.error(f"串口打开失败: {e}")
        self.serial.flush()

        # 初始化数据列表 [头帧，模式，X方向，Y方向，角度，二维码1，二维码2，尾帧]
        self.send_buffer = [0xFF, 0, 0, 0, 0, 0, 0, 0, 0, 0xFE]

    # 生成串口数据、发送数据并等待回传结果
    def __send_serial_msg(
            self,
            mode: Mode,
            x_dis = None,
            y_dis = None,
            angel: int = None,
            qr_info: str = None,
    ):
        if mode == Mode.x_distance:
            assert x_dis is not None, print("未指定x方向移动距离")
            self.send_buffer[1] = mode.value
            self.send_buffer[2] = (x_dis >> 8) & 0xFF
            self.send_buffer[3] = x_dis & 0xff

        elif mode == Mode.y_distance:
            assert y_dis is not None, print("未指定y方向移动距离")
            self.send_buffer[1] = mode.value
            self.send_buffer[2] = (y_dis >> 8) & 0xFF
            self.send_buffer[3] = y_dis & 0xff

        elif mode == Mode.rotate:
            assert angel is not None, print("未设置角度")
            self.send_buffer[1] = mode.value
            self.send_buffer[4] = get_int8(angel)

        # 通知下位机扫码
        elif mode == Mode.qrcode:
            self.send_buffer[1] = mode.value
            assert qr_info is not None, print("未输入二维码信息")
            self.send_buffer[1] = mode.value
            
            task1, task2 = int(qr_info[:3]), int(qr_info[4:])
            self.send_buffer[5] = task1 >> 8
            self.send_buffer[6] = task1 & 0xFF
            self.send_buffer[7] = task2 >> 8
            self.send_buffer[8] = task2 & 0xFF

        elif mode == Mode.x_dis_mm:
            assert x_dis is not None, print("未指定x方向移动距离，单位:毫米")
            self.send_buffer[1] = mode.value
            self.send_buffer[2] = get_int8(x_dis)

        elif mode == Mode.y_dim_mm:
            assert y_dis is not None, print("未指定x方向移动距离，单位:毫米")
            self.send_buffer[1] = mode.value
            self.send_buffer[3] = get_int8(y_dis)
            
        # 将抓子收回原位
        elif mode == Mode.back_home:
            self.send_buffer[1] = mode.value
        
        
        # 陀螺仪重置
        elif mode == Mode.reset:
            self.send_buffer[1] = mode.value
            
        # 我新加的陀螺仪
        elif mode == Mode.gyroscope:
            self.send_buffer[1] = mode.value

        # 从原料区抓取物料块
        elif mode == Mode.grub_1:
            self.send_buffer[1] = mode.value

        # 从地面抓取物料块
        elif mode == Mode.grub_2:
            self.send_buffer[1] = mode.value

        # 将物料块放到地面上
        elif mode == Mode.down_1:
            self.send_buffer[1] = mode.value

        # 在精加工区，将物料块放到另一个物料块
        elif mode == Mode.down_2:
            self.send_buffer[1] = mode.value

        # 调整升降台的位置
        elif mode == Mode.adjust_height:
            self.send_buffer[1] = mode.value
            if isinstance(x_dis, HeightMode):
                self.send_buffer[2] = x_dis.value
            else:
                raise ValueError(
                    "高度模式选择错误，现有的模式有", [mode.name for mode in HeightMode]
                )

        elif mode == Mode.adjust_height_manual:
            # self.send_buffer[1] = mode.value
            # self.send_buffer[2] = x_dis.value
            raise NotImplementedError("这个模式还没有实现")

        elif mode == Mode.mix_mode:
            self.send_buffer[1] = mode.value
            if isinstance(y_dis, MixMode):
                self.send_buffer[2] = y_dis.value
            else:
                raise ValueError()
            self.send_buffer[3] = get_int8(x_dis)

        elif mode == Mode.new_move:
            self.send_buffer[1] = mode.value


        else:
            raise ValueError(
                "下位机模式选择错误，现有的模式有", [mode.name for mode in Mode]
            )
        self.serial.write(bytes(self.send_buffer))
        self.__wait_for_movement_done()
        time.sleep(0.05)

    # 在下发动作后，比如前进，旋转等，下位机执行结束后会回传任务结束指令[0xFF, 0x01, 0xFE]
    def __wait_for_movement_done(self):
        while True:
            header = ord(self.serial.read())
            if header == self.send_buffer[0]:
                if ord(self.serial.read()) == 0x01:
                    return True

    
    
    
    c
                
    # 向下位机发送二维码信息
    def send_qr_info(self, qr_info: str):
        assert qr_info, print("二维码信息为空")
        print(qr_info)
        self.__send_serial_msg(mode=Mode.qrcode, qr_info=qr_info)

    # 通知下位机扫码
    def notice_qr_info(self):
        self.__send_serial_msg(mode=Mode.qrcode)

    # 距离控制，支持x和y同时输入，先运行x再运行y
    def set_distance(self, x: float = 0, y: float = 0):
        x = 1e-9 if x == 0 else x
        y = 1e-9 if y == 0 else y
        x_dis = int(x * 100)
        y_dis = int(y * 100)
        if x_dis != 0:
            self.__send_serial_msg(mode=Mode.x_distance, x_dis=x_dis)
        if y_dis != 0:
            self.__send_serial_msg(mode=Mode.y_distance, y_dis=y_dis)

    # 较为精细的距离控制
    def move_in_mm(self, x: int = 0, y: int = 0):
        x = 128 if x > 128 else int(x)
        x = -127 if x < -127 else int(x)
        y = 128 if y > 128 else int(y)
        y = -127 if y < -127 else int(y)
        if x != 0:
            self.__send_serial_msg(mode=Mode.x_dis_mm, x_dis=x)
        if y != 0:
            self.__send_serial_msg(mode=Mode.y_dim_mm, y_dis=y)
        

    # 陀螺仪重置
    def reset(self):
        self.__send_serial_msg(mode=Mode.reset)
        print("gyroscope reset finish")
        
    # 我自己加的陀螺仪
    def gyroscope(self):
        self.__send_serial_msg(mode=Mode.gyroscope)
        print("gyroscope finish")

    # 将爪子转回原位
    def back(self):
        self.__send_serial_msg(mode=Mode.back_home)

    # 旋转，角度定义为[-127, 128]之间
    def rotate(self, angle: int):
        assert 128 >= angle >= -127, print("角度应当在[-127, 128]之间")
        self.__send_serial_msg(mode=Mode.rotate, angel=angle)

    # 右转
    def turn_right(self):
        self.rotate(-70)
        #self.reset()
        #self.gyroscope()

    # 左转
    def turn_left(self):
        self.rotate(70)
        #self.reset()
        #self.gyroscope()

    def test(self, num):
        self.send_buffer[1] = 3
        self.send_buffer[4] = num

        self.serial.write(bytes(self.send_buffer))

    # 从原料区抓取物料块
    def grubBlockFromRawArea(self):
        self.__send_serial_msg(mode=Mode.grub_1)

    def new_move(self):
        self.__send_serial_msg(mode=Mode.new_move)

    # 从地面抓取物料块
    def grubBlockFromGround(self):
        self.__send_serial_msg(mode=Mode.grub_2)

    # 将物料块放到圆环上
    def putBlockToCircle(self):
        self.__send_serial_msg(mode=Mode.down_1)

    # 精加工区，将物料块放到另一个物料块上
    def putBlockToAnotherBlock(self):
        self.__send_serial_msg(mode=Mode.down_2)

    # 调整升降台到合适的位置    1.读取二维码  2.识别原料区  3.识别圆环   4.识别物料块圆心
    def adjustHeight(self, target_height: HeightMode):
        heightConfigs = [mode for mode in HeightMode]
        if target_height not in heightConfigs:
            raise ValueError("小车高度模式中没有这个模式{0}".format(target_height))
        self.__send_serial_msg(mode=Mode.adjust_height, x_dis=target_height)

    """
        混合模式: 支持在小车的移动过程中移动升降台，减少时间
        输入参数：
            height_mode: 期望的模式，支持单纯的升降台移动，以及夹取后的直接离开
            move_dis: 小车移动距离（仅限X方向移动）
        返回参数：
            无；当接收到下位机信号后，函数结束
    """

    def move_while_adjusting_height(self, mix_mode, move_dis: float):
        if abs(move_dis) > 1.25:
            raise ValueError("太远了，这个模式最远支持1.25m")
        dis = 100 * move_dis
        self.__send_serial_msg(mode=Mode.mix_mode, x_dis=dis, y_dis=mix_mode)


    def get_qrPos(self) -> str:
        buffer = [0xFF, 0, 0, 0, 0, 0, 0, 0, 0,0xFE]
        buffer[1] = 54
        
        result = []
        self.serial.write(bytes(self.send_buffer))
        while True:
            header = ord(self.serial.read())
            if header == 0xFF:
                for i in range(7):
                    result.append(self.serial.read().decode("gbk"))
                print(result)
                if self.serial.read() == 0xFE:
                    break
        
               # break
            
        #buffer = [0xFF, 0, 0, 0, 0, 0, 0, 0, 0, 0xFE]
        #buffer[1] = 54
        #try:
         #    #发送指令
         #   self.serial.write(bytes(buffer))
         #   result = []
         #   while True:
         #       data = self.serial.read()
         #       if not data:
         #           continue
         #       header = ord(data)
         #       if header == 0xFF:
         #           for _ in range(7):
         #               byte_data = self.serial.read()
         #               if byte_data:
         #                   result.append(byte_data)
          #          break
            # 将字节列表转换为字符串
          #  result_str = ''.join([byte.decode('utf-8', errors='ignore') for byte in result])
           # return result_str
        #except serial.SerialException as e:
         #   print(f"串口通信错误: {e}")
         #   return ""
        #except UnicodeDecodeError as e:
        #    print(f"解码错误: {e}")
        #    return ""
        return result

