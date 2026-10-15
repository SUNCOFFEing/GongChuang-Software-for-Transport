from typing import Tuple
import numpy as np
import cv2 as cv
from pyzbar.pyzbar import decode
from imutils import contours
import math

from loguru import logger

from .config import color_list

# 输入两个点的坐标，获取两个点之间的距离，并取整
def Distance(x1, y1, x2, y2) -> int:
    x = abs(x1 - x2)
    y = abs(y1 - y2)
    return int(round(math.sqrt(x * x + y * y)))


# 图像识别类，包含摄像头的初始化以及后续的识别
class Detection(object):
    # 颜色矩阵
    #lower_green = np.array([32, 69, 49])(原)
    #upper_green = np.array([84, 255, 255])
    
    # 更严格的绿色范围(可以）
    lower_green = np.array([40, 80, 40])  # 提高最低饱和度
    upper_green = np.array([80, 255, 200])  # 限制最大亮度
    
    lower_red = np.array([86, 90, 150])
    upper_red = np.array([180, 255, 255])
    
    lower_blue = np.array([0, 101, 0])  
    upper_blue = np.array([37, 255, 255])
    
    

    

    

    def __init__(self, camera_index) -> None:
        self.camera_index = camera_index
        self.cap = cv.VideoCapture(camera_index)
        assert self.cap.isOpened(), print("摄像头打开失败")
        # print("摄像头初始化成功")
        print("摄像头初始化成功")
        _, frame = self.cap.read()
        
        
        self.width = frame.shape[1]
        self.height = frame.shape[0]
        self.debug = False
        self.test = False
        self.cv_big_version = int(cv.__version__[0])

    def set_debug(self, whether_debug: bool):
        if whether_debug:
            self.debug = True
        else:
            self.debug = False

    def skip_some(self, count=5):
        for i in range(count):
            _, _ = self.cap.read()

    # 获取二维码信息
    def get_qr_info(self, data_len=-1) -> str:
        if self.test:
            return "123+321"
        data = ""
        data_flag = False
        while True:
            _, frame = self.cap.read()
            for barcode in decode(frame):
                data_ = barcode.data.decode("utf-8")
                if self.debug:
                    (x, y, w, h) = barcode.rect
                    cv.rectangle(frame, (x, y), (x + w, y + h), (255, 255, 0), 2)
                    cv.putText(
                        frame, data_, (x, y), cv.FONT_HERSHEY_PLAIN, 1.0, (0, 0, 255)
                    )
                # 没有数据长度限制
                if not self.debug:
                    if data_len == -1:
                        data = data_
                        data_flag = True
                        break
                    else:
                        if len(data_) == data_len:
                            data = data_
                            data_flag = True
                            break

            if self.debug:
                cv.imshow("frame", frame)
                k = cv.waitKey(1) & 0xFF
                if k == 27:
                    cv.destroyWindow("frame")
                    break
            if not self.debug and data_flag:
                break
        return data

    # 返回圆心相对于图像中心的比例，x为正，表示圆心在中心右边，需右移
    # y为正，表示圆心在中心下边，需下移
    def get_circle_center(self) -> Tuple[float, float]:
        if self.test:
            return 0.0, 0.0
        self.skip_some()
        count = count_ori = 2
        D_X = []
        D_Y = []
        while True:
            _, img = self.cap.read()
            img = cv.medianBlur(img, 5)
            cimg = cv.cvtColor(img, cv.COLOR_BGR2GRAY)

            circles = cv.HoughCircles(
                cimg,
                cv.HOUGH_GRADIENT,
                1,
                100,
                param1=100,
                param2=50,
                minRadius=150,
                maxRadius=200,
            )
            
            

            # 判断霍夫检测是否检测到圆
            if not isinstance(circles, np.ndarray):
                if self.debug:
                    cv.imshow("frame", cimg)
                    k = cv.waitKey(1) & 0xFF
                    if k == 27:
                        break

                continue

            # 限制，当只有一个圆时
            if len(circles[0]) == 1:
                circles = np.uint16(np.around(circles))
                # print(circles.shape)
                circle = circles[0, 0, :]
                # print(circle.shape)
                #draw the outer circle
                cv.circle(cimg, (circle[0], circle[1]), circle[2], (0, 255, 0), 2)
                #draw the center of the circle
                cv.circle(cimg, (circle[0], circle[1]), 2, (0, 0, 255), 3)
                
                
                #cv.imshow('Camera', cimg)
                #cv.imshow("c", cimg)
                #cv.waitKey()
                #cv.destroyAllWindows()
                
                x, y = circle[0], circle[1]
                dx = (x - self.width / 2) / self.width * 2
                dy = (y - self.height / 2) / self.height * 2
                D_X.append(dx)
                D_Y.append(dy)
                count = count - 1

            if self.debug:
                cv.imshow("frame", cimg)
                k = cv.waitKey(1) & 0xFF
                if k == 27:
                    break

            # 记录连续多次的圆心，取平均
            if count < 1:
                DeltaX = 0
                DeltaY = 0
                for dx, dy in zip(D_X, D_Y):
                    DeltaX = DeltaX + dx
                    DeltaY = DeltaY + dy
                if not self.debug:
                    break
                else:
                    print(DeltaX / len(D_X), DeltaY / len(D_Y))
                    count = count_ori

        return DeltaX / len(D_X), DeltaY / len(D_Y)

    # 识别原料区不同颜色的物料块
    def detect_color(self, color) -> bool:
        if self.test:
            return True
        min_height = 180  # 色块的最小高度
        min_width = 100  # 色块的最小宽度
        assert color in color_list[1:], print("没写这个颜色")
        lower_color = None
        upper_color = None
        if color == "red":
            lower_color = self.lower_red
            upper_color = self.upper_red
        elif color == "green":
            lower_color = self.lower_green
            upper_color = self.upper_green
        elif color == "blue":
            lower_color = self.lower_blue
            upper_color = self.upper_blue
        else:
            print("!!没这个颜色")
        while True:
            _, frame = self.cap.read()
            cutted_frame = frame[240:480, 220:420]
            hsv_frame = cv.cvtColor(cutted_frame, cv.COLOR_RGB2HSV)
            img = cv.inRange(hsv_frame, lower_color, upper_color)
            if self.cv_big_version == 4:
                cnts, _ = cv.findContours(img, cv.RETR_TREE, cv.CHAIN_APPROX_NONE)
            else:
                raise RuntimeError("cv版本不对")

            if self.debug:
                cv.drawContours(cutted_frame, cnts, -1, (255, 0, 0), 2)
                cv.imshow("frame", frame)
                cv.imshow("cutted_frame", cutted_frame)
                cv.imshow("hsv_frame", hsv_frame)
                cv.imshow("after_hsv", img)
                k = cv.waitKey(1) & 0xFF
                if k == 27:
                    cv.destroyAllWindows()
                    break

            if len(cnts) > 0:
                s = []
                max_index = 0
                (cnts, boundingRects) = contours.sort_contours(cnts)
                for cnt in cnts:
                    s.append(cv.contourArea(cnt))
                    max_index = s.index(max(s))
                    (_, _, w, h) = boundingRects[max_index]
                if w > min_width and h > min_height:
                    print(w)
                    print(h)
                    print(color)
                    if not self.debug:
                        return True
                    else:
                        pass
                else:
                    pass

    # 返回圆心相对于图像中心的比例，x为正，表示圆心在中心右边，需右移
    # y为正，表示圆心在中心下边，需下移
    def get_colored_circle_center(self, color, min_r=100) -> Tuple[float, float]:
        if self.test:
            return 0.0, 0.0

        assert color in color_list[1:], print("没写这个颜色")
        if color == "red":
            lower_color = self.lower_red
            upper_color = self.upper_red
        elif color == "green":
            lower_color = self.lower_green
            upper_color = self.upper_green
        else:
            lower_color = self.lower_blue
            upper_color = self.upper_blue

        self.skip_some()
        count = count_ori = 2
        D_X = []
        D_Y = []
        while True:
            _, ori_img = self.cap.read()
            # 提取相应颜色区域
            hsv_frame = cv.cvtColor(ori_img, cv.COLOR_RGB2HSV)
            img = cv.inRange(hsv_frame, lower_color, upper_color)
            contours, _ = cv.findContours(img, cv.RETR_TREE, cv.CHAIN_APPROX_SIMPLE)
            max_index, max_area = (0, 0)

            # 寻找最大的轮廓
            for i, contour in enumerate(contours):
                if cv.contourArea(contour) > max_area:
                    max_index = i
                    max_area = cv.contourArea(contour)

            # 如果最大轮廓的面积够大，计算圆心
            if max_area > 3.14 * (min_r ** 2):
                (x, y), radius = cv.minEnclosingCircle(contours[max_index])
                center = (int(x), int(y))
                radius = int(radius)
                cv.circle(ori_img, center, radius, (0, 255, 0), 2)
                cv.circle(ori_img, center, 4, (0, 255, 255), 3)
                dx = (x - self.width / 2) / self.width * 2
                dy = (y - self.height / 2) / self.height * 2
                D_X.append(dx)
                D_Y.append(dy)
                count -= 1
            else:
                pass

            # debug模式下，显示图像
            if self.debug:
                cv.imshow('ori_img', ori_img)
                cv.imshow('img', img)
                k = cv.waitKey(1) & 0xFF
                if k == 27:
                    break

            # 返回差值
            if count < 1:
                DeltaX = 0
                DeltaY = 0
                for dx, dy in zip(D_X, D_Y):
                    DeltaX = DeltaX + dx
                    DeltaY = DeltaY + dy
                if not self.debug:
                    return DeltaX / len(D_X), DeltaY / len(D_Y)
                else:
                    print(DeltaX / len(D_X), DeltaY / len(D_Y))
                    count = count_ori

    def __del__(self):
        logger.info('摄像头检测类销毁')
        self.cap.release()
        del self.cap


if __name__ == "__main__":
    cap_index = 0  # 摄像头索引
    detect = Detection(0)
    detect.set_debug(True)  # 调试模式，会把检测结果显示出来，设置为False的话就不会有图像显示

    # 所有的识别都是通过按下ESC退出，然后进入下一阶段

    # 颜色识别
    for color in ["red", "green", "blue"]:
        detect.detect_color(color)

    # for color in ["red", "green", "blue"]:
    #     detect.get_colored_circle_center(color)

    # # 二维码识别
    # info = detect.get_qr_info(data_len=7)  # 超时时间，20s内没有读取到就退出
    # print(info)

    # # 圆心检测
    # dx, dy = detect.get_circle_center()
    # print("x方向误差{0}, y方向误差{1}".format(dx, dy))

    # # 直线检测
    # k, d_y = detect.get_line_info()
    # print("检测到直线斜率{0}, y方向与中心差值{1}".format(k, d_y))
