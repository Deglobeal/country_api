import requests
import json

BASE_URL = "https://stunning-forgiveness-production.up.railway.app"

def test_all_patterns():
    """Test all possible URL patterns based on the error page"""
    
    patterns = [
        # Root and admin
        ("GET", "/", "API Root"),
        ("GET", "/admin/", "Admin"),
        
        # Countries endpoints
        ("POST", "/countries/refresh", "Refresh countries"),
        ("GET", "/countries", "List countries"),
        ("GET", "/countries/Afghanistan", "Get country by name"),
        ("DELETE", "/countries/Afghanistan/delete", "Delete country"),
        
        # Status and image
        ("GET", "/status", "Status"),
        ("GET", "/countries/image", "Countries image"),
        
        # Alternative patterns
        ("GET", "/get-status", "Get status alternative"),
        ("GET", "/countries/status", "Countries status"),
        ("GET", "/image", "Image"),
        ("GET", "/get-country-image", "Get country image"),
    ]
    
    print("🔍 Testing All Possible URL Patterns")
    print("=" * 60)
    
    working_endpoints = []
    
    for method, endpoint, description in patterns:
        url = BASE_URL + endpoint
        print(f"\nTesting: {description}")
        print(f"URL: {method} {url}")
        
        try:
            if method == "GET":
                response = requests.get(url, timeout=10)
            elif method == "POST":
                response = requests.post(url, timeout=15)
            elif method == "DELETE":
                response = requests.delete(url, timeout=10)
            
            print(f"Status: {response.status_code}")
            
            if response.status_code == 200:
                working_endpoints.append((method, endpoint, description))
                if endpoint != "/countries/image":
                    try:
                        data = response.json()
                        print("✓ Working - JSON response")
                    except:
                        print("✓ Working - Non-JSON response")
                else:
                    print("✓ Working - Image endpoint")
            elif response.status_code == 204:
                working_endpoints.append((method, endpoint, description))
                print("✓ Working - No Content")
            else:
                print(f"✗ Failed: {response.text[:100]}...")
                
        except requests.exceptions.Timeout:
            print("✗ Timeout")
        except Exception as e:
            print(f"✗ Error: {e}")
    
    return working_endpoints

def test_country_names():
    """Test different country name formats"""
    print("\n\n🔍 Testing Country Name Formats")
    print("=" * 60)
    
    test_names = [
        "United States",
        "United%20States",  # URL encoded
        "United%20States%20of%20America",
        "France",
        "Germany", 
        "China",
        "Afghanistan"
    ]
    
    for name in test_names:
        url = f"{BASE_URL}/countries/{name}"
        print(f"\nTesting: {name}")
        print(f"URL: {url}")
        
        try:
            response = requests.get(url, timeout=10)
            print(f"Status: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                print(f"✓ Found: {data.get('name')}")
            else:
                print(f"Response: {response.text[:100]}...")
                
        except Exception as e:
            print(f"Error: {e}")

def test_query_params():
    """Test query parameters with different URL patterns"""
    print("\n\n🔍 Testing Query Parameters")
    print("=" * 60)
    
    base_urls = [
        "/countries",
        "/countries/"
    ]
    
    params_list = [
        {"region": "Africa"},
        {"currency": "USD"},
        {"sort": "gdp_desc"}
    ]
    
    for base in base_urls:
        for params in params_list:
            url = BASE_URL + base
            print(f"\nTesting: {base} with {params}")
            
            try:
                response = requests.get(url, params=params, timeout=10)
                print(f"Status: {response.status_code}")
                
                if response.status_code == 200:
                    data = response.json()
                    print(f"✓ Working - {len(data)} countries returned")
                else:
                    print(f"Response: {response.text[:100]}...")
                    
            except Exception as e:
                print(f"Error: {e}")

if __name__ == "__main__":
    print("🚀 Railway API Diagnosis")
    print("Base URL:", BASE_URL)
    print("=" * 60)
    
    # Test all patterns
    working = test_all_patterns()
    
    # Test country names
    test_country_names()
    
    # Test query parameters
    test_query_params()
    
    # Summary
    print("\n\n📊 SUMMARY")
    print("=" * 60)
    print(f"Working endpoints: {len(working)}")
    for method, endpoint, desc in working:
        print(f"✓ {method} {endpoint} - {desc}")