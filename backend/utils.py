#封装密码哈希和验证逻辑，基于 bcrypt 算法保证密码安全存储
#bcrypt 算法：自带盐值（salt），避免彩虹表攻击；
#自动弃用：deprecated="auto" 自动识别并拒绝旧的加密算法，提升安全性

from passlib.context import CryptContext

# 初始化密码加密上下文：使用bcrypt算法，自动弃用旧算法
pwd_ctx = CryptContext(schemes=["bcrypt"], deprecated="auto")

# 明文密码转哈希密码（入库前调用）
def get_hashed_password(plain_password):
    return pwd_ctx.hash(plain_password)

# 验证明文密码与哈希密码是否匹配（登录时调用）
def verify_hashed_password(plain_password, hashed_password):
    return pwd_ctx.verify(plain_password, hashed_password)
