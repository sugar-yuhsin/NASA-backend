"""
簡化的 API 路由模組
只包含海洋數據和 ML 預測功能
"""

from fastapi import APIRouter

# 嘗試載入簡化版海洋數據路由
try:
    from app.routers import ocean_data_simple
    ocean_data_available = True
except ImportError:
    ocean_data_available = False
    print("⚠️ 海洋數據路由載入失敗，將跳過")

# 嘗試載入機器學習預測路由
try:
    from app.routers import ml_prediction_simple
    ml_prediction_available = True
except ImportError:
    ml_prediction_available = False
    print("⚠️ ML 預測路由載入失敗，將跳過")

# 創建主要 API 路由器
api_router = APIRouter()

# 條件性載入海洋數據路由
if ocean_data_available:
    api_router.include_router(
        ocean_data_simple.router,
        prefix="/ocean-data",
        tags=["海洋數據"]
    )

# 條件性載入 ML 預測路由
if ml_prediction_available:
    api_router.include_router(
        ml_prediction_simple.router,
        prefix="/ml",
        tags=["機器學習預測"]
    )
