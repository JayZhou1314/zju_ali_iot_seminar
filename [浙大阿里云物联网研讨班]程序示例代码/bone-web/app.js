import { createApp } from "@bone/web";
// 引入各个页面组件
import Home from "./app/pages/home";
import Dashboard from "./app/pages/dashboard";
import NotFound from "./app/pages/not-found";

// 创建App实例
export default createApp({
    // 设置应用ID
    appName: "training",
    // 配置路由信息
    router: {
        routes: [
            {
                // 页面路径
                path: "/",
                // 页面组件
                page: Home
            },
            {
                path: "/dashboard",
                page: Dashboard
            }
        ],
        // routes中路由无法匹配时显示的404页面
        notFound: NotFound
    }
})