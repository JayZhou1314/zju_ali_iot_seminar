#!/usr/bin/python
# coding=utf-8
import time
import json
import random
import hashlib
import httplib2
from iot_device import IoTDevice

# device config
device_conf = {
    "product_key": "your_productKey",
    "device_name": "your_deviceName",
    "device_secret": "your_deviceSecret",
    "version": "1.0.0"
}

# device random_msg config
device_random_data = {
    "RelativeHumidity": "{{random_float(50,60)}}",
    "IndoorTemperature": "{{random_float(15,20)}}",
    "BatteryPercentage": "{{calc_battery(2)}}",
    # ":events": {
    #     "BatteryAlert": {
    #         # 实现电量的自动报警需要修改这部分的代码在设备类中实现
    #         "BatteryPercentage": "{{98}}"
    #     }
    # },
    ":services": ["setTemp"]
}


# 定义计算电池电量损失的函数
def calc_battery(cost_rate):
    hour = (time.time() - 1525015289.10) / 3600  # 计算当前时间秒
    cost = hour * cost_rate
    print(round(100 - cost, 2))
    return round(100 - cost, 2)


# 定义随机取整数函数
def random_int(min, max):
    return random.randint(min, max)


# 定义随机取浮点数函数
def random_float(min, max):
    return round(random.uniform(min, max), 2)


device = IoTDevice(
    pk=device_conf["product_key"],
    dn=device_conf["device_name"],
    ds=device_conf["device_secret"])


# 连接状态打印回调函数
def connect_cb(rc):
    if rc != 0:
        print("unexpected disconnected with code:%d" % rc)
    else:
        print("mqtt connect successfully!")
        # my_air_condition.set({"IndoorTemperature":30})
        # device.report_ota_progress(-2)


# 发布状态打印回调函数
def post_cb(code, id, msg):
    if code == 200:
        print("id:%s post successfully" % id)
    else:
        print("post failed")


# 打印服务调用的回调函数，里面需要添加指令的解析以及参数处理返回结果
def service_cb(service_id, params):
    print("received service call, method:%s params:%s" % (service_id, params))


# 打印OTA升级服务调用的回调函数
def upgrade_cb(code, data, message):
    if code == "1000":
        print("upgrade message received, data:%s" % data)
        # report 10% progress
        device.report_ota_progress(10)

        h = httplib2.Http()
        rsp, content = h.request(data["url"])

        device.report_ota_progress(80)

        # check size
        if len(content) != data["size"]:
            device.report_ota_progress(-2)

        # check md5
        content_md5 = hashlib.md5(content).hexdigest()
        if content_md5 != data["md5"]:
            device.report_ota_progress(-3)

        # update version
        device.version = data["version"]

        # ota finished
        time.sleep(5)
        device.report_ota_progress(100)

        # report new version
        device.report_version(data["version"])
    else:
        print("upgrade error with code: %s, message: %s" % (code, message))


device.version = device_conf["version"]
device.callback_set(connect_cb, post_cb, service_cb, upgrade_cb)
device.connect()
flag = 1


# 程序运行主函数，原始文件中的random_loop
def random_loop(device, flag):
    device_random_eval = json.dumps(device_random_data).replace('"{{', '').replace('}}"', '')
    while True:
        time.sleep(5)
        device_random_msg = eval(device_random_eval)

        # 检查电量报警是否触发，低于30%开始事件上报
        if device_random_msg["BatteryPercentage"] <= 30:
            device_random_msg[":events"] = {
                "lowBatteryAlert": {
                    "BatteryPercentage": device_random_msg["BatteryPercentage"]
                }
            }
        # 事件信息检查上报
        if device_random_msg.has_key(':events'):
            events = device_random_msg.pop(':events')
            for e in events:
                device.on_event(e, events[e])

        # # 设备服务订阅
        if device_random_msg.has_key(':services'):
            service_ids = device_random_msg.pop(':services')
            for service_id in service_ids:
                device.register_service(service_id)

        device.post(device_random_msg)


random_loop(device, flag)
