import logging
from typing import Annotated

from fastapi import APIRouter, Body, Header, status, Request

from app.schema.postlogin_dto import (
    InitPostloginSessionRequest,
    RenewTokenRequest,
    TokenResponse
)
from app.service.postlogin_service import postlogin_service

_log = logging.getLogger(__name__)

router = APIRouter(prefix="/postlogin", tags=["postlogin"])


@router.post(
    path="/init-session",
    operation_id="init_postlogin_session",
    name="init_postlogin_session",
    summary="Initialize postlogin user session",
    response_model=TokenResponse,
    status_code=status.HTTP_200_OK,
)
async def init_postlogin_user_session(
    request: Request,
    session_request: Annotated[InitPostloginSessionRequest, Body(
        ...,
        title="Session Initialization Data",
        description="Data required to initialize a postlogin session.",
        openapi_examples={
            "sme_example": {
                "summary": "SME Channel Example",
                "description": "Initialize session for SME channel",
                "value": {
                    "data": {
                        "cif": "1234567890",
                        "basicCustomerInfo": {
                            "customer_id": "CUST123",
                            "customer_name": "John Doe",
                            "customer_type": "SME"
                        },
                        "tokenKey": "valid_token_key_123",
                        "payload": {
                            "channelId": "sme"
                        }
                    }
                }
            }
        }
    )],
    x_request_id: str = Header(default="", alias="x-request-id")
) -> TokenResponse:
    """
    Initialize postlogin user session
    
    This endpoint creates a new session for a user after they have been authenticated
    through an external system. It validates the provided token and creates internal
    session tokens for the user.
    
    **session_request**: Session initialization data containing CIF, customer info, token key, and payload
    
    **x-request-id**: Optional request ID header for tracking
    
    **return**: Token response with access token, refresh token, and success message
    """
    _log.debug("PostloginAPI initializing user session")
    
    data = session_request.data
    
    result = await postlogin_service.init_postlogin_user_session(
        cif=data.cif,
        basic_customer_info=data.basic_customer_info,
        token_key=data.token_key,
        payload=data.payload.dict(),
        request_id_header=x_request_id
    )
    
    return TokenResponse(
        token=result["token"],
        refresh_token=result["refreshToken"],
        message=result["message"]
    )


@router.post(
    path="/renew-token",
    operation_id="renew_postlogin_token",
    name="renew_postlogin_token",
    summary="Renew postlogin user token",
    response_model=TokenResponse,
    status_code=status.HTTP_200_OK,
)
async def renew_postlogin_user_token(
    renew_request: Annotated[RenewTokenRequest, Body(
        ...,
        title="Token Renewal Data",
        description="Data required to renew a postlogin token.",
        openapi_examples={
            "renewal_example": {
                "summary": "Token Renewal Example",
                "description": "Renew token using refresh token",
                "value": {
                    "data": {
                        "refreshToken": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
                    }
                }
            }
        }
    )]
) -> TokenResponse:
    """
    Renew postlogin user token
    
    This endpoint allows renewal of access tokens using a valid refresh token.
    It validates the refresh token, checks the session validity with external
    services, and issues new tokens.
    
    **renew_request**: Token renewal data containing the refresh token
    
    **return**: Token response with new access token, refresh token, and success message
    """
    _log.debug("PostloginAPI renewing user token")
    
    data = renew_request.data
    
    result = await postlogin_service.renew_postlogin_user_token(
        refresh_token=data.refresh_token
    )
    
    return TokenResponse(
        token=result["token"],
        refresh_token=result["refreshToken"],
        message=result["message"]
    )


@router.get(
    path="/health",
    operation_id="postlogin_health",
    name="postlogin_health",
    summary="Health check for postlogin service",
    status_code=status.HTTP_200_OK,
)
async def health_check():
    """
    Health check endpoint for postlogin service
    
    **return**: Simple health status
    """
    return {"status": "healthy", "service": "postlogin"}
