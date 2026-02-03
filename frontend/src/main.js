import { createApp } from "vue";
import App from "./App.vue";
import router from "./router.js";
import "./axios";    //axios是一个基于Promise的HTTP客户端，用于发送异步请求
import TheHeader from "@/components/layout/TheHeader.vue";
import TheFooter from "@/components/layout/TheFooter.vue";

import { createPinia } from "pinia";    //Pinia是Vue 3的官方状态管理库，用于管理跨组件共享的状态
import VueGtag from "vue-gtag";  //vue-gtag是Google Analytics集成插件

const app = createApp(App);

const pinia = createPinia();

app.component("the-header", TheHeader);
app.component("the-footer", TheFooter);

app.use(router);
app.use(VueGtag, { config: { id: import.meta.env.VITE_GA_MEASUREMENT_ID } }); // 配置Google Analytics
app.use(pinia);

app.mount("#app");
