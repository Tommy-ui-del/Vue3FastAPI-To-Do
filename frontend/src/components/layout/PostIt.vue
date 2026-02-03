<template>
  <!-- 便签纸风格的容器组件 -->
  <div class="post-it-note">
    <!-- 插槽，用于放置内容 -->
    <slot></slot>
  </div>
</template>

<style scoped>

.post-it-note {
  margin: 20px 0px 0px 10px;
  padding: 1em;
  background: #ffffd4; /* 便签纸的黄色背景 */
  position: relative;
  min-height: 10em;
  margin-bottom: 30px;
  box-shadow: rgba(17, 17, 26, 0.05) 0px 4px 16px,
    rgba(17, 17, 26, 0.05) 0px 8px 32px;
}

/* 伪元素的核心作用是给元素的「特定部分」添加样式，或者创建一个「虚拟的元素」，这个虚拟元素不存在于 HTML 的 DOM 结构中，只在 CSS 渲染时生效
不需要额外添加 <div> 等标签来做折角，HTML 只需要保留核心内容（便签里的文字）*/

/* 便签纸底部的折叠效果 */
.post-it-note:after {
  content: ""; /*必须设置 content 属性（即使值为空字符串 ""），否则伪元素不会被浏览器渲染显示，等于无效。 */
  position: absolute;
  bottom: -2em;
  left: 0;
  right: 2em;
  border-width: 1em;
  border-style: solid;
  border-color: #ffffd4;
}
.post-it-note:before {
  content: "";
  position: absolute;
  bottom: -2em;
  right: 0;
  border-width: 2em 2em 0 0;
  border-style: solid;
  border-color: #dcdc46 transparent;
}

@media (max-width: 768px) {
  .post-it-note {
    margin-right: 10px;
  }
}
</style>
