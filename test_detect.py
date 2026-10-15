#!/usr/bin/python3
# coding:utf-8
import cv2 as cv
from models.Detection import Detection
from models.MoveControl import MoveControl
from models.config import pi, color_list, HeightMode, MixMode


if __name__ == "__main__":

    # cap1 = cv.VideoCapture(0)
    # print(cap1.read()[1].shape)
    # cap1.release()
    # del cap1

    # cap2 = cv.VideoCapture(2)
    # print(cap2.read()[1].shape)
    # exit(0)
    # qr_detect = Detection('/dev/qr_cam33')
    
    # mc = MoveControl("/dev/ttyUSB0", 115200)
    # # down_detect = Detection(2)

    # # 回到启停区
    # mc.putBlockToAnotherBlock()
    # exit(0)
    # mc.grubBlockFromGround()

    # mc.adjustHeight(target_height=HeightMode.qrPos)
    # qr_detect = Detection(0)
    # info = qr_detect.get_qr_info()
    # del qr_detect
    # print(info)
    
    
    # down_detect = Detection(0)
    # for color in color_list[1:]:
    #     mc.adjustHeight(target_height=HeightMode.rawArea)
    #     down_detect.detect_color(color)
    #     mc.grubBlockFromRawArea()


    # for color in color_list[1:]:
    #     # mc.adjustHeight(target_height=HeightMode.rawArea)
    #     # down_detect.get_circle_center(color)
    #     mc.putBlockToCircle()
    # mc.set_distance(x = 0.5)
    # mc.set_distance(y = -0.55)
    # mc.turn_left()
    # exit(0)
    
    # mc.adjustHeight(target_height=HeightMode.circleArea)

    down_detect = Detection(1)
    down_detect.debug = True
    thresh = 0.03; dis_max = 127
    while True:
        d_x, d_y = down_detect.get_colored_circle_center('blue', min_r=50)
        print(d_x, d_y)
        # if abs(d_x) > thresh:
        #     # mc.move_in_mm(y=d_x * dis_max)
        #     print('y: ' , d_x * dis_max)
        #     continue
        # if abs(d_y) > thresh:
        #     # mc.move_in_mm(x=-d_y * dis_max * 0.75)
        #     print('x: ' , -d_y * dis_max * 0.75)
        # if abs(d_x) < thresh and abs(d_y) < thresh:
        #     break
    # mc.move_in_mm(y = -8)
    # mc.move_in_mm(x = 5)
    mc.putBlockToAnotherBlock()
    exit(0)

    # mc.adjustHeight(target_height=HeightMode.circleArea)
    # thresh = 0.05; dis_max = 72
    # while True:
    #     d_x, d_y = down_detect.get_circle_center()
    #     if abs(d_x) > thresh:
    #         mc.move_in_mm(x=-d_x * dis_max * 0.75)
    #         continue
    #     if abs(d_y) > thresh:
    #         mc.move_in_mm(y=-d_y * dis_max)
    #     if abs(d_x) < thresh and abs(d_y) < thresh:
    #         break

    # mc.putBlockToCircle()

