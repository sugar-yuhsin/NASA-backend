"""
機器學習預測路由 - 簡化版
處理 CSV 上傳和模型預測，不依賴複雜套件
"""

from fastapi import APIRouter, UploadFile, File, HTTPException
from typing import Dict, List, Any
import csv
import io
import os

router = APIRouter()

# 模型檔案路徑
MODEL_PATH = "shark_rf_model_round_18.joblib"

# 全域模型變數
_model = None

def load_model():
    """載入 joblib 模型"""
    global _model
    
    if _model is None:
        try:
            # 檢查模型檔案是否存在
            if not os.path.exists(MODEL_PATH):
                raise FileNotFoundError(f"模型檔案不存在: {MODEL_PATH}")
            
            # 載入必要套件
            import joblib
            import numpy as np
            
            _model = joblib.load(MODEL_PATH)
            print(f"✅ 模型載入成功: {type(_model).__name__}")
            
            return _model, None
            
        except ImportError as e:
            error_msg = f"缺少必要套件: {e}. 請安裝: pip install joblib scikit-learn numpy"
            return None, error_msg
        except Exception as e:
            error_msg = f"載入模型失敗: {e}"
            return None, error_msg
    
    return _model, None

def process_csv_for_ml(csv_content: str, expected_features: int = 13):
    """處理 CSV 內容並準備 ML 特徵"""
    try:
        # 解析 CSV
        csv_reader = csv.DictReader(io.StringIO(csv_content))
        headers = csv_reader.fieldnames
        
        if not headers:
            return None, None, "CSV 檔案沒有標題行"
        
        # 識別數值欄位（排除已知的非數值欄位）
        non_numeric_fields = {
            'date', 'individual_id', 'is_in_eddy', 'eddy_type', 
            'Date', 'Individual_ID', 'is_in_eddy', 'eddy_type'
        }
        
        numeric_headers = [h for h in headers if h not in non_numeric_fields]
        
        data_rows = []
        for row in csv_reader:
            numeric_row = []
            for header in numeric_headers:
                try:
                    value = float(row.get(header, 0))
                    numeric_row.append(value)
                except (ValueError, TypeError):
                    numeric_row.append(0.0)
            
            if len(numeric_row) > 0:
                data_rows.append(numeric_row)
        
        if not data_rows:
            return None, None, "CSV 檔案沒有有效的數據行"
        
        # 調整特徵數量以匹配模型期望
        if len(numeric_headers) > expected_features:
            # 如果特徵太多，取前 N 個
            data_rows = [row[:expected_features] for row in data_rows]
            numeric_headers = numeric_headers[:expected_features]
        elif len(numeric_headers) < expected_features:
            # 如果特徵太少，用0填充
            for i in range(len(data_rows)):
                while len(data_rows[i]) < expected_features:
                    data_rows[i].append(0.0)
            
            # 添加虛擬標題
            while len(numeric_headers) < expected_features:
                numeric_headers.append(f"feature_{len(numeric_headers) + 1}")
        
        return data_rows, numeric_headers, None
        
    except Exception as e:
        return None, None, f"CSV 處理失敗: {e}"

@router.post("/predict")
async def predict_with_csv(file: UploadFile = File(...)):
    """
    上傳 CSV 檔案並使用 RF 模型進行預測
    
    - **file**: 上傳的 CSV 檔案 (.csv 格式)
    
    返回預測結果和統計信息
    """
    try:
        # 驗證檔案類型
        if not file.filename or not file.filename.lower().endswith('.csv'):
            raise HTTPException(
                status_code=400,
                detail="只支援 CSV 檔案，請上傳 .csv 格式的檔案"
            )
        
        # 載入模型
        model, error = load_model()
        if error:
            raise HTTPException(status_code=500, detail=error)
        
        # 讀取檔案內容
        contents = await file.read()
        csv_content = contents.decode('utf-8')
        
        # 獲取模型期望的特徵數量
        expected_features = getattr(model, 'n_features_in_', 13)
        
        # 處理 CSV 數據
        data_rows, headers, process_error = process_csv_for_ml(csv_content, expected_features)
        if process_error:
            raise HTTPException(status_code=400, detail=process_error)
        
        # 進行預測
        try:
            import numpy as np
            
            X = np.array(data_rows)
            predictions = model.predict(X)
            
            # 準備返回結果
            result = {
                "status": "success",
                "file_info": {
                    "filename": file.filename,
                    "rows_processed": len(data_rows),
                    "features_used": len(headers),
                    "feature_names": headers
                },
                "model_info": {
                    "model_type": str(type(model).__name__),
                    "expected_features": expected_features,
                    "model_path": MODEL_PATH
                },
                "predictions": {
                    "values": predictions.tolist(),
                    "count": len(predictions)
                }
            }
            
            # 添加預測統計
            unique_vals, counts = np.unique(predictions, return_counts=True)
            result["predictions"]["distribution"] = dict(zip(unique_vals.tolist(), counts.tolist()))
            
            # 嘗試獲取預測機率
            try:
                probabilities = model.predict_proba(X)
                # 只返回前10個樣本的機率以避免響應過大
                sample_probs = probabilities[:min(10, len(probabilities))]
                result["predictions"]["sample_probabilities"] = sample_probs.tolist()
                result["predictions"]["probability_shape"] = probabilities.shape
            except:
                result["predictions"]["probabilities_available"] = False
            
            return result
            
        except ImportError:
            raise HTTPException(
                status_code=500, 
                detail="缺少 numpy 套件，請安裝: pip install numpy"
            )
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"預測失敗: {e}"
            )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"處理請求失敗: {str(e)}"
        )

@router.get("/model-info")
async def get_model_info():
    """獲取模型詳細信息"""
    try:
        model, error = load_model()
        
        info = {
            "model_path": MODEL_PATH,
            "file_exists": os.path.exists(MODEL_PATH),
            "status": "loaded" if model else "error",
        }
        
        if error:
            info["error"] = error
        
        if os.path.exists(MODEL_PATH):
            info["file_size_mb"] = round(os.path.getsize(MODEL_PATH) / (1024 * 1024), 2)
        
        if model:
            info["model_type"] = str(type(model).__name__)
            
            # 獲取模型屬性
            model_attrs = {}
            for attr in ['n_features_in_', 'classes_', 'n_estimators', 'max_depth', 'n_classes_']:
                if hasattr(model, attr):
                    value = getattr(model, attr)
                    if hasattr(value, 'tolist'):
                        value = value.tolist()
                    model_attrs[attr] = value
            
            info["model_attributes"] = model_attrs
        
        return info
        
    except Exception as e:
        return {
            "error": f"獲取模型信息失敗: {str(e)}",
            "model_path": MODEL_PATH,
            "file_exists": os.path.exists(MODEL_PATH)
        }

@router.post("/predict-batch")
async def predict_batch_data(data: Dict[str, Any]):
    """
    批量預測接口，接受 JSON 格式的特徵數據
    
    - **data**: {"features": [[特徵1, 特徵2, ...], ...], "feature_names": [...]}
    """
    try:
        if "features" not in data:
            raise HTTPException(
                status_code=400,
                detail="請提供 'features' 欄位，格式: {\"features\": [[值1, 值2, ...], ...]}"
            )
        
        features = data["features"]
        if not isinstance(features, list) or not features:
            raise HTTPException(
                status_code=400,
                detail="features 必須是非空的二維列表"
            )
        
        # 載入模型
        model, error = load_model()
        if error:
            raise HTTPException(status_code=500, detail=error)
        
        try:
            import numpy as np
            
            X = np.array(features)
            predictions = model.predict(X)
            
            result = {
                "status": "success",
                "predictions": predictions.tolist(),
                "count": len(predictions),
                "input_shape": X.shape
            }
            
            # 添加預測機率
            try:
                probabilities = model.predict_proba(X)
                result["probabilities"] = probabilities.tolist()
            except:
                result["probabilities_available"] = False
            
            return result
            
        except ImportError:
            raise HTTPException(
                status_code=500,
                detail="缺少 numpy 套件，請安裝: pip install numpy"
            )
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"預測失敗: {e}"
            )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"處理請求失敗: {str(e)}"
        )

@router.post("/reload-model")
async def reload_model():
    """重新載入模型"""
    global _model
    try:
        _model = None  # 清除快取
        model, error = load_model()
        
        if error:
            return {
                "status": "error",
                "message": error
            }
        
        return {
            "status": "success",
            "message": "模型重新載入成功",
            "model_type": str(type(model).__name__)
        }
        
    except Exception as e:
        return {
            "status": "error",
            "message": f"重新載入模型失敗: {str(e)}"
        }