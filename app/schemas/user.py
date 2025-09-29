"""
用戶相關的 Pydantic 模型
用於 API 請求和響應的數據驗證
"""

from pydantic import BaseModel, EmailStr, Field
from typing import Optional
from datetime import datetime


class UserBase(BaseModel):
    """用戶基礎模型"""
    email: EmailStr = Field(..., description="用戶郵箱")
    username: str = Field(..., min_length=3, max_length=50, description="用戶名")


class UserCreate(UserBase):
    """創建用戶模型"""
    password: str = Field(..., min_length=8, description="密碼，至少8位")


class UserUpdate(BaseModel):
    """更新用戶模型"""
    email: Optional[EmailStr] = Field(None, description="用戶郵箱")
    username: Optional[str] = Field(None, min_length=3, max_length=50, description="用戶名")
    is_active: Optional[bool] = Field(None, description="是否啟用")


class UserInDB(UserBase):
    """數據庫中的用戶模型"""
    id: int
    hashed_password: str
    is_active: bool = True
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class User(UserBase):
    """用戶響應模型"""
    id: int
    is_active: bool = True
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class UserProfile(User):
    """用戶詳細資料模型"""
    full_name: Optional[str] = Field(None, description="全名")
    bio: Optional[str] = Field(None, max_length=500, description="個人簡介")
    avatar_url: Optional[str] = Field(None, description="頭像URL")
    last_login: Optional[datetime] = Field(None, description="最後登入時間")