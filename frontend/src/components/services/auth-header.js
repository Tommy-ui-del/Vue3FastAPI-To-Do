//生成带有JWT token的认证头，用于API请求
export default function authHeader() {
  // 从localStorage获取用户信息
  let user = JSON.parse(localStorage.getItem("user"));
  // 如果用户已登录且有access_token，返回带有Bearer token的Authorization头
  if (user && user["access_token"]) {
    return { Authorization: "Bearer " + user.access_token };
  } else {
    return {};  // 否则返回空对象
  }
}
