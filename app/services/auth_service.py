"""
認證服務
處理 JWT 令牌生成、驗證、用戶認證等邏輯
"""

from datetime import datetime, timedelta
from typing import Optional, Union

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from passlib.context import CryptContext

from app.core.config import settings
from app.schemas.auth import TokenData
from app.schemas.user import User

# 密碼加密上下文
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# OAuth2 方案
oauth2_scheme = OAuth2PasswordBearer(tokenUrl=f"{settings.API_V1_STR}/auth/login")


class AuthService:
    """認證服務類"""
    
    @staticmethod
    def verify_password(plain_password: str, hashed_password: str) -> bool:
        """驗證密碼"""
        return pwd_context.verify(plain_password, hashed_password)
    
    @staticmethod
    def get_password_hash(password: str) -> str:
        """獲取密碼雜湊"""
        return pwd_context.hash(password)
    
    @staticmethod
    def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
        """創建存取令牌"""
        to_encode = data.copy()
        
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(minutes=15)
        
        to_encode.update({"exp": expire})
        encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
        return encoded_jwt
    
    @staticmethod
    def create_refresh_token(data: dict) -> str:
        """創建重新整理令牌"""
        to_encode = data.copy()
        expire = datetime.utcnow() + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
        to_encode.update({"exp": expire, "type": "refresh"})
        encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
        return encoded_jwt
    
    @staticmethod
    def verify_token(token: str) -> Union[str, None]:
        """驗證令牌並返回使用者郵箱"""
        try:
            payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
            email: str = payload.get("sub")
            if email is None:
                return None
            return email
        except JWTError:
            return None
    
    @staticmethod
    async def get_current_user(token: str = Depends(oauth2_scheme)) -> User:
        """獲取當前使用者"""
        credentials_exception = HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="無法驗證憑證",
            headers={"WWW-Authenticate": "Bearer"},
        )
        
        try:
            payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
            email: str = payload.get("sub")
            if email is None:
                raise credentials_exception
            token_data = TokenData(email=email)
        except JWTError:
            raise credentials_exception
        
        # 這裡應該從資料庫獲取使用者
        # user = await UserService.get_user_by_email(token_data.email)
        # if user is None:
        #     raise credentials_exception
        # return user
        
        # 暫時返回示例使用者
        return User(
            id=1,
            email=token_data.email,
            username="example_user",
            is_active=True,
            created_at=datetime.utcnow()
        )
    
    @staticmethod
    async def get_current_active_user(current_user: User = Depends(get_current_user)) -> User:
        """獲取當前活躍使用者"""
        if not current_user.is_active:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="非活躍使用者"
            )
        return current_user
    
    @staticmethod
    async def authenticate_user(email: str, password: str) -> Union[User, None]:
        """認證使用者"""
        # 這裡應該從資料庫獲取使用者並驗證密碼
        # user = await UserService.get_user_by_email(email)
        # if not user:
        #     return None
        # if not AuthService.verify_password(password, user.hashed_password):
        #     return None
        # return user
        
        # 暫時的示例認證邏輯
        if email == "admin@example.com" and password == "admin123":
            return User(
                id=1,
                email=email,
                username="admin",
                is_active=True,
                created_at=datetime.utcnow()
            )
        return None
    
    @staticmethod
    async def register_user(user_data: dict) -> User:
        """註冊新使用者"""
        # 這裡應該實作實際的使用者註冊邏輯
        # hashed_password = AuthService.get_password_hash(user_data.password)
        # user = await UserService.create_user({
        #     **user_data.dict(exclude={"password"}),
        #     "hashed_password": hashed_password
        # })
        # return user
        
        # 暫時返回示例使用者
        return User(
            id=2,
            email=user_data.get("email", "new@example.com"),
            username=user_data.get("username", "newuser"),
            is_active=True,
            created_at=datetime.utcnow()
        )