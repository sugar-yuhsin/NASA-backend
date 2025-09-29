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

# 全域變數和函數
OCEAN_DATA_PATH = "comprehensive_shark_ocean_features - comprehensive_shark_ocean_features.csv"

def safe_float(value):
    """安全轉換為浮點數"""
    try:
        return float(value) if value else None
    except:
        return None

# 如果路由載入失敗，提供完整的海洋數據和ML預測端點
if not router_loaded:
    print("📋 正在載入完整的海洋數據和ML預測端點...")
    
    # ============================
    # 海洋數據 API
    # ============================
    
    @app.get("/api/v1/ocean-data/query/{target_date}")
    async def query_ocean_data_by_date(target_date: str):
        """根據日期查詢海洋數據（包含經度和緯度）"""
        try:
            # 解析日期
            query_date = datetime.strptime(target_date, '%Y-%m-%d').date()
            
            # 查詢 CSV 數據
            matching_records = []
            
            with open(OCEAN_DATA_PATH, 'r', encoding='utf-8') as file:
                reader = csv.DictReader(file)
                
                for row in reader:
                    row_date = datetime.strptime(row['Date'], '%Y-%m-%d').date()
                    if row_date == query_date:
                        matching_records.append(row)
            
            if not matching_records:
                raise HTTPException(
                    status_code=404, 
                    detail=f"找不到日期 {target_date} 的海洋數據"
                )
            
            # 計算平均值
            sst_values = [safe_float(record['SST_Value']) for record in matching_records]
            chl_values = [safe_float(record['CHL_Value']) for record in matching_records]
            ssha_values = [safe_float(record['SSHA_Value']) for record in matching_records]
            longitude_values = [safe_float(record['Longitude']) for record in matching_records]
            latitude_values = [safe_float(record['Latitude']) for record in matching_records]
            
            # 過濾 None 值
            sst_values = [v for v in sst_values if v is not None]
            chl_values = [v for v in chl_values if v is not None]
            ssha_values = [v for v in ssha_values if v is not None]
            longitude_values = [v for v in longitude_values if v is not None]
            latitude_values = [v for v in latitude_values if v is not None]
            
            avg_sst = sum(sst_values) / len(sst_values) if sst_values else None
            avg_chl = sum(chl_values) / len(chl_values) if chl_values else None
            avg_ssha = sum(ssha_values) / len(ssha_values) if ssha_values else None
            avg_longitude = sum(longitude_values) / len(longitude_values) if longitude_values else None
            avg_latitude = sum(latitude_values) / len(latitude_values) if latitude_values else None
            
            return {
                "status": "success",
                "date": target_date,
                "sst_value": round(avg_sst, 6) if avg_sst is not None else None,
                "chl_value": round(avg_chl, 6) if avg_chl is not None else None,
                "ssha_value": round(avg_ssha, 6) if avg_ssha is not None else None,
                "longitude": round(avg_longitude, 6) if avg_longitude is not None else None,
                "latitude": round(avg_latitude, 6) if avg_latitude is not None else None,
                "data_count": len(matching_records),
                "message": "查詢成功"
            }
            
        except ValueError:
            raise HTTPException(
                status_code=400, 
                detail="日期格式錯誤，請使用 YYYY-MM-DD 格式"
            )
        except FileNotFoundError:
            raise HTTPException(
                status_code=500, 
                detail="海洋數據檔案不存在"
            )
        except Exception as e:
            raise HTTPException(
                status_code=500, 
                detail=f"查詢失敗: {str(e)}"
            )
    
    @app.get("/api/v1/ocean-data/available-dates")
    async def get_available_dates():
        """獲取可用的日期列表"""
        try:
            dates = set()
            
            with open(OCEAN_DATA_PATH, 'r', encoding='utf-8') as file:
                reader = csv.DictReader(file)
                
                for row in reader:
                    if len(dates) >= 20:  # 限制返回數量
                        break
                    dates.add(row['Date'])
            
            return {
                "status": "success",
                "available_dates": sorted(list(dates)),
                "total_count": len(dates),
                "message": "可用日期列表 (前20個)"
            }
            
        except Exception as e:
            raise HTTPException(
                status_code=500, 
                detail=f"讀取可用日期失敗: {str(e)}"
            )
    
    # 保留舊的簡單端點以保持向後兼容
    @app.get("/simple-ocean-data/{date}")
    async def get_simple_ocean_data(date: str):
        """簡單的海洋數據查詢端點（向後兼容）"""
        try:
            # 重新導向到新的 API
            result = await query_ocean_data_by_date(date)
            
            # 轉換格式以保持兼容性
            return {
                "status": "success",
                "date": date,
                "data": {
                    "sst_value": result.get("sst_value"),
                    "chl_value": result.get("chl_value"), 
                    "ssha_value": result.get("ssha_value"),
                    "longitude": result.get("longitude"),
                    "latitude": result.get("latitude")
                }
            }
            
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"查詢失敗: {str(e)}")
    
    # ============================
    # 機器學習預測 API
    # ============================
    
    # ML 相關全域變數
    MODEL_PATH = "shark_rf_model_round_18.joblib"
    _model = None
    
    def load_ml_model():
        """載入機器學習模型"""
        global _model
        
        if _model is None:
            try:
                import joblib
                import os
                
                if not os.path.exists(MODEL_PATH):
                    return None, f"模型檔案不存在: {MODEL_PATH}"
                
                _model = joblib.load(MODEL_PATH)
                return _model, "模型載入成功"
                
            except ImportError:
                return None, "請安裝 joblib: pip install joblib"
            except Exception as e:
                return None, f"載入模型失敗: {e}"
        
        return _model, "模型已載入"
    
    @app.get("/api/v1/ml/model-info")
    async def get_model_info():
        """獲取模型信息"""
        try:
            import os
            model, message = load_ml_model()
            
            info = {
                "model_path": MODEL_PATH,
                "file_exists": os.path.exists(MODEL_PATH),
                "status": "loaded" if model else "not_loaded",
                "message": message
            }
            
            if os.path.exists(MODEL_PATH):
                info["file_size_mb"] = round(os.path.getsize(MODEL_PATH) / (1024 * 1024), 2)
            
            if model:
                info["model_type"] = str(type(model).__name__)
                
                # 嘗試獲取額外信息
                try:
                    if hasattr(model, 'n_features_in_'):
                        info['n_features'] = model.n_features_in_
                    if hasattr(model, 'feature_names_in_'):
                        info['feature_names'] = model.feature_names_in_.tolist()
                    if hasattr(model, 'classes_'):
                        info['classes'] = model.classes_.tolist()
                    if hasattr(model, 'n_estimators'):
                        info['n_estimators'] = model.n_estimators
                except:
                    pass
            
            return info
            
        except Exception as e:
            return {"error": f"獲取模型信息失敗: {str(e)}"}

if __name__ == "__main__":
    import uvicorn
    
    uvicorn.run(
        "main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG,
        log_level="info" if not settings.DEBUG else "debug",
    )