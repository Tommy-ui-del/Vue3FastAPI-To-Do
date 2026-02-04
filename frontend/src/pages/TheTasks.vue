<template>
  <!-- 使用网格布局容器 -->
  <div class="grid-container">
    <!-- 头部组件 -->
    <the-header class="header" />
    <!-- 任务列表区域 -->
    <div class="grid-item-todo">
      <!-- 使用PostIt组件作为容器 -->
      <post-it>
        <!-- 如果没有任务，显示提示信息 -->
        <div v-if="currentTasks.length === 0" class="no-tasks" style="display: flex; flex-direction: column">
          <div class="unselectable"> {{ formatDate(new Date(currentDate)) }} </div>
          <h2 class="unselectable">无任务可展示</h2>
        </div>
        <!-- 如果有任务，显示任务列表 -->
        <div v-else>
          <!-- 显示当前日期 -->
          <h1 class="unselectable">
            {{ formatDate(new Date(currentDate)) }}
          </h1>
          <!-- 任务列表表头 -->
          <div class="flex-headers unselectable">
            <div class="header-number">#</div>
            <div class="header-text">描述</div>
            <div class="header-edit" v-show="showButtons">编辑</div>
            <div class="header-delete" v-show="showButtons">删除</div>
            <div class="header-completed">状态</div>
          </div>
        </div>
        <!-- 使用draggable组件实现任务拖拽排序 -->
        <draggable :list="currentTasks" item-key="task_id" @change="taskStore.updateTaskPriorities()">
          <template #item="{ element }">
            <div class="flexbox">
              <!--！！！！！！！！！！！！！！！！！！！！！！！！！在draggable的#item插槽中，Vue 模板会将注释、文本、标签都视为独立的节点, vuedraggable 的#item插槽要求其内容只能有一个 “直接根节点”,不能将注释放在与flexbox同级的位置（在#item下）！！！！！！！！！！！！！！！！！！！-->
              <!-- 任务优先级 -->
              <div class="flex-id">
                <p>{{ element.priority }}</p>
              </div>
              <!-- 任务文本，双击可编辑 -->
              <div class="flex-text" :class="{ editSelectedBorder: element.editable }"
                @dblclick="taskStore.checkUncheck(element)">
                <p :contenteditable="element.editable" @input="editText" @blur=" taskStore.applyEditChanges(element)">
                  {{ element.text }}
                </p>
              </div>
              <!-- 任务操作按钮 -->
              <div class="flex-buttons" @mouseover="showButtons = element.priority" @mouseout="showButtons = null">
                <!-- 编辑按钮 -->
                <img src="@/assets/tasks/edit.png" class="edit-img" v-show="showButtons === element.priority"
                  @click="toggleEditable(element)" :class="{ editSelected: element.editable }" />
                <!-- 删除按钮 -->
                  <img src="@/assets/tasks/delete.png" alt="delete-image" class="delete-img"
                  @click="taskStore.deleteTask(element)" v-show="showButtons === element.priority" />
                <!-- 完成状态切换按钮 -->
                  <img @click="taskStore.checkUncheck(element)" :src="element.completed ? checkedBox : uncheckedBox"
                  alt="status" class="status-img" />
              </div>
            </div>
          </template>
        </draggable>
        <!-- 添加新任务的表单 -->
        <div>
          <form class="form-control" @submit.prevent="taskStore.addNewTask" v-if="!isLoading">
            <input class="task-input" @blur="taskStore.clearInvalidInput" @keyup="taskStore.clearInvalidInput"
              v-model="enteredText" type="text" aria-label="Add task" />
            <button class="button-74">添加</button>
          </form>
          <!-- 加载动画 -->
          <the-spinner v-else></the-spinner>
        </div>
        <!-- 无效输入提示 -->
        <span v-if="invalidInput" class="invalid-input">请输入文本</span>
      </post-it>
    </div>

    <!-- 日历区域 -->
    <div class="grid-item-calendar">
      <h1>{{ currentDate }}</h1>
      <!-- 日历组件 -->
      <Datepicker inline :enableTimePicker="false" :monthChangeOnScroll="false" v-model="currentDate" autoApply
        @update:modelValue="handleDate" />
        <!-- 任务统计 -->
      <div v-if="totalTasks" class="task-status">
        <p>
          # 总任务: <span id="total-tasks">{{ totalTasks }}</span>
        </p>
        <p>
          # 已完成任务:
          <span id="complete-tasks">{{ completedTasks }}</span>
        </p>
        <p>
          #未完成任务:
          <span id="uncomplete-tasks">{{ notCompletedTasks }}</span>
        </p>
      </div>
    </div>
    <!-- 底部组件 -->
    <the-footer class="footer" />
  </div>
</template>

<script setup>
// 导入Vue的响应式API
import { ref, onMounted, watch } from "vue";
// 导入Pinia的storeToRefs函数
import { storeToRefs } from "pinia";

// 导入拖拽组件
import draggable from "vuedraggable";

// 导入布局组件
import PostIt from "@/components/layout/PostIt.vue";
import TheSpinner from "@/components/layout/TheSpinner.vue";

// 导入任务store
import { useTaskStore } from "@/store/taskStore";

// 导入日历组件
import Datepicker from "@vuepic/vue-datepicker";
import "@vuepic/vue-datepicker/dist/main.css";

// 获取任务store实例
const taskStore = useTaskStore();
// 从store中解构状态
const {
  currentDate,
  invalidInput,
  enteredText,
  editedText,
  isLoading,
  currentTasks
} = storeToRefs(taskStore);

// 导入任务状态图标
const checkedBox = new URL("@/assets/tasks/checked_box.png", import.meta.url).href;
const uncheckedBox = new URL("@/assets/tasks/unchecked_box.png", import.meta.url).href;
// 控制操作按钮显示
const showButtons = ref(null);
// 任务统计变量
const notCompletedTasks = ref(null);
const completedTasks = ref(null);
const totalTasks = ref(null);
// 计算任务完成情况
const calculateTaskCompletions = () => {
  totalTasks.value = currentTasks.value.length;
  notCompletedTasks.value = currentTasks.value.filter(
    (task) => !task.completed
  ).length;
  completedTasks.value = totalTasks.value - notCompletedTasks.value

}
// 监听任务列表变化，更新统计信息
watch([currentTasks], (newValue) => {
  calculateTaskCompletions();
}, { deep: true });

// 自定义函数，将日期格式化为"DD month-long YYYY"格式
const formatDate = (dateInput) => {
  return dateInput.toLocaleDateString("en-US", {
    month: "long",
    year: "numeric",
    day: "numeric",
  });
}
// 将日期格式化为YYYY-MM-DD格式
const formattedDate = (date) => {
  return date.toISOString().split('T')[0]
};
// 处理日期选择事件
const handleDate = async (selectedDate) => {
  currentDate.value = formattedDate(selectedDate);
  // 加载选中日期的任务
  await taskStore.loadTasksByDate(selectedDate);
};

// listen to input inside edited paragraph text 监听任务文本编辑
const editText = (event) => {
  editedText.value = event.target.innerText;
}

// make SELECTED paragraph tag editable 切换任务文本的可编辑状态
// No link with backend - elements become not editable after refresh
const toggleEditable = (task) => {
  task.editable = !task.editable;
}
// 组件挂载时加载当前日期的任务
onMounted(async () => {
  await taskStore.loadTasksByDate(new Date())
  calculateTaskCompletions();

});

</script>

<style scoped>
/* 使用Kalam字体 */
* {
  font-family: "Kalam", cursive;
}

/* 标题居中 */
h1 {
  text-align: center;
}

/* 禁止选择文本 */
.unselectable {
  -webkit-touch-callout: none;
  -webkit-user-select: none;
  -khtml-user-select: none;
  -moz-user-select: none;
  -ms-user-select: none;
  -o-user-select: none;
  user-select: none;
}

/* 添加任务表单样式 */
.form-control {
  margin-top: 20px;
  display: flex;
  height: 40px;
  justify-content: space-between;
  margin-bottom: 10px;
}

/* 任务输入框样式 */
.task-input {
  width: 80%;
  margin-left: 30px;
  margin-right: 10px;
  line-height: 25px;
  font-size: 18px;
  background-color: #fbeee0;
  border: 2px solid #422800;
}

/* 无任务提示样式 */
.no-tasks {
  height: 100px;
  justify-content: center;
  display: flex;
  align-items: center;
  font-weight: bold;
  font-size: 20px;
  margin-top: 40px;
}

/* 使用网格布局 */
.grid-container {
  min-height: 100vh;
  display: grid;
  grid-template-areas:
    "header header"
    "todo calendar"
    "footer footer";
  grid-template-rows: 60px 1fr 60px;
  grid-template-columns: 1fr 1fr;
  gap: 10px;
}

/* 任务列表区域 */
.grid-item-todo {
  grid-area: todo;
}

/* 日历区域 */
.grid-item-calendar {
  grid-area: calendar;
}

/* 响应式设计，适配移动设备 */
@media (max-width: 768px) {
  .grid-container {
    grid-template-columns: 1fr;
    grid-template-rows: 50px 1fr 1fr 50px;
    gap: 1px;
  }

  .header {
    grid-row: 1;
  }

  .grid-item-todo {
    margin-top: 2px;
    grid-row: 2;
    grid-column: 1;
  }

  .grid-item-calendar {
    grid-row: 3;
    grid-column: 1;
  }

  .footer {
    grid-row: 4/5;
  }

  .form-control {
    flex-direction: column;
    align-items: center;
    margin-bottom: 60px;
  }

  .button-74 {
    width: 90px;
    flex-shrink: 0;
    margin-top: 10px;
    margin-right: 40px;
  }
}

/* 任务列表表头样式 */
.flex-headers {
  display: flex;
  border-bottom: 2px solid black;
  margin: 0px 10px;
  font-size: 16px;
  padding: 5px 0px;
  font-weight: bold;
}

/* 表头各列样式 */
.header-number {
  text-align: center;
  justify-content: center;
  align-content: center;
  align-items: center;
  flex-basis: 20px;
}

.header-text {
  margin-right: auto;
  margin-left: 10px;
}

.header-edit,
.header-delete,
.header-completed {
  margin-right: 5px;
}

/* 任务项样式 */
.flexbox {
  display: flex;
  justify-content: space-between;
  margin: 0 10px;
  cursor: default;
}

/* 任务优先列样式 */
.flex-id {
  flex-basis: 15px;
  display: flex;
  justify-content: center;
  align-items: center;
  margin-top: 3px;
}

.flex-id p {
  font-weight: bold;
  margin-block-start: 0px;
  margin-block-end: 0px;
}

/* 任务文本样式 */
.flex-text {
  text-align: justify;
  margin-left: 15px;
  flex: 1;
  line-height: 12pt;
}

.flex-text p {
  outline: none;
}

/* 段落样式 */
p {
  margin-block-start: 10px;
  margin-block-end: 0px;
}

/* 编辑状态的文本样式 */
.editSelectedBorder {
  border: 0.5px solid orange;
  cursor: auto;
}

/* 任务操作按钮区域样式 */
.flex-buttons {
  flex-basis: 70px;
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 3px;
}

/* 编辑按钮样式 */
.edit-img {
  width: 30px;
  height: 30px;
  margin-right: -5px;
}

.editSelected {
  transform: rotate(19deg);
}

/* 删除按钮样式 */
.delete-img {
  width: 30px;
  height: 30px;
}

.delete-img:hover {
  filter: invert(39%) sepia(5%) saturate(4834%) hue-rotate(314deg) brightness(91%) contrast(100%);
}

/* 完成状态按钮样式 */
.status-img {
  width: 30px;
  height: 30px;
  margin-left: auto;
  margin-right: 5px;
}

/* 按钮样式 */
.button-74 {
  background-color: #fbeee0;
  border: 2px solid #422800;
  border-radius: 25px;
  box-shadow: #422800 3px 3px 0 0;
  color: #422800;
  cursor: pointer;
  font-weight: 300;
  font-size: 16px;
  padding: 0 18px;
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

.button-74:hover {
  background-color: #fff;
}

.button-74:active {
  box-shadow: #422800 2px 2px 0 0;
  transform: translate(2px, 2px);
}

/* 无效输入提示样式 */
.invalid-input {
  color: #b04b4b;
  margin-right: 50px;
  font-weight: bold;
}

/* 任务统计样式 */
.task-status p {
  display: inline-block;
  margin-right: 20px;
}

#total-tasks {
  color: black;
  font-weight: bold;
}

#complete-tasks {
  color: #479d16;
  font-weight: bold;
}

#uncomplete-tasks {
  color: #841460;
  font-weight: bold;
}
</style>

