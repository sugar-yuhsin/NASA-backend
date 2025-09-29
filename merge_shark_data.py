#!/usr/bin/env python3
"""
合併鯊魚數據檔案並添加標籤
- v8.1_comprehensive_shark_features.csv: 有鯊魚數據 (label=1)
- v8.1_standardized_random_features.csv: 無鯊魚數據 (label=0)
"""

import pandas as pd
import os

def merge_shark_data():
    """合併兩個 CSV 檔案並添加鯊魚標籤"""
    
    # 檔案路徑
    shark_file = "v8.1_comprehensive_shark_features.csv"
    random_file = "v8.1_standardized_random_features.csv"
    output_file = "merged_shark_ocean_data.csv"
    
    print("🦈 開始處理鯊魚數據合併...")
    
    # 檢查檔案是否存在
    if not os.path.exists(shark_file):
        print(f"❌ 找不到鯊魚數據檔案: {shark_file}")
        return False
    
    if not os.path.exists(random_file):
        print(f"❌ 找不到隨機數據檔案: {random_file}")
        return False
    
    try:
        # 讀取鯊魚數據 (有鯊魚)
        print(f"📊 讀取鯊魚數據: {shark_file}")
        shark_df = pd.read_csv(shark_file)
        shark_df['has_shark'] = 1  # 添加鯊魚標籤
        print(f"   ✅ 鯊魚數據: {len(shark_df)} 行")
        
        # 讀取隨機數據 (無鯊魚)
        print(f"📊 讀取隨機數據: {random_file}")
        random_df = pd.read_csv(random_file)
        random_df['has_shark'] = 0  # 添加無鯊魚標籤
        print(f"   ✅ 隨機數據: {len(random_df)} 行")
        
        # 合併數據
        print("🔗 合併數據...")
        merged_df = pd.concat([shark_df, random_df], ignore_index=True)
        print(f"   ✅ 合併後總計: {len(merged_df)} 行")
        
        # 檢查數據分佈
        shark_count = merged_df['has_shark'].sum()
        no_shark_count = len(merged_df) - shark_count
        print(f"   🦈 有鯊魚數據: {shark_count} 行")
        print(f"   🌊 無鯊魚數據: {no_shark_count} 行")
        
        # 保存合併後的數據
        print(f"💾 保存合併數據到: {output_file}")
        merged_df.to_csv(output_file, index=False)
        
        # 顯示合併後的欄位
        print(f"📋 合併後的欄位 ({len(merged_df.columns)} 個):")
        for i, col in enumerate(merged_df.columns, 1):
            print(f"   {i:2d}. {col}")
        
        # 顯示前幾行示例
        print("\n📖 合併後數據示例 (前3行):")
        print(merged_df.head(3).to_string())
        
        print(f"\n✅ 數據合併完成！輸出檔案: {output_file}")
        return True
        
    except Exception as e:
        print(f"❌ 處理過程中出錯: {e}")
        return False

def verify_merged_data():
    """驗證合併後的數據"""
    output_file = "merged_shark_ocean_data.csv"
    
    if not os.path.exists(output_file):
        print(f"❌ 找不到合併檔案: {output_file}")
        return False
    
    try:
        df = pd.read_csv(output_file)
        
        print("\n🔍 數據驗證:")
        print(f"   總行數: {len(df)}")
        print(f"   總欄位數: {len(df.columns)}")
        print(f"   有鯊魚 (has_shark=1): {df['has_shark'].sum()} 行")
        print(f"   無鯊魚 (has_shark=0): {(df['has_shark'] == 0).sum()} 行")
        
        # 檢查日期範圍
        df['Date'] = pd.to_datetime(df['Date'])
        print(f"   日期範圍: {df['Date'].min()} 到 {df['Date'].max()}")
        
        # 檢查是否有重複的日期和位置
        duplicates = df.duplicated(['Date', 'Longitude', 'Latitude']).sum()
        print(f"   重複記錄: {duplicates} 行")
        
        return True
        
    except Exception as e:
        print(f"❌ 驗證過程中出錯: {e}")
        return False

if __name__ == "__main__":
    # 執行合併
    success = merge_shark_data()
    
    if success:
        # 驗證合併結果
        verify_merged_data()
    else:
        print("❌ 數據合併失敗")