<template>
    <div style="display: flex; justify-content: center; align-items: center; height: 100vh;">
        <div>
            <h2 style="text-align: center;">
                Authenticating via Google credentials...
            </h2>
            <div style="display: flex; justify-content: center;">
                <!-- 自定义加载组件：显示转圈/跳动等加载动画 -->
                <the-spinner></the-spinner>
            </div>
        </div>
    </div>
</template>


  
  
<script setup>
import TheSpinner from "@/components/layout/TheSpinner.vue";   // 导入加载动画组件

import { onMounted } from 'vue';  // 导入生命周期钩子
import { useAuthStore } from "@/store/authStore";   // 导入认证store


const authStore = useAuthStore();   // 获取认证store实例

// 处理Google认证的函数
//() => 是箭头函数，比普通 function() 写法更简洁，且会继承外层作用域的 this（在 Vue 组件中非常实用）
const authenticateViaBackend = async () => {
    // 从URL哈希中提取access_token
    const accessToken = new URLSearchParams(window.location.hash.substring(1)).get('access_token');
    // 调用store中的loginWithGoogle方法进行后端认证
    const authenticationSuccess = await authStore.loginWithGoogle(accessToken);

    if (authenticationSuccess) {
       // 认证成功，关闭弹窗
        window.close();

        // 如果有父窗口（打开弹窗的窗口），重定向到首页
        if (window.opener) {
            window.opener.location.href = '/';

        }
    }
};

// 组件挂载后执行认证
onMounted(async () => {
    await authenticateViaBackend();
})

</script>
  
  
  