import win32gui
import win32ui
import ctypes
from ctypes import windll
import time
import numpy as np
from numpy.ctypeslib import ndpointer
import cv2

lib = ctypes.cdll.LoadLibrary('./recolor.so')
recolor = lib.recolor
recolor.restype = None
recolor.argtypes = [ndpointer(ctypes.c_ubyte, flags="C_CONTIGUOUS"), ctypes.c_size_t]

def screenshot(hwnd):
    left, top, right, bot = win32gui.GetClientRect(hwnd)
    w = right - left
    h = bot - top

    hwndDC = win32gui.GetWindowDC(hwnd)
    mfcDC  = win32ui.CreateDCFromHandle(hwndDC)
    saveDC = mfcDC.CreateCompatibleDC()

    saveBitMap = win32ui.CreateBitmap()
    saveBitMap.CreateCompatibleBitmap(mfcDC, w, h)
    saveDC.SelectObject(saveBitMap)

    result = windll.user32.PrintWindow(hwnd, saveDC.GetSafeHdc(), 3)

    img = None

    if result == 1:
        bmpstr = saveBitMap.GetBitmapBits(True)
        img = np.frombuffer(bmpstr, dtype=np.uint8)
        img.shape = (h, w, 4)

    win32gui.DeleteObject(saveBitMap.GetHandle())
    saveDC.DeleteDC()
    mfcDC.DeleteDC()
    win32gui.ReleaseDC(hwnd, hwndDC)

    return img

def remove_bar(image):
    cropped = image[-1264 :, :]

    return cropped

def crop_and_downsize(image, target_height, target_width, downsize_ratio):
    height, width = image.shape[:2]
    hmin = height // 2 - target_height // 2
    wmin = width // 2 - target_width // 2

    cropped = image[hmin : hmin + target_height : downsize_ratio, wmin : wmin + target_width : downsize_ratio]

    return cropped

def process(image):
    hsv = cv2.cvtColor(image[:, :, :3], cv2.COLOR_BGR2HSV) #convert rgba image to hsv
    height, width = image.shape[:2]

    recolor(hsv, height * width)
    #for i in range(height):
    #    for j in range(width):
    #        if hsv[i][j][1] >= 64 and hsv[i][j][2] >= 32 and (hsv[i][j][0] < 110 or hsv[i][j][0] > 120): #not own pixel, probably enemy
    #            hsv[i][j][0] = 0
    return hsv