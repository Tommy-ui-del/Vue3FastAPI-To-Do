<template>
  <template v-if="authStore.isAuthenticated">
    <!-- 如果用户已认证，显示任务列表 -->
    <TheTasks />
  </template>
  <template v-else>
    <!-- 如果用户未认证，显示仪表盘 -->
    <TheDashboard />
  </template>
</template>

<script setup>
// import TheDashboard from "./TheDashboard.vue";
// import TheTasks from "./TheTasks.vue";
import { defineAsyncComponent } from "vue";    //用于异步加载组件，优化性能

import { useAuthStore } from "@/store/authStore";  //认证管理状态

//（）=>import (),动态导入实现路由懒加载（按需加载，优化性能）
const TheDashboard = defineAsyncComponent(() => import("./TheDashboard.vue"));
const TheTasks = defineAsyncComponent(() => import("./TheTasks.vue"));

const authStore = useAuthStore();  //获取认证store实例

// 从localStorage读取用户信息，初始化认证状态//恢复用户登录状态
if (localStorage.getItem("user")) {
  authStore.isAuthenticated = true;
} else {
  authStore.isAuthenticated = false;
}
</script>
