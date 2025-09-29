"""
簡化版主應用程式 - 用於測試海洋數據功能
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# 簡化的設定
class SimpleSettings:
    PROJECT_NAME = "NASA Hackathon API"
    PROJECT_DESCRIPTION = "NASA 黑客松 FastAPI 應用程式"
    VERSION = "0.1.0"
    API_V1_STR = "/api/v1"
    DEBUG = True
    HOST = "0.0.0.0"
    PORT = 8000
    ALLOWED_HOSTS = ["*"]

settings = SimpleSettings()

def create_application() -> FastAPI:
    """創建 FastAPI 應用程式實例"""
    
    app = FastAPI(
        title=settings.PROJECT_NAME,
        description=settings.PROJECT_DESCRIPTION,
        version=settings.VERSION,
        openapi_url=f"{settings.API_V1_STR}/openapi.json",
        docs_url="/docs",
        redoc_url="/redoc",
    )

    # 設定 CORS 中間件
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.ALLOWED_HOSTS,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # 註冊路由
    try:
        from app.routers.ocean_data import router as ocean_router
        app.include_router(ocean_router, prefix=f"{settings.API_V1_STR}/ocean-data", tags=["海洋數據"])
    except ImportError as e:
        print(f"⚠️ 無法載入海洋數據路由: {e}")

    return app

# 創建應用程式實例
app = create_application()

@app.get("/")
async def root():
    """根端點 - 健康檢查"""
    return {
        "message": "Welcome to NASA Hackathon API! 🚀",
        "status": "healthy",
        "version": settings.VERSION,
        "docs": "/docs",
        "ocean_data_endpoint": "/api/v1/ocean-data/public/date/2014-07-10"
    }

@app.get("/health")
async def health_check():
    """健康檢查端點"""
    return {
        "status": "healthy",
        "version": settings.VERSION,
    }

if __name__ == "__main__":
    import uvicorn
    
    uvicorn.run(
        "test_main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG,
        log_level="info",
    )