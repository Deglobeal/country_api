import requests

BASE_URL = "http://localhost:8000"

# Quick test function
def quick_test(endpoint, method='GET', data=None):
    url = f"{BASE_URL}{endpoint}"
    try:
        if method == 'GET':
            response = requests.get(url)
        elif method == 'POST':
            response = requests.post(url, json=data)
        elif method == 'DELETE':
            response = requests.delete(url)
        
        print(f"{method} {endpoint}")
        print(f"Status: {response.status_code}")
        
        if response.status_code != 200:
            print(f"Response: {response.text}")
        else:
            data = response.json()
            if endpoint == '/countries':
                print(f"Count: {len(data)} countries")
            elif endpoint == '/status':
                print(f"Total countries: {data.get('total_countries')}")
        
        print("-" * 50)
        return response
        
    except Exception as e:
        print(f"Error: {e}")
        return None

# Run quick tests
if __name__ == "__main__":
    print("QUICK API TESTS")
    print("=" * 50)
    
    quick_test("/countries/refresh", "POST")
    quick_test("/countries")
    quick_test("/countries?region=Africa")
    quick_test("/countries?sort=gdp_desc")
    quick_test("/countries/Nigeria")
    quick_test("/countries/NonExistentCountry")
    quick_test("/status")
    quick_test("/countries/image")