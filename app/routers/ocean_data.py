"""
海洋數據路由
處理鯊魚海洋特徵數據的 API 端點
"""

from fastapi import APIRouter, HTTPException, status, Query, Depends
from typing import List, Optional
from datetime import date, datetime

from app.schemas.ocean_data import (
    OceanDataRequest,
    OceanDataResponse, 
    OceanDataDetail,
    OceanDataSummary,
    DateRangeRequest,
    OceanDataListResponse
)
from app.services.ocean_data_service import ocean_data_service
from app.schemas.user import User
from app.services.auth_service import AuthService

router = APIRouter()


@router.get("/date/{target_date}", response_model=OceanDataResponse)
async def get_ocean_data_by_date(
    target_date: date,
    current_user: User = Depends(AuthService.get_current_user)
):
    """根據日期獲取海洋數據 (SST, CHL, SSHA 的平均值)"""
    try:
        result = ocean_data_service.get_data_by_date(target_date)
        
        if result is None:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="海洋數據服務不可用"
            )
        
        return result
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"獲取海洋數據失敗: {str(e)}"
        )


@router.post("/date", response_model=OceanDataResponse)
async def get_ocean_data_by_date_post(
    request: OceanDataRequest,
    current_user: User = Depends(AuthService.get_current_user)
):
    """通過 POST 請求根據日期獲取海洋數據"""
    try:
        result = ocean_data_service.get_data_by_date(request.date)
        
        if result is None:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="海洋數據服務不可用"
            )
        
        return result
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"獲取海洋數據失敗: {str(e)}"
        )


@router.get("/date/{target_date}/details", response_model=List[OceanDataDetail])
async def get_detailed_ocean_data_by_date(
    target_date: date,
    current_user: User = Depends(AuthService.get_current_user)
):
    """獲取指定日期的詳細海洋數據（所有記錄）"""
    try:
        result = ocean_data_service.get_detailed_data_by_date(target_date)
        return result
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"獲取詳細海洋數據失敗: {str(e)}"
        )


@router.get("/date/{target_date}/summary", response_model=OceanDataSummary)
async def get_ocean_data_summary_by_date(
    target_date: date,
    current_user: User = Depends(AuthService.get_current_user)
):
    """獲取指定日期的海洋數據統計摘要"""
    try:
        result = ocean_data_service.get_data_summary_by_date(target_date)
        
        if result is None:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="海洋數據服務不可用"
            )
        
        return result
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"獲取海洋數據摘要失敗: {str(e)}"
        )


@router.get("/range", response_model=OceanDataListResponse)
async def get_ocean_data_by_date_range(
    start_date: date = Query(..., description="開始日期"),
    end_date: date = Query(..., description="結束日期"),
    current_user: User = Depends(AuthService.get_current_user)
):
    """獲取日期範圍內的海洋數據"""
    try:
        if start_date > end_date:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="開始日期不能晚於結束日期"
            )
        
        result = ocean_data_service.get_data_by_date_range(start_date, end_date)
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"獲取日期範圍海洋數據失敗: {str(e)}"
        )


@router.post("/range", response_model=OceanDataListResponse)
async def get_ocean_data_by_date_range_post(
    request: DateRangeRequest,
    current_user: User = Depends(AuthService.get_current_user)
):
    """通過 POST 請求獲取日期範圍內的海洋數據"""
    try:
        result = ocean_data_service.get_data_by_date_range(request.start_date, request.end_date)
        return result
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"獲取日期範圍海洋數據失敗: {str(e)}"
        )


@router.get("/dates", response_model=List[date])
async def get_available_dates(
    current_user: User = Depends(AuthService.get_current_user)
):
    """獲取所有可用的日期列表"""
    try:
        result = ocean_data_service.get_available_dates()
        return result
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"獲取可用日期失敗: {str(e)}"
        )


@router.post("/reload")
async def reload_ocean_data(
    current_user: User = Depends(AuthService.get_current_user)
):
    """重新載入海洋數據"""
    try:
        ocean_data_service.reload_data()
        return {"message": "海洋數據重新載入成功"}
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"重新載入海洋數據失敗: {str(e)}"
        )


# 不需要認證的端點（用於快速測試）
@router.get("/public/date/{target_date}", response_model=OceanDataResponse)
async def get_ocean_data_public(target_date: date):
    """公開端點：根據日期獲取海洋數據（不需要認證）"""
    try:
        result = ocean_data_service.get_data_by_date(target_date)
        
        if result is None:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="海洋數據服務不可用"
            )
        
        return result
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"獲取海洋數據失敗: {str(e)}"
        )