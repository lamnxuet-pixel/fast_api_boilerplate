import logging
import os
import uuid
from typing import Dict, Any, Optional

import httpx
from fastapi import HTTPException

_log = logging.getLogger(__name__)


class TokenVerificationService:
    """Service for verifying external tokens"""
    
    def __init__(self):
        self.sme_verify_base_url = os.getenv('SME_VERIFY_BASE_URL')
        self.sme_verify_token_key = os.getenv('SME_VERIFY_TOKEN_KEY')
    
    async def verify_sme_token(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """
        Verify SME token with external API
        
        Args:
            payload: Dictionary containing userId, requestId, and tokenKey
            
        Returns:
            Dictionary with isValid boolean and message
        """
        if not self.sme_verify_base_url:
            raise HTTPException(status_code=500, detail="SME_VERIFY_BASE_URL is not defined")
        
        if not self.sme_verify_token_key:
            raise HTTPException(status_code=500, detail="SME_VERIFY_TOKEN_KEY is not defined")
        
        url = f"{self.sme_verify_base_url.rstrip('/')}/corporate/relationship-management/marketing/v1/customer/validate-session"
        
        headers = {
            'Apikey': self.sme_verify_token_key,
            'Content-Type': 'application/json',
            'x-request-id': payload.get('requestId') or payload.get('userId') or str(uuid.uuid4()),
            'x-session-token': payload.get('tokenKey', ''),
            'x-user-id': payload.get('userId', ''),
        }
        
        _log.info(f"Verify url: {url}")
        _log.info(f"x-request-id: {headers.get('x-request-id')}")
        _log.info(f"x-session-token: {headers.get('x-session-token')}")
        _log.info(f"x-user-id: {headers.get('x-user-id')}")
        
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(url, json={}, headers=headers)
                
                if response.status_code != 200:
                    _log.info(f'Error verify tokenKey: {response.status_code}')
                    return {"isValid": False, "message": "Error verify tokenKey"}
                
                response_data = response.json()
                _log.info(f'verify tokenKey: {response_data}')
                
                # Check if token is not expired
                is_valid = not response_data.get('data', {}).get('isExpire', True)
                
                return {"isValid": is_valid, "message": None}
                
        except Exception as error:
            _log.error(f'Error verify tokenKey: {error}')
            return {"isValid": False, "message": "Error verify tokenKey"}
    
    async def verify_token(self, bu: str, token_key: str, user_id: str, request_id: Optional[str] = None) -> bool:
        """
        Verify token based on business unit
        
        Args:
            bu: Business unit (SME, etc.)
            token_key: Token to verify
            user_id: User ID
            request_id: Optional request ID
            
        Returns:
            Boolean indicating if token is valid
        """
        _log.info(f'bu: {bu}')
        
        if bu == 'SME':
            if not user_id:
                raise HTTPException(status_code=400, detail='Missing userId')
            
            sme_payload = {
                'userId': user_id,
                'requestId': request_id or '',
                'tokenKey': token_key
            }
            
            result = await self.verify_sme_token(sme_payload)
            return result.get('isValid', False)
        else:
            raise HTTPException(status_code=400, detail='Missing BU')


# Global token verification service instance
token_verification_service = TokenVerificationService()
