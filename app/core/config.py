"""
簡化的應用程式配置設定
只保留必要的設定
"""

import os
from typing import List
from pydantic_settings import BaseSettings
from pydantic import Field


class Settings(BaseSettings):
    """簡化的應用程式設定類"""
    
    # 基本應用設定
    PROJECT_NAME: str = Field(default="NASA 海洋數據與ML預測 API", description="專案名稱")
    PROJECT_DESCRIPTION: str = Field(
        default="NASA 海洋數據查詢和機器學習預測 API", 
        description="專案描述"
    )
    VERSION: str = Field(default="1.0.0", description="版本號")
    DEBUG: bool = Field(default=True, description="除錯模式")
    
    # 伺服器設定
    HOST: str = Field(default="0.0.0.0", description="主機位址")
    PORT: int = Field(default=8000, description="埠號")
    
    # API 設定
    API_V1_STR: str = Field(default="/api/v1", description="API v1 前綴")
    ALLOWED_HOSTS: List[str] = Field(
        default=["*"], 
        description="允許的主機列表"
    )
    
    # 檔案上傳設定
    MAX_FILE_SIZE: int = Field(
        default=50 * 1024 * 1024,  # 50MB，增加到50MB以支援更大的CSV檔案
        description="最大檔案大小（位元組）"
    )
    UPLOAD_DIR: str = Field(
        default="uploads",
        description="上傳目錄"
    )
    
    # ML 模型設定
    ML_MODEL_PATH: str = Field(
        default="shark_rf_model_round_18.joblib",
        description="機器學習模型檔案路徑"
    )
    
    # 海洋數據設定
    OCEAN_DATA_PATH: str = Field(
        default="comprehensive_shark_ocean_features - comprehensive_shark_ocean_features.csv",
        description="海洋數據 CSV 檔案路徑"
    )
    
    # 日誌設定
    LOG_LEVEL: str = Field(default="INFO", description="日誌等級")
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = True
        extra = "ignore"  # 忽略額外的環境變數


# 創建全域設定實例
settings = Settings()


def get_cors_origins() -> List[str]:
    """獲取 CORS 允許的源"""
    if settings.DEBUG:
        # 開發模式允許所有來源
        return ["*"]
    return settings.ALLOWED_HOSTS


def is_production() -> bool:
    """檢查是否為生產環境"""
    return not settings.DEBUG and os.getenv("ENVIRONMENT") == "production"