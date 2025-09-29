"""
認證相關的 Pydantic 模型
用於登入、註冊、令牌等數據驗證
"""

from pydantic import BaseModel, EmailStr, Field
from typing import Optional


class Token(BaseModel):
    """JWT 令牌模型"""
    access_token: str = Field(..., description="訪問令牌")
    token_type: str = Field(default="bearer", description="令牌類型")


class TokenData(BaseModel):
    """令牌數據模型"""
    email: Optional[str] = Field(None, description="用戶郵箱")


class UserLogin(BaseModel):
    """用戶登入模型"""
    email: EmailStr = Field(..., description="用戶郵箱")
    password: str = Field(..., min_length=8, description="密碼")


class UserRegister(BaseModel):
    """用戶註冊模型"""
    email: EmailStr = Field(..., description="用戶郵箱")
    username: str = Field(..., min_length=3, max_length=50, description="用戶名")
    password: str = Field(..., min_length=8, description="密碼，至少8位")
    confirm_password: str = Field(..., min_length=8, description="確認密碼")

    def validate_passwords_match(self):
        """驗證密碼是否匹配"""
        if self.password != self.confirm_password:
            raise ValueError("密碼不匹配")
        return self


class PasswordReset(BaseModel):
    """密碼重置模型"""
    email: EmailStr = Field(..., description="用戶郵箱")


class PasswordResetConfirm(BaseModel):
    """密碼重置確認模型"""
    token: str = Field(..., description="重置令牌")
    new_password: str = Field(..., min_length=8, description="新密碼，至少8位")
    confirm_password: str = Field(..., min_length=8, description="確認新密碼")

    def validate_passwords_match(self):
        """驗證密碼是否匹配"""
        if self.new_password != self.confirm_password:
            raise ValueError("密碼不匹配")
        return self


class PasswordChange(BaseModel):
    """密碼更改模型"""
    current_password: str = Field(..., description="當前密碼")
    new_password: str = Field(..., min_length=8, description="新密碼，至少8位")
    confirm_password: str = Field(..., min_length=8, description="確認新密碼")

    def validate_passwords_match(self):
        """驗證密碼是否匹配"""
        if self.new_password != self.confirm_password:
            raise ValueError("密碼不匹配")
        return self