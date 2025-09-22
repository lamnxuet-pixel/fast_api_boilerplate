import logging
from typing import Dict, Any

from fastapi import APIRouter, Header, HTTPException, status
from fastapi.responses import JSONResponse

_log = logging.getLogger(__name__)

router = APIRouter(prefix="/corporate/relationship-management/marketing/v1", tags=["mock"])


@router.post(
    path="/customer/validate-session",
    operation_id="validate_session",
    name="validate_session",
    summary="Mock API for validating SME customer session",
    status_code=status.HTTP_200_OK,
)
async def validate_session(
    apikey: str = Header(..., alias="Apikey"),
    x_request_id: str = Header(..., alias="x-request-id"),
    x_session_token: str = Header(..., alias="x-session-token"),
    x_user_id: str = Header(..., alias="x-user-id"),
) -> JSONResponse:
    """
    Mock API endpoint for validating SME customer session
    
    This endpoint simulates the external SME validation service.
    It validates the session token and returns whether it's expired or not.
    
    Headers:
        - Apikey: API key for authentication
        - x-request-id: Request ID for tracking
        - x-session-token: Session token to validate
        - x-user-id: User ID
    
    Returns:
        JSON response with validation result
    """
    _log.info(f"Mock validate session called with:")
    _log.info(f"  Apikey: {apikey}")
    _log.info(f"  x-request-id: {x_request_id}")
    _log.info(f"  x-session-token: {x_session_token}")
    _log.info(f"  x-user-id: {x_user_id}")
    
    # Validate required headers
    if not apikey:
        raise HTTPException(status_code=401, detail="Missing Apikey header")
    
    if not x_session_token:
        raise HTTPException(status_code=400, detail="Missing x-session-token header")
    
    if not x_user_id:
        raise HTTPException(status_code=400, detail="Missing x-user-id header")
    
    # Mock validation logic
    # In a real scenario, this would check against actual session data
    
    # For demo purposes:
    # - Tokens starting with "valid" are considered valid (not expired)
    # - Tokens starting with "expired" are considered expired
    # - All other tokens are considered valid by default
    
    is_expired = False
    
    if x_session_token.startswith("expired"):
        is_expired = True
    elif x_session_token.startswith("invalid"):
        # Simulate invalid token scenario
        raise HTTPException(status_code=401, detail="Invalid session token")
    
    response_data = {
        "status": "success",
        "data": {
            "isExpire": is_expired,
            "userId": x_user_id,
            "sessionToken": x_session_token,
            "validatedAt": "2024-01-01T00:00:00Z"
        },
        "message": "Session validation completed"
    }
    
    _log.info(f"Mock validate session response: {response_data}")
    
    return JSONResponse(content=response_data, status_code=200)
