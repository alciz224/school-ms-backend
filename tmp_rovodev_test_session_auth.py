"""
Test script for session-based authentication API v2.
"""

import requests
import json

BASE_URL = "http://127.0.0.1:8000"

def test_session_auth():
    """Test the session-based authentication flow."""
    
    # Create a session to maintain cookies
    session = requests.Session()
    
    print("=" * 80)
    print("Testing Session-Based Authentication API v2")
    print("=" * 80)
    
    # Step 1: Get CSRF token
    print("\n1. Getting CSRF token...")
    response = session.get(f"{BASE_URL}/api/v2/auth/csrf/")
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    
    if response.status_code == 200:
        csrf_token = response.json().get('data', {}).get('csrf_token')
        print(f"CSRF Token: {csrf_token}")
    else:
        print("Failed to get CSRF token")
        return
    
    # Step 2: Register a new user
    print("\n2. Registering a new user...")
    register_data = {
        "email": "testuser@example.com",
        "password": "SecurePass123!",
        "password_confirm": "SecurePass123!",
        "first_name": "Test",
        "last_name": "User"
    }
    
    headers = {
        "X-CSRFToken": csrf_token,
        "Content-Type": "application/json"
    }
    
    response = session.post(
        f"{BASE_URL}/api/v2/auth/register/",
        json=register_data,
        headers=headers
    )
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    print(f"Cookies: {dict(session.cookies)}")
    
    # Step 3: Check session status
    print("\n3. Checking session status...")
    response = session.get(f"{BASE_URL}/api/v2/auth/status/")
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    
    # Step 4: Logout
    print("\n4. Logging out...")
    response = session.post(
        f"{BASE_URL}/api/v2/auth/logout/",
        headers=headers
    )
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    print(f"Cookies after logout: {dict(session.cookies)}")
    
    # Step 5: Try to access status after logout (should fail)
    print("\n5. Checking session status after logout...")
    response = session.get(f"{BASE_URL}/api/v2/auth/status/")
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    
    # Step 6: Login again
    print("\n6. Logging in again...")
    login_data = {
        "identifier": "testuser@example.com",
        "password": "SecurePass123!"
    }
    
    response = session.post(
        f"{BASE_URL}/api/v2/auth/login/",
        json=login_data,
        headers=headers
    )
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    print(f"Cookies: {dict(session.cookies)}")
    
    # Step 7: Check session status again
    print("\n7. Checking session status after login...")
    response = session.get(f"{BASE_URL}/api/v2/auth/status/")
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    
    print("\n" + "=" * 80)
    print("Test completed!")
    print("=" * 80)

if __name__ == "__main__":
    test_session_auth()
