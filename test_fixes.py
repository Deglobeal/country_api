import requests
import sys

BASE_URL = "http://localhost:8000"

def test_endpoint(method, endpoint, expected_codes, description):
    print(f"\nTesting: {description}")
    print(f"Endpoint: {method} {endpoint}")
    
    try:
        if method == 'GET':
            response = requests.get(f"{BASE_URL}{endpoint}")
        elif method == 'POST':
            response = requests.post(f"{BASE_URL}{endpoint}")
        elif method == 'DELETE':
            response = requests.delete(f"{BASE_URL}{endpoint}")
        
        if response.status_code in expected_codes:
            print(f"✓ PASS - Status: {response.status_code}")
            if response.status_code != 200 and response.status_code != 204:
                print(f"Response: {response.text}")
            return True
        else:
            print(f"✗ FAIL - Status: {response.status_code} (Expected: {expected_codes})")
            print(f"Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"✗ ERROR - {e}")
        return False

print("Testing Country API Fixes")
print("=" * 50)

# Test DELETE with combined endpoint
test_endpoint('DELETE', '/countries/Afghanistan', [204, 404], "DELETE country")

# Test GET with same endpoint
test_endpoint('GET', '/countries/Afghanistan', [200, 404], "GET country")

# Test image endpoint (might still be 404 if no image generated)
test_endpoint('GET', '/countries/image', [200, 404], "Get countries image")

# Test refresh with improved error handling
test_endpoint('POST', '/countries/refresh', [200, 503], "Refresh countries")

print("\n" + "=" * 50)
print("Testing complete!")