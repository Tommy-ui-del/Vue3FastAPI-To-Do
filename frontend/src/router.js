import { createRouter, createWebHistory } from "vue-router";  // 导入路由创建函数

// 使用动态导入实现路由懒加载    ,import() 自动返回Promise对象
//路由懒加载() => import()就是把 “所有页面一次性加载” 改成 “用到哪个页面才加载哪个页面”
const TheHome = () => import("./pages/TheHome.vue");
const TheLogin = () => import("@/pages/TheLogin.vue");  // 别名路径（@通常指向src目录）
const TheRegistration = () => import("./pages/TheRegistration.vue");
const TheDemo = () => import("./pages/TheDemo.vue");
const NotFound = () => import("./pages/NotFound.vue");

// 定义路由配置
const routes = [
  {
    path: "/",              // URL路径
    name: "Home",           // 路由名称
    component: TheHome,     // 对应的组件
  },
  {
    path: "/login",
    name: "Authorization",
    component: TheLogin,
  },
  {
    path: "/register",
    name: "Registration",
    component: TheRegistration,
  },
  {
    path: "/demo",
    name: "Demo",
    component: TheDemo,
  },
  {
    path: "/callback/",
    component: () => import("@/pages/GoogleCallback.vue"),
  },
  { path: "/:notFound(.*)", component: NotFound },
];

// 创建路由实例
const router = createRouter({
  history: createWebHistory(),   // 使用HTML5 History模式
  routes,                        //路由配置
});

export default router;      //导出路由实例，，让其他组件接收
