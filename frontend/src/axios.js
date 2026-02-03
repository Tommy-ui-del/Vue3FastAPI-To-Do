import axios from "axios";
import { useAuthStore } from "@/store/authStore.js";   // 导入认证store

// 创建axios实例并配置基础地址（核心修改）
const axiosInstance = axios.create({
  // 指向后端FastAPI的服务地址+端口
  baseURL: 'http://localhost:8000',
  timeout: 10000, // 可选：请求超时时间
})


//response interceptor，响应拦截器
axiosInstance.interceptors.response.use(
  // If the response is successful, just return it，如果响应成功，直接返回
  (response) => {
    return response;
  },
  async (error) => {
    const originalRequest = error.config;
    // don't refresh if either access or refresh token is invalid， 如果是刷新token请求失败，直接登出
    if (
      error.response && originalRequest.url.includes("refresh")
    ) {
      const authStore = useAuthStore();
      authStore.logout();
    }
    // refresh token if it is expired 如果是401错误且不是重试请求，尝试刷新token
    else if (
      error.response && error.response.status === 401 &&
      !originalRequest._retry
    ) {
      originalRequest._retry = true; // 标记为重试请求，避免无限循环
      const authStore = useAuthStore();
      // get newly assigned access token，获取新的access token
      const newAccessToken = await authStore.refreshToken();
      // retry original request，更新原始请求的认证头
      originalRequest.headers["Authorization"] = "Bearer " + newAccessToken;
      // 重试原始请求
      return axios.request(originalRequest);
    } else {
      // some other error，其他错误直接拒绝
      console.log("Other error");
      return Promise.reject(error);
    }
  }
);
export default axiosInstance; // 导出配置好的axios实例