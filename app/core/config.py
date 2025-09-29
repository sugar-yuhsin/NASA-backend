"""
應用程式配置設定
使用 Pydantic Settings 管理環境變數和配置
"""

import os
from typing import List, Optional
from pydantic_settings import BaseSettings
from pydantic import Field


class Settings(BaseSettings):
    """應用程式設定類"""
    
    # 基本應用設定
    PROJECT_NAME: str = Field(default="NASA Hackathon API", description="專案名稱")
    PROJECT_DESCRIPTION: str = Field(
        default="NASA 黑客松 FastAPI 應用程式", 
        description="專案描述"
    )
    VERSION: str = Field(default="0.1.0", description="版本號")
    DEBUG: bool = Field(default=False, description="除錯模式")
    
    # 伺服器設定
    HOST: str = Field(default="0.0.0.0", description="主機位址")
    PORT: int = Field(default=8000, description="埠號")
    
    # API 設定
    API_V1_STR: str = Field(default="/api/v1", description="API v1 前綴")
    ALLOWED_HOSTS: List[str] = Field(
        default=["*"], 
        description="允許的主機列表"
    )
    
    # 安全設定
    SECRET_KEY: str = Field(
        default="your-secret-key-here-please-change-in-production",
        description="JWT 密鑰"
    )
    ALGORITHM: str = Field(default="HS256", description="JWT 演算法")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = Field(
        default=30, 
        description="存取令牌過期時間（分鐘）"
    )
    REFRESH_TOKEN_EXPIRE_DAYS: int = Field(
        default=7, 
        description="重新整理令牌過期時間（天）"
    )
    
    # 資料庫設定
    DATABASE_URL: str = Field(
        default="postgresql://user:password@localhost/dbname",
        description="資料庫連線 URL"
    )
    DATABASE_POOL_SIZE: int = Field(
        default=5, 
        description="資料庫連線池大小"
    )
    DATABASE_MAX_OVERFLOW: int = Field(
        default=10, 
        description="資料庫連線池最大溢出"
    )
    
    # Redis 設定（用於快取和工作階段）
    REDIS_URL: str = Field(
        default="redis://localhost:6379/0",
        description="Redis 連線 URL"
    )
    
    # 日誌設定
    LOG_LEVEL: str = Field(default="INFO", description="日誌等級")
    LOG_FORMAT: str = Field(
        default="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        description="日誌格式"
    )
    
    # 檔案上傳設定
    MAX_FILE_SIZE: int = Field(
        default=10 * 1024 * 1024,  # 10MB
        description="最大檔案大小（位元組）"
    )
    UPLOAD_DIR: str = Field(
        default="uploads",
        description="上傳目錄"
    )
    
    # 郵件設定
    SMTP_HOST: Optional[str] = Field(default=None, description="SMTP 主機")
    SMTP_PORT: Optional[int] = Field(default=587, description="SMTP 埠")
    SMTP_USERNAME: Optional[str] = Field(default=None, description="SMTP 使用者名稱")
    SMTP_PASSWORD: Optional[str] = Field(default=None, description="SMTP 密碼")
    EMAIL_FROM: Optional[str] = Field(default=None, description="寄件者郵箱")
    
    # 外部 API 設定
    NASA_API_KEY: Optional[str] = Field(default=None, description="NASA API 金鑰")
    NASA_API_BASE_URL: str = Field(
        default="https://api.nasa.gov",
        description="NASA API 基本 URL"
    )
    
    # 監控設定
    ENABLE_METRICS: bool = Field(default=True, description="啟用指標收集")
    METRICS_PORT: int = Field(default=9090, description="指標埠")
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = True


# 創建全域設定實例
settings = Settings()


def get_database_url() -> str:
    """獲取資料庫連線 URL"""
    return settings.DATABASE_URL


def get_cors_origins() -> List[str]:
    """獲取 CORS 允許的源"""
    if settings.DEBUG:
        # 開發模式允許所有來源
        return ["*"]
    return settings.ALLOWED_HOSTS


def is_production() -> bool:
    """檢查是否為生產環境"""
    return not settings.DEBUG and os.getenv("ENVIRONMENT") == "production"


def get_log_config() -> dict:
    """獲取日誌配置"""
    return {
        "version": 1,
        "disable_existing_loggers": False,
        "formatters": {
            "default": {
                "format": settings.LOG_FORMAT,
            },
        },
        "handlers": {
            "default": {
                "formatter": "default",
                "class": "logging.StreamHandler",
                "stream": "ext://sys.stdout",
            },
        },
        "root": {
            "level": settings.LOG_LEVEL,
            "handlers": ["default"],
        },
    }