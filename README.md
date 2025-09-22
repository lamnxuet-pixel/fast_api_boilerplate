Files Created/Modified:
New Files:
app/conf/env/redis_config.py - Redis configuration
app/service/redis_service.py - Redis service layer
app/service/token_verification_service.py - External token validation
app/service/postlogin_service.py - Main postlogin business logic
app/schema/postlogin_dto.py - Data models and validation
app/api/postlogin_api.py - REST API endpoints
app/api/mock_api.py - Mock validation API
test_postlogin_example.py - Test script
POSTLOGIN_README.md - Comprehensive documentation
Modified Files:
requirements.txt - Added Redis and HTTP client dependencies
app/main.py - Added Redis lifecycle management and API tags
app/api/__init__.py - Registered new API routers
app/conf/app_settings.py - Added Redis settings import
app/conf/env/security_settings.py - Added allowed paths for postlogin endpoints
docker-compose.yaml - Added Redis container
🚀 How to Use:
Install dependencies:
Start with Docker:
Or start manually:
Test the functionality:
Access API documentation:
Swagger UI: http://localhost:8000/docs
ReDoc: http://localhost:8000/redoc