"""
機器學習預測路由
處理 CSV 上傳和 shark_rf_model 預測
"""

from fastapi import APIRouter, UploadFile, File, HTTPException
from fastapi.responses import JSONResponse
import joblib
import pandas as pd
import numpy as np
import io
from typing import Dict, List, Any
import os

router = APIRouter()

# 模型檔案路徑
MODEL_PATH = "shark_rf_model_round_18.joblib"

# 全域模型變數（載入一次，重複使用）
_model = None

def load_model():
    """載入 joblib 模型"""
    global _model
    
    if _model is None:
        try:
            if not os.path.exists(MODEL_PATH):
                raise FileNotFoundError(f"模型檔案不存在: {MODEL_PATH}")
            
            _model = joblib.load(MODEL_PATH)
            print(f"✅ 成功載入模型: {type(_model)}")
            
        except Exception as e:
            print(f"❌ 載入模型失敗: {e}")
            raise
    
    return _model

def preprocess_data(df: pd.DataFrame) -> pd.DataFrame:
    """數據預處理"""
    try:
        # 這裡根據你的模型需求進行數據預處理
        # 例如：處理缺失值、特徵選擇、數據轉換等
        
        # 移除非數值列（如果有的話）
        numeric_columns = df.select_dtypes(include=[np.number]).columns
        df_processed = df[numeric_columns].copy()
        
        # 處理缺失值
        df_processed = df_processed.fillna(0)
        
        print(f"✅ 數據預處理完成，特徵數: {df_processed.shape[1]}, 樣本數: {df_processed.shape[0]}")
        
        return df_processed
        
    except Exception as e:
        print(f"❌ 數據預處理失敗: {e}")
        raise

@router.post("/predict")
async def predict_with_csv(file: UploadFile = File(...)):
    """
    上傳 CSV 檔案並使用 RF 模型進行預測
    
    - **file**: 上傳的 CSV 檔案
    
    返回預測結果和相關統計信息
    """
    try:
        # 驗證檔案類型
        if not file.filename.endswith('.csv'):
            raise HTTPException(
                status_code=400,
                detail="只支援 CSV 檔案，請上傳 .csv 格式的檔案"
            )
        
        # 讀取 CSV 檔案
        contents = await file.read()
        csv_data = io.StringIO(contents.decode('utf-8'))
        df = pd.read_csv(csv_data)
        
        print(f"📁 收到 CSV 檔案: {file.filename}")
        print(f"📊 原始數據形狀: {df.shape}")
        print(f"📋 欄位名稱: {list(df.columns)}")
        
        # 載入模型
        model = load_model()
        
        # 數據預處理
        df_processed = preprocess_data(df)
        
        # 進行預測
        predictions = model.predict(df_processed)
        
        # 如果模型支援，也可以獲取預測機率
        try:
            prediction_proba = model.predict_proba(df_processed)
            has_proba = True
        except:
            prediction_proba = None
            has_proba = False
        
        # 準備返回結果
        results = {
            "status": "success",
            "file_info": {
                "filename": file.filename,
                "original_rows": len(df),
                "original_columns": len(df.columns),
                "processed_rows": len(df_processed),
                "processed_columns": len(df_processed.columns)
            },
            "model_info": {
                "model_type": str(type(model).__name__),
                "model_path": MODEL_PATH
            },
            "predictions": {
                "values": predictions.tolist(),
                "count": len(predictions),
                "unique_predictions": len(np.unique(predictions))
            }
        }
        
        # 如果有預測機率，加入結果
        if has_proba:
            results["predictions"]["probabilities"] = prediction_proba.tolist()
        
        # 添加統計信息
        if len(np.unique(predictions)) <= 10:  # 分類問題
            unique, counts = np.unique(predictions, return_counts=True)
            results["predictions"]["distribution"] = dict(zip(unique.tolist(), counts.tolist()))
        else:  # 回歸問題
            results["predictions"]["statistics"] = {
                "mean": float(np.mean(predictions)),
                "std": float(np.std(predictions)),
                "min": float(np.min(predictions)),
                "max": float(np.max(predictions)),
                "median": float(np.median(predictions))
            }
        
        return results
        
    except Exception as e:
        print(f"❌ 預測失敗: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"預測失敗: {str(e)}"
        )

@router.post("/predict-detailed")
async def predict_with_csv_detailed(file: UploadFile = File(...)):
    """
    上傳 CSV 檔案並返回詳細的預測結果（包含原始數據）
    """
    try:
        # 驗證檔案類型
        if not file.filename.endswith('.csv'):
            raise HTTPException(
                status_code=400,
                detail="只支援 CSV 檔案，請上傳 .csv 格式的檔案"
            )
        
        # 讀取 CSV 檔案
        contents = await file.read()
        csv_data = io.StringIO(contents.decode('utf-8'))
        df = pd.read_csv(csv_data)
        
        # 載入模型並預測
        model = load_model()
        df_processed = preprocess_data(df)
        predictions = model.predict(df_processed)
        
        # 將預測結果加到原始數據中
        df_result = df.copy()
        df_result['prediction'] = predictions
        
        # 嘗試獲取預測機率
        try:
            prediction_proba = model.predict_proba(df_processed)
            # 如果是二分類，添加機率
            if prediction_proba.shape[1] == 2:
                df_result['probability_class_0'] = prediction_proba[:, 0]
                df_result['probability_class_1'] = prediction_proba[:, 1]
            else:
                # 多分類，添加每個類別的機率
                for i in range(prediction_proba.shape[1]):
                    df_result[f'probability_class_{i}'] = prediction_proba[:, i]
        except:
            pass
        
        # 轉換為字典格式返回
        result_data = df_result.to_dict('records')
        
        return {
            "status": "success",
            "file_info": {
                "filename": file.filename,
                "total_rows": len(df_result)
            },
            "data": result_data
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"詳細預測失敗: {str(e)}"
        )

@router.get("/model-info")
async def get_model_info():
    """獲取模型信息"""
    try:
        model = load_model()
        
        info = {
            "model_type": str(type(model).__name__),
            "model_path": MODEL_PATH,
            "file_exists": os.path.exists(MODEL_PATH),
            "file_size_mb": round(os.path.getsize(MODEL_PATH) / (1024 * 1024), 2) if os.path.exists(MODEL_PATH) else 0
        }
        
        # 嘗試獲取模型的額外信息
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
        raise HTTPException(
            status_code=500,
            detail=f"獲取模型信息失敗: {str(e)}"
        )

@router.post("/reload-model")
async def reload_model():
    """重新載入模型"""
    global _model
    try:
        _model = None  # 清除快取
        model = load_model()
        
        return {
            "status": "success",
            "message": "模型重新載入成功",
            "model_type": str(type(model).__name__)
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"重新載入模型失敗: {str(e)}"
        )