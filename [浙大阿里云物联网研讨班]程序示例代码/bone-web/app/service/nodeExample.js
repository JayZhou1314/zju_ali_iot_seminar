const Client = require('aliyun-api-gateway').Client;
const UUID = require('uuid');

// 用appKey和appSecret初始化客户端
const client = new Client('24865918', 'f3bf2b9f432fba7a5e5922c85f7bb405');

const Gateway = async ({url, apiVer, params, iotToken}) => {

    return await client.post(url, {
        data: {
            id: UUID.v1(), // 请求唯一标识，必填
            version: '1.0', // 协议版本，固定值1.0
            request: {
                iotToken, // iottoken，选填
                apiVer // api版本，必填
            },
            params: params || {} // 业务参数，必填
        },
        headers: {
            accept: 'application/json'
        },
        timeout: 3000
    });

};

const params = {
    url: 'http://api.link.aliyun.com/kit/debug/ping',
    apiVer: '1.0.0',
    params: {
        // 接口参数
        "input":"value1"
    }
}

Gateway(params)
    .then(res => console.log(res))
    .catch(res => console.log(res));
