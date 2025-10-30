# quick_test.py
import requests

BASE_URL = "https://stunning-forgiveness-production.up.railway.app"

def quick_check():
    print("🔍 Quick Production Check...")
    
    endpoints = [
        "/status",
        "/countries",
        "/countries/United%20States", 
        "/countries/image"
    ]
    
    for endpoint in endpoints:
        try:
            response = requests.get(f"{BASE_URL}{endpoint}", timeout=10)
            print(f"✅ {endpoint}: {response.status_code}")
            if endpoint == "/status" and response.status_code == 200:
                print(f"   Data: {response.json()}")
        except Exception as e:
            print(f"❌ {endpoint}: {e}")
    
    # Test refresh
    try:
        response = requests.post(f"{BASE_URL}/countries/refresh", timeout=30)
        print(f"✅ /countries/refresh: {response.status_code}")
        if response.status_code == 200:
            print(f"   Response: {response.json()}")
    except Exception as e:
        print(f"❌ /countries/refresh: {e}")

if __name__ == '__main__':
    quick_check()