from re import sub
import time
import os
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

# 初始化参数
desired_caps = {
    "platformName": "Android",
    "platformVersion": "12",
    "deviceName": "1C271FDF6005P2",
    "appPackage": "org.videolan.vlc",
    "appActivity": ".StartActivity",
    # 'appActivity': '.gui.MainActivity',
    'noReset': True,  # 不要重置App，如果为False的话，执行完脚本后，app的数据会清空，比如你原本登录了，执行完脚本后就退出登录了
    'newCommandTimeout': 7200,  # 命令的时间间隔
    # 'unicodeKeyboard': True,  # 绕过手机键盘操作，unicodeKeyboard是使用unicode编码方式发送字符串，即中文
    # 'resetKeyboard': True,  # 绕过手机键盘操作，resetKeyboard是将键盘隐藏起来
}

# 启动app
driver = webdriver.Remote('http://localhost:4723/wd/hub', desired_caps)
# time.sleep(1)
# driver.find_element(by=AppiumBy.ID, value='skip_button').click()
# time.sleep(1)

# 功耗测试触发
app_uid = get_app_uid()
subprocess.call('adb shell dumpsys battery unplug')
subprocess.call('adb shell dumpsys batterystats --reset')

# 触发video进行播放
driver.find_element(by=AppiumBy.ID, value="org.videolan.vlc:id/nav_more").click()
time.sleep(1)
driver.find_element(by=AppiumBy.ID, value="org.videolan.vlc:id/mrl_item_uri").click()

# ans = 0
for i in range(1):
    print("i： ", i+1)
    time.sleep(1200)

    # 获取功耗
    app_cost = get_app_cost(app_uid=app_uid)
    print(f"App total cost: {app_cost} mAh") 
    
    # 保存文件
    subprocess.call('adb shell dumpsys batterystats > /sdcard/Documents/{}_consumption.txt'.format(time.strftime("%Y_%m_%d_%H_%M_%S")))

print("done")
driver.quit()
