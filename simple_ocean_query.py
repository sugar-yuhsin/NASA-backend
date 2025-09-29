"""
極簡版海洋數據查詢功能
直接使用 CSV 模組讀取數據，避免複雜依賴
"""

import csv
from datetime import datetime, date
from typing import Dict, List, Optional
import json

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

def get_sample_dates(limit: int = 10) -> List[str]:
    """獲取樣本日期"""
    csv_file = "comprehensive_shark_ocean_features - comprehensive_shark_ocean_features.csv"
    dates = set()
    
    try:
        with open(csv_file, 'r', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            
            for row in reader:
                if len(dates) >= limit:
                    break
                dates.add(row['Date'])
        
        return sorted(list(dates))[:limit]
        
    except Exception as e:
        print(f"讀取樣本日期失敗: {e}")
        return []

def main():
    """主測試函數"""
    print("🧪 NASA 海洋數據簡易測試")
    print("=" * 50)
    
    # 獲取樣本日期
    sample_dates = get_sample_dates(5)
    print(f"📅 前 5 個可用日期: {sample_dates}")
    
    # 測試幾個日期
    test_dates = [
        date(2014, 7, 10),
        date(2014, 7, 15),
        date(2014, 8, 1),  # 可能沒有數據的日期
    ]
    
    print("\n🔍 測試查詢結果:")
    print("-" * 30)
    
    for test_date in test_dates:
        result = get_ocean_data_by_date(test_date)
        print(f"\n日期: {test_date}")
        print(f"結果: {json.dumps(result, indent=2, ensure_ascii=False)}")
    
    print("\n" + "=" * 50)
    print("測試完成！")
    
    # 互動式查詢
    print("\n💡 你可以輸入日期進行查詢 (格式: YYYY-MM-DD)")
    print("輸入 'quit' 退出")
    
    while True:
        try:
            user_input = input("\n請輸入日期: ").strip()
            
            if user_input.lower() == 'quit':
                break
            
            query_date = datetime.strptime(user_input, '%Y-%m-%d').date()
            result = get_ocean_data_by_date(query_date)
            print(json.dumps(result, indent=2, ensure_ascii=False))
            
        except ValueError:
            print("❌ 日期格式錯誤，請使用 YYYY-MM-DD 格式")
        except KeyboardInterrupt:
            print("\n👋 再見！")
            break

if __name__ == "__main__":
    main()