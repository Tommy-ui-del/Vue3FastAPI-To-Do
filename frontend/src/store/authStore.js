import { defineStore } from "pinia";
import axios from "@/axios";
import router from "@/router.js";
import { trackUserLoggedInGA, trackUserRegistrationGA, trackUserLoggedInWithGoogleGA } from '@/gaUtils';  // 导入Google Analytics跟踪函数

// 定义认证store
export const useAuthStore = defineStore("authentication", {
  // 定义状态
  state: () => ({
    // initialize state from local storage to enable user to stay logged in
    // user: JSON.parse(localStorage.getItem("user")),
    errorLogIn: false,   // 登录错误状态
    errorMessage: "",     // 错误信息
    isAuthenticated: false,  // 用户是否已认证
    errorRegister: false,  // 注册错误状态
  }),

  // 定义方法
  actions: {
    // 用户名密码登录
    async login(username, password) {
      //URLSearchParams：创建一个表单数据对象，将用户名和密码以键值对形式存入，用于构造 x-www-form-urlencoded 格式的请求体
      const params = new URLSearchParams();
      params.append("username", username);
      params.append("password", password);

      // 设置请求头Header，JWT是Token（令牌，验证身份，授权）实现的一种方式
      const headers = {
        Accept: "application/json", //告诉服务器，客户端期望接收 JSON 格式的响应
        "Content-Type": "application/x-www-form-urlencoded", //告诉服务器，发送的请求体是表单编码格式（和 URLSearchParams 对应
      };
      // 使用 axios 库向后端接口 user/jwt/create/ 发送 POST 请求，传递表单参数和请求头
      await axios
        .post("user/jwt/create/", params, {
          headers: headers,
        })
        .then((response) => {
          // store user details and jwt in local storage to keep user logged in between page refreshes
          // 将用户信息和后端返回的 JWT Token 存入浏览器本地存储，实现 “页面刷新后保持登录状态” 的效果
          localStorage.setItem("user", JSON.stringify(response.data));
          // update pinia state ，更新认证状态
          this.isAuthenticated = true;
          // 重定向到首页
          router.push({ name: "Home" });
          // 跟踪用户登录事件
          trackUserLoggedInGA();

        })

         // 处理错误信息
        .catch((error) => {
          console.log(error);
          this.errorLogIn = true;
          // catching connection refused error
          if (error.message === "Network Error") {
            this.errorMessage = error.message;
          } else {
            this.errorMessage = "Incorrect username/email or password";
          }
        });
    },

    // 触发Google OAuth认证流程
    googleAuthenticate() {
      // 从环境变量获取Google客户端ID
      let clientID = import.meta.env.VITE_GOOGLE_CLIENT_ID
      let authEndpoint = 'https://accounts.google.com/o/oauth2/auth'
      let scope = 'openid profile email'
      let responseType = 'token'
      let redirectURI = `${window.location.origin}/callback`
      // 计算回调URL
      const authUrl = `${authEndpoint}?client_id=${clientID}&redirect_uri=${redirectURI}&scope=${scope}&response_type=${responseType}`;
      // Calculate the center position
      const left = window.screen.width / 2 - 300; // Adjust 300 to half of the pop-up window width
      const top = window.screen.height / 2 - 300; // Adjust 300 to half of the pop-up window height

      // 构建Google OAuth URL
      const popupWindow = window.open(authUrl, "_blank", `width=600,height=600,left=${left},top=${top}`);

      // Optional: Focus on the new window， 聚焦到新窗口
      if (popupWindow) {
        popupWindow.focus();
      }
    },

    // 使用Google access token登录
    async loginWithGoogle(accessToken) {
      try {
        const googleLoginURL = "/user/google-login/";
         // 发送Google token到后端验证
        const response = await axios.post(googleLoginURL, {
          access_token: accessToken,
        });
        // 存储用户信息和JWT token到localStorage
        localStorage.setItem("user", JSON.stringify(response.data));
        // 更新认证状态
        this.isAuthenticated = true;
        // 跟踪Google登录事件
        trackUserLoggedInWithGoogleGA();
        return true;
      } catch (error) {
        console.log("Error while authenticating with Google", error);
        throw error;
      }
    },

    // 用户注册
    //payload 是用户提交的注册表单数据（通常包含用户名、密码、邮箱等信息）
    async register(payload) {
      await axios
        .post("users/register/", payload, {
          headers: {
            "Content-Type": "application/json",
          },
        })
        .then((response) => {
          console.log(
            `User ${response.data.username} has been successfully created!`
          );
          // 重定向到登录页
          router.push({ name: "Authorization" });
          // 跟踪用户注册事件
          trackUserRegistrationGA();
        })
        .catch((error) => {
          console.log(error);
          this.errorRegister = error.response.data.detail;
        });
    },

     // 用户登出
    logout() {
      // 清除localStorage中的用户信息
      localStorage.removeItem("user");
      // 更新认证状态
      this.isAuthenticated = false;
      // 重新加载页面
      location.reload();
    },

    // 刷新JWT token
    //“无感刷新”，避免用户因 Access Token 过期而频繁重新登录
    async refreshToken() {
      // 从localStorage获取用户信息
      var user = localStorage.getItem("user");
      user = JSON.parse(user);
      const refresh = user["refresh_token"];
      // 临时移除用户信息
      localStorage.removeItem("user");

      // 发送刷新token请求
      const response = await axios.post("user/jwt/refresh/", {
        refresh_token: refresh,
      });
      // reassign user in local storage 重新存储用户信息
      user["access_token"] = response.data.access_token;
      user["refresh_token"] = response.data.refresh_token;
      localStorage.setItem("user", JSON.stringify(user));
      // 返回新的access_token
      return response.data.access_token;
    },
    
    // 清除错误状态
    //是前端状态管理的辅助函数，用于重置错误标记，让界面恢复正常
    clearError() {
      this.errorLogIn = false;
    },
  },
});
