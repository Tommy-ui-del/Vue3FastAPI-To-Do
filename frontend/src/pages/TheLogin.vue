<template>
  <!-- 使用PostIt组件作为容器，提供便签纸风格的UI -->
  <PostIt class="post-it">
    <!-- 登录表单，提交时调用handleLogin方法 -->
    <form @submit.prevent="handleLogin">
      <h2>Login to Continue</h2>
      <!-- 用户名/邮箱输入框 -->
      <div class="icon-div">
        <img src="@/assets/register/user.png" alt="user" class="user-img" />
        <input type="text" placeholder="Username or Email" name="uname" required v-model="username"
          @blur="authStore.clearError()" />
      </div>

       <!-- 密码输入框 -->
      <div class="icon-div">
        <img src="@/assets/register/password.png" alt="password" class="password-img" />

        <input id="inline-input" :type="passwordType" placeholder="Password" name="psw" required v-model="password"
          @blur="authStore.clearError()" />
          <!-- 显示/隐藏密码的图标 -->
          <img :src="showPassword ? openEyesURL : closedEyesURL" alt="show-password" class="show-password-img"
          @click="toggleShow" />
      </div>
      <!-- 登录按钮 -->
      <button class="button-74" type="submit">Login</button>
      <!-- 错误消息显示 -->
      <div id="error-message" v-if="errorLogIn">
        {{ errorMessage }}
      </div>


      <!-- 注册链接 -->
      <div style="margin-top: 15px;">
        Don't have an account yet?
        <router-link to="/register">Register</router-link>
      </div>

      <!-- 分隔线 -->
      <p class="decorated mt-5" style="user-select: none"><span>or</span></p>

      <!-- Google登录按钮 -->
      <div class="icon-div" id="google" @click="authStore.googleAuthenticate()">
        <img src="@/assets/register/google.png" alt="password" class="password-img" />
        <input id="inline-input" placeholder="Continue with Google" readonly style="cursor: pointer;" />
      </div>

    </form>
  </PostIt>
</template>

<script setup>
// 导入Vue的ref函数，用于创建响应式数据
import { ref } from "vue";
// 导入认证store，用于处理登录逻辑
import { useAuthStore } from "@/store/authStore.js";
// 导入PostIt组件，作为容器
import PostIt from "@/components/layout/PostIt.vue";
// 导入storeToRefs，用于从store中解构响应式数据
import { storeToRefs } from "pinia";
// 导入Google Analytics事件跟踪函数
import { event } from "vue-gtag";

// 获取认证store实例
const authStore = useAuthStore();

// 导入显示/隐藏密码的图标URL
const openEyesURL = new URL("@/assets/register/eyes.png", import.meta.url).href;
const closedEyesURL = new URL("@/assets/register/closed_eyes.png", import.meta.url).href;

// 创建响应式数据
const username = ref("");  // 用户名/邮箱
const password = ref("");  // 密码
const showPassword = ref(false);  // 是否显示密码
const passwordType = ref("password");  // 密码输入框类型

// 从store中解构错误状态
const { errorMessage, errorLogIn } = storeToRefs(authStore);

// 切换密码显示/隐藏
const toggleShow = () => {
  showPassword.value = !showPassword.value;
  if (showPassword.value) {
    passwordType.value = "text"; // 显示密码
  } else {
    passwordType.value = "password"; // 隐藏密码
  }
}
// 处理登录
const handleLogin = async () => {
  // 调用store中的login方法进行登录
  await authStore.login(username.value, password.value);
  // 跟踪用户登录事件
  await userLoggedInGA();

}

// 跟踪用户登录事件的函数
const userLoggedInGA = async () => {
  event("user-logged-in", {
    event_category: "analytics",
    event_label: "User",
    value: 1,
  });
}

</script>

<style scoped>
* {
  font-family: "Kalam", cursive;
}

.post-it {
  font-size: 15px;
  width: 200px;
  position: relative;
  left: 50%;
  transform: translateX(-50%);
  padding-top: 50px;
  padding-bottom: 50px;
}

.user-img {
  width: 25px;
  height: 25px;
}

.password-img {
  width: 20px;
  height: 20px;
  margin-left: 3px;
}

.show-password-img {
  width: 25px;
  height: 25px;
  margin-right: 3px;
}

#error-message {
  color: red;
  font-weight: bold;
  margin-top: 10px;
}

#icon {
  margin-right: 10px;
}

#google:hover {
  background-color: rgb(238, 238, 172);
}


.fa-icons {
  font-size: 18px;
  margin-left: 5px;
}

.icon-div {
  display: flex;
  flex-direction: row;
  border: 1px solid #374669;
  border-radius: 5px;
  background: #fff;
  align-items: center;
  overflow: hidden;
  margin-top: 2px;
  margin-bottom: 5px;
}

.icon-div input {
  outline: none;
  border: none;
  background: none;
  font-size: 1em;
  padding: 0.5em;
  color: inherit;
  flex: auto 1 1;
  width: 100%;
  background: none;
  background-color: transparent;
}

.button-74 {
  background-color: #fbeee0;
  border: 2px solid #422800;
  border-radius: 25px;
  box-shadow: #422800 4px 4px 0 0;
  color: #422800;
  cursor: pointer;
  display: inline-block;
  font-weight: 600;
  font-size: 18px;
  padding: 0 18px;
  line-height: 40px;
  text-align: center;
  text-decoration: none;
  user-select: none;
  -webkit-user-select: none;
  touch-action: manipulation;
  margin-top: 10px;
  margin-bottom: 0px;
}

.button-74:hover {
  background-color: #fff;
}

.button-74:active {
  box-shadow: #422800 2px 2px 0 0;
  transform: translate(2px, 2px);
}

@media (min-width: 768px) {
  .button-74 {
    min-width: 120px;
    padding: 0 25px;
  }
}


/* headlines with lines */
.decorated {
  overflow: hidden;
  text-align: center;
}

.decorated>span {
  position: relative;
  display: inline-block;
}

.decorated>span:before,
.decorated>span:after {
  content: "";
  position: absolute;
  top: 50%;
  border-bottom: 1px solid;
  width: 100vw;
  margin: 0 20px;
}

.decorated>span:before {
  right: 100%;
}

.decorated>span:after {
  left: 100%;
}
</style>
