import React, { Component } from "react";
import { APIGateway } from "@bone/linkdevelop-sdk";
import { Card, Grid, Feedback, Progress, Input, Button } from '@bone/bone-web-ui';
import style from './index.css';
import MyChart from './components/chart';
import MyBatteryChart from './components/batteryChart';
import * as config from '../../config';

const { Row, Col } = Grid;
const Toast = Feedback.toast;

export default class Dashboard extends Component {
    //设定组件的显示初始状态
    state = {
        temperature: 1,
        humidity: 1,
        batteryLife: 98,
        setTemp: 0
    }

    //React组件生命周期：完成浏览器加载后运行
    componentDidMount() {
        //为组件设置定时器，100ms运行一次定时器中的函数
        this.timer = setInterval(() => { this.onDataChange(), this.onCheckEvent() }, 1000);
    }

    //React组件生命周期：组件卸载后，卸载定时器
    componentWillUnmount() {
        clearInterval(this.timer);
    }

    //获取当前最新设备上传属性的函数
    onDataChange = () => {
        APIGateway.request("https://api.link.aliyun.com/thing/device/properties/query", {
            version: "1.1.0",
            data: {
                // 接口参数
                "productKey": config.productKey,
                "deviceName": config.deviceName
            }
        }).then(response => {
            //从API返回数据中提取属性值，通过react组件setState方法更新页面
            response.data.forEach(element => {
                if (element.attribute === "BatteryPercentage") {
                    this.setState({
                        batteryLife: element.value
                    });
                }
                if (element.attribute === "IndoorTemperature") {
                    this.setState({
                        temperature: element.value
                    });
                }
                if (element.attribute === "RelativeHumidity") {
                    this.setState({
                        humidity: element.value
                    });
                }
            });
        }).catch(error => {
            console.log(error);
        });
    }

    //获取设备事件快照官方API
    onCheckEvent() {
        APIGateway.request("https://api.link.aliyun.com/thing/device/event/get", {
            version: "1.1.0",
            data: {
                // 接口参数
                "productKey": config.productKey,
                "deviceName": config.deviceName,
                "eventIdentifier": "lowBatteryAlert"
            }
        }).then(response => {
            if (response.data.eventCode === "lowBatteryAlert") {
                // console.log((Date.now() - response.data.timestamp) / 1000);
                //判断最新一次获取到的事件快照与当前时刻时差不超过5秒，认为是最新事件，进行弹窗
                if ((Date.now() - response.data.timestamp) / 1000 <= 5) {
                    this.onToastShow(response.data.eventName, response.data.eventType, response.data.eventBody)
                }
            }
        }).catch(error => {
            console.log(error);
        });
    }

    //控制页面弹窗
    onToastShow = (eventName, eventType, eventBody) => {
        Toast.show({
            offset: [0, 200],
            hasMask: true,
            type: 'error',
            content: eventName + '：' + this.state.batteryLife,
        });
    }

    //调用官方服务API接口
    onInvokeService() {
        APIGateway.request("https://api.link.aliyun.com/thing/device/service/invoke", {
            version: "1.1.0",
            data: {
                // 接口参数
                "productKey": config.productKey,
                "deviceName": config.deviceName,
                "inputParams": { IndoorTemperature: this.state.setTemp },
                "method": "setTemp",
            }
        }).then(response => {
            if(response.code===200){
                Toast.show({
                    offset: [0, 200],
                    hasMask: true,
                    type: 'success',
                    content: '设定温度成功' + '：' + this.state.setTemp,
                });
            }
            else{
                Toast.show({
                    offset: [0, 200],
                    hasMask: true,
                    type: 'error',
                    content: '设定温度失败' + '：' + response.message,
                });
            }
        }).catch(error => {
            console.log(error);
        });
    }

    //组件页面渲染函数
    render() {
        const colResponsiveProps = {
            xs: 10,
            sm: 10,
            md: 10,
            lg: 10,
            xl: 10,
        };
        const batteryColResponsiveProps = {
            xs: 4,
            sm: 4,
            md: 4,
            lg: 4,
            xl: 4,
        };
        return (
            <div className={style.container}>
                <Row className={style.row}>
                    <Col {...colResponsiveProps}>
                        <MyChart
                            number={this.state.temperature}
                            threshold={50}
                            unit='°C'
                            title="室内温度"
                            chartColor={'#53A0FD'}
                        />
                    </Col>
                    <Col {...batteryColResponsiveProps} className={style.batteryColResponsiveProps} style={{ margin: '0 auto' }}>
                        <MyBatteryChart
                            number={this.state.batteryLife}
                            threshold={102}
                            unit='%'
                            title="电池电量"
                            chartColor={'#FF7256'}
                        />
                        <div className={style.addbar}>
                            <Input
                                className={style.input}
                                placeholder="服务测试输入"
                                onChange={value => {this.setState({ setTemp: parseFloat(value) })}}
                                onPressEnter={this.onInvokeService.bind(this)}
                            />
                            <Button type="primary" onClick={this.onInvokeService.bind(this)}>下发服务指令</Button>
                        </div>
                    </Col>
                    <Col {...colResponsiveProps}>
                        <MyChart
                            number={this.state.humidity}
                            threshold={102}
                            unit='%'
                            title="室内相对湿度"
                            chartColor={"#3CB371"}
                        />
                    </Col>
                </Row>
            </div>
        )
    }
}