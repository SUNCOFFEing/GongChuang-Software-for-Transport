import cv2 as cv
import numpy as np
import os


class HsvSelector(object):
    def __init__(
            self, input_source, cap_index=None, img_path=None, video_path=None
    ) -> None:
        """
        input_source: 0 代表摄像头，1代表图片, 2代表视频
        """
        self.input_source = input_source
        self.display_type = "img" if input_source == 1 else "video"

        if input_source == 0:
            assert cap_index is not None, print("请指定摄像头标号")
            self.cap = cv.VideoCapture(cap_index)
            assert self.cap.isOpened(), print("摄像头未打开")

        elif input_source == 1:
            assert img_path is not None, print("请指定图片路径")
            assert os.path.exists(img_path), print("{0}路径下没有图片".format(img_path))
            self.image = cv.imread(img_path)

        elif input_source == 2:
            assert video_path is not None, print("请指定视频路径")
            assert os.path.exists(video_path), print("{0}路径下没有视频".format(video_path))
            self.cap = cv.VideoCapture(video_path)
            assert self.cap.isOpened(), print("视频文件未成功加载")

        else:
            raise ValueError("不支持此输入类型")

    def nothing(self, x):
        pass

    def start(self):
        window_name = "hsv_selector"
        cv.namedWindow(window_name)
        cv.createTrackbar("h_low", window_name, 0, 180, self.nothing)
        cv.createTrackbar("h_high", window_name, 180, 180, self.nothing)
        cv.createTrackbar("s_low", window_name, 0, 255, self.nothing)
        cv.createTrackbar("s_high", window_name, 255, 255, self.nothing)
        cv.createTrackbar("v_low", window_name, 0, 255, self.nothing)
        cv.createTrackbar("v_high", window_name, 255, 255, self.nothing)

        while True:
            h_low = cv.getTrackbarPos("h_low", window_name)
            h_high = cv.getTrackbarPos("h_high", window_name)
            s_low = cv.getTrackbarPos("s_low", window_name)
            s_high = cv.getTrackbarPos("s_high", window_name)
            v_low = cv.getTrackbarPos("v_low", window_name)
            v_high = cv.getTrackbarPos("v_high", window_name)

            color_low = np.array([h_low, s_low, v_low])
            color_high = np.array([h_high, s_high, v_high])

            if self.display_type == "img":
                img = self.image
            elif self.display_type == "video":
                _, img = self.cap.read()
            hsv_img = cv.cvtColor(img, cv.COLOR_RGB2HSV)
            mask = cv.inRange(hsv_img, color_low, color_high)
            result_img = cv.bitwise_and(img, img, mask=mask)

            cv.imshow("res", result_img)
            k = cv.waitKey(1) & 0xFF

            if k == 27:
                break
            elif k == ord("s"):
                text_low = "low_thresh = [{0}, {1}, {2}]".format(h_low, s_low, v_low)
                text_high = "high_thresh = [{0}, {1}, {2}]".format(
                    h_high, s_high, v_high
                )
                print(f"HSV数组为：\n{text_low},{text_high}")
            else:
                pass

    def __del__(self):
        self.cap.release()


if __name__ == "__main__":
    selector = HsvSelector(0, cap_index=0)
    selector.start()
