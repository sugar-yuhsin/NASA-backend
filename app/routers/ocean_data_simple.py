"""
簡化版海洋數據路由
直接使用 CSV 模組，避免 pandas 依賴問題
"""

from fastapi import APIRouter, HTTPException
import csv
from datetime import datetime, date
from typing import Dict, Optional

router = APIRouter()

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
    csv_file = "merged_shark_ocean_data.csv"
    
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
                "data_count": 0,
                "records": [],
                "summary": {
                    "shark_count": 0,
                    "no_shark_count": 0,
                    "total_records": 0,
                    "shark_presence_rate": 0.0,
                    "averages": {
                        "sst_value": None,
                        "chl_value": None,
                        "ssha_value": None,
                        "longitude": None,
                        "latitude": None
                    }
                },
                "message": "該日期無數據"
            }
        
        # 計算平均值
        sst_values = [safe_float(record['SST_Value']) for record in matching_records]
        chl_values = [safe_float(record['CHL_Concentration']) for record in matching_records]  # 新檔案用 CHL_Concentration
        ssha_values = [safe_float(record['SSHA_Value']) for record in matching_records]
        longitude_values = [safe_float(record['Longitude']) for record in matching_records]
        latitude_values = [safe_float(record['Latitude']) for record in matching_records]
        has_shark_values = [int(record['has_shark']) for record in matching_records]  # 新增：鯊魚標籤
        
        # 過濾 None 值
        sst_values = [v for v in sst_values if v is not None]
        chl_values = [v for v in chl_values if v is not None]
        ssha_values = [v for v in ssha_values if v is not None]
        longitude_values = [v for v in longitude_values if v is not None]
        latitude_values = [v for v in latitude_values if v is not None]
        
        avg_sst = sum(sst_values) / len(sst_values) if sst_values else None
        avg_chl = sum(chl_values) / len(chl_values) if chl_values else None
        avg_ssha = sum(ssha_values) / len(ssha_values) if ssha_values else None
        avg_longitude = sum(longitude_values) / len(longitude_values) if longitude_values else None
        avg_latitude = sum(latitude_values) / len(latitude_values) if latitude_values else None
        
        # 處理所有記錄，返回完整數據
        processed_records = []
        for record in matching_records:
            processed_record = {
                "longitude": safe_float(record['Longitude']),
                "latitude": safe_float(record['Latitude']),
                "sst_value": safe_float(record['SST_Value']),
                "chl_value": safe_float(record['CHL_Concentration']),
                "ssha_value": safe_float(record['SSHA_Value']),
                "has_shark": bool(int(record['has_shark'])),
                "individual_id": record.get('Individual_ID', ''),
                "sst_gradient": safe_float(record.get('SST_Gradient', 0)),
                "chl_gradient": safe_float(record.get('CHL_Gradient', 0)),
                "ssha_gradient": safe_float(record.get('SSHA_Gradient', 0)),
                "thermal_front_strength": safe_float(record.get('Thermal_Front_Strength', 0)),
                "productivity_index": safe_float(record.get('Productivity_Index', 0)),
                "is_in_eddy": record.get('is_in_eddy', 'False').lower() == 'true',
                "eddy_type": record.get('eddy_type', 'none'),
                "daily_movement_km": safe_float(record.get('Daily_Movement_km', 0))
            }
            processed_records.append(processed_record)
        
        # 計算摘要統計
        shark_records = [r for r in processed_records if r['has_shark']]
        no_shark_records = [r for r in processed_records if not r['has_shark']]
        shark_presence_rate = len(shark_records) / len(processed_records)
        
        return {
            "date": str(target_date),
            "data_count": len(processed_records),
            "records": processed_records,  # 所有記錄
            "summary": {
                "shark_count": len(shark_records),
                "no_shark_count": len(no_shark_records),
                "total_records": len(processed_records),
                "shark_presence_rate": round(shark_presence_rate, 6),
                "averages": {
                    "sst_value": round(avg_sst, 6) if avg_sst is not None else None,
                    "chl_value": round(avg_chl, 6) if avg_chl is not None else None,
                    "ssha_value": round(avg_ssha, 6) if avg_ssha is not None else None,
                    "longitude": round(avg_longitude, 6) if avg_longitude is not None else None,
                    "latitude": round(avg_latitude, 6) if avg_latitude is not None else None
                }
            },
            "message": "查詢成功"
        }
        
    except FileNotFoundError:
        return {
            "date": str(target_date),
            "data_count": 0,
            "records": [],
            "summary": {
                "shark_count": 0,
                "no_shark_count": 0,
                "total_records": 0,
                "shark_presence_rate": 0.0,
                "averages": {
                    "sst_value": None,
                    "chl_value": None,
                    "ssha_value": None,
                    "longitude": None,
                    "latitude": None
                }
            },
            "error": "CSV 檔案不存在"
        }
    except Exception as e:
        return {
            "date": str(target_date),
            "data_count": 0,
            "records": [],
            "summary": {
                "shark_count": 0,
                "no_shark_count": 0,
                "total_records": 0,
                "shark_presence_rate": 0.0,
                "averages": {
                    "sst_value": None,
                    "chl_value": None,
                    "ssha_value": None,
                    "longitude": None,
                    "latitude": None
                }
            },
            "error": f"讀取數據失敗: {str(e)}"
        }

@router.get("/date/{target_date}")
async def get_ocean_data_by_date_simple(target_date: str):
    """
    根據日期獲取該日期的所有海洋數據記錄 (簡化版，無需認證)
    
    - **target_date**: 日期 (格式: YYYY-MM-DD, 例如 2014-07-10)
    
    返回該日期的所有記錄，包含:
    - records: 所有該日期的記錄列表，每筆記錄包含：
        - sst_value: 海表溫度值
        - chl_value: 葉綠素濃度值  
        - ssha_value: 海面高度異常值
        - longitude: 經度
        - latitude: 緯度
        - has_shark: 是否有鯊魚 (boolean)
        - individual_id: 個體ID
        - 其他環境參數...
    - summary: 摘要統計
        - shark_count: 有鯊魚的記錄數
        - no_shark_count: 無鯊魚的記錄數
        - shark_presence_rate: 鯊魚出現率
        - averages: 各參數平均值
    """
    try:
        # 解析日期
        query_date = datetime.strptime(target_date, '%Y-%m-%d').date()
        
        # 獲取數據
        result = get_ocean_data_by_date(query_date)
        
        if "error" in result:
            raise HTTPException(status_code=500, detail=result["error"])
        
        return result
        
    except ValueError:
        raise HTTPException(
            status_code=400, 
            detail="日期格式錯誤，請使用 YYYY-MM-DD 格式，例如: 2014-07-10"
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"伺服器錯誤: {str(e)}")

@router.post("/date")
async def get_ocean_data_post_simple(request: dict):
    """
    通過 POST 請求獲取海洋數據 (簡化版，無需認證)
    
    請求體範例:
    ```json
    {
        "date": "2014-07-10"
    }
    ```
    """
    try:
        if "date" not in request:
            raise HTTPException(status_code=400, detail="請求中缺少 'date' 欄位")
        
        # 解析日期
        query_date = datetime.strptime(request["date"], '%Y-%m-%d').date()
        
        # 獲取數據
        result = get_ocean_data_by_date(query_date)
        
        if "error" in result:
            raise HTTPException(status_code=500, detail=result["error"])
        
        return result
        
    except ValueError:
        raise HTTPException(
            status_code=400, 
            detail="日期格式錯誤，請使用 YYYY-MM-DD 格式，例如: 2014-07-10"
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"伺服器錯誤: {str(e)}")

@router.get("/available-dates")
async def get_available_dates_simple():
    """獲取前 20 個可用日期 (簡化版，無需認證)"""
    csv_file = "comprehensive_shark_ocean_features - comprehensive_shark_ocean_features.csv"
    dates = set()
    
    try:
        with open(csv_file, 'r', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            
            for row in reader:
                if len(dates) >= 20:
                    break
                dates.add(row['Date'])
        
        return {
            "available_dates": sorted(list(dates)),
            "total_count": len(dates),
            "message": "可用日期列表 (前20個)"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"讀取可用日期失敗: {str(e)}")