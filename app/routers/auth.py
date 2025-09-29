"""
認證相關路由
處理用戶登入、註冊、JWT 令牌管理等
"""

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from datetime import timedelta

from app.schemas.auth import Token, UserLogin, UserRegister
from app.schemas.user import User, UserCreate
from app.core.config import settings
from app.services.auth_service import AuthService

router = APIRouter()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


@router.post("/register", response_model=User, status_code=status.HTTP_201_CREATED)
async def register(user_data: UserRegister):
    """用戶註冊"""
    try:
        # 這裡應該調用實際的用戶服務
        # user = await AuthService.register_user(user_data)
        # return user
        
        # 暫時返回示例數據
        return {
            "id": 1,
            "email": user_data.email,
            "username": user_data.username,
            "is_active": True,
            "created_at": "2024-01-01T00:00:00Z"
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"註冊失敗: {str(e)}"
        )


@router.post("/login", response_model=Token)
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    """用戶登入"""
    try:
        # 這裡應該調用實際的認證服務
        # user = await AuthService.authenticate_user(form_data.username, form_data.password)
        # if not user:
        #     raise HTTPException(
        #         status_code=status.HTTP_401_UNAUTHORIZED,
        #         detail="用戶名或密碼錯誤",
        #         headers={"WWW-Authenticate": "Bearer"},
        #     )
        
        # access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        # access_token = AuthService.create_access_token(
        #     data={"sub": user.email}, expires_delta=access_token_expires
        # )
        
        # 暫時返回示例令牌
        return {
            "access_token": "example_jwt_token",
            "token_type": "bearer"
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"登入失敗: {str(e)}",
            headers={"WWW-Authenticate": "Bearer"},
        )


@router.post("/refresh", response_model=Token)
async def refresh_token(current_user: User = Depends(AuthService.get_current_user)):
    """刷新訪問令牌"""
    try:
        # access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        # access_token = AuthService.create_access_token(
        #     data={"sub": current_user.email}, expires_delta=access_token_expires
        # )
        
        # 暫時返回示例令牌
        return {
            "access_token": "refreshed_jwt_token",
            "token_type": "bearer"
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"令牌刷新失敗: {str(e)}",
            headers={"WWW-Authenticate": "Bearer"},
        )


@router.get("/me", response_model=User)
async def get_current_user_info(current_user: User = Depends(AuthService.get_current_user)):
    """獲取當前用戶信息"""
    return current_user


@router.post("/logout")
async def logout(current_user: User = Depends(AuthService.get_current_user)):
    """用戶登出"""
    # 在實際應用中，你可能需要將令牌加入黑名單
    return {"message": "登出成功"}