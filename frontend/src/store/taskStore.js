// 导入Pinia的defineStore函数，用于创建状态管理store
import { defineStore } from "pinia";
// 导入认证头函数，用于在API请求中添加JWT token
import authHeader from "@/components/services/auth-header";
// 导入配置好的axios实例
import axios from "@/axios"
// 导入Google Analytics跟踪函数
import { trackTaskCreatedGA, trackTaskDeletedGA, trackTaskCheckedUncheckedGA, trackTaskEditedGA, trackTaskDraggedGA } from '@/gaUtils';

// 定义任务管理store
export const useTaskStore = defineStore("tasks", {
  // 定义状态
  state: () => ({
    currentDate: new Date().toISOString().slice(0, 10), // 当前选中的日期，格式为YYYY-MM-DD
    enteredText: "", // 新任务的输入文本
    editedText: "", // 编辑任务时的文本
    invalidInput: false, // 输入是否无效的标志
    isLoading: false,   // 加载状态标志
    currentTasks: []  // 当前日期的任务列表
  }),
  // 定义方法
  actions: {
    // 将日期格式化为YYYY-MM-DD格式
    formattedDate(date) {
      return date.toISOString().split('T')[0]
    },
    // 获取优先级已更改的任务
    // TODO: 将此方法改为getter
    getChangedPriorities() {
      const changedPriorities = {};
      // 遍历当前任务列表
      for (const [index, task] of this.currentTasks.entries()) {
        // 如果任务的优先级与当前索引+1不匹配，则记录变化
        if (task.priority !== index + 1) {
          changedPriorities[task.id] = index + 1
          task.priority = index + 1;
        }
      }
      return changedPriorities;
    },
    // 根据日期加载任务
    async loadTasksByDate(date) {
      // 格式化日期
      const formatted_date = this.formattedDate(date)
      try {
        // 发送GET请求获取指定日期的任务
        const response = await axios.get("task/", { params: { selected_date: formatted_date }, headers: authHeader() })
        // 更新当前任务列表
        this.currentTasks = response.data
        // 为每个任务添加editable属性，控制是否可编辑
        this.currentTasks.forEach((task) => {
          task.editable = false;
        })

      } catch (err) {
        console.log(`Error when getting task for date ${date}, $(err)`)
      }

    },

    // 更新任务
    async updateTask(updatedTask) {
      // 在当前任务列表中查找要更新的任务
      const index = this.currentTasks.findIndex(task => task.id === updatedTask.id);
      if (index !== -1) {
        //替换找到的任务
        this.currentTasks[index] = updatedTask;
      }
    },

    // Checking or unchecking specific object in an array 切换任务完成状态
    async checkUncheck(task) {
      try {
        // 发送PATCH请求切换任务完成状态
        const response = await axios.patch(
          `task/${task.id}/`,
          { completed: task.completed ? false : true },
          { headers: authHeader() }
        );
        // 更新任务
        await this.updateTask(response.data)
        // 跟踪任务状态变化事件
        await trackTaskCheckedUncheckedGA();
      } catch (err) {
        console.log(err);
      }
    },
    // 应用任务文本编辑
    async applyEditChanges(task) {
      // 检查编辑内容是否有变化
      if (this.editedText && this.editedText !== task.text) {
        try {
          // 发送PATCH请求更新任务文本
          const response = await axios.patch(
            `task/${task.id}/`,
            { text: this.editedText },
            { headers: authHeader() }
          );
          // 更新任务
          await this.updateTask(response.data)
          // 跟踪任务编辑事件
          await trackTaskEditedGA();
        } catch (err) {
          console.log(err);
        }
      }
    },

    // adding the task - Post Request 添加新任务
    async addNewTask() {
      // priority is 1 if there are not tasks on that day, else it is autoincremented
      // 如果当前日期没有任务，优先级为1，否则为当前任务数+1
      const priority = this.currentTasks.length === 0 ? 1 : this.currentTasks.length + 1
      // 检查输入是否为空
      if (this.enteredText !== "") {
        // 设置加载状态
        this.isLoading = true;
        try {
           // 发送POST请求创建新任务
          const response = await axios.post(
            "task/",
            {
              priority: priority,
              text: this.enteredText,
              posted_at: this.currentDate
            },
            {
              headers: authHeader(),
            }
          );
          // 将新任务添加到当前任务列表
          this.currentTasks.push(response.data)
          // 清空输入框
          this.enteredText = "";
          // 跟踪任务创建事件
          await trackTaskCreatedGA();
        } catch (err) {
          console.log(err);
        }
        // 清除加载状态
        this.isLoading = false;
      } else {
        // 设置无效输入标志
        this.invalidInput = true;
      }
    },
    // clear invalid input - to be used at blur 清除无效输入标志
    clearInvalidInput() {
      this.invalidInput = false;
    },
    // Deleting specific task 删除任务

    async deleteTask(task) {
      try {
         // 发送DELETE请求删除任务
        await axios.delete(`task/${task.id}/`, {
          headers: authHeader(),
        });

        // remove deleted task from the array 从当前任务列表中移除已删除的任务
        this.currentTasks = this.currentTasks.filter(element => element.id !== task.id);
        // 跟踪任务删除事件
        await trackTaskDeletedGA();
      } catch (err) {
        console.log(err);
      }
      // 更新剩余任务的优先级
      this.updateTaskPriorities();
    },
    // 更新任务优先级
    async updateTaskPriorities() {
      // 获取优先级已更改的任务
      const changedPriorities = this.getChangedPriorities();
      // 如果没有优先级变化，直接返回
      if (Object.keys(changedPriorities).length === 0) {
        return
      }

      // taskPriorities hold id/newPriority key-value pairs /taskPriorities保存id/newPriority键值对
      try {
        // 发送PATCH请求更新任务优先级
        await axios.patch("task/update-order/",
          {
            priorities: changedPriorities,
          },
          {
            headers: authHeader(),
          }
        )
        // 跟踪任务拖拽事件
        await trackTaskDraggedGA();
      }
      catch (err) {
        console.log("Error updating priorities", err);
      }
    },
  },
});
