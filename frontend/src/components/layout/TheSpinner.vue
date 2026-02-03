<!--提供一个简单的自定义圆形加载动画（Spinner）,用于在异步操作（如API请求）进行时显示加载状态，提供视觉反馈，让用户知道系统正在处理请求-->
<template>
  <div id="loading"></div>
</template>

<style scoped>
#loading {
  display: inline-block;
  width: 35px;
  height: 35px;
  position: relative;
  margin-left: auto;
  margin-right: auto;
  margin-top: 30px;
  left: 0;
  right: 0;
  bottom: 1px;
  padding: 0px;
  border: 3px solid rgba(139, 155, 48, 0.3);
  border-radius: 50%;
  border-top-color: rgb(192, 138, 46);
  /* 应用旋转动画：1秒一圈，缓动效果，无限循环 */
  animation: spin 1s ease-in-out infinite;
  -webkit-animation: spin 1s ease-in-out infinite;
}

/* 定义名为spin的动画（标准写法） */
@keyframes spin {
  to {
    -webkit-transform: rotate(360deg);
  }
}
@-webkit-keyframes spin {
  to {
    -webkit-transform: rotate(360deg);
  }
}
</style>
