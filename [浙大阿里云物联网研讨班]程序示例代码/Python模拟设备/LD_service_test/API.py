# coding=utf-8
# https://github.com/sunfuze/api-gateway-demo-sign-python
import uuid
import json

import time

from com.aliyun.api.gateway.sdk import client
from com.aliyun.api.gateway.sdk.http import request
from com.aliyun.api.gateway.sdk.common import constant

host = "https://api.link.aliyun.com"
url = "/thing/device/event/timeline/get"

cli = client.DefaultClient(app_key="your_appKey", app_secret="your_appSecret")

# post form

req_post = request.Request(host=host, protocol=constant.HTTPS, url=url, method="POST", time_out=30000)

# 进行api测试修改下列参数即可
bodyMap = {
    'id': str(uuid.uuid4()),
    'version': "1.0",
    'request': {
        'iotToken': "xxxx",
        'apiVer': "1.1.0"
    },
    'params': {
        # 接口参数
        'productKey': "your_productKey",
        'deviceName': "yor_deviceName",
        'eventIdentifier': "lowBatteryAlert",
        'eventType': "alert",
        'start': int(time.time()) - 5,
        'end': int(time.time()),
        'pageSize': 1,
        'ordered': 1
    }
}

headers = {
    'accept': 'application/json'
}

req_post.set_body(bodyMap)
req_post.set_headers(headers)
req_post.set_content_type(constant.CONTENT_TYPE_JSON)
print cli.execute(req_post)
