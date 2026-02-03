<template>
  <footer>
    <!-- 显示版权信息 -->
    <p class="footer-text">
      <strong>Bekzod Mirahmedov</strong> &copy; &nbsp; <!-- 加粗 / 版权符号 /自动更新显示当前年份 -->
      {{ new Date().getFullYear() }}
    </p>
  </footer>
</template>

<style scoped>
/*grid-area: footer;：将页脚元素放入父级网格容器中名为 footer 的区域（前提是父容器已通过 grid-template-areas 定义了该区域）
  Flexbox容器，单行显示内容
  justify-content  水平方向
  align-items 垂直方向
  margin-top: auto;：这是实现「粘性页脚」的关键技巧。在 Flexbox 布局中，margin-top: auto 会让页脚自动 “推” 到页面的最底部，无论页面内容多少，都能保证页脚始终在视口底部，不会因为内容太短而悬空。
*/
footer {
  grid-area: footer;
  background-color: bisque;
  /* making FOOTER inside of the grid flexbox */
  display: flex;
  justify-content: center;
  align-items: center;
  margin-top: auto;
}
</style>
