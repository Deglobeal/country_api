# test_json_responses.py
import requests
import json

BASE_URL = "https://your-railway-app.railway.app"  # Replace with your actual URL

def test_json_responses():
    print("Testing JSON Response Format...")
    
    # Test 1: 404 for non-existent country
    print("\n1. Testing 404 response...")
    try:
        response = requests.get(f"{BASE_URL}/countries/NonExistentCountry123")
        print(f"   Status: {response.status_code}")
        print(f"   Content-Type: {response.headers.get('content-type')}")
        
        # Check if it's JSON
        if 'application/json' in response.headers.get('content-type', ''):
            data = response.json()
            print(f"   ✓ JSON Response: {data}")
        else:
            print(f"   ✗ Not JSON: {response.text[:100]}")
    except Exception as e:
        print(f"   ✗ Error: {e}")
    
    # Test 2: DELETE non-existent country
    print("\n2. Testing DELETE 404...")
    try:
        response = requests.delete(f"{BASE_URL}/countries/NonExistentCountry123")
        print(f"   Status: {response.status_code}")
        print(f"   Content-Type: {response.headers.get('content-type')}")
        
        if response.status_code == 404:
            if 'application/json' in response.headers.get('content-type', ''):
                data = response.json()
                print(f"   ✓ JSON 404: {data}")
            else:
                print(f"   ✗ Not JSON: {response.text[:100]}")
    except Exception as e:
        print(f"   ✗ Error: {e}")
    
    # Test 3: Invalid endpoint
    print("\n3. Testing invalid endpoint...")
    try:
        response = requests.get(f"{BASE_URL}/invalid-endpoint")
        print(f"   Status: {response.status_code}")
        print(f"   Content-Type: {response.headers.get('content-type')}")
        
        if 'application/json' in response.headers.get('content-type', ''):
            data = response.json()
            print(f"   ✓ JSON Error: {data}")
        else:
            print(f"   ✗ Not JSON: {response.text[:100]}")
    except Exception as e:
        print(f"   ✗ Error: {e}")

if __name__ == "__main__":
    test_json_responses()