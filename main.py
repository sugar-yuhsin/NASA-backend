"""
NASA Hackathon FastAPI Application
主應用程式進入點
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from contextlib import asynccontextmanager

from app.core.config import settings
from app.routers import api_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    """應用程式生命週期管理"""
    # 啟動時執行
    print("🚀 NASA Hackathon API 正在啟動...")
    yield
    # 關閉時執行
    print("👋 NASA Hackathon API 正在關閉...")


def create_application() -> FastAPI:
    """創建 FastAPI 應用程式實例"""
    
    app = FastAPI(
        title=settings.PROJECT_NAME,
        description=settings.PROJECT_DESCRIPTION,
        version=settings.VERSION,
        openapi_url=f"{settings.API_V1_STR}/openapi.json",
        lifespan=lifespan,
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

    # 設定信任主機中間件
    app.add_middleware(
        TrustedHostMiddleware, 
        allowed_hosts=settings.ALLOWED_HOSTS
    )

    # 註冊路由
    app.include_router(api_router, prefix=settings.API_V1_STR)

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
    }


@app.get("/health")
async def health_check():
    """健康檢查端點"""
    return {
        "status": "healthy",
        "timestamp": "2024-01-01T00:00:00Z",
        "version": settings.VERSION,
    }


# 添加簡化的海洋數據查詢端點（作為備用）
@app.get("/ocean-data-simple/{target_date}")
async def get_ocean_data_simple_fallback(target_date: str):
    """簡化版海洋數據查詢端點（無需認證，作為備用）"""
    import csv
    from datetime import datetime
    
    try:
        # 解析日期
        query_date = datetime.strptime(target_date, '%Y-%m-%d').date()
        
        # 查詢 CSV 數據
        csv_file = "comprehensive_shark_ocean_features - comprehensive_shark_ocean_features.csv"
        matching_records = []
        
        with open(csv_file, 'r', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            
            for row in reader:
                row_date = datetime.strptime(row['Date'], '%Y-%m-%d').date()
                if row_date == query_date:
                    matching_records.append(row)
        
        if not matching_records:
            return {
                "date": str(query_date),
                "sst_value": None,
                "chl_value": None,
                "ssha_value": None,
                "data_count": 0,
                "message": "該日期無數據"
            }
        
        # 計算平均值
        def safe_float(value):
            try:
                return float(value) if value else None
            except:
                return None
        
        sst_values = [safe_float(record['SST_Value']) for record in matching_records]
        chl_values = [safe_float(record['CHL_Value']) for record in matching_records]
        ssha_values = [safe_float(record['SSHA_Value']) for record in matching_records]
        
        # 過濾 None 值
        sst_values = [v for v in sst_values if v is not None]
        chl_values = [v for v in chl_values if v is not None]
        ssha_values = [v for v in ssha_values if v is not None]
        
        avg_sst = sum(sst_values) / len(sst_values) if sst_values else None
        avg_chl = sum(chl_values) / len(chl_values) if chl_values else None
        avg_ssha = sum(ssha_values) / len(ssha_values) if ssha_values else None
        
        return {
            "date": str(query_date),
            "sst_value": round(avg_sst, 6) if avg_sst is not None else None,
            "chl_value": round(avg_chl, 6) if avg_chl is not None else None,
            "ssha_value": round(avg_ssha, 6) if avg_ssha is not None else None,
            "data_count": len(matching_records),
            "message": "查詢成功"
        }
        
    except ValueError:
        return {"error": "日期格式錯誤，請使用 YYYY-MM-DD 格式"}
    except FileNotFoundError:
        return {"error": "CSV 檔案不存在"}
    except Exception as e:
        return {"error": f"查詢失敗: {str(e)}"}


if __name__ == "__main__":
    import uvicorn
    
    uvicorn.run(
        "main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG,
        log_level="info" if not settings.DEBUG else "debug",
    )