# test_fixes.py
import requests
import json

BASE_URL = "https://your-railway-app.railway.app"  # Replace with your actual URL

def test_delete_method():
    print("Testing DELETE method...")
    
    # Test 1: Delete non-existent country (should return 404)
    try:
        response = requests.delete(f"{BASE_URL}/countries/NonExistentCountry123")
        print(f"DELETE non-existent: Status {response.status_code}")
        if response.status_code == 404:
            data = response.json()
            if data.get('error') == 'Country not found':
                print("✓ DELETE returns correct 404 for non-existent country")
            else:
                print(f"✗ Wrong error message: {data}")
        else:
            print(f"✗ Expected 404, got {response.status_code}")
    except Exception as e:
        print(f"✗ DELETE test failed: {e}")
    
    # Test 2: Delete an actual country (first refresh to ensure data exists)
    try:
        # First refresh to get data
        refresh = requests.post(f"{BASE_URL}/countries/refresh")
        if refresh.status_code == 200:
            # Try to delete a real country
            response = requests.delete(f"{BASE_URL}/countries/Nigeria")
            print(f"DELETE real country: Status {response.status_code}")
            if response.status_code == 204:
                print("✓ DELETE returns 204 for successful deletion")
            else:
                print(f"✗ Expected 204, got {response.status_code}")
        else:
            print("✗ Could not refresh data for DELETE test")
    except Exception as e:
        print(f"✗ DELETE test failed: {e}")

def test_error_handling():
    print("\nTesting Error Handling...")
    
    # Test 404 error format
    try:
        response = requests.get(f"{BASE_URL}/countries/InvalidCountryName123")
        print(f"404 test: Status {response.status_code}")
        if response.status_code == 404:
            data = response.json()
            if 'error' in data:
                print("✓ 404 returns proper JSON error format")
            else:
                print(f"✗ 404 missing error field: {data}")
        else:
            print(f"✗ Expected 404, got {response.status_code}")
    except Exception as e:
        print(f"✗ 404 test failed: {e}")
    
    # Test invalid endpoint
    try:
        response = requests.get(f"{BASE_URL}/invalid-endpoint")
        data = response.json()
        if 'error' in data:
            print("✓ Invalid endpoint returns JSON error")
        else:
            print(f"✗ Invalid endpoint wrong format: {data}")
    except Exception as e:
        print(f"✗ Invalid endpoint test failed: {e}")

if __name__ == "__main__":
    test_delete_method()
    test_error_handling()