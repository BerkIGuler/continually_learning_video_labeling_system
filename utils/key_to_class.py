import cv2
import numpy as np


def generate_key():
    # while True:
    #     try:
    #         key = cv2.waitKey(0)
    #         print(key)
    #     except:
    #         print("error")
    cv2.imshow("window", np.zeros((100, 100, 3)))
    while True:
        try:
            key = cv2.waitKey() & 0xFF
            print(key, chr(key))
        except Exception as e:
            print(e)


if __name__ == "__main__":
    generate_key()
