<template>
  <!-- 头部组件 -->
  <the-header></the-header>
  <main>
    <!-- 欢迎标题 -->
    <h1>欢迎使用待办事项APP</h1>
    <h2>简单但强大的任务管理应用</h2>
    
    <!-- 演示链接区域 -->
    <div class="linksbox">
      <post-it id="demo-link">
        <div class="inner-demo-link">
          <p>
            <strong> 试试演示操作。 无需注册! </strong>
          </p>
          <!-- 演示按钮，点击跳转到演示页面并跟踪事件 -->
          <button @click="router.push({ name: 'Demo' });demoAnalytics();" class="button-74">
            演示
          </button>
        </div>
      </post-it>
    </div>

    <!-- 轮播图区域，展示应用功能 -->
    <div class="swip">
      <swiper :slidesPerView="1"    
              :spaceBetween="30" 
              :loop="true" 
              :lazy="true" 
              :centeredSlides="true" 
              :pagination="{ clickable: true,}" 
              :autoplay="{delay: 5000,
              // disableOnInteraction: false,
              }" 
              :navigation="true" 
              :modules="modules"
      >
        <!--swiper-lazy 是 Swiper 懒加载需要的类名，标记这张图片需要懒加载    rel="preload"：提示浏览器预加载这张图片，提前缓存资源，提升切换时的流畅度-->
        <swiper-slide><img :src="slide1URL" alt="slide 1" class="slide-1 swiper-lazy" rel="preload" /></swiper-slide>
        <swiper-slide><img :src="slide2URL" alt="slide 2" class="slide-2 swiper-lazy" rel="preload" /></swiper-slide>
        <swiper-slide><img :src="slide3URL" alt="slide 3" class="slide-3 swiper-lazy" rel="preload" /></swiper-slide>
      
      </swiper>
    </div>
  </main>

  <!-- 底部组件 -->
  <the-footer class="footer"></the-footer>
</template>

<script setup>
// 导入Vue的ref函数，用于创建响应式数据
import { ref } from "vue";
// 导入Swiper组件，提供了在模板中使用的 <swiper> 和 <swiper-slide> 标签，只能提供基本的轮播结构，但没有任何功能
import { Swiper, SwiperSlide } from "swiper/vue";
// 导入PostIt组件，作为容器
import PostIt from "@/components/layout/PostIt.vue";
// 导入Google Analytics事件跟踪函数
import { event } from "vue-gtag";

// 导入Swiper的模块，默认只提供最基础的功能，需要的功能（如导航、分页、自动播放、懒加载等）都需要单独导入
import SwiperCore, {
  Navigation,
  Pagination,
  Scrollbar,
  A11y,
  Autoplay,
  Lazy,
} from "swiper";

// 导入Swiper的样式，自带的编好的样式，浏览器直接渲染
import "swiper/css";
import "swiper/css/navigation";
import "swiper/css/pagination";
import "swiper/css/autoplay";
import "swiper/css/lazy";

// 导入路由器，用于页面跳转
import { useRouter } from "vue-router";

// 配置Swiper使用的模块
SwiperCore.use([Navigation, Pagination, Scrollbar, A11y, Autoplay, Lazy]);
//传入 Swiper 所需的功能模块（如 Pagination、Autoplay、Lazy 等），因为现代 Swiper 采用模块化设计，需要导入并注册模块才能使用对应功能
//在 Vue 3 中，<swiper> 组件的 modules 属性期望接收一个响应式引用，这是 Swiper Vue 组件的设计要求，确保模块数组能被正确地传递和监听
const modules = ref([Navigation, Pagination, Scrollbar, A11y, Autoplay, Lazy]);

const router = useRouter();

// 导入轮播图图片URL,方便后续在模板或逻辑里引用这个资源
const slide1URL = new URL("@/assets/tasks_slide_1.webp", import.meta.url).href;
const slide2URL = new URL("@/assets/tasks_slide_2.webp", import.meta.url).href;
const slide3URL = new URL("@/assets/tasks_slide_3.webp", import.meta.url).href;

// 跟踪演示按钮点击事件的函数：定义一个埋点函数，当用户点击「演示」按钮时，调用这个函数就能把 “按钮被点击” 的行为上报给分析平台，方便后续做用户行为分析（比如统计 Demo 按钮的点击量）
const demoAnalytics = async () => {
  event("demo-button-clicked", {
    event_category: "analytics",
    event_label: "Demo",
    value: 1,
  });
}
</script>

<style scoped>
* {
  font-family: "Kalam", cursive;
}

.slide-1 {
  width: 90%;
  height: 50%;
}

.slide-2 {
  width: 70%;
  height: 70%;
}

.slide-3 {
  width: 50%;
  height: 50%;
  margin-bottom: 15px;
}

.linksbox {
  display: flex;
  justify-content: center;
  margin-bottom: 5px;
}

#demo-link {
  display: flex;
  width: 60%;
  justify-content: center;
  align-items: center;
  padding: 0px;
  min-height: 5em;
  background: #bbe1f5;
  border-top-left-radius: 15px;
  border-top-right-radius: 15px;
}

#demo-link:after {
  content: "";
  border-color: #bbe1f5;
  border-bottom-left-radius: 15px;
  bottom: -1em;
  left: 0;
  right: 1em;
  border-width: 0.5em;
}

#demo-link:before {
  border-color: #53b2e5 transparent;
  bottom: -1em;
  border-width: 1em 1em 0 0;
}

.inner-demo-link {
  display: flex;
  flex-direction: column;
  align-items: center;
}

main {
  display: flex;
  flex-direction: column;
  min-height: 90vh;
}

.footer {
  margin-top: auto;
}

.button-74 {
  background-color: #2179b8;
  border: 2px solid transparent;
  border-radius: 25px;
  cursor: pointer;
  font-weight: 300;
  font-size: 16px;
  padding: 3px 18px;
  line-height: 20px;
  text-align: center;
  text-decoration: none;
  color: #bbe1f5;
  user-select: none;
  -webkit-user-select: none;
  touch-action: manipulation;
  flex: 0;
  width: 120px;
  margin-bottom: 10px;
}

.button-74:hover {
  background-color: #18458e;
}
</style>

<style>
.swiper-button-next,
.swiper-button-prev {
  color: lightsalmon;
  height: 0px;
  width: 15px;
}

.swiper-pagination-bullet {
  margin-right: 5px !important;
}
</style>
