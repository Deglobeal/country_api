import requests
import json

BASE_URL = "https://stunning-forgiveness-production.up.railway.app/countries"

def test_endpoint(method, endpoint, data=None):
    """Test a single endpoint and print results"""
    url = f"{BASE_URL}{endpoint}"
    
    print(f"\n{'='*60}")
    print(f"Testing: {method} {endpoint}")
    print(f"URL: {url}")
    
    try:
        if method == "GET":
            response = requests.get(url, timeout=15)
        elif method == "POST":
            response = requests.post(url, timeout=30)  # Longer timeout for refresh
        elif method == "DELETE":
            response = requests.delete(url, timeout=15)
        
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            if endpoint == "/image":
                print("✓ Image received (binary data)")
            else:
                try:
                    data = response.json()
                    print("✓ JSON Response:")
                    print(json.dumps(data, indent=2)[:500] + "..." if len(str(data)) > 500 else "")
                except:
                    print("✓ Response (non-JSON):", response.text[:200])
        elif response.status_code == 204:
            print("✓ Success (No Content)")
        else:
            print(f"✗ Error Response: {response.text}")
            
    except requests.exceptions.Timeout:
        print("✗ Timeout - Endpoint took too long to respond")
    except requests.exceptions.ConnectionError:
        print("✗ Connection Error - Cannot reach the server")
    except Exception as e:
        print(f"✗ Unexpected error: {e}")

# Test all endpoints
print("🚀 Testing Railway Deployment - Manual Endpoint Check")
print("Base URL:", BASE_URL)

# Test endpoints in recommended order
test_endpoint("GET", "/status")
test_endpoint("GET", "")  # Get all countries
test_endpoint("GET", "/image")
test_endpoint("POST", "/refresh")

# Test specific country (try common names)
for country_name in ["United States", "France", "Germany", "China"]:
    test_endpoint("GET", f"/{country_name}")

# Test filters
test_endpoint("GET", "/?region=Africa")
test_endpoint("GET", "/?currency=USD")
test_endpoint("GET", "/?sort=gdp_desc")

# Test error cases
test_endpoint("GET", "/NonexistentCountry")
test_endpoint("GET", "/invalid/endpoint")

print("\n" + "="*60)
print("Testing completed!")