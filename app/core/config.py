import os
from typing import List, Optional
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """应用配置"""
    
    # API 配置
    api_title: str = "Bangumi Data API"
    api_description: str = "A FastAPI wrapper for bangumi-data"
    api_version: str = "1.0.0"
    
    # 服务器配置
    host: str = "0.0.0.0"
    port: int = 8000
    
    # API Key 配置
    api_keys: Optional[str] = None
    require_api_key: bool = False
    
    # 缓存配置
    cache_ttl: int = 3600  # 1小时
    
    # CORS 配置
    cors_origins: List[str] = ["*"]
    cors_methods: List[str] = ["GET", "POST", "PUT", "DELETE"]
    cors_headers: List[str] = ["*"]
    
    # 日志配置
    log_level: str = "INFO"
    
    @property
    def api_keys_list(self) -> List[str]:
        """将API_KEYS字符串转换为列表"""
        if not self.api_keys:
            return []
        return [key.strip() for key in self.api_keys.split(",") if key.strip()]
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False


settings = Settings()