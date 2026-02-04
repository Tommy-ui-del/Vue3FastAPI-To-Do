<template>
  <header>
    <!-- 应用图标 -->
    <img src="@/assets/note.png" alt="" />
    <!-- 导航区域 -->
    <nav>
      <h1 class="app-name">
        <!-- 应用名称链接，点击跳转到首页 -->
        <router-link :to="{ name: 'Home' }"> 待办 APP </router-link>
      </h1>
    </nav>
    <!-- 未登录状态显示注册和登录按钮 -->
    <button v-if="!loggedIn" @click="router.push({ name: 'Registration' })" class="button-74">
      注册
    </button>
    <button v-if="!loggedIn" @click="router.push({ name: 'Authorization' })" class="button-74" id="login-button">
      登录
    </button>
    <!-- 已登录状态显示登出按钮 -->
    <button v-else class="button-74" @click="authStore.logout()">登出</button>
  </header>
</template>

<script setup>
// 导入认证store，用于检查用户登录状态
import { useAuthStore } from "@/store/authStore.js";
// 导入Vue的computed函数，用于创建计算属性
import { computed } from "vue";
// 导入路由器，用于页面跳转
import { useRouter } from "vue-router";

const router = useRouter();
const authStore = useAuthStore();
// 创建计算属性，检查用户是否已登录（只读），无参数的箭头函数，作用是直接返回 authStore.isAuthenticated 的值
const loggedIn = computed(() => authStore.isAuthenticated);
</script>

<style scoped>
* {
  font-family: "Kalam", cursive;
}

header {
  grid-area: header;
  margin-top: 2px;
  background-color: bisque;
  /* making HEADER inside of the grid flexbox */
  display: flex;  /* Flexbox容器 维度-->一维（行或列）；典型场景-->导航栏、按钮组、居中*/
  justify-content: center;  /* 水平居中*/
  align-items: center; /* 垂直居中 */
}

header nav {
  margin-left: 10px;
  display: flex;
  width: 100%;
}

/*Vue 的 <router-link> 组件在渲染到 DOM 时会被转换成 <a> 标签 */
header a {
  text-decoration: none;
  color: black;
}

.button-74 {
  background-color: #fbeee0;
  border: 2px solid #422800;
  border-radius: 25px;
  box-shadow: #422800 3px 3px 0 0;
  color: #422800;
  cursor: pointer;  /* 鼠标悬停时，鼠标样式,提示是可点击元素 */
  font-weight: 300;
  font-size: 16px;
  padding: 3px 18px;
  line-height: 20px;
  text-align: center;
  text-decoration: none;
  user-select: none;
  -webkit-user-select: none;
  touch-action: manipulation;
  flex: 0;
  margin-right: 15px;
  flex-basis: 100px;
}

/*针对 id="login-button" 的元素设置的样式 */
#login-button {
  flex-basis: 90px;
  flex-shrink: 0;
}

/*针对 <header> 标签下所有 <img> 元素的样式 */
header img {
  width: 30px;
  margin-left: 10px;
}

/*鼠标悬停在 class="button-74" 元素上时触发的样式 */
.button-74:hover {
  background-color: #fff;
}

/*** 鼠标点击（激活状态）**  */
.button-74:active {
  box-shadow: #422800 2px 2px 0 0;
  transform: translate(2px, 2px);
}

@media only screen and (max-width: 460px) {
  .greetings {
    margin-left: 10px;
  }
}
</style>
