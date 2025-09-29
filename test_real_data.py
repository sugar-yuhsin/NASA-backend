#!/usr/bin/env python3
"""
使用真實的鯊魚海洋數據測試 ML 模型
"""

import joblib
import pandas as pd
import numpy as np
from sklearn.preprocessing import StandardScaler

def load_and_test_model():
    """載入模型並測試"""
    model_path = "shark_rf_model_round_18.joblib"
    data_path = "comprehensive_shark_ocean_features - comprehensive_shark_ocean_features.csv"
    
    print("🚀 載入模型和數據...")
    
    # 載入模型
    try:
        model = joblib.load(model_path)
        print(f"✅ 模型載入成功: {type(model).__name__}")
        print(f"📊 模型需要 {model.n_features_in_} 個特徵")
        
        if hasattr(model, 'classes_'):
            print(f"🎯 模型類別: {model.classes_}")
        
    except Exception as e:
        print(f"❌ 模型載入失敗: {e}")
        return
    
    # 載入數據
    try:
        df = pd.read_csv(data_path)
        print(f"📁 數據載入成功: {df.shape[0]} 行, {df.shape[1]} 列")
        print(f"📋 欄位名稱: {list(df.columns)}")
        
    except Exception as e:
        print(f"❌ 數據載入失敗: {e}")
        return
    
    # 選擇數值特徵進行預測
    print("\n🔍 處理特徵...")
    
    # 移除非數值欄位
    non_numeric_cols = ['Date', 'Individual_ID', 'is_in_eddy', 'eddy_type']
    numeric_cols = [col for col in df.columns if col not in non_numeric_cols]
    
    print(f"📊 數值欄位: {len(numeric_cols)} 個")
    print(f"📋 數值欄位列表: {numeric_cols}")
    
    # 準備特徵數據
    X = df[numeric_cols].copy()
    
    # 處理缺失值
    X = X.fillna(0)
    
    print(f"🔢 特徵數據形狀: {X.shape}")
    
    # 如果特徵數量不匹配，選擇前 N 個特徵
    if X.shape[1] != model.n_features_in_:
        print(f"⚠️  特徵數量不匹配，選擇前 {model.n_features_in_} 個特徵")
        X = X.iloc[:, :model.n_features_in_]
        print(f"🔢 調整後的特徵數據形狀: {X.shape}")
    
    # 進行預測
    print("\n🧪 開始預測...")
    
    try:
        # 只用前 10 行進行測試，避免輸出太多
        X_test = X.head(10)
        predictions = model.predict(X_test)
        
        print(f"✅ 預測完成!")
        print(f"📈 預測結果: {predictions}")
        print(f"🎯 預測類別分佈: {np.bincount(predictions)}")
        
        # 如果模型支援預測機率
        try:
            probabilities = model.predict_proba(X_test)
            print(f"📊 預測機率形狀: {probabilities.shape}")
            print(f"📈 前3個樣本的預測機率:")
            for i in range(min(3, len(probabilities))):
                print(f"   樣本 {i+1}: {probabilities[i]}")
        except:
            print("ℹ️  模型不支援機率預測")
        
        # 顯示一些統計信息
        print(f"\n📊 數據統計:")
        print(f"   總樣本數: {len(df)}")
        print(f"   測試樣本數: {len(X_test)}")
        print(f"   預測為類別 0 的數量: {np.sum(predictions == 0)}")
        print(f"   預測為類別 1 的數量: {np.sum(predictions == 1)}")
        
        # 顯示一些原始數據
        print(f"\n📋 前3行原始數據特徵:")
        for i in range(min(3, len(X_test))):
            print(f"   樣本 {i+1}: {X_test.iloc[i].values[:5]}... (只顯示前5個特徵)")
            print(f"   預測: {predictions[i]}")
        
        return True
        
    except Exception as e:
        print(f"❌ 預測失敗: {e}")
        return False

def main():
    """主函數"""
    print("🦈 開始測試鯊魚海洋數據 ML 預測...")
    
    success = load_and_test_model()
    
    if success:
        print("\n✅ 測試成功完成!")
    else:
        print("\n❌ 測試失敗!")

if __name__ == "__main__":
    main()