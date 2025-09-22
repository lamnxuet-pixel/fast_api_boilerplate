from fastapi import APIRouter

from .account_api import router as account_router
from .auth_api import router as auth_router
from .user_api import router as user_router
from .postlogin_api import router as postlogin_router
from .mock_api import router as mock_router

api_router = APIRouter()
api_router.include_router(auth_router)
api_router.include_router(account_router)
api_router.include_router(user_router)
api_router.include_router(postlogin_router)
api_router.include_router(mock_router)

__all__ = ["auth_router", "user_router", "account_router", "postlogin_router", "mock_router", "api_router"]
