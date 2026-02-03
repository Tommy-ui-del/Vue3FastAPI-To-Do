import { event } from "vue-gtag";  // 导入vue-gtag的事件函数

// 跟踪任务创建事件
export const trackTaskCreatedGA = async () => {
    event("task-created", {
        event_category: "analytics",
        event_label: "Task",
        value: 1,
    });
};

// 跟踪任务删除事件
export const trackTaskDeletedGA = async () => {
    event("task-deleted", {
        event_category: "analytics",
        event_label: "Task",
        value: 1,
    });
};

// 跟踪任务勾选/取消勾选事件
export const trackTaskCheckedUncheckedGA = async () => {
    event("task-checked-unchecked", {
        event_category: "analytics",
        event_label: "Task",
        value: 1,
    });
};

// 跟踪任务拖拽事件
export const trackTaskDraggedGA = async () => {
    event("task-dragged", {
        event_category: "analytics",
        event_label: "Task",
        value: 1,
    });
};

// 跟踪任务编辑事件
export const trackTaskEditedGA = async () => {
    event("task-edited", {
        event_category: "analytics",
        event_label: "Task",
        value: 1,
    });
};

// 跟踪用户登录事件
export const trackUserLoggedInGA = async () => {
    event("user-logged-in", {
        event_category: "analytics",
        event_label: "User",
        value: 1,
    });
};

// 跟踪Google登录事件
export const trackUserLoggedInWithGoogleGA = async () => {
    event("user-google-log-in", {
        event_category: "analytics",
        event_label: "User",
        value: 1,
    });
};

// 跟踪用户注册事件
export const trackUserRegistrationGA = async () => {
    event("user-registered", {
        event_category: "analytics",
        event_label: "User",
        value: 1,
    });
};

