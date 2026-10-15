import cv2

def check_available_cameras(max_index=10):
    available_cameras = []
    for i in range(max_index):
        cap = cv2.VideoCapture(i)
        if cap.isOpened():
            print(f"摄像头索引 {i} 可用")
            available_cameras.append(i)
            cap.release()
        else:
            print(f"摄像头索引 {i} 不可用")
    return available_cameras


if __name__ == "__main__":
    available_cameras = check_available_cameras()
    if available_cameras:
        print(f"可用的摄像头索引为: {available_cameras}")
    else:
        print("未找到可用的摄像头。")
