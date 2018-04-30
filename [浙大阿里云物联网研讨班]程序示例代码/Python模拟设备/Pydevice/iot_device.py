#!/usr/bin/python
# coding=utf-8
import paho.mqtt.client as mqtt
import json
import random
import hashlib
import hmac
import threading


# 这个类为消息接受的线程
class MessageThread:
    def __init__(self, on_message_cb):
        self._msg = None
        self._on_message_cb = on_message_cb
        self._event = threading.Event()

        self._thread = threading.Thread(target=self._thread_main)
        self._thread.daemon = True
        self._thread.start()

        threading.Thread(target=self._thread_main)

    def async_post_message(self, msg):
        self._msg = msg
        self._event.set()

    def _thread_main(self):
        while True:
            self._event.wait()
            if self._on_message_cb != None:
                self._on_message_cb(self._msg)
            self._event.clear()


class IoTDevice(object):
    PORT = 1883
    HOST = ".iot-as-mqtt.cn-shanghai.aliyuncs.com"

    PROPERTY_TOPIC = "/sys/%s/%s/thing/event/property/post"
    EVENT_TOPIC = "/sys/%s/%s/thing/event/%s/post"
    SERVICE_TOPIC = "/sys/%s/%s/thing/service/%s"

    OTA_VERSION_TOPIC = "/ota/device/inform/%s/%s"
    OTA_UPGRADE_TOPIC = "/ota/device/upgrade/%s/%s"
    OTA_PROGRESS_TOPIC = "/ota/device/progress/%s/%s"

    # 初始化设备的productKey、deviceName、deviceSecret
    def __init__(self, pk, dn, ds):
        self._product_key = pk
        self._device_name = dn
        self._device_secret = ds
        self._mqtt_client = None
        self._version = None

        # self._host = pk + self.HOST
        self._host = pk + self.HOST
        self._port = self.PORT

        self._property_topic = self.PROPERTY_TOPIC % (self._product_key, self._device_name)
        self._property_reply_topic = self._property_topic + "_reply"
        self._version_topic = self.OTA_VERSION_TOPIC % (self._product_key, self._device_name)
        self._upgrade_topic = self.OTA_UPGRADE_TOPIC % (self._product_key, self._device_name)
        self._progress_topic = self.OTA_PROGRESS_TOPIC % (self._product_key, self._device_name)

        self._event_topic_reply_list = []
        self._service_topic_dict = {}
        self._service_topic_list = None

        self._conn_cb = None
        self._post_cb = None
        self._service_cb = None
        self._upgrade_cb = None

        # 设备的多线程接收类
        self._thread = MessageThread(self._on_async_message)

    # 执行设备各状态回调函数的初始化
    def callback_set(self, conn_cb, post_cb, service_cb, upgrade_cb):
        self._conn_cb = conn_cb
        self._post_cb = post_cb
        self._service_cb = service_cb
        self._upgrade_cb = upgrade_cb

    @property
    def device_name(self):
        return self._device_name

    @property
    def version(self):
        return self._version

    @version.setter
    def version(self, ver):
        self._version = ver

    def _on_connect(self, client, userdata, flags, rc):
        if self._conn_cb != None:
            if rc == 0:
                # subscribe topic
                self._mqtt_client.subscribe(self._property_reply_topic, 1)
                self._mqtt_client.subscribe(self._upgrade_topic, 1)

                # publish version
                self.report_version(self._version)

            self._conn_cb(rc)

    def _on_disconnect(self, client, userdata, rc):
        if self._conn_cb != None:
            self._conn_cb(rc)

    def _on_message(self, client, userdata, msg):
        # print "%s %s" % (msg.topic, msg.payload)
        self._thread.async_post_message(msg)

    def _on_async_message(self, msg):
        if msg.topic == self._property_reply_topic:
            if self._post_cb != None:
                ret_obj = json.loads(msg.payload)
                self._post_cb(ret_obj["code"], ret_obj["id"], ret_obj["message"])
        elif msg.topic == self._upgrade_topic:
            if self._upgrade_cb != None:
                ret_obj = json.loads(msg.payload)
                data = ret_obj["data"] if ret_obj.has_key("data") else None
                self._upgrade_cb(ret_obj["code"], data, ret_obj["message"])

        else:
            # 没有找到常用的topic，直接将topic的题目打印出来
            for real_event_topic_reply in self._event_topic_reply_list:
                if msg.topic == real_event_topic_reply:
                    print("topic %s recv!" % real_event_topic_reply)
                    return

            # 可以在其它业务topic中找到接受的topic
            # 回调函数返回结果还需要再上报到相应的topic
            for real_service_topic in self._service_topic_dict:
                if msg.topic == real_service_topic:
                    if self._service_cb != None:
                        ret_obj = json.loads(msg.payload)
                        self._service_cb(self._service_topic_dict[real_service_topic], ret_obj["params"])
                    return

    # 连接目标服务器的函数
    def connect(self):
        print("--start connect--")
        print("product_key:", self._product_key,
              "\ndevice_name:", self._device_name,
              "\ndevice_secret:", self._device_secret)

        client_id = "%s&&&%s|securemode=3,signmethod=hmacsha1,gw=1|" % (self._product_key, self._device_name)
        username = self._device_name + "&" + self._product_key

        # calc sign
        # 计算签名
        sign_content = "clientId%sdeviceName%sproductKey%s" % (
            self._product_key + "&&&" + self._device_name,
            self._device_name,
            self._product_key)
        password = hmac.new(self._device_secret, sign_content, hashlib.sha1).hexdigest()

        print("sign_content:", sign_content, "\npassword:", password)

        # mqtt client start initialize
        self._mqtt_client = mqtt.Client(client_id=client_id, clean_session=True)
        self._mqtt_client.username_pw_set(username, password)
        self._mqtt_client.on_connect = self._on_connect
        self._mqtt_client.on_disconnect = self._on_disconnect
        self._mqtt_client.on_message = self._on_message

        # mqtt client start connect
        self._mqtt_client.connect(host=self._host, port=self._port, keepalive=60)
        self._mqtt_client.loop_start()

    # 定义设备上报函数
    def post(self, value):
        payload = {
            "id": random.randint(100, 100000),
            "version": "1.0",
            "params": value,
            "method": "thing.event.property.post"
        }
        # 加了这部分的打印内容
        # print "publish topic:%s payload:%s" % (self._property_topic, json.dumps(payload))
        self._mqtt_client.publish(self._property_topic, json.dumps(payload), qos=1)

    # 设备处理事件
    def on_event(self, event_id, value):
        payload = {
            "id": random.randint(100, 100000),
            "version": "1.0",
            "params": value,
            "method": "thing.event.%s.post" % event_id
        }

        real_event_topic = self.EVENT_TOPIC % (self._product_key, self._device_name, event_id)
        real_event_topic_reply = real_event_topic + "_reply"

        self._event_topic_reply_list.append(real_event_topic_reply)
        self._mqtt_client.subscribe(real_event_topic_reply, 1)
        self._mqtt_client.publish(real_event_topic, json.dumps(payload), qos=1)

    # 设备注册函数
    def register_service(self, service_id):
        real_service_topic = self.SERVICE_TOPIC % (self._product_key, self.device_name, service_id)
        self._service_topic_dict[real_service_topic] = service_id
        self._mqtt_client.subscribe(real_service_topic, 1)

    # 设备上报OTA升级进度数据封装
    def report_ota_progress(self, progress):
        payload = {
            "id": random.randint(100, 100000),
            "params": {
                "step": str(progress),
                "desc": ""
            }
        }
        print("%s %s" % (self._progress_topic, json.dumps(payload)))
        self._mqtt_client.publish(self._progress_topic, json.dumps(payload), qos=1)

    # OTA升级设备上报当前版本号
    def report_version(self, ver):
        self._version = ver
        payload = {
            "id": random.randint(100, 100000),
            "params": {
                "version": ver
            }
        }
        print("%s %s" % (self._version_topic, json.dumps(payload)))
        self._mqtt_client.publish(self._version_topic, json.dumps(payload), qos=1)

   