import cv2

# 打开摄像头，参数 0 表示使用默认摄像头，如果有多个摄像头，可以尝试 1、2 等
cap = cv2.VideoCapture(0)

if not cap.isOpened():
    print("无法打开摄像头")
    exit()

while True:
    # 读取摄像头的一帧画面
    ret, frame = cap.read()

    if not ret:
        print("无法接收帧（摄像头流结束？）")
        break #break

    # 在窗口中显示画面
    cv2.imshow('Camera Feed', frame)

    # 按下 'q' 键退出循环
    if cv2.waitKey(1) == ord('q'):
        break

# 释放摄像头资源
cap.release()
# 关闭所有 OpenCV 窗口
cv2.destroyAllWindows()