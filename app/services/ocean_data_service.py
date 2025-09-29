"""
海洋數據服務
處理 CSV 檔案讀取和數據查詢邏輯
"""

import pandas as pd
import numpy as np
from datetime import date, datetime
from typing import List, Optional, Dict, Any
from pathlib import Path

from app.schemas.ocean_data import (
    OceanDataResponse, 
    OceanDataDetail, 
    OceanDataSummary,
    OceanDataListResponse
)


class OceanDataService:
    """海洋數據服務類"""
    
    def __init__(self):
        self.csv_file_path = "comprehensive_shark_ocean_features - comprehensive_shark_ocean_features.csv"
        self._data_cache = None
        self._load_data()
    
    def _load_data(self):
        """載入 CSV 數據"""
        try:
            if Path(self.csv_file_path).exists():
                self._data_cache = pd.read_csv(self.csv_file_path)
                # 轉換日期欄位
                self._data_cache['Date'] = pd.to_datetime(self._data_cache['Date']).dt.date
                print(f"✅ 成功載入 {len(self._data_cache)} 筆海洋數據")
            else:
                print(f"⚠️ CSV 檔案不存在: {self.csv_file_path}")
                self._data_cache = pd.DataFrame()
        except Exception as e:
            print(f"❌ 載入 CSV 檔案失敗: {e}")
            self._data_cache = pd.DataFrame()
    
    def get_data_by_date(self, query_date: date) -> Optional[OceanDataResponse]:
        """根據日期獲取海洋數據"""
        if self._data_cache.empty:
            return None
        
        # 篩選指定日期的數據
        filtered_data = self._data_cache[self._data_cache['Date'] == query_date]
        
        if filtered_data.empty:
            return OceanDataResponse(
                date=query_date,
                sst_value=None,
                chl_value=None,
                ssha_value=None,
                data_count=0
            )
        
        # 計算平均值（如果有多筆記錄）
        avg_sst = filtered_data['SST_Value'].mean() if not filtered_data['SST_Value'].isna().all() else None
        avg_chl = filtered_data['CHL_Value'].mean() if not filtered_data['CHL_Value'].isna().all() else None  
        avg_ssha = filtered_data['SSHA_Value'].mean() if not filtered_data['SSHA_Value'].isna().all() else None
        
        return OceanDataResponse(
            date=query_date,
            sst_value=round(avg_sst, 6) if avg_sst is not None else None,
            chl_value=round(avg_chl, 6) if avg_chl is not None else None,
            ssha_value=round(avg_ssha, 6) if avg_ssha is not None else None,
            data_count=len(filtered_data)
        )
    
    def get_detailed_data_by_date(self, query_date: date) -> List[OceanDataDetail]:
        """獲取指定日期的詳細數據"""
        if self._data_cache.empty:
            return []
        
        filtered_data = self._data_cache[self._data_cache['Date'] == query_date]
        
        result = []
        for _, row in filtered_data.iterrows():
            detail = OceanDataDetail(
                date=row['Date'],
                longitude=self._safe_float(row['Longitude']),
                latitude=self._safe_float(row['Latitude']),
                individual_id=self._safe_int(row['Individual_ID']),
                sst_value=self._safe_float(row['SST_Value']),
                sst_gradient=self._safe_float(row['SST_Gradient']),
                thermal_front_strength=self._safe_float(row['Thermal_Front_Strength']),
                chl_value=self._safe_float(row['CHL_Value']),
                chl_gradient=self._safe_float(row['CHL_Gradient']),
                productivity_index=self._safe_float(row['Productivity_Index']),
                ssha_value=self._safe_float(row['SSHA_Value']),
                ssha_gradient=self._safe_float(row['SSHA_Gradient']),
                is_in_eddy=self._safe_bool(row['is_in_eddy']),
                eddy_type=str(row['eddy_type']) if pd.notna(row['eddy_type']) else None,
                dist_to_eddy_center_km=self._safe_float(row['dist_to_eddy_center_km']),
                daily_movement_km=self._safe_float(row['Daily_Movement_km']),
                ocean_complexity_score=self._safe_float(row['Ocean_Complexity_Score'])
            )
            result.append(detail)
        
        return result
    
    def get_data_summary_by_date(self, query_date: date) -> Optional[OceanDataSummary]:
        """獲取指定日期的數據統計摘要"""
        if self._data_cache.empty:
            return None
        
        filtered_data = self._data_cache[self._data_cache['Date'] == query_date]
        
        if filtered_data.empty:
            return OceanDataSummary(
                date=query_date,
                record_count=0,
                avg_sst_value=None,
                avg_chl_value=None,
                avg_ssha_value=None,
                min_sst_value=None,
                max_sst_value=None,
                min_chl_value=None,
                max_chl_value=None,
                min_ssha_value=None,
                max_ssha_value=None
            )
        
        return OceanDataSummary(
            date=query_date,
            record_count=len(filtered_data),
            avg_sst_value=self._safe_float(filtered_data['SST_Value'].mean()),
            avg_chl_value=self._safe_float(filtered_data['CHL_Value'].mean()),
            avg_ssha_value=self._safe_float(filtered_data['SSHA_Value'].mean()),
            min_sst_value=self._safe_float(filtered_data['SST_Value'].min()),
            max_sst_value=self._safe_float(filtered_data['SST_Value'].max()),
            min_chl_value=self._safe_float(filtered_data['CHL_Value'].min()),
            max_chl_value=self._safe_float(filtered_data['CHL_Value'].max()),
            min_ssha_value=self._safe_float(filtered_data['SSHA_Value'].min()),
            max_ssha_value=self._safe_float(filtered_data['SSHA_Value'].max())
        )
    
    def get_data_by_date_range(self, start_date: date, end_date: date) -> OceanDataListResponse:
        """獲取日期範圍內的數據"""
        if self._data_cache.empty:
            return OceanDataListResponse(
                total_records=0,
                date_range=f"{start_date} 到 {end_date}",
                data=[]
            )
        
        # 篩選日期範圍
        filtered_data = self._data_cache[
            (self._data_cache['Date'] >= start_date) & 
            (self._data_cache['Date'] <= end_date)
        ]
        
        # 按日期分組並計算每日平均值
        daily_data = []
        unique_dates = sorted(filtered_data['Date'].unique())
        
        for date_item in unique_dates:
            daily_filtered = filtered_data[filtered_data['Date'] == date_item]
            
            avg_sst = daily_filtered['SST_Value'].mean() if not daily_filtered['SST_Value'].isna().all() else None
            avg_chl = daily_filtered['CHL_Value'].mean() if not daily_filtered['CHL_Value'].isna().all() else None
            avg_ssha = daily_filtered['SSHA_Value'].mean() if not daily_filtered['SSHA_Value'].isna().all() else None
            
            daily_data.append(OceanDataResponse(
                date=date_item,
                sst_value=round(avg_sst, 6) if avg_sst is not None else None,
                chl_value=round(avg_chl, 6) if avg_chl is not None else None,
                ssha_value=round(avg_ssha, 6) if avg_ssha is not None else None,
                data_count=len(daily_filtered)
            ))
        
        return OceanDataListResponse(
            total_records=len(filtered_data),
            date_range=f"{start_date} 到 {end_date}",
            data=daily_data
        )
    
    def get_available_dates(self) -> List[date]:
        """獲取所有可用的日期"""
        if self._data_cache.empty:
            return []
        
        return sorted(self._data_cache['Date'].unique())
    
    def reload_data(self):
        """重新載入數據"""
        self._load_data()
    
    def _safe_float(self, value) -> Optional[float]:
        """安全轉換為浮點數"""
        try:
            if pd.isna(value):
                return None
            return float(value)
        except (ValueError, TypeError):
            return None
    
    def _safe_int(self, value) -> Optional[int]:
        """安全轉換為整數"""
        try:
            if pd.isna(value):
                return None
            return int(value)
        except (ValueError, TypeError):
            return None
    
    def _safe_bool(self, value) -> Optional[bool]:
        """安全轉換為布林值"""
        try:
            if pd.isna(value):
                return None
            if isinstance(value, str):
                return value.upper() in ['TRUE', '1', 'YES']
            return bool(value)
        except (ValueError, TypeError):
            return None


# 創建全域服務實例
ocean_data_service = OceanDataService()