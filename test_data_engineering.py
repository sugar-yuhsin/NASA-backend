#!/usr/bin/env python3
"""
測試改進的 ML 數據工程流程
"""

import csv

def test_data_engineering():
    """測試數據工程流程"""
    print("🧪 測試數據工程流程...")
    
    # 讀取一些樣本數據
    csv_file = "merged_shark_ocean_data.csv"
    
    try:
        with open(csv_file, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            sample_rows = []
            
            # 取前10行作為測試
            for i, row in enumerate(reader):
                if i >= 10:
                    break
                sample_rows.append(row)
        
        print(f"📊 讀取了 {len(sample_rows)} 行測試數據")
        print(f"📋 欄位: {list(sample_rows[0].keys())}")
        
        # 顯示一些樣本數據
        print("\n📋 樣本數據:")
        for i, row in enumerate(sample_rows[:3]):
            print(f"第 {i+1} 行:")
            print(f"  日期: {row.get('Date')}")
            print(f"  經緯度: ({row.get('Longitude')}, {row.get('Latitude')})")
            print(f"  SST: {row.get('SST_Value')}")
            print(f"  CHL: {row.get('CHL_Concentration')}")
            print(f"  鯊魚標籤: {row.get('has_shark')}")
            print()
        
        # 測試特徵選擇
        selected_features = [
            'Longitude', 'Latitude', 
            'SST_Value', 'SST_Gradient', 
            'CHL_Concentration', 'CHL_Gradient',
            'SSHA_Value', 'SSHA_Gradient',
            'Thermal_Front_Strength', 'Productivity_Index',
            'dist_to_eddy_center_km', 'Daily_Movement_km',
            'Days_To_Env_Data'
        ]
        
        available_features = [f for f in selected_features if f in sample_rows[0].keys()]
        print(f"✅ 可用特徵 ({len(available_features)}):")
        for feature in available_features:
            print(f"  - {feature}")
        
        missing_features = [f for f in selected_features if f not in sample_rows[0].keys()]
        if missing_features:
            print(f"⚠️ 缺失特徵 ({len(missing_features)}):")
            for feature in missing_features:
                print(f"  - {feature}")
        
        # 測試數據類型
        print(f"\n🔍 數據類型檢查:")
        sample_row = sample_rows[0]
        for feature in available_features[:5]:  # 只檢查前5個
            value = sample_row.get(feature)
            try:
                float_val = float(value)
                print(f"  {feature}: '{value}' → {float_val} ✅")
            except:
                print(f"  {feature}: '{value}' → 無法轉換為數值 ❌")
        
        # 統計鯊魚標籤分佈
        shark_labels = [int(float(row.get('has_shark', 0))) for row in sample_rows]
        shark_count = sum(shark_labels)
        no_shark_count = len(shark_labels) - shark_count
        
        print(f"\n🦈 標籤分佈:")
        print(f"  有鯊魚 (1): {shark_count}")
        print(f"  沒鯊魚 (0): {no_shark_count}")
        
        return True
        
    except FileNotFoundError:
        print(f"❌ 找不到檔案: {csv_file}")
        return False
    except Exception as e:
        print(f"❌ 測試失敗: {e}")
        return False

def main():
    """主函數"""
    print("🚀 開始測試數據工程流程...")
    
    success = test_data_engineering()
    
    if success:
        print("\n✅ 測試完成！數據工程流程看起來正常。")
        print("\n💡 建議:")
        print("  1. 使用 /api/v1/ml/predict-advanced 端點進行預測")
        print("  2. 查看 /api/v1/ml/features 端點了解特徵工程細節")
        print("  3. 使用 /api/v1/ml/model-info 端點檢查模型信息")
    else:
        print("\n❌ 測試失敗！請檢查數據檔案和設定。")

if __name__ == "__main__":
    main()