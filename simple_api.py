"""
簡化版 FastAPI 海洋數據 API
不依賴複雜的 Pydantic 模型和認證系統
"""

from fastapi import FastAPI, HTTPException, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
import csv
from datetime import datetime, date
from typing import Dict, Optional, List, Any
import json
import io
import os

app = FastAPI(
    title="NASA 海洋數據 API",
    description="簡化版海洋數據查詢 API",
    version="1.0.0"
)

# 設定 CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def parse_date(date_str: str) -> date:
    """解析日期字符串"""
    try:
        return datetime.strptime(date_str, '%Y-%m-%d').date()
    except:
        return None

def safe_float(value: str) -> Optional[float]:
    """安全轉換為浮點數"""
    try:
        if value == '' or value is None:
            return None
        return float(value)
    except:
        return None

def get_ocean_data_by_date(target_date: date) -> Dict:
    """根據日期獲取海洋數據"""
    csv_file = "comprehensive_shark_ocean_features - comprehensive_shark_ocean_features.csv"
    
    matching_records = []
    
    try:
        with open(csv_file, 'r', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            
            for row in reader:
                row_date = parse_date(row['Date'])
                if row_date == target_date:
                    matching_records.append(row)
        
        if not matching_records:
            return {
                "date": str(target_date),
                "sst_value": None,
                "chl_value": None,
                "ssha_value": None,
                "data_count": 0,
                "message": "該日期無數據"
            }
        
        # 計算平均值
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
            "date": str(target_date),
            "sst_value": round(avg_sst, 6) if avg_sst is not None else None,
            "chl_value": round(avg_chl, 6) if avg_chl is not None else None,
            "ssha_value": round(avg_ssha, 6) if avg_ssha is not None else None,
            "data_count": len(matching_records),
            "message": "查詢成功"
        }
        
    except FileNotFoundError:
        return {
            "date": str(target_date),
            "sst_value": None,
            "chl_value": None,
            "ssha_value": None,
            "data_count": 0,
            "error": "CSV 檔案不存在"
        }
    except Exception as e:
        return {
            "date": str(target_date),
            "sst_value": None,
            "chl_value": None,
            "ssha_value": None,
            "data_count": 0,
            "error": f"讀取數據失敗: {str(e)}"
        }

@app.get("/")
async def root():
    """根端點"""
    return {
        "message": "🌊 NASA 海洋數據 API",
        "version": "1.0.0",
        "docs": "/docs",
        "example": "/ocean-data/2014-07-10"
    }

@app.get("/ocean-data/{date}")
async def get_ocean_data(date: str):
    """
    根據日期獲取海洋數據
    
    - **date**: 日期 (格式: YYYY-MM-DD, 例如 2014-07-10)
    
    返回該日期的:
    - sst_value: 海表溫度值
    - chl_value: 葉綠素值  
    - ssha_value: 海面高度異常值
    """
    try:
        # 解析日期
        query_date = datetime.strptime(date, '%Y-%m-%d').date()
        
        # 獲取數據
        result = get_ocean_data_by_date(query_date)
        
        if "error" in result:
            raise HTTPException(status_code=500, detail=result["error"])
        
        return result
        
    except ValueError:
        raise HTTPException(
            status_code=400, 
            detail="日期格式錯誤，請使用 YYYY-MM-DD 格式，例如: 2014-07-10"
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"伺服器錯誤: {str(e)}")

@app.post("/ocean-data")
async def get_ocean_data_post(request: dict):
    """
    通過 POST 請求獲取海洋數據
    
    請求體範例:
    ```json
    {
        "date": "2014-07-10"
    }
    ```
    """
    try:
        if "date" not in request:
            raise HTTPException(status_code=400, detail="請求中缺少 'date' 欄位")
        
        # 解析日期
        query_date = datetime.strptime(request["date"], '%Y-%m-%d').date()
        
        # 獲取數據
        result = get_ocean_data_by_date(query_date)
        
        if "error" in result:
            raise HTTPException(status_code=500, detail=result["error"])
        
        return result
        
    except ValueError:
        raise HTTPException(
            status_code=400, 
            detail="日期格式錯誤，請使用 YYYY-MM-DD 格式，例如: 2014-07-10"
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"伺服器錯誤: {str(e)}")

@app.get("/available-dates")
async def get_available_dates():
    """獲取前 20 個可用日期"""
    csv_file = "comprehensive_shark_ocean_features - comprehensive_shark_ocean_features.csv"
    dates = set()
    
    try:
        with open(csv_file, 'r', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            
            for row in reader:
                if len(dates) >= 20:
                    break
                dates.add(row['Date'])
        
        return {
            "available_dates": sorted(list(dates)),
            "total_count": len(dates),
            "message": "可用日期列表 (前20個)"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"讀取可用日期失敗: {str(e)}")

# ============================
# 機器學習預測功能
# ============================

# 模型檔案路徑
MODEL_PATH = "shark_rf_model_round_18.joblib"

# 全域模型變數
_model = None

def load_ml_model():
    """載入 joblib 模型"""
    global _model
    
    if _model is None:
        try:
            # 檢查是否有 joblib
            import joblib
            
            if not os.path.exists(MODEL_PATH):
                return None, f"模型檔案不存在: {MODEL_PATH}"
            
            _model = joblib.load(MODEL_PATH)
            return _model, "模型載入成功"
            
        except ImportError:
            return None, "請安裝 joblib: pip install joblib"
        except Exception as e:
            return None, f"載入模型失敗: {e}"
    
    return _model, "模型已載入"

def process_csv_for_prediction(csv_content: str) -> tuple:
    """處理 CSV 內容進行預測"""
    try:
        csv_reader = csv.DictReader(io.StringIO(csv_content))
        data_rows = []
        columns = None
        
        for row in csv_reader:
            if columns is None:
                columns = list(row.keys())
            
            # 轉換數值類型
            processed_row = []
            for key, value in row.items():
                try:
                    # 嘗試轉換為浮點數
                    processed_row.append(float(value))
                except (ValueError, TypeError):
                    # 如果無法轉換，使用 0
                    processed_row.append(0.0)
            
            data_rows.append(processed_row)
        
        return data_rows, columns, None
        
    except Exception as e:
        return None, None, f"CSV 處理失敗: {e}"

@app.post("/ml/predict")
async def predict_with_csv(file: UploadFile = File(...)):
    """
    上傳 CSV 檔案並使用 RF 模型進行預測
    
    - **file**: 上傳的 CSV 檔案
    """
    try:
        # 驗證檔案類型
        if not file.filename.endswith('.csv'):
            raise HTTPException(
                status_code=400,
                detail="只支援 CSV 檔案，請上傳 .csv 格式的檔案"
            )
        
        # 載入模型
        model, message = load_ml_model()
        if model is None:
            raise HTTPException(status_code=500, detail=message)
        
        # 讀取 CSV 檔案
        contents = await file.read()
        csv_content = contents.decode('utf-8')
        
        # 處理 CSV 數據
        data_rows, columns, error = process_csv_for_prediction(csv_content)
        if error:
            raise HTTPException(status_code=400, detail=error)
        
        if not data_rows:
            raise HTTPException(status_code=400, detail="CSV 檔案沒有有效的數據行")
        
        # 進行預測
        try:
            import numpy as np
            predictions = model.predict(np.array(data_rows))
            
            # 計算統計信息
            prediction_list = predictions.tolist()
            unique_predictions = list(set(prediction_list))
            
            result = {
                "status": "success",
                "file_info": {
                    "filename": file.filename,
                    "rows_processed": len(data_rows),
                    "columns": columns,
                    "column_count": len(columns) if columns else 0
                },
                "model_info": {
                    "model_type": str(type(model).__name__),
                    "model_path": MODEL_PATH
                },
                "predictions": {
                    "values": prediction_list,
                    "count": len(prediction_list),
                    "unique_values": unique_predictions,
                    "unique_count": len(unique_predictions)
                }
            }
            
            # 如果預測值種類少，顯示分佈
            if len(unique_predictions) <= 10:
                distribution = {}
                for pred in prediction_list:
                    distribution[pred] = distribution.get(pred, 0) + 1
                result["predictions"]["distribution"] = distribution
            
            return result
            
        except ImportError:
            raise HTTPException(status_code=500, detail="請安裝 numpy: pip install numpy")
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"預測失敗: {e}")
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"處理失敗: {str(e)}")

@app.get("/ml/model-info")
async def get_model_info():
    """獲取模型信息"""
    try:
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

@app.post("/ml/predict-simple")
async def predict_simple(data: Dict[str, Any]):
    """
    簡單預測接口，接受 JSON 數據
    
    - **data**: {"features": [[值1, 值2, ...], [值1, 值2, ...], ...]}
    """
    try:
        model, message = load_ml_model()
        if model is None:
            raise HTTPException(status_code=500, detail=message)
        
        if "features" not in data:
            raise HTTPException(status_code=400, detail="請提供 'features' 欄位")
        
        features = data["features"]
        if not isinstance(features, list) or not features:
            raise HTTPException(status_code=400, detail="features 必須是非空的列表")
        
        try:
            import numpy as np
            predictions = model.predict(np.array(features))
            
            return {
                "status": "success",
                "predictions": predictions.tolist(),
                "count": len(predictions)
            }
            
        except ImportError:
            raise HTTPException(status_code=500, detail="請安裝 numpy: pip install numpy")
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"預測失敗: {e}")
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"處理失敗: {str(e)}")

@app.get("/health")
async def health_check():
    """健康檢查"""
    return {"status": "healthy", "message": "API 運行正常"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)