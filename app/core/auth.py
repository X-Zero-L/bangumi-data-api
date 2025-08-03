from fastapi import HTTPException, Security
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from app.core.config import settings


security = HTTPBearer(auto_error=False)


async def verify_api_key(credentials: HTTPAuthorizationCredentials = Security(security)):
    """验证API Key"""
    if not settings.require_api_key:
        return True
        
    if not credentials:
        raise HTTPException(
            status_code=401,
            detail="API key required"
        )
    
    if not settings.api_keys or credentials.credentials not in settings.api_keys:
        raise HTTPException(
            status_code=401,
            detail="Invalid API key"
        )
    
    return True