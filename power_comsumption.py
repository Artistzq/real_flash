from re import sub
import time
import os
import sys
import subprocess
from subprocess import Popen, PIPE
from appium import webdriver
from appium.webdriver.common.appiumby import AppiumBy

def get_app_uid():
    process = subprocess.Popen('adb shell "ps | grep \'org.videolan.vlc\'"', shell=False, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    res = process.communicate()
    uid_temp = res[0].decode().split()[0]
    temp = uid_temp.split("_")
    return temp[0] + temp[1]

def get_app_cost(app_uid):
    process = subprocess.Popen(f'adb shell "dumpsys batterystats | grep \'UID {app_uid}\'"', shell=False, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    target_log = process.communicate()[0].decode()
    print(target_log)
    details = target_log[target_log.find("(") + 1 : target_log.find(")")].strip()
    details = details.split(" ")
    total_cost = 0.
    for para in details:
        cost = float(para.split("=")[1])
        total_cost += cost
    return total_cost

# # 功耗测试触发
duration = int(sys.argv[1])

subprocess.call('adb shell dumpsys battery unplug')
subprocess.call('adb shell dumpsys batterystats --reset')

print("start")
time.sleep(duration)

# 获取功耗
app_cost = get_app_cost(get_app_uid())
print(f"App total cost: {app_cost} mAh") 

# 保存文件
subprocess.call('adb shell dumpsys batterystats > /sdcard/Documents/{}_consumption.txt'.format(time.strftime("%Y_%m_%d_%H_%M_%S")))
print("done")