#!/usr/bin/env python3
"""
測試機器學習模型預測功能
直接使用 joblib 載入模型並進行預測
"""

import os
import csv
import sys

def test_model_loading():
    """測試模型載入"""
    model_path = "shark_rf_model_round_18.joblib"
    
    print("🔍 檢查模型檔案...")
    if not os.path.exists(model_path):
        print(f"❌ 模型檔案不存在: {model_path}")
        return None
    
    print(f"✅ 模型檔案存在: {model_path}")
    print(f"📁 檔案大小: {os.path.getsize(model_path) / (1024 * 1024):.2f} MB")
    
    try:
        import joblib
        print("✅ joblib 已安裝")
    except ImportError:
        print("❌ joblib 未安裝，請執行: pip install joblib")
        return None
    
    try:
        model = joblib.load(model_path)
        print(f"✅ 模型載入成功: {type(model).__name__}")
        return model
    except Exception as e:
        print(f"❌ 模型載入失敗: {e}")
        return None

def get_model_info(model):
    """獲取模型詳細信息"""
    if model is None:
        return
    
    print("\n📊 模型信息:")
    print(f"   類型: {type(model).__name__}")
    
    # 嘗試獲取模型屬性
    attrs_to_check = [
        'n_features_in_',
        'feature_names_in_',
        'classes_',
        'n_estimators',
        'max_depth',
        'n_classes_'
    ]
    
    for attr in attrs_to_check:
        if hasattr(model, attr):
            value = getattr(model, attr)
            if hasattr(value, 'tolist'):
                value = value.tolist()
            print(f"   {attr}: {value}")

def create_sample_csv():
    """創建測試用的 CSV 檔案"""
    csv_filename = "test_prediction.csv"
    
    # 創建一些測試數據
    test_data = [
        ["feature1", "feature2", "feature3", "feature4"],
        [1.0, 2.0, 3.0, 4.0],
        [2.5, 3.5, 4.5, 5.5],
        [0.5, 1.5, 2.5, 3.5],
        [3.0, 4.0, 5.0, 6.0]
    ]
    
    with open(csv_filename, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerows(test_data)
    
    print(f"✅ 創建測試 CSV 檔案: {csv_filename}")
    return csv_filename

def test_prediction_with_csv(model, csv_filename):
    """測試使用 CSV 檔案進行預測"""
    if model is None:
        return
    
    try:
        import numpy as np
        print("✅ numpy 已安裝")
    except ImportError:
        print("❌ numpy 未安裝，請執行: pip install numpy")
        return
    
    print(f"\n🧪 測試預測 - 使用 {csv_filename}")
    
    try:
        # 讀取 CSV 檔案
        data_rows = []
        with open(csv_filename, 'r', encoding='utf-8') as f:
            reader = csv.reader(f)
            headers = next(reader)  # 跳過標題行
            
            for row in reader:
                # 轉換為數值
                numeric_row = []
                for value in row:
                    try:
                        numeric_row.append(float(value))
                    except ValueError:
                        numeric_row.append(0.0)
                data_rows.append(numeric_row)
        
        print(f"📊 讀取數據: {len(data_rows)} 行, {len(headers)} 列")
        print(f"📋 欄位: {headers}")
        
        if not data_rows:
            print("❌ 沒有有效的數據行")
            return
        
        # 進行預測
        X = np.array(data_rows)
        print(f"🔢 數據形狀: {X.shape}")
        
        predictions = model.predict(X)
        print(f"✅ 預測完成!")
        print(f"📈 預測結果: {predictions.tolist()}")
        
        # 統計信息
        unique_predictions = np.unique(predictions)
        print(f"🎯 預測種類: {len(unique_predictions)} 種")
        print(f"📊 不同預測值: {unique_predictions.tolist()}")
        
        # 如果模型支援預測機率
        try:
            probabilities = model.predict_proba(X)
            print(f"📊 預測機率形狀: {probabilities.shape}")
            print(f"📈 第一個樣本的機率: {probabilities[0].tolist()}")
        except:
            print("ℹ️  模型不支援機率預測")
        
    except Exception as e:
        print(f"❌ 預測失敗: {e}")

def test_simple_prediction(model):
    """測試簡單數據預測"""
    if model is None:
        return
    
    try:
        import numpy as np
    except ImportError:
        return
    
    print("\n🧪 測試簡單預測")
    
    try:
        # 創建簡單的測試數據
        test_data = np.array([[1, 2, 3, 4], [5, 6, 7, 8]])
        predictions = model.predict(test_data)
        
        print(f"✅ 簡單預測成功!")
        print(f"📊 測試數據: {test_data.tolist()}")
        print(f"📈 預測結果: {predictions.tolist()}")
        
    except Exception as e:
        print(f"❌ 簡單預測失敗: {e}")

def main():
    """主函數"""
    print("🚀 開始測試機器學習模型...")
    
    # 測試模型載入
    model = test_model_loading()
    
    # 獲取模型信息
    get_model_info(model)
    
    # 創建測試 CSV
    csv_filename = create_sample_csv()
    
    # 測試 CSV 預測
    test_prediction_with_csv(model, csv_filename)
    
    # 測試簡單預測
    test_simple_prediction(model)
    
    print("\n✅ 測試完成!")
    
    # 清理測試檔案
    if os.path.exists(csv_filename):
        os.remove(csv_filename)
        print(f"🧹 清理測試檔案: {csv_filename}")

if __name__ == "__main__":
    main()