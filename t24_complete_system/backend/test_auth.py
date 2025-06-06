# Authentication Test Script
# This script tests the authentication functionality with the default credentials

import requests
import json
import sys

BASE_URL = "http://localhost:8000"
AUTH_ENDPOINT = "/api/v1/token"  # <-- Fixed endpoint

def test_authentication(email, password):
    """Test authentication with provided credentials"""
    print(f"Testing authentication for {email}...")
    
    try:
        response = requests.post(
            f"{BASE_URL}{AUTH_ENDPOINT}",
            data={"username": email, "password": password},
            headers={"Content-Type": "application/x-www-form-urlencoded"}
        )
        
        if response.status_code == 200:
            print(f"✅ Authentication successful for {email}")
            token_data = response.json()
            print(f"Access token received: {token_data['access_token'][:20]}...")
            return True
        else:
            print(f"❌ Authentication failed for {email}")
            print(f"Status code: {response.status_code}")
            print(f"Response: {response.text}")
            return False
    except Exception as e:
        print(f"❌ Error during authentication test: {e}")
        return False

def main():
    # Test admin credentials
    admin_success = test_authentication("admin@t24leads.se", "admin123")
    
    # Test partner credentials
    partner_success = test_authentication("partner1@t24leads.se", "partner1")
    
    # Print summary
    print("\n=== Authentication Test Summary ===")
    print(f"Admin authentication: {'✅ Success' if admin_success else '❌ Failed'}")
    print(f"Partner authentication: {'✅ Success' if partner_success else '❌ Failed'}")
    
    # Return exit code based on test results
    if admin_success and partner_success:
        print("\n✅ All authentication tests passed!")
        return 0
    else:
        print("\n❌ Some authentication tests failed!")
        return 1

if __name__ == "__main__":
    sys.exit(main())
