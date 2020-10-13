#encoding:utf-8
import cv2 as cv
import numpy as np
import math
from selenium import webdriver
from selenium.webdriver.common.action_chains import ActionChains
import time
import random

def FindLines(image):
    image = cv.cvtColor(image, cv.COLOR_BGR2GRAY)  # 二值化
    blurred = cv.GaussianBlur(image, (5, 5), 0)  # 高斯模糊
    canny = cv.Canny(blurred, 200, 400)  # canny边缘检测
    lines = cv.HoughLinesP(canny, 1, np.pi / 180, 20, minLineLength=15, maxLineGap=8)  # 霍夫变换寻找直线
    return lines[:, 0, :]  # 返回直线

# 这里对直线进行过滤
def FindResultLises(lines):
    resultLines = []
    for x1, y1, x2, y2 in lines:
        if (abs(y2 - y1) < 5 or abs(x2 - x1) < 5) and min(x1, x2) > 60:  # 只要垂直于坐标轴的直线并且起始位置在60像素以上
            resultLines.append([x1, y1, x2, y2])
    return resultLines


# 判断点是否在直线上
def distAbs(point_exm, list_exm):
    x, y = point_exm
    x1, y1, x2, y2 = list_exm
    dist_1 = math.sqrt(abs((y2 - y1) + (x2 - x1) + 1))  # 直线的长度
    dist_2 = math.sqrt(abs((y1 - y) + (x1 - x) + 1)) + math.sqrt(abs((y2 - y) + (x2 - x) + 1))  # 点到两直线两端点距离和
    return abs(dist_2 - dist_1)


# 交点函数 y = kx + b 求交点位置
def findPoint(line1, line2):
    poit_status = False
    x1, y1, x2, y2 = line1
    x3, y3, x4, y4 = line2
    x = y = 0

    if (x2 - x1) == 0: # 垂直x轴
        k1 = None
        b1 = 0
    else:
        k1 = 1.0 * (y2 - y1) / (x2 - x1)
        b1 = y1 * 1.0 - k1 * x1 * 1.0

    if (x4 - x3) == 0:
        k2 = None
        b2 = 0
    else:
        k2 = 1.0 * (y4 - y3) / (x4 - x3)
        b2 = y3 * 1.0 - k2 * x3 * 1.0

    if k1 is None:
        if not k2 is None:
            x = x1
            y = k2 * x1 + b2
            poit_status = True
    elif k2 is None:
        x = x3
        y = k1 * x3 + b1
        poit_status = True
    elif k1 != k2:
        x = (b2 - b1) * 1.0 / (k1 - k2)
        y = k1 * x * 1.0 + b1 * 1.0
        poit_status = True

    return poit_status, [x, y]


# 求交点
def linePoint(resultLines):
    for x1, y1, x2, y2 in resultLines:
        for x3, y3, x4, y4 in resultLines:
            point_is_exist, [x, y] = findPoint([x1, y1, x2, y2], [x3, y3, x4, y4])   # 两线是否有交点
            if point_is_exist:
                dist_len1 = distAbs([x, y], [x1, y1, x2, y2])
                dist_len2 = distAbs([x, y], [x3, y3, x4, y4])
                if dist_len1 < 5 and dist_len2 < 5:  # 如果误差在5内我们认为点在直线上
                    # 判断交点在行直线中是左端点还是右端点
                    if abs(y2 - y1) < 5:
                        # x1是行直线
                        if abs(x1 - x) + abs(y1 - y) < 5:  # 左端点
                            return -1, [x, y]
                        else:
                            return 1, [x, y]
                    else:
                        # x2是行直线
                        if abs(x3 - x) + abs(y3 - y) < 5:
                            return -1, [x, y]
                        else:
                            return 1, [x, y]
    return 0, [0, 0]


def moveTrack(xoffset):  # 通过加速减速模拟滑动轨迹
    updistance = xoffset * 4 / 5
    t = 0.2
    v = 0
    steps_list = []
    current_offset = 0
    while current_offset < xoffset:
        if current_offset < updistance:
            a = 2 + random.random() * 2
        else:
            a = -random.uniform(12, 13)
        vo = v
        v = vo + a * t
        x = vo * t + 1 / 2 * a * (t * t)
        x = round(x, 2)
        current_offset += abs(x)
        steps_list.append(abs(x))
    # 上面的 sum(steps_list) 会比实际的大一点，所以再模拟一个往回拉的动作，补平多出来的距离
    disparty = sum(steps_list) - xoffset
    last1 = round(-random.random() - disparty, 2)
    last2 = round(-disparty - last1, 2)
    steps_list.append(last1)
    steps_list.append(last2)
    return steps_list

def findCentre(L_or_R, point_x):
    if L_or_R == -1:
        xoffset = point_x[0] + 20
    elif L_or_R == 1:
        xoffset = point_x[0] - 20
    return xoffset

def findMoveTrajectory():
    img0 = cv.imread(r'./yuantu.png')  # 读取图片
    line0 = FindLines(img0)  # 找到直线
    lines = FindResultLises(line0)  # 筛选直线
    L_or_R, point_x = linePoint(lines)  # 交点坐标跟走向
    xoffset = findCentre(L_or_R, point_x)  # 计算阴影中心X轴坐标
    steps = moveTrack(xoffset)  # 生成运动轨迹
    return steps

def a():
    print("nima")
if __name__ == '__main__':
    browser = webdriver.Chrome(r'C:\Users\Administrator\Desktop\chromedriver.exe') # 打开浏览器
    browser.get('http://www.geetest.com/Register')  # 输入网址
    browser.find_element_by_xpath('//input[@placeholder="手机号码"]').send_keys('156********')  # 输入手机号
    browser.find_element_by_xpath('//div[contains(text(),"获取验证码")]').click()  # 点击获取验证码
    time.sleep(2)
    browser.find_element_by_class_name('geetest_window').screenshot('./yuantu.png')  # 验证码截图
    time.sleep(2)
    steps = findMoveTrajectory()  # 获取移动轨迹
    artice = browser.find_element_by_class_name('geetest_slider_button')  # 选取按钮
    action = ActionChains(browser)
    action.click_and_hold(artice).perform()  # 按住移动按钮
    action.reset_actions()
    for step in steps:  # 循环移动
        action.reset_actions()
        action.pause(0.01).move_by_offset(step, 0).perform() # 移动
    time.sleep(0.5)
    action.release(artice).perform() # 放开按钮
    time.sleep(5)  # 查看有没有成功
