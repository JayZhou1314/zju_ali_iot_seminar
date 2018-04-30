import React, { Component } from "react";
import { Chart, Geom, Axis, Tooltip, Coord, Label, Legend, View, Guide, Shape } from 'bizcharts';
const { Arc, Text } = Guide;


export default class MyBatteryChart extends Component {

    state = {
        number: this.props.number,
        threshold: this.props.threshold,
        unit: this.props.unit,
        title: this.props.title,
        chartColor: this.props.chartColor,
    }

    componentWillReceiveProps = () => {
        this.setState({
            number: this.props.number,
            threshold: this.props.threshold,
            unit: this.props.unit,
            title: this.props.title
        })
    }

    render() {

        const data1 = [];
        for (let i = 0; i < this.state.threshold; (i += parseInt(this.state.threshold / 50))) {
            const item = {};
            item.type = i + '';
            item.value = 10;
            data1.push(item);
        }

        const data2 = [];
        for (let i = 0; i < this.state.threshold; (i += parseInt(this.state.threshold / 50))) {
            const item = {};
            item.type = i + '';
            item.value = 10;
            if ((this.state.number - i) <= 1) {
                item.value = 14;
            }
            if (i > (this.state.number - parseInt(this.state.threshold / 50))) {
                item.value = 0;
            }
            data2.push(item);
        }

        const cols = {
            type: {
                range: [0, 1]
            },
            value: {
                sync: true
            }
        }
        const colsView2 = {
            type: {
                tickCount: 3
            }
        }
        return (

            <Chart height={window.innerHeight*0.9} scale={cols} padding={[0, 0, 200, 0]} forceFit>
                <View data={data1}>
                    <Coord type='polar' startAngle={-9 / 8 * Math.PI} endAngle={1 / 8 * Math.PI} radius={0.8} innerRadius={0.75} />
                    <Geom type="interval" position="type*value" color='rgba(0, 0, 0, 0.09)' size={6} />
                </View>
                <View data={data1} scale={colsView2}>
                    <Coord type='polar' startAngle={-9 / 8 * Math.PI} endAngle={1 / 8 * Math.PI} radius={0.55} innerRadius={0.95} />
                    <Geom type="interval" position="type*value" color='rgba(0, 0, 0, 0.09)' size={6} />
                    <Axis name='type'
                        grid={null}
                        line={null}
                        tickLine={null}
                        label={{
                            offset: -20,
                            textStyle: {
                                fontSize: 15,
                                fill: '#CBCBCB',
                                textAlign: 'center'
                            },
                            formatter: val => {
                                if (val == (this.state.threshold) - 1) {
                                    return this.state.threshold;
                                }
                                return val;
                            }
                        }}
                    />
                    <Axis name='value' visible={false} />
                </View>
                <View data={data2} >
                    <Coord type='polar' startAngle={-9 / 8 * Math.PI} endAngle={1 / 8 * Math.PI} radius={0.8} innerRadius={0.75} />
                    <Geom type="interval" position="type*value" color={['value', this.props.chartColor]} opacity={1} size={6} />
                    <Guide>
                        <Text position={['50%', '65%']}
                            content={(this.state.number) + this.state.unit}
                            style={{
                                fill: '#262626',
                                fontSize: 20,
                                textAlign: 'center',
                                textBaseline: 'middle'
                            }} />
                        <Text position={['50%', '75%']}
                            content={this.state.title}
                            style={{
                                fill: '#262626',
                                fontSize: 20,
                                textAlign: 'center',
                                textBaseline: 'middle'
                            }}
                        />
                    </Guide>
                </View>
            </Chart>
        )
    }
}