"""
簡化的 NASA 海洋數據與ML預測 FastAPI 應用程式
test for modify
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import csv
from datetime import datetime, date
from typing import Dict, Optional
import uvicorn

# 嘗試載入配置（如果可用）
try:
    from app.core.config import settings, get_cors_origins
    config_available = True
except ImportError:
    print("⚠️ 配置模組載入失敗，使用預設設定")
    config_available = False
    
    # 簡單的設定類
    class SimpleSettings:
        PROJECT_NAME = "NASA 海洋數據與ML預測 API"
        PROJECT_DESCRIPTION = "海洋數據查詢和機器學習預測 API"
        VERSION = "1.0.0"
        HOST = "0.0.0.0"
        PORT = 8000
        API_V1_STR = "/api/v1"
        ALLOWED_HOSTS = ["*"]
        
    settings = SimpleSettings()
    
    def get_cors_origins():
        return ["*"]

def create_application() -> FastAPI:
    """創建 FastAPI 應用程式實例"""
    
    app = FastAPI(
        title=settings.PROJECT_NAME,
        description=settings.PROJECT_DESCRIPTION,
        version=settings.VERSION,
        openapi_url=f"{settings.API_V1_STR}/openapi.json" if hasattr(settings, 'API_V1_STR') else "/openapi.json"
    )

    # 設定 CORS 中間件
    app.add_middleware(
        CORSMiddleware,
        allow_origins=get_cors_origins(),
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # 嘗試載入路由
    try:
        from app.routers import api_router
        
        # 註冊 API 路由
        app.include_router(
            api_router, 
            prefix=settings.API_V1_STR if hasattr(settings, 'API_V1_STR') else "/api/v1"
        )
        
        router_loaded = True
        
    except ImportError as e:
        print(f"⚠️ API 路由載入失敗: {e}")
        print("📝 將使用基本的回退端點")
        router_loaded = False

    return app, router_loaded


# 創建應用程式實例
app, router_loaded = create_application()


@app.get("/")
async def root():
    """根端點"""
    return {
        "message": f"歡迎使用 {settings.PROJECT_NAME}",
        "version": settings.VERSION,
        "status": "running",
        "router_loaded": router_loaded,
        "endpoints": {
            "docs": "/docs",
            "redoc": "/redoc",
            "health": "/health"
        }
    }

@app.get("/health")
async def health_check():
    """健康檢查端點"""
    return {
        "status": "healthy",
        "service": settings.PROJECT_NAME,
        "version": settings.VERSION,
        "router_loaded": router_loaded
    }

# 如果路由載入失敗，提供簡單的海洋數據查詢端點
if not router_loaded:
    print("📋 正在載入簡單的海洋數據端點...")
    
    @app.get("/simple-ocean-data/{date}")
    async def get_simple_ocean_data(date: str):
        """簡單的海洋數據查詢端點（回退版本）"""
        try:
            # 讀取 CSV 檔案
            csv_filename = "comprehensive_shark_ocean_features - comprehensive_shark_ocean_features.csv"
            
            with open(csv_filename, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    if row['Date'] == date:
                        return {
                            "status": "success",
                            "date": date,
                            "data": {
                                "sst_value": float(row.get('SST_Value', 0)),
                                "chl_value": float(row.get('CHL_Value', 0)),
                                "ssha_value": float(row.get('SSHA_Value', 0)),
                                "longitude": float(row.get('Longitude', 0)),
                                "latitude": float(row.get('Latitude', 0))
                            }
                        }
            
            raise HTTPException(status_code=404, detail=f"找不到日期 {date} 的數據")
            
        except FileNotFoundError:
            raise HTTPException(status_code=500, detail="海洋數據檔案不存在")
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"讀取數據失敗: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    
    uvicorn.run(
        "main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG,
        log_level="info" if not settings.DEBUG else "debug",
    )