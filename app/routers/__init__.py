"""
主要 API 路由模組
包含所有 API 路由的註冊
"""

from fastapi import APIRouter

from app.routers import users, items, auth

# 嘗試載入簡化版海洋數據路由
try:
    from app.routers import ocean_data_simple
    ocean_data_available = True
except ImportError:
    ocean_data_available = False
    print("⚠️ 海洋數據路由載入失敗，將跳過")

# 創建主要 API 路由器
api_router = APIRouter()

# 註冊各個子路由
api_router.include_router(
    auth.router,
    prefix="/auth",
    tags=["認證"]
)

api_router.include_router(
    users.router,
    prefix="/users",
    tags=["用戶管理"]
)

api_router.include_router(
    items.router,
    prefix="/items",
    tags=["項目管理"]
)

# 條件性載入海洋數據路由
if ocean_data_available:
    api_router.include_router(
        ocean_data_simple.router,
        prefix="/ocean-data",
        tags=["海洋數據"]
    )
