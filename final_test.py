# final_test.py
import requests
import json

BASE_URL = "http://localhost:8000"  # Change to your actual URL

def test_endpoints():
    print("Testing all endpoints...")
    
    # Test status
    response = requests.get(f"{BASE_URL}/status")
    print(f"Status: {response.status_code} - {response.json()}")
    
    # Test countries list with GDP sorting
    response = requests.get(f"{BASE_URL}/countries?sort=gdp_desc")
    if response.status_code == 200:
        data = response.json()
        print(f"GDP Descending - First: {data[0]['name']} (${data[0]['estimated_gdp']})")
        print(f"GDP Descending - Last: {data[-1]['name']} (${data[-1]['estimated_gdp']})")
    
    # Test DELETE
    response = requests.delete(f"{BASE_URL}/countries/Nigeria")
    print(f"DELETE Nigeria: {response.status_code}")
    
    # Test image
    response = requests.get(f"{BASE_URL}/countries/image")
    print(f"Image: {response.status_code} - Content-Type: {response.headers.get('Content-Type')}")

if __name__ == "__main__":
    test_endpoints()