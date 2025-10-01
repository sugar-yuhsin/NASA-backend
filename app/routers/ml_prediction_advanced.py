"""
改進的機器學習預測路由
包含完整的數據工程流程
"""

from fastapi import APIRouter, UploadFile, File, HTTPException
from typing import Dict, List, Any, Optional
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
            if not os.path.exists(MODEL_PATH):
                raise FileNotFoundError(f"模型檔案不存在: {MODEL_PATH}")
            
            import joblib
            _model = joblib.load(MODEL_PATH)
            print(f"✅ 模型載入成功: {type(_model).__name__}")
            return _model, None
            
        except ImportError as e:
            return None, f"缺少必要套件: {e}"
        except Exception as e:
            return None, f"載入模型失敗: {e}"
    
    return _model, None

def data_engineering_pipeline(csv_content: str) -> tuple:
    """
    完整的數據工程流程
    1. 解析 CSV
    2. 特徵選擇
    3. 數據清理
    4. 特徵工程
    5. 數據標準化
    """
    try:
        # 1. 解析 CSV
        csv_reader = csv.DictReader(io.StringIO(csv_content))
        rows = list(csv_reader)
        
        if not rows:
            return None, None, None, "CSV 檔案沒有數據"
        
        headers = list(rows[0].keys())
        print(f"📋 原始欄位: {headers}")
        
        # 2. 特徵選擇 - 選擇對鯊魚預測有用的特徵
        selected_features = [
            'Longitude', 'Latitude', 
            'SST_Value', 'SST_Gradient', 
            'CHL_Concentration', 'CHL_Gradient',
            'SSHA_Value', 'SSHA_Gradient',
            'Thermal_Front_Strength', 'Productivity_Index',
            'dist_to_eddy_center_km', 'Daily_Movement_km',
            'Days_To_Env_Data'
        ]
        
        # 檢查哪些特徵存在
        available_features = [f for f in selected_features if f in headers]
        print(f"📊 可用特徵: {available_features}")
        
        # 3. 數據清理和特徵工程
        processed_data = []
        labels = []  # 如果有標籤的話
        
        for row in rows:
            # 提取特徵
            feature_vector = []
            
            for feature in available_features:
                value = row.get(feature, '0')
                
                # 處理特殊值
                if feature in ['is_in_eddy']:
                    # 布林值轉數值
                    feature_vector.append(1.0 if value.lower() in ['true', '1', 'yes'] else 0.0)
                elif feature == 'eddy_type':
                    # 類別變數編碼
                    eddy_mapping = {'none': 0, 'anticyclonic': 1, 'cyclonic': 2}
                    feature_vector.append(float(eddy_mapping.get(value.lower(), 0)))
                else:
                    # 數值特徵
                    try:
                        numeric_value = float(value) if value != '' else 0.0
                        # 處理異常值
                        if abs(numeric_value) > 1e6:  # 處理極端值
                            numeric_value = 0.0
                        feature_vector.append(numeric_value)
                    except (ValueError, TypeError):
                        feature_vector.append(0.0)
            
            # 特徵工程 - 創建新特徵
            if len(feature_vector) >= 4:  # 確保有足夠的基本特徵
                # 溫度與葉綠素的交互作用
                sst_chl_interaction = feature_vector[2] * feature_vector[4] if len(feature_vector) > 4 else 0.0
                feature_vector.append(sst_chl_interaction)
                
                # 距離特徵（從原點的距離）
                if len(feature_vector) >= 2:
                    distance_from_origin = (feature_vector[0]**2 + feature_vector[1]**2)**0.5
                    feature_vector.append(distance_from_origin)
            
            processed_data.append(feature_vector)
            
            # 提取標籤（如果存在）
            if 'has_shark' in row:
                labels.append(int(float(row['has_shark'])))
        
        # 4. 特徵名稱
        final_feature_names = available_features.copy()
        if len(processed_data) > 0 and len(processed_data[0]) > len(available_features):
            final_feature_names.extend(['SST_CHL_Interaction', 'Distance_From_Origin'])
        
        # 5. 數據標準化（簡單版本）
        if processed_data:
            import numpy as np
            data_array = np.array(processed_data)
            
            # 基本統計信息
            means = np.mean(data_array, axis=0)
            stds = np.std(data_array, axis=0)
            
            # 避免除以零
            stds = np.where(stds == 0, 1, stds)
            
            # 標準化
            normalized_data = (data_array - means) / stds
            
            return normalized_data.tolist(), final_feature_names, labels, None
        
        return processed_data, final_feature_names, labels, None
        
    except Exception as e:
        return None, None, None, f"數據工程失敗: {e}"

@router.post("/predict-advanced")
async def predict_with_advanced_preprocessing(file: UploadFile = File(...)):
    """
    上傳 CSV 檔案，進行完整數據工程後預測
    
    包含：
    - 特徵選擇
    - 數據清理
    - 特徵工程
    - 數據標準化
    - 模型預測
    """
    try:
        # 驗證檔案
        if not file.filename or not file.filename.lower().endswith('.csv'):
            raise HTTPException(status_code=400, detail="只支援 CSV 檔案")
        
        # 載入模型
        model, error = load_model()
        if error:
            raise HTTPException(status_code=500, detail=error)
        
        # 讀取檔案
        contents = await file.read()
        csv_content = contents.decode('utf-8')
        
        # 數據工程流程
        processed_data, feature_names, labels, process_error = data_engineering_pipeline(csv_content)
        if process_error:
            raise HTTPException(status_code=400, detail=process_error)
        
        # 調整特徵數量以匹配模型
        model_features = getattr(model, 'n_features_in_', 13)
        
        if len(processed_data[0]) > model_features:
            # 取前 N 個特徵
            processed_data = [row[:model_features] for row in processed_data]
            feature_names = feature_names[:model_features]
        elif len(processed_data[0]) < model_features:
            # 補零
            for i in range(len(processed_data)):
                while len(processed_data[i]) < model_features:
                    processed_data[i].append(0.0)
            while len(feature_names) < model_features:
                feature_names.append(f'feature_{len(feature_names)}')
        
        # 預測
        import numpy as np
        X = np.array(processed_data)
        predictions = model.predict(X)
        
        # 如果模型支援，獲取預測機率
        probabilities = None
        try:
            probabilities = model.predict_proba(X)
        except:
            pass
        
        # 準備結果
        result = {
            "status": "success",
            "data_engineering": {
                "original_samples": len(processed_data),
                "features_used": len(feature_names),
                "feature_names": feature_names,
                "preprocessing_steps": [
                    "特徵選擇", "數據清理", "特徵工程", "數據標準化"
                ]
            },
            "model_info": {
                "model_type": str(type(model).__name__),
                "expected_features": model_features,
                "model_classes": getattr(model, 'classes_', [0, 1]).tolist()
            },
            "predictions": {
                "values": predictions.tolist(),
                "count": len(predictions)
            }
        }
        
        # 添加預測機率
        if probabilities is not None:
            result["predictions"]["probabilities"] = probabilities.tolist()
            
            # 預測信心度
            max_probs = np.max(probabilities, axis=1)
            result["predictions"]["confidence"] = {
                "mean": float(np.mean(max_probs)),
                "min": float(np.min(max_probs)),
                "max": float(np.max(max_probs))
            }
        
        # 如果有真實標籤，計算準確度
        if labels:
            accuracy = np.mean(predictions == np.array(labels))
            result["evaluation"] = {
                "accuracy": float(accuracy),
                "true_labels_available": True
            }
        
        # 預測統計
        unique_preds, counts = np.unique(predictions, return_counts=True)
        result["predictions"]["distribution"] = dict(zip(unique_preds.tolist(), counts.tolist()))
        
        return result
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"預測失敗: {str(e)}")

@router.post("/predict")
async def predict_with_csv(file: UploadFile = File(...)):
    """
    簡單版本的預測（向後相容）
    """
    # 重定向到高級預測
    return await predict_with_advanced_preprocessing(file)

@router.get("/model-info")
async def get_model_info():
    """獲取模型詳細信息"""
    try:
        model, error = load_model()
        if error:
            return {"error": error}
        
        info = {
            "model_path": MODEL_PATH,
            "file_exists": os.path.exists(MODEL_PATH),
            "model_type": str(type(model).__name__),
            "file_size_mb": round(os.path.getsize(MODEL_PATH) / (1024 * 1024), 2)
        }
        
        # 模型屬性
        attrs = ['n_features_in_', 'classes_', 'n_estimators', 'max_depth', 'feature_names_in_']
        for attr in attrs:
            if hasattr(model, attr):
                value = getattr(model, attr)
                if hasattr(value, 'tolist'):
                    value = value.tolist()
                info[attr] = value
        
        return info
        
    except Exception as e:
        return {"error": f"獲取模型信息失敗: {str(e)}"}

@router.get("/features")
async def get_feature_info():
    """獲取特徵工程信息"""
    return {
        "selected_features": [
            "Longitude", "Latitude", 
            "SST_Value", "SST_Gradient", 
            "CHL_Concentration", "CHL_Gradient",
            "SSHA_Value", "SSHA_Gradient",
            "Thermal_Front_Strength", "Productivity_Index",
            "dist_to_eddy_center_km", "Daily_Movement_km",
            "Days_To_Env_Data"
        ],
        "engineered_features": [
            "SST_CHL_Interaction", "Distance_From_Origin"
        ],
        "preprocessing_steps": [
            "1. 特徵選擇 - 選擇與鯊魚預測相關的特徵",
            "2. 數據清理 - 處理缺失值和異常值",
            "3. 特徵工程 - 創建交互特徵和距離特徵",
            "4. 數據標準化 - Z-score 標準化"
        ]
    }