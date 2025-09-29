"""
項目管理路由
處理項目相關的 CRUD 操作
"""

from fastapi import APIRouter, Depends, HTTPException, status, Query
from typing import List, Optional

from app.schemas.item import Item, ItemCreate, ItemUpdate
from app.schemas.user import User
from app.services.auth_service import AuthService

router = APIRouter()


@router.get("/", response_model=List[Item])
async def get_items(
    skip: int = Query(0, ge=0, description="跳過的項目數"),
    limit: int = Query(100, ge=1, le=1000, description="返回的項目數"),
    search: Optional[str] = Query(None, description="搜索關鍵字"),
    current_user: User = Depends(AuthService.get_current_user)
):
    """獲取項目列表"""
    # items = await ItemService.get_items(skip=skip, limit=limit, search=search)
    # return items
    
    # 暫時返回示例數據
    return [
        {
            "id": 1,
            "title": "NASA 月球探測項目",
            "description": "研究月球地質結構和資源分布",
            "is_active": True,
            "owner_id": current_user.id if hasattr(current_user, 'id') else 1,
            "created_at": "2024-01-01T00:00:00Z",
            "updated_at": "2024-01-01T00:00:00Z"
        },
        {
            "id": 2,
            "title": "火星殖民地規劃",
            "description": "設計未來火星殖民地的基礎設施",
            "is_active": True,
            "owner_id": current_user.id if hasattr(current_user, 'id') else 1,
            "created_at": "2024-01-02T00:00:00Z",
            "updated_at": "2024-01-02T00:00:00Z"
        }
    ]


@router.get("/{item_id}", response_model=Item)
async def get_item(
    item_id: int,
    current_user: User = Depends(AuthService.get_current_user)
):
    """根據 ID 獲取項目"""
    # item = await ItemService.get_item(item_id)
    # if not item:
    #     raise HTTPException(
    #         status_code=status.HTTP_404_NOT_FOUND,
    #         detail="項目不存在"
    #     )
    # return item
    
    # 暫時返回示例數據
    if item_id == 1:
        return {
            "id": 1,
            "title": "NASA 月球探測項目",
            "description": "研究月球地質結構和資源分布",
            "is_active": True,
            "owner_id": current_user.id if hasattr(current_user, 'id') else 1,
            "created_at": "2024-01-01T00:00:00Z",
            "updated_at": "2024-01-01T00:00:00Z"
        }
    else:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="項目不存在"
        )


@router.post("/", response_model=Item, status_code=status.HTTP_201_CREATED)
async def create_item(
    item_data: ItemCreate,
    current_user: User = Depends(AuthService.get_current_user)
):
    """創建新項目"""
    try:
        # item = await ItemService.create_item(item_data, current_user.id)
        # return item
        
        # 暫時返回示例數據
        return {
            "id": 3,
            "title": item_data.title,
            "description": item_data.description,
            "is_active": True,
            "owner_id": current_user.id if hasattr(current_user, 'id') else 1,
            "created_at": "2024-01-01T00:00:00Z",
            "updated_at": "2024-01-01T00:00:00Z"
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"創建項目失敗: {str(e)}"
        )


@router.put("/{item_id}", response_model=Item)
async def update_item(
    item_id: int,
    item_data: ItemUpdate,
    current_user: User = Depends(AuthService.get_current_user)
):
    """更新項目信息"""
    try:
        # item = await ItemService.update_item(item_id, item_data, current_user.id)
        # if not item:
        #     raise HTTPException(
        #         status_code=status.HTTP_404_NOT_FOUND,
        #         detail="項目不存在或無權限修改"
        #     )
        # return item
        
        # 暫時返回示例數據
        return {
            "id": item_id,
            "title": item_data.title or "更新後的項目",
            "description": item_data.description or "更新後的描述",
            "is_active": item_data.is_active if item_data.is_active is not None else True,
            "owner_id": current_user.id if hasattr(current_user, 'id') else 1,
            "created_at": "2024-01-01T00:00:00Z",
            "updated_at": "2024-01-01T00:00:00Z"
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"更新項目失敗: {str(e)}"
        )


@router.delete("/{item_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_item(
    item_id: int,
    current_user: User = Depends(AuthService.get_current_user)
):
    """刪除項目"""
    # success = await ItemService.delete_item(item_id, current_user.id)
    # if not success:
    #     raise HTTPException(
    #         status_code=status.HTTP_404_NOT_FOUND,
    #         detail="項目不存在或無權限刪除"
    #     )
    
    # 暫時不做任何操作
    pass