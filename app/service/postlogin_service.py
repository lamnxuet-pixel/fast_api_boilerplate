import json
import logging
import time
from typing import Dict, Any, Optional, Tuple

from fastapi import HTTPException

from app.schema.postlogin_dto import SessionData, BasicCustomerInfo
from app.security import auth_handler
from app.service.redis_service import redis_service
from app.service.token_verification_service import token_verification_service
from app.conf.env.redis_config import redis_settings

_log = logging.getLogger(__name__)


class PostloginService:
    """Service for handling postlogin session management"""
    
    def __init__(self):
        self.session_ttl = redis_settings.SME_SESSION_TTL
    
    async def init_postlogin_user_session(
        self,
        cif: str,
        basic_customer_info: BasicCustomerInfo,
        token_key: str,
        payload: Dict[str, Any],
        request_id_header: str = ""
    ) -> Dict[str, Any]:
        """
        Initialize postlogin user session
        
        Args:
            cif: Customer identification number
            basic_customer_info: Basic customer information
            token_key: Token key for validation
            payload: Additional payload data
            request_id_header: Request ID from header
            
        Returns:
            Dictionary containing tokens and success message
        """
        # Validate channel ID
        channel_id = payload.get('channelId')
        if not channel_id:
            raise HTTPException(status_code=400, detail='Invalid channel id')
        
        # Mock channel setting - in real app, this would query database
        channel_setting = await self._get_channel_setting(channel_id)
        if not channel_setting:
            raise HTTPException(status_code=404, detail=f'Cannot find channel with id {channel_id}')
        
        post_login_bu = channel_setting.get('postLoginBu')
        if not post_login_bu:
            raise HTTPException(status_code=404, detail=f'Missing BU in channel with id {channel_id}')
        
        bu = post_login_bu.upper()
        chat_username = f"VPB-{bu}-{cif}"
        
        # Check Redis connection
        if not redis_service.is_connected:
            _log.error('Redis connection not available')
            raise HTTPException(status_code=500, detail='Internal Server Error')
        
        try:
            # Create session data
            current_time = int(time.time() * 1000)  # milliseconds
            session_data = SessionData(
                cif=cif,
                chat_username=chat_username,
                basic_customer_info=basic_customer_info,
                token_key=token_key,
                bu=bu,
                created_at=current_time,
                updated_at=current_time,
                request_id_header=request_id_header,
                payload=payload
            )
            
            # Create tokens
            token, refresh_token = await self._create_tokens(bu, session_data.dict())
            
            # Save session data to Redis
            redis_key = f"session:{chat_username}"
            await redis_service.set(redis_key, session_data.dict(), self.session_ttl)
            
            return {
                "token": token,
                "refreshToken": refresh_token,
                "message": f"{bu} session initialized successfully"
            }
            
        except Exception as err:
            _log.error(f"Error in init_postlogin_user_session: {err}")
            raise HTTPException(status_code=500, detail='Internal Server Error')
    
    async def renew_postlogin_user_token(self, refresh_token: str) -> Dict[str, Any]:
        """
        Renew postlogin user token
        
        Args:
            refresh_token: Refresh token to validate
            
        Returns:
            Dictionary containing new tokens and success message
        """
        if not refresh_token:
            raise HTTPException(status_code=400, detail='Refresh token is required')
        
        # Decode refresh token
        try:
            payload_refresh_token = auth_handler._decode_access_token(refresh_token)
        except HTTPException as e:
            raise HTTPException(status_code=400, detail='Invalid refresh token')
        
        chat_username = payload_refresh_token.get('chatUsername')
        bu = payload_refresh_token.get('bu')
        
        if not chat_username or not bu:
            raise HTTPException(status_code=400, detail='Invalid refresh token')
        
        # Get session data from Redis
        redis_key = f"session:{chat_username}"
        session_data_json = await redis_service.get(redis_key)
        
        if not session_data_json:
            raise HTTPException(status_code=404, detail='Session not found')
        
        try:
            parsed_session_data = json.loads(session_data_json)
        except json.JSONDecodeError:
            raise HTTPException(status_code=500, detail='Invalid session data')
        
        token_key = parsed_session_data.get('tokenKey')
        cif = parsed_session_data.get('cif')
        request_id_header = parsed_session_data.get('requestIdHeader', '')
        
        if not token_key:
            raise HTTPException(status_code=400, detail='Invalid tokenKey')
        
        # Verify token with external service
        request_id_payload = request_id_header or ""
        is_valid_token = await token_verification_service.verify_token(
            bu, token_key, cif, request_id_payload
        )
        
        if not is_valid_token:
            raise HTTPException(status_code=401, detail=f'Verify {bu} token failed')
        
        _log.info(f'redisKey: {redis_key}')
        _log.info(f'sessionData: {session_data_json}')
        _log.info(f'payloadRefreshToken: {payload_refresh_token}')
        
        try:
            # Update session data
            parsed_session_data['updated_at'] = int(time.time() * 1000)
            
            # Create new tokens
            token, new_refresh_token = await self._create_tokens(bu, parsed_session_data)
            
            # Update Redis
            await redis_service.set(redis_key, parsed_session_data, self.session_ttl)
            
            return {
                "token": token,
                "refreshToken": new_refresh_token,
                "message": f"{bu} token renewed successfully"
            }
            
        except Exception as err:
            _log.error(f"Error in renew_postlogin_user_token: {err}")
            raise HTTPException(status_code=500, detail='Internal Server Error')
    
    async def _create_tokens(self, bu: str, session_data: Dict[str, Any]) -> Tuple[str, str]:
        """
        Create access token and refresh token
        
        Args:
            bu: Business unit
            session_data: Session data dictionary
            
        Returns:
            Tuple of (access_token, refresh_token)
        """
        # Create token data
        token_data = {
            "chatUsername": session_data.get("chat_username"),
            "bu": bu,
            "cif": session_data.get("cif"),
            "tokenKey": session_data.get("token_key")
        }
        
        # Create access token
        access_token = auth_handler.create_access_token(token_data)
        
        # Create refresh token (using same logic for now, but could have different expiration)
        refresh_token = auth_handler.create_access_token(token_data)
        
        return access_token, refresh_token
    
    async def _get_channel_setting(self, channel_id: str) -> Optional[Dict[str, Any]]:
        """
        Get channel setting by ID
        
        In a real application, this would query the database.
        For now, we'll return a mock setting.
        
        Args:
            channel_id: Channel ID to lookup
            
        Returns:
            Channel setting dictionary or None
        """
        # Mock channel settings
        mock_channels = {
            "1": {"id": "1", "postLoginBu": "SME"},
            "2": {"id": "2", "postLoginBu": "RETAIL"},
            "sme": {"id": "sme", "postLoginBu": "SME"},
            "retail": {"id": "retail", "postLoginBu": "RETAIL"}
        }
        
        return mock_channels.get(channel_id)


# Global postlogin service instance
postlogin_service = PostloginService()
