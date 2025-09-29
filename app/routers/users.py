"""
用戶管理路由
處理用戶 CRUD 操作
"""

from fastapi import APIRouter, Depends, HTTPException, status, Query
from typing import List, Optional

from app.schemas.user import User, UserCreate, UserUpdate
from app.services.auth_service import AuthService

router = APIRouter()


@router.get("/", response_model=List[User])
async def get_users(
    skip: int = Query(0, ge=0, description="跳過的項目數"),
    limit: int = Query(100, ge=1, le=1000, description="返回的項目數"),
    current_user: User = Depends(AuthService.get_current_user)
):
    """獲取用戶列表"""
    # 這裡應該調用實際的用戶服務
    # users = await UserService.get_users(skip=skip, limit=limit)
    # return users
    
    # 暫時返回示例數據
    return [
        {
            "id": 1,
            "email": "user1@example.com",
            "username": "user1",
            "is_active": True,
            "created_at": "2024-01-01T00:00:00Z"
        },
        {
            "id": 2,
            "email": "user2@example.com", 
            "username": "user2",
            "is_active": True,
            "created_at": "2024-01-02T00:00:00Z"
        }
    ]


@router.get("/{user_id}", response_model=User)
async def get_user(
    user_id: int,
    current_user: User = Depends(AuthService.get_current_user)
):
    """根據 ID 獲取用戶"""
    # user = await UserService.get_user(user_id)
    # if not user:
    #     raise HTTPException(
    #         status_code=status.HTTP_404_NOT_FOUND,
    #         detail="用戶不存在"
    #     )
    # return user
    
    # 暫時返回示例數據
    if user_id == 1:
        return {
            "id": 1,
            "email": "user1@example.com",
            "username": "user1",
            "is_active": True,
            "created_at": "2024-01-01T00:00:00Z"
        }
    else:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="用戶不存在"
        )


@router.post("/", response_model=User, status_code=status.HTTP_201_CREATED)
async def create_user(
    user_data: UserCreate,
    current_user: User = Depends(AuthService.get_current_user)
):
    """創建新用戶"""
    try:
        # user = await UserService.create_user(user_data)
        # return user
        
        # 暫時返回示例數據
        return {
            "id": 3,
            "email": user_data.email,
            "username": user_data.username,
            "is_active": True,
            "created_at": "2024-01-01T00:00:00Z"
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"創建用戶失敗: {str(e)}"
        )


@router.put("/{user_id}", response_model=User)
async def update_user(
    user_id: int,
    user_data: UserUpdate,
    current_user: User = Depends(AuthService.get_current_user)
):
    """更新用戶信息"""
    try:
        # user = await UserService.update_user(user_id, user_data)
        # if not user:
        #     raise HTTPException(
        #         status_code=status.HTTP_404_NOT_FOUND,
        #         detail="用戶不存在"
        #     )
        # return user
        
        # 暫時返回示例數據
        return {
            "id": user_id,
            "email": user_data.email or "updated@example.com",
            "username": user_data.username or "updated_user",
            "is_active": True,
            "created_at": "2024-01-01T00:00:00Z"
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"更新用戶失敗: {str(e)}"
        )


@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user(
    user_id: int,
    current_user: User = Depends(AuthService.get_current_user)
):
    """刪除用戶"""
    # success = await UserService.delete_user(user_id)
    # if not success:
    #     raise HTTPException(
    #         status_code=status.HTTP_404_NOT_FOUND,
    #         detail="用戶不存在"
    #     )
    
    # 暫時不做任何操作
    pass