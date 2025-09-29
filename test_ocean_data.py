"""
簡化的海洋數據測試腳本
直接讀取 CSV 並提供簡單的查詢功能
"""

import pandas as pd
from datetime import date, datetime
from typing import Optional, Dict, Any
import json

class SimpleOceanDataTest:
    """簡化的海洋數據測試類"""
    
    def __init__(self):
        self.csv_file_path = "comprehensive_shark_ocean_features - comprehensive_shark_ocean_features.csv"
        self.data = None
        self.load_data()
    
    def load_data(self):
        """載入 CSV 數據"""
        try:
            self.data = pd.read_csv(self.csv_file_path)
            # 轉換日期欄位
            self.data['Date'] = pd.to_datetime(self.data['Date']).dt.date
            print(f"✅ 成功載入 {len(self.data)} 筆海洋數據")
            print(f"📅 日期範圍: {self.data['Date'].min()} 到 {self.data['Date'].max()}")
            print(f"📊 可用欄位: {list(self.data.columns)}")
        except Exception as e:
            print(f"❌ 載入 CSV 檔案失敗: {e}")
            self.data = None
    
    def get_data_by_date(self, query_date: date) -> Optional[Dict[str, Any]]:
        """根據日期獲取海洋數據"""
        if self.data is None:
            return None
        
        # 篩選指定日期的數據
        filtered_data = self.data[self.data['Date'] == query_date]
        
        if filtered_data.empty:
            return {
                "date": str(query_date),
                "sst_value": None,
                "chl_value": None,
                "ssha_value": None,
                "data_count": 0,
                "message": "該日期無數據"
            }
        
        # 計算平均值（如果有多筆記錄）
        avg_sst = filtered_data['SST_Value'].mean() if not filtered_data['SST_Value'].isna().all() else None
        avg_chl = filtered_data['CHL_Value'].mean() if not filtered_data['CHL_Value'].isna().all() else None  
        avg_ssha = filtered_data['SSHA_Value'].mean() if not filtered_data['SSHA_Value'].isna().all() else None
        
        return {
            "date": str(query_date),
            "sst_value": round(avg_sst, 6) if avg_sst is not None else None,
            "chl_value": round(avg_chl, 6) if avg_chl is not None else None,
            "ssha_value": round(avg_ssha, 6) if avg_ssha is not None else None,
            "data_count": len(filtered_data),
            "message": "查詢成功"
        }
    
    def get_sample_dates(self, limit: int = 10):
        """獲取樣本日期"""
        if self.data is None:
            return []
        
        unique_dates = sorted(self.data['Date'].unique())
        return [str(d) for d in unique_dates[:limit]]

def main():
    """主測試函數"""
    print("🧪 NASA 海洋數據測試")
    print("=" * 50)
    
    # 創建測試實例
    ocean_test = SimpleOceanDataTest()
    
    if ocean_test.data is None:
        print("❌ 無法載入數據，程式結束")
        return
    
    # 獲取樣本日期
    sample_dates = ocean_test.get_sample_dates(5)
    print(f"\n📅 前 5 個可用日期: {sample_dates}")
    
    # 測試幾個日期
    test_dates = [
        date(2014, 7, 10),
        date(2014, 7, 15),
        date(2014, 8, 1),  # 可能沒有數據的日期
    ]
    
    print("\n🔍 測試查詢結果:")
    print("-" * 30)
    
    for test_date in test_dates:
        result = ocean_test.get_data_by_date(test_date)
        print(f"\n日期: {test_date}")
        print(f"結果: {json.dumps(result, indent=2, ensure_ascii=False)}")
    
    print("\n" + "=" * 50)
    print("測試完成！")

if __name__ == "__main__":
    main()