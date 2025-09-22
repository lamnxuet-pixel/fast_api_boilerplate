# Postlogin Session Management

This module provides postlogin session management functionality similar to the Strapi implementation you provided. It includes session initialization, token renewal, and external token verification.

## Features

- **Session Initialization**: Create sessions for users authenticated through external systems
- **Token Renewal**: Refresh access tokens using refresh tokens
- **Redis Session Storage**: Store session data in Redis with TTL
- **External Token Verification**: Validate tokens with external SME services
- **Mock API**: Testing endpoint for external validation service

## API Endpoints

### 1. Initialize Session
```
POST /api/v1/postlogin/init-session
```

**Request Body:**
```json
{
  "data": {
    "cif": "1234567890",
    "basicCustomerInfo": {
      "customer_id": "CUST123",
      "customer_name": "John Doe",
      "customer_type": "SME"
    },
    "tokenKey": "external_token_key",
    "payload": {
      "channelId": "sme"
    }
  }
}
```

**Response:**
```json
{
  "token": "jwt_access_token",
  "refreshToken": "jwt_refresh_token",
  "message": "SME session initialized successfully"
}
```

### 2. Renew Token
```
POST /api/v1/postlogin/renew-token
```

**Request Body:**
```json
{
  "data": {
    "refreshToken": "jwt_refresh_token"
  }
}
```

**Response:**
```json
{
  "token": "new_jwt_access_token",
  "refreshToken": "new_jwt_refresh_token", 
  "message": "SME token renewed successfully"
}
```

### 3. Health Check
```
GET /api/v1/postlogin/health
```

**Response:**
```json
{
  "status": "healthy",
  "service": "postlogin"
}
```

### 4. Mock Validation API
```
POST /api/v1/corporate/relationship-management/marketing/v1/customer/validate-session
```

**Headers:**
- `Apikey`: API key for authentication
- `x-request-id`: Request ID for tracking
- `x-session-token`: Session token to validate
- `x-user-id`: User ID

**Response:**
```json
{
  "status": "success",
  "data": {
    "isExpire": false,
    "userId": "1234567890",
    "sessionToken": "token",
    "validatedAt": "2024-01-01T00:00:00Z"
  },
  "message": "Session validation completed"
}
```

## Configuration

### Environment Variables

```bash
# Redis Settings
REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_PASSWORD=
REDIS_DB=0
SME_SESSION_TTL=3600

# SME Token Verification
SME_VERIFY_BASE_URL=http://localhost:8000/api/v1
SME_VERIFY_TOKEN_KEY=your-api-key
```

### Dependencies Added

- `redis==5.0.8`: Redis Python client
- `aioredis==2.0.1`: Async Redis client
- `httpx==0.27.2`: HTTP client for external API calls

## Architecture

### Components

1. **PostloginService** (`app/service/postlogin_service.py`)
   - Main business logic for session management
   - Handles session initialization and token renewal

2. **RedisService** (`app/service/redis_service.py`)
   - Redis connection and session storage management
   - Provides async Redis operations

3. **TokenVerificationService** (`app/service/token_verification_service.py`)
   - Handles external token validation
   - Supports SME token verification

4. **PostloginAPI** (`app/api/postlogin_api.py`)
   - REST API endpoints for postlogin operations
   - Request/response validation

5. **MockAPI** (`app/api/mock_api.py`)
   - Mock endpoint for testing external services
   - Simulates SME validation service

### Data Models

- `InitPostloginSessionRequest`: Session initialization request
- `RenewTokenRequest`: Token renewal request
- `SessionData`: Redis session storage model
- `TokenResponse`: API response model

## Session Flow

1. **Initialization**:
   - Validate input data (CIF, customer info, token key)
   - Verify channel settings and get business unit (BU)
   - Create chat username: `VPB-{BU}-{CIF}`
   - Generate JWT tokens
   - Store session data in Redis with TTL

2. **Token Renewal**:
   - Validate refresh token
   - Retrieve session data from Redis
   - Verify external token is still valid
   - Generate new JWT tokens
   - Update session data in Redis

3. **External Verification**:
   - Call external SME validation API
   - Check if token is expired
   - Return validation result

## Testing

Run the test script to verify functionality:

```bash
# Start the FastAPI server
uvicorn app.main:app --reload

# In another terminal, run the test
python test_postlogin_example.py
```

## Mock Testing Scenarios

The mock API supports different testing scenarios based on token values:

- Tokens starting with `"valid"`: Considered valid (not expired)
- Tokens starting with `"expired"`: Considered expired
- Tokens starting with `"invalid"`: Return 401 error
- All other tokens: Considered valid by default

## Security Considerations

- All postlogin endpoints are configured as allowed paths in security settings
- Session data is stored in Redis with TTL for automatic cleanup
- External token validation adds an extra security layer
- JWT tokens have configurable expiration times

## Integration Notes

This implementation maintains the same core functionality as the original Strapi code while adapting it to FastAPI patterns:

- Uses Pydantic models for validation instead of lodash
- Implements async/await patterns throughout
- Uses FastAPI dependency injection
- Follows Python naming conventions
- Provides comprehensive error handling and logging
