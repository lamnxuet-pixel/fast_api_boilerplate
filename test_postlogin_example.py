#!/usr/bin/env python3
"""
Example script to test the postlogin functionality
"""
import asyncio
import json
import httpx


BASE_URL = "http://localhost:8000/api/v1"


async def test_postlogin_flow():
    """Test the complete postlogin flow"""
    
    async with httpx.AsyncClient() as client:
        print("🚀 Testing Postlogin API Flow")
        print("=" * 50)
        
        # Test 1: Initialize postlogin session
        print("\n1. Testing session initialization...")
        
        init_payload = {
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
        
        headers = {
            "Content-Type": "application/json",
            "x-request-id": "test-request-123"
        }
        
        try:
            response = await client.post(
                f"{BASE_URL}/postlogin/init-session",
                json=init_payload,
                headers=headers
            )
            
            if response.status_code == 200:
                print("✅ Session initialization successful!")
                result = response.json()
                print(f"   Token: {result['token'][:50]}...")
                print(f"   Refresh Token: {result['refreshToken'][:50]}...")
                print(f"   Message: {result['message']}")
                
                refresh_token = result['refreshToken']
                
                # Test 2: Renew token
                print("\n2. Testing token renewal...")
                
                renew_payload = {
                    "data": {
                        "refreshToken": refresh_token
                    }
                }
                
                renew_response = await client.post(
                    f"{BASE_URL}/postlogin/renew-token",
                    json=renew_payload,
                    headers={"Content-Type": "application/json"}
                )
                
                if renew_response.status_code == 200:
                    print("✅ Token renewal successful!")
                    renew_result = renew_response.json()
                    print(f"   New Token: {renew_result['token'][:50]}...")
                    print(f"   New Refresh Token: {renew_result['refreshToken'][:50]}...")
                    print(f"   Message: {renew_result['message']}")
                else:
                    print(f"❌ Token renewal failed: {renew_response.status_code}")
                    print(f"   Response: {renew_response.text}")
                    
            else:
                print(f"❌ Session initialization failed: {response.status_code}")
                print(f"   Response: {response.text}")
                
        except Exception as e:
            print(f"❌ Error during testing: {e}")
        
        # Test 3: Test mock validation API
        print("\n3. Testing mock validation API...")
        
        try:
            mock_headers = {
                "Apikey": "test-api-key",
                "x-request-id": "test-request-456",
                "x-session-token": "valid_token_123",
                "x-user-id": "1234567890"
            }
            
            mock_response = await client.post(
                f"{BASE_URL}/corporate/relationship-management/marketing/v1/customer/validate-session",
                json={},
                headers=mock_headers
            )
            
            if mock_response.status_code == 200:
                print("✅ Mock validation API successful!")
                mock_result = mock_response.json()
                print(f"   Status: {mock_result['status']}")
                print(f"   Is Expired: {mock_result['data']['isExpire']}")
                print(f"   Message: {mock_result['message']}")
            else:
                print(f"❌ Mock validation API failed: {mock_response.status_code}")
                print(f"   Response: {mock_response.text}")
                
        except Exception as e:
            print(f"❌ Error during mock API testing: {e}")
        
        # Test 4: Health check
        print("\n4. Testing health check...")
        
        try:
            health_response = await client.get(f"{BASE_URL}/postlogin/health")
            
            if health_response.status_code == 200:
                print("✅ Health check successful!")
                health_result = health_response.json()
                print(f"   Status: {health_result['status']}")
                print(f"   Service: {health_result['service']}")
            else:
                print(f"❌ Health check failed: {health_response.status_code}")
                
        except Exception as e:
            print(f"❌ Error during health check: {e}")
        
        print("\n" + "=" * 50)
        print("🎉 Postlogin API testing completed!")


if __name__ == "__main__":
    print("Make sure the FastAPI server is running on http://localhost:8000")
    print("You can start it with: uvicorn app.main:app --reload")
    print("\nPress Enter to continue...")
    input()
    
    asyncio.run(test_postlogin_flow())
