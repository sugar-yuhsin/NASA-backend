"""
改進的機器學習預測路由
包含完整的數據工程和預處理流程
"""

from fastapi import APIRouter, UploadFile, File, HTTPException
from fastapi.responses import JSONResponse
from typing import Dict, List, Any, Optional
import io
import os
import numpy as np

router = APIRouter()

# 模型檔案路徑
MODEL_PATH = "shark_rf_model_round_18.joblib"

# 全域模型變數
_model = None

def load_ml_model():
    """載入 joblib 模型"""
    global _model
    
    if _model is None:
        try:
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

@router.post("/predict")
async def predict_with_csv_advanced(
    file: UploadFile = File(...),
    enable_augmentation: bool = False
):
    """
    上傳 CSV 檔案並使用 RF 模型進行預測（包含完整數據工程）
    
    - **file**: 上傳的 CSV 檔案
    - **enable_augmentation**: 是否啟用數據增強（生成負樣本）
    
    返回預測結果和詳細的處理信息
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
        
        print(f"📁 收到 CSV 檔案: {file.filename}")
        
        # 使用改進的數據處理流程
        try:
            from data_processor import process_uploaded_csv
            
            features, feature_names, error = process_uploaded_csv(
                csv_content, 
                enable_augmentation=enable_augmentation
            )
            
            if error:
                raise HTTPException(status_code=400, detail=error)
            
            if features is None or len(features) == 0:
                raise HTTPException(status_code=400, detail="處理後沒有有效的數據行")
            
            print(f"🔧 數據預處理完成: {features.shape[0]} 行, {features.shape[1]} 列")
            print(f"📋 特徵: {feature_names}")
            
        except ImportError:
            # 如果無法載入數據處理器，回退到簡單處理
            print("⚠️ 無法載入數據處理器，使用簡單處理流程")
            features, feature_names, error = simple_process_csv(csv_content)
            if error:
                raise HTTPException(status_code=400, detail=error)
        
        # 檢查特徵數量是否匹配模型要求
        required_features = model.n_features_in_
        if features.shape[1] != required_features:
            print(f"⚠️ 特徵數量不匹配，調整為 {required_features} 個特徵")
            
            if features.shape[1] > required_features:
                # 如果特徵太多，選擇前 N 個
                features = features[:, :required_features]
                feature_names = feature_names[:required_features] if feature_names else None
            else:
                # 如果特徵不夠，用0填充
                padding = np.zeros((features.shape[0], required_features - features.shape[1]))
                features = np.hstack([features, padding])
                
                # 更新特徵名稱
                if feature_names:
                    for i in range(len(feature_names), required_features):
                        feature_names.append(f"feature_{i}")
        
        print(f"🔢 最終特徵形狀: {features.shape}")
        
        # 進行預測
        try:
            predictions = model.predict(features)
            
            # 計算統計信息
            prediction_list = predictions.tolist()
            unique_predictions = list(set(prediction_list))
            
            result = {
                "status": "success",
                "file_info": {
                    "filename": file.filename,
                    "rows_processed": len(features),
                    "features_used": required_features,
                    "feature_names": feature_names[:required_features] if feature_names else None,
                    "data_augmentation_enabled": enable_augmentation
                },
                "model_info": {
                    "model_type": str(type(model).__name__),
                    "model_path": MODEL_PATH,
                    "required_features": required_features
                },
                "predictions": {
                    "values": prediction_list,
                    "count": len(prediction_list),
                    "unique_values": unique_predictions,
                    "unique_count": len(unique_predictions)
                }
            }
            
            # 如果是二分類問題，添加詳細統計
            if len(unique_predictions) <= 2:
                distribution = {}
                for pred in prediction_list:
                    distribution[pred] = distribution.get(pred, 0) + 1
                
                result["predictions"]["distribution"] = distribution
                
                # 添加百分比
                total = len(prediction_list)
                percentages = {k: round(v/total*100, 2) for k, v in distribution.items()}
                result["predictions"]["percentages"] = percentages
            
            # 嘗試獲取預測機率
            try:
                probabilities = model.predict_proba(features)
                result["predictions"]["probabilities_summary"] = {
                    "shape": probabilities.shape,
                    "mean_confidence": float(np.mean(np.max(probabilities, axis=1))),
                    "min_confidence": float(np.min(np.max(probabilities, axis=1))),
                    "max_confidence": float(np.max(np.max(probabilities, axis=1)))
                }
                
                # 只回傳前10個樣本的機率（避免數據太大）
                if len(probabilities) <= 10:
                    result["predictions"]["probabilities"] = probabilities.tolist()
                else:
                    result["predictions"]["probabilities_sample"] = probabilities[:10].tolist()
                    result["predictions"]["note"] = "只顯示前10個樣本的預測機率"
                
            except Exception as e:
                print(f"⚠️ 無法獲取預測機率: {e}")
            
            return result
            
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"預測失敗: {e}")
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"處理失敗: {str(e)}")

def simple_process_csv(csv_content: str) -> tuple:
    """簡單的 CSV 處理流程（回退方案）"""
    try:
        import csv
        import io
        
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
        
        features = np.array(data_rows) if data_rows else None
        return features, columns, None
        
    except Exception as e:
        return None, None, f"CSV 處理失敗: {e}"

@router.get("/model-info")
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
                if hasattr(model, 'max_depth'):
                    info['max_depth'] = model.max_depth
            except:
                pass
        
        return info
        
    except Exception as e:
        return {"error": f"獲取模型信息失敗: {str(e)}"}

@router.get("/processing-info")
async def get_processing_info():
    """獲取數據處理流程信息"""
    try:
        from data_processor import OceanDataProcessor
        
        # 創建一個示例處理器來獲取信息
        processor = OceanDataProcessor("")
        
        return {
            "status": "available",
            "features": processor.features,
            "feature_count": len(processor.features),
            "processing_steps": [
                "1. 載入數據",
                "2. 篩選日期範圍", 
                "3. 篩選特徵",
                "4. 添加時間特徵 (Day_of_Year, Month)",
                "5. 填補缺失值 (中位數策略)",
                "6. 數據增強 (可選) - 生成負樣本",
                "7. 最終數據清理"
            ],
            "augmentation_available": True,
            "description": "完整的數據工程流程，包含特徵工程、缺失值處理和數據增強"
        }
        
    except ImportError:
        return {
            "status": "not_available",
            "message": "數據處理器模組不可用",
            "fallback": "使用簡單的數值轉換處理"
        }