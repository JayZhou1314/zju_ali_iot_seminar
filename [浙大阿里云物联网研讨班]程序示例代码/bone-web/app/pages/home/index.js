import React, { Component } from "react";
// 以CSS Modules方式引入Home页样式
import style from "./index.css";
// 引入图片
import LOGO from "./LOGO.png";

// 导出Home页组件
export default class Home extends Component {
    render(){
        return <div className={style.container}>
            <img className={ style.logo } src={ LOGO } />
            <p className={ style.welcome }>Hello Bone!</p>
        </div>
    }
}