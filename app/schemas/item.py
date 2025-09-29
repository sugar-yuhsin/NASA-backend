"""
項目相關的 Pydantic 模型
用於項目管理的 API 請求和響應數據驗證
"""

from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


class ItemBase(BaseModel):
    """項目基礎模型"""
    title: str = Field(..., min_length=1, max_length=200, description="項目標題")
    description: Optional[str] = Field(None, max_length=1000, description="項目描述")


class ItemCreate(ItemBase):
    """創建項目模型"""
    pass


class ItemUpdate(BaseModel):
    """更新項目模型"""
    title: Optional[str] = Field(None, min_length=1, max_length=200, description="項目標題")
    description: Optional[str] = Field(None, max_length=1000, description="項目描述")
    is_active: Optional[bool] = Field(None, description="是否啟用")


class ItemInDB(ItemBase):
    """數據庫中的項目模型"""
    id: int
    owner_id: int
    is_active: bool = True
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class Item(ItemBase):
    """項目響應模型"""
    id: int
    owner_id: int
    is_active: bool = True
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class ItemWithOwner(Item):
    """包含擁有者信息的項目模型"""
    owner_username: str = Field(..., description="擁有者用戶名")
    owner_email: str = Field(..., description="擁有者郵箱")


class ItemStats(BaseModel):
    """項目統計模型"""
    total_items: int = Field(..., description="總項目數")
    active_items: int = Field(..., description="活躍項目數")
    inactive_items: int = Field(..., description="非活躍項目數")
    items_created_today: int = Field(..., description="今日創建項目數")
    items_updated_today: int = Field(..., description="今日更新項目數")