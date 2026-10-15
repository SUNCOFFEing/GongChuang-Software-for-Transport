

import cv2
import numpy as np

try:
    # 打开默认的摄像头（通常是电脑的内建摄像头）
    cap = cv2.VideoCapture(0)

    # 检查摄像头是否成功打开
    if not cap.isOpened():
        print("无法打开摄像头")
        exit()

    # 设置摄像头的分辨率，这里设置为 1280x720
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)

    while True:
        # 捕获一帧视频
        ret, frame = cap.read()

        # 如果成功捕获到帧
        if not ret:
            print("无法接收帧，退出...")
            break

        # 将图像转换为灰度图，因为霍夫圆检测需要单通道图像
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

        # 对图像进行高斯模糊，减少噪声影响
        #blurred = cv2.GaussianBlur(gray, (9, 9), 2)
        _, img = cap.read()
        img = cv2.medianBlur(img, 5)
        cimg = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        # 使用霍夫圆变换检测圆形
        circles = cv2.HoughCircles(
                cimg,
                cv2.HOUGH_GRADIENT,
                1,
                100,
                param1=100,
                param2=50,
                minRadius=50,
                maxRadius=150,
            )
        

        # 如果检测到圆形
        if circles is not None:
            circles = np.round(circles[0, :]).astype("int")
            for (x, y, r) in circles:
                # 绘制圆形轮廓
                cv2.circle(frame, (x, y), r, (0, 255, 0), 2)
                # 绘制圆心
                cv2.circle(frame, (x, y), 2, (0, 0, 255), 3)

        # 显示捕获到的图像
        cv2.imshow('Camera', frame)

        # 按 'q' 键退出a
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

except Exception as e:
    print(f"发生错误: {e}")
finally:
    # 释放摄像头并关闭所有窗口
    if 'cap' in locals() and cap.isOpened():
        cap.release()
    cv2.destroyAllWindows()
