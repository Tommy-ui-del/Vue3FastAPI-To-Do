<template>
  <!-- 使用PostIt组件作为容器，提供便签纸风格的UI -->
  <PostIt class="post-it">
    <!-- 注册表单，提交时调用submitRegistrationDetails方法 -->
    <form @submit.prevent="submitRegistrationDetails">
      <div class="container">
        <h2>Create an Account</h2>

        <!-- 姓名输入框 -->
        <div class="icon-div" :class="{ isError: errorName }">
          <img src="@/assets/register/user.png" alt="user" class="user-img" />
          <input type="text" placeholder="Enter name" v-model="name" @blur="errorName = ''" @keypress="errorName = ''" />
        </div>
        <!-- 姓名错误提示 -->
        <span v-if="errorName" class="error">{{ errorName }}<br /></span>

        <!-- 邮箱输入框 -->
        <!-- @blur 是 Vue 中的事件修饰符，用于监听元素的失去焦点事件,当用户离开输入框时，清除对应的错误提示,常与 @keypress 事件配合使用，在用户开始输入时就清除错误提示-->
        <div class="icon-div" :class="{ isError: errorEmail }">
          <img src="@/assets/register/email.png" alt="email" class="email-img" />
          <input type="text" placeholder="Enter email" v-model="email" @blur="errorEmail = ''"
            @keypress="errorEmail = ''" />
        </div>
        <!-- 邮箱错误提示 -->
        <span v-if="errorEmail" class="error">{{ errorEmail }}<br /></span>
        
        <!-- 用户名输入框 -->
        <div class="icon-div" :class="{ isError: errorUsername }">
          <img src="@/assets/register/username.png" alt="username" class="username-img" />
          <input type="text" placeholder="Enter username" v-model="username" @blur="errorUsername = ''"
            @keypress="errorUsername = ''" />
        </div>
        <!-- 用户名错误提示 -->
        <span v-if="errorUsername" class="error">{{ errorUsername }}<br /></span>
        
        <!-- 密码输入框 -->
        <div class="icon-div" :class="{ isError: errorPassword }">
          <img src="@/assets/register/password.png" alt="password" class="password-img" />
          <input id="inline-input" :type="passwordType" placeholder="Enter password" v-model="password"
            @blur="errorPassword = ''" @keypress="errorPassword = ''" />
            <!-- 显示/隐藏密码的图标 -->
            <img :src="showPassword ? openEyesURL : closedEyesURL" alt="show-password" class="show-password-img"
            @click="toggleShow" />
        </div>

        <!-- 密码确认输入框 -->
        <div class="icon-div" :class="{ isError: errorPassword }">
          <!-- 密码匹配状态图标 -->
          <img alt="password-verification" class="verification-img"
            :src="passwordsMatch ? lockedPasswordURL : unlockedPasswordURL" :class="passwordsMatch
              ? 'password-is-confirmed'
              : 'password-not-confirmed'
              " />
          <input :type="passwordType" placeholder="Re-enter password" v-model="passwordConfirmation"
            @blur="errorPassword = ''" @keypress="errorPassword = ''" />
        </div>
        <!-- 密码错误提示 -->
        <span v-if="errorPassword" class="error" style="margin-top: 5px; display: block">{{ errorPassword }}</span>
       
        <!-- 后端返回的注册错误提示 -->
        <span v-if="errorRegister" class="error" style="margin-top: 5px; display: block">
          {{ errorRegister }}</span>
        <span v-else><br /></span>
        <!-- 注册按钮 -->
        <button class="button-74" type="submit">Register</button>

        <!-- 登录链接 -->
        <div style="margin-top: 15px;">
          Already have an account?
          <router-link to="/login">Login</router-link>
        </div>

        <!-- 分隔线 -->
        <p class="decorated mt-5" style="user-select: none"><span>or</span></p>
        
        <!-- Google登录按钮 -->
        <div class="icon-div" id="google" @click="authStore.googleAuthenticate()">
          <img src="@/assets/register/google.png" alt="password" class="password-img" />
          <input id="inline-input" placeholder="Continue with Google" readonly style="cursor: pointer;" />
        </div>
      </div>
    </form>
  </PostIt>
</template>

<script setup>
// 导入Vue的ref和watch函数，用于创建响应式数据和监听数据变化
import { ref, watch } from "vue";
// 导入认证store，用于处理注册逻辑
import { useAuthStore } from "@/store/authStore.js";
// 导入PostIt组件，作为容器
import PostIt from "@/components/layout/PostIt.vue";
// 导入storeToRefs，用于从store中解构响应式数据
import { storeToRefs } from "pinia";
const authStore = useAuthStore();

// pulling registration error from backend 从store中解构注册错误状态
const { errorRegister } = storeToRefs(authStore);
const name = ref("");
const email = ref("");
// 邮箱正则表达式，用于验证邮箱格式
const emailRegEx =
  /^(([^<>()\]\\.,;:\s@"]+(\.[^<>()\]\\.,;:\s@"]+)*)|(".+"))@((\[[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}])|(([a-zA-Z\-0-9]+\.)+[a-zA-Z]{2,24}))$/;

// 错误状态
const errorName = ref("");  // 姓名错误
const errorEmail = ref("");  // 邮箱错误
const errorUsername = ref("");  // 用户名错误
const errorPassword = ref("");  // 密码错误

// 注册信息
const username = ref("");  // 用户名
const password = ref("");  // 密码
const passwordConfirmation = ref("");  // 确认密码
const showPassword = ref(false);  // 是否显示密码
const passwordType = ref("password");  // 密码输入框类型
const passwordsMatch = ref(false);  // 密码是否匹配

// 导入图标URL
const lockedPasswordURL = new URL("@/assets/register/locked.png", import.meta.url).href;
const unlockedPasswordURL = new URL("@/assets/register/unlocked.png", import.meta.url).href;
const openEyesURL = new URL("@/assets/register/eyes.png", import.meta.url).href;
const closedEyesURL = new URL("@/assets/register/closed_eyes.png", import.meta.url).href;

// 切换密码显示/隐藏
function toggleShow() {
  showPassword.value = !showPassword.value;
  if (showPassword.value) {
    passwordType.value = "text"; // 显示密码
  } else {
    passwordType.value = "password"; // 隐藏密码
  }
}
// 提交注册信息
async function submitRegistrationDetails() {
  // validate name 验证姓名
  if (name.value === "") {
    errorName.value = "Please Enter Name";
  } else {
    errorName.value = "";
  }

  // validate email   验证邮箱
  if (email.value === null || email.value === "") {
    errorEmail.value = "Please Enter Email";
  } else if (!emailRegEx.test(email.value)) {
    errorEmail.value = "Please Enter Valid Email";
  } else {
    errorEmail.value = "";
  }

  // validate username  验证用户名
  if (username.value === "") {
    errorUsername.value = "Please Enter Username";
  } else {
    errorUsername.value = "";
  }

  // validate passwords match 验证密码
  if (password.value === "" || passwordConfirmation.value === "") {
    errorPassword.value = "Please Enter Password";
  } else if (password.value !== passwordConfirmation.value) {
    errorPassword.value = "Passwords do not match";
  } else {
    errorPassword.value = "";
  }

  // checking all errors at once 检查所有错误是否为空
  let errorsArray = [
    errorName.value,
    errorEmail.value,
    errorUsername.value,
    errorPassword.value,
  ];
  const checker = (arr) => arr.every((arr) => arr === "");
  // 如果没有错误，提交注册信息
  if (checker(errorsArray)) {
    const payload = {
      name: name.value,
      email: email.value,
      username: username.value,
      password: password.value,
    };
    await authStore.register(payload);
  }
}

// Clear error from backend if any of the inputs change  监听输入变化，清除后端返回的错误
watch([name, username, email, password, passwordConfirmation], () => {
  errorRegister.value = false;
});

// 监听密码变化，检查密码是否匹配
watch([password, passwordConfirmation], () => {
  if (passwordConfirmation.value !== password.value) {
    passwordsMatch.value = false;
  } else {
    passwordsMatch.value = true;
  }
});
</script>

<style scoped>
* {
  font-family: "Kalam", cursive;
}

.user-img,
.email-img,
.username-img {
  width: 25px;
  height: 25px;
}

.password-img,
.verification-img {
  width: 20px;
  height: 20px;
  margin-left: 2px;
}

.show-password-img {
  width: 25px;
  height: 25px;
  margin-right: 3px;
}

.password-is-confirmed {
  filter: invert(50%) sepia(31%) saturate(1012%) hue-rotate(60deg) brightness(98%) contrast(87%);
}

.password-not-confirmed {
  filter: invert(14%) sepia(67%) saturate(5511%) hue-rotate(356deg) brightness(86%) contrast(98%);
}

#icon {
  margin-right: 10px;
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
}

.icon-div input {
  outline: none;
  border: none;
  background: none;
  font-size: 1em;
  padding: 0.3em;
  color: inherit;
  flex: auto 1 1;
  width: 100%;
  background: none;
  background-color: transparent;
}

.post-it {
  font-size: 15px;
  width: 200px;
  position: relative;
  left: 50%;
  transform: translateX(-50%);
}

#google:hover {
  background-color: rgb(238, 238, 172);
}


.error {
  color: red;
}

.isError {
  border: 0.5px solid red;
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