import cv2
import numpy as np
import matplotlib.pyplot as plt
from pre_process import _reshape_img, get_model


def segment_img(_img, limit):
    for i in range(0, _img.shape[0] - 1):
        for j in range(0, _img.shape[1] - 1):
            if int(_img[i, j + 1]) - int(_img[i, j]) >= limit:
                _img[i, j] = 0
            elif int(_img[i, j - 1]) - int(_img[i, j]) >= limit:
                _img[i, j] = 0
    return _img


class Calculate:
    def __init__(self, img_name="new.jpg"):
        model_name = "ridge_model"
        img_file = 'images/resized/{}'.format(img_name)
        orig_img = 'images/Fractured Bone/{}'.format(img_name)

        img_t = cv2.imread(img_file, cv2.IMREAD_COLOR)
        img = cv2.imread(orig_img, cv2.IMREAD_COLOR)

        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        median = cv2.medianBlur(gray, 5)

        model = get_model(model_name)
        pred_thresh = int(model.predict([_reshape_img(img_t)]))
        bool, threshold_img = cv2.threshold(median, pred_thresh, 255, cv2.THRESH_BINARY)
        line = []

        for i in range(0, gray.shape[0]):
            tmp_initial = []
            tmp_final = []
            for j in range(0, gray.shape[1] - 1):
                if threshold_img[i, j] == 0 and (threshold_img[i, j + 1]) == 255:
                    tmp_initial.append((i, j))
                if threshold_img[i, j] == 255 and (threshold_img[i, j + 1]) == 0:
                    tmp_final.append((i, j))

            x = [each for each in zip(tmp_initial, tmp_final)]
            x.sort(key=lambda each: each[1][1] - each[0][1])
            try:
                line.append(x[len(x) - 1])
            except IndexError:
                pass
        err = 15
        danger_points = []
        dist_list = []

        for i in range(1, len(line) - 1):
            dist_list.append(line[i][1][1] - line[i][0][1])
            try:
                prev_ = line[i - 3]
                next_ = line[i + 3]
                dist_prev = prev_[1][1] - prev_[0][1]
                dist_next = next_[1][1] - next_[0][1]
                diff = abs(dist_next - dist_prev)
                if diff > err:
                    data = (diff, line[i])
                    if len(danger_points):
                        prev_data = danger_points[len(danger_points) - 1]
                        if abs(prev_data[0] - data[0]) > 2 or data[1][0] - prev_data[1][0] != 1:
                            danger_points.append(data)
                    else:
                        danger_points.append(data)
            except:
                pass
            start, end = line[i]
            mid = int((start[0] + end[0]) / 2), int((start[1] + end[1]) / 2)
        for i in range(0, len(danger_points) - 1, 2):
            try:
                start_rect = danger_points[i][1][0][::-1]
                start_rect = (start_rect[0] - 40, start_rect[1] - 40)
                end_rect = danger_points[i + 1][1][1][::-1]
                end_rect = (end_rect[0] + 40, end_rect[1] + 40)
                cv2.rectangle(img, start_rect, end_rect, (0, 255, 0), 2)
            except:
                pass
        self.fig1, ax1 = plt.subplots(1, 1)
        self.fig2, ax2 = plt.subplots(1, 1)
        self.fig3, ax3 = plt.subplots(1, 1)
        x = np.arange(1, gray.shape[0] - 1)
        y = dist_list
        cv2.calcHist(gray, [0], None, [256], [0, 256])
        try:
            ax1.plot(x, y)
        except:
            pass

        img = np.rot90(img)
        ax2.imshow(img)
        ax3.hist(gray.ravel(), 256, [0, 256])
        cv2.waitKey(0)
        cv2.destroyAllWindows()


if __name__ == "__main__":
    prediction = Calculate()
