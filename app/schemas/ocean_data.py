"""
海洋數據相關的 Pydantic 模型
用於鯊魚海洋特徵數據的 API 請求和響應
"""

from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import date


class OceanDataRequest(BaseModel):
    """海洋數據查詢請求模型"""
    date: date = Field(..., description="查詢的日期 (YYYY-MM-DD)")


class OceanDataResponse(BaseModel):
    """海洋數據響應模型"""
    date: date = Field(..., description="日期")
    sst_value: Optional[float] = Field(None, description="海表溫度值")
    chl_value: Optional[float] = Field(None, description="葉綠素值") 
    ssha_value: Optional[float] = Field(None, description="海面高度異常值")
    data_count: int = Field(..., description="該日期的數據筆數")


class OceanDataDetail(BaseModel):
    """詳細的海洋數據模型（包含所有欄位）"""
    date: date = Field(..., description="日期")
    longitude: Optional[float] = Field(None, description="經度")
    latitude: Optional[float] = Field(None, description="緯度")
    individual_id: Optional[int] = Field(None, description="個體ID")
    sst_value: Optional[float] = Field(None, description="海表溫度值")
    sst_gradient: Optional[float] = Field(None, description="海表溫度梯度")
    thermal_front_strength: Optional[float] = Field(None, description="溫度鋒面強度")
    chl_value: Optional[float] = Field(None, description="葉綠素值")
    chl_gradient: Optional[float] = Field(None, description="葉綠素梯度")
    productivity_index: Optional[float] = Field(None, description="生產力指數")
    ssha_value: Optional[float] = Field(None, description="海面高度異常值")
    ssha_gradient: Optional[float] = Field(None, description="海面高度異常梯度")
    is_in_eddy: Optional[bool] = Field(None, description="是否在渦流中")
    eddy_type: Optional[str] = Field(None, description="渦流類型")
    dist_to_eddy_center_km: Optional[float] = Field(None, description="到渦流中心距離(公里)")
    daily_movement_km: Optional[float] = Field(None, description="日移動距離(公里)")
    ocean_complexity_score: Optional[float] = Field(None, description="海洋複雜度評分")


class OceanDataSummary(BaseModel):
    """海洋數據統計摘要"""
    date: date = Field(..., description="日期")
    record_count: int = Field(..., description="記錄數量")
    avg_sst_value: Optional[float] = Field(None, description="平均海表溫度")
    avg_chl_value: Optional[float] = Field(None, description="平均葉綠素值")
    avg_ssha_value: Optional[float] = Field(None, description="平均海面高度異常值")
    min_sst_value: Optional[float] = Field(None, description="最小海表溫度")
    max_sst_value: Optional[float] = Field(None, description="最大海表溫度")
    min_chl_value: Optional[float] = Field(None, description="最小葉綠素值") 
    max_chl_value: Optional[float] = Field(None, description="最大葉綠素值")
    min_ssha_value: Optional[float] = Field(None, description="最小海面高度異常值")
    max_ssha_value: Optional[float] = Field(None, description="最大海面高度異常值")


class DateRangeRequest(BaseModel):
    """日期範圍查詢請求"""
    start_date: date = Field(..., description="開始日期")
    end_date: date = Field(..., description="結束日期")
    
    def model_post_init(self, __context):
        """驗證日期範圍"""
        if self.start_date > self.end_date:
            raise ValueError("開始日期不能晚於結束日期")


class OceanDataListResponse(BaseModel):
    """海洋數據列表響應"""
    total_records: int = Field(..., description="總記錄數")
    date_range: str = Field(..., description="日期範圍")
    data: List[OceanDataResponse] = Field(..., description="數據列表")