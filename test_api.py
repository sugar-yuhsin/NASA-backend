"""
測試簡化版海洋數據 API
"""

import requests
import json
from datetime import date

def test_api():
    base_url = "http://localhost:8000"
    
    print("🧪 測試海洋數據 API")
    print("=" * 50)
    
    # 測試根端點
    try:
        response = requests.get(f"{base_url}/")
        print(f"根端點: {response.status_code}")
        print(json.dumps(response.json(), indent=2, ensure_ascii=False))
    except Exception as e:
        print(f"❌ 根端點測試失敗: {e}")
    
    print("\n" + "-" * 30)
    
    # 測試海洋數據查詢
    test_dates = ["2014-07-10", "2014-07-15", "2014-08-01"]
    
    for test_date in test_dates:
        try:
            response = requests.get(f"{base_url}/ocean-data/{test_date}")
            print(f"\n📅 日期 {test_date}: {response.status_code}")
            print(json.dumps(response.json(), indent=2, ensure_ascii=False))
        except Exception as e:
            print(f"❌ 日期 {test_date} 測試失敗: {e}")
    
    print("\n" + "-" * 30)
    
    # 測試 POST 方式
    try:
        post_data = {"date": "2014-07-10"}
        response = requests.post(f"{base_url}/ocean-data", json=post_data)
        print(f"\nPOST 方式: {response.status_code}")
        print(json.dumps(response.json(), indent=2, ensure_ascii=False))
    except Exception as e:
        print(f"❌ POST 測試失敗: {e}")
    
    print("\n" + "-" * 30)
    
    # 測試可用日期
    try:
        response = requests.get(f"{base_url}/available-dates")
        print(f"\n可用日期: {response.status_code}")
        data = response.json()
        print(f"前 5 個日期: {data['available_dates'][:5]}")
        print(f"總計: {data['total_count']} 個日期")
    except Exception as e:
        print(f"❌ 可用日期測試失敗: {e}")

if __name__ == "__main__":
    test_api()