from datetime import datetime
from typing import Optional, Dict, Any
from pydantic import BaseModel, Field, validator


class BasicCustomerInfo(BaseModel):
    """Basic customer information model"""
    customer_id: Optional[str] = None
    customer_name: Optional[str] = None
    customer_type: Optional[str] = None
    # Add other customer fields as needed


class PostloginPayload(BaseModel):
    """Payload data for postlogin session"""
    channel_id: str = Field(..., description="Channel ID")
    # Add other payload fields as needed


class InitPostloginSessionRequest(BaseModel):
    """Request model for initializing postlogin session"""
    data: 'InitPostloginSessionData'


class InitPostloginSessionData(BaseModel):
    """Data model for initializing postlogin session"""
    cif: str = Field(..., min_length=1, description="Customer Identification Number")
    basic_customer_info: BasicCustomerInfo = Field(..., description="Basic customer information")
    token_key: str = Field(..., min_length=1, description="Token key for validation")
    payload: PostloginPayload = Field(..., description="Additional payload data")
    
    @validator('cif')
    def validate_cif(cls, v):
        if not v or not v.strip():
            raise ValueError('CIF cannot be empty')
        return v.strip()
    
    @validator('token_key')
    def validate_token_key(cls, v):
        if not v or not v.strip():
            raise ValueError('Token key cannot be empty')
        return v.strip()


class RenewTokenRequest(BaseModel):
    """Request model for renewing token"""
    data: 'RenewTokenData'


class RenewTokenData(BaseModel):
    """Data model for renewing token"""
    refresh_token: str = Field(..., min_length=1, description="Refresh token")


class SessionData(BaseModel):
    """Session data stored in Redis"""
    cif: str
    chat_username: str
    basic_customer_info: BasicCustomerInfo
    token_key: str
    bu: str
    created_at: int
    updated_at: int
    request_id_header: Optional[str] = ""
    payload: Optional[Dict[str, Any]] = {}


class TokenResponse(BaseModel):
    """Response model for token operations"""
    token: str
    refresh_token: str
    message: str


class ChannelSetting(BaseModel):
    """Channel setting model"""
    id: str
    post_login_bu: Optional[str] = Field(None, alias="postLoginBu")
    
    class Config:
        populate_by_name = True


# Update forward references
InitPostloginSessionRequest.model_rebuild()
RenewTokenRequest.model_rebuild()
