import requests
import time

BASE_URL = "http://127.0.0.1:8000"

# Endpoints to test
ENDPOINTS = [
    ("Refresh Country Data (POST)", "POST", f"{BASE_URL}/countries/refresh", None),
    ("Get All Countries (GET)", "GET", f"{BASE_URL}/countries", None),
    ("Get African Countries (GET)", "GET", f"{BASE_URL}/countries?region=Africa", None),
    ("Get Countries Sorted by GDP (GET)", "GET", f"{BASE_URL}/countries?sort=gdp_desc", None),
    ("Get Specific Country (Nigeria)", "GET", f"{BASE_URL}/countries/Nigeria", None),
    ("Get API Status", "GET", f"{BASE_URL}/status", None),
    ("Get Summary Image", "GET", f"{BASE_URL}/countries/image", None),
]


def wait_for_server(max_attempts=30, delay=2):
    """Wait until the Django server starts responding."""
    print("⏳ Waiting for server to start...")
    for i in range(max_attempts):
        try:
            res = requests.get(f"{BASE_URL}/status", timeout=3)
            if res.status_code == 200:
                print("✅ Server is ready!\n")
                return True
        except requests.exceptions.RequestException:
            pass
        print(f"Still waiting... ({i+1}/{max_attempts})")
        time.sleep(delay)
    print("❌ Server did not start in time.")
    return False


def test_endpoint(name, method, url, data=None):
    print(f"🔹 Testing: {name}")
    try:
        if method == "GET":
            res = requests.get(url, timeout=10)
        elif method == "POST":
            res = requests.post(url, json=data or {}, timeout=15)
        else:
            print(f"⚠️ Unsupported method {method}")
            return

        print(f"   Status: {res.status_code}")
        if "image" in url:
            print("   ✅ Image response received.")
            with open("summary.png", "wb") as f:
                f.write(res.content)
        else:
            try:
                print("   ✅ Success:", res.json())
            except Exception:
                print("   ⚠️ Non-JSON Response:", res.text[:100])
        print()
    except Exception as e:
        print(f"   ❌ Error testing {name}: {e}\n")


if __name__ == "__main__":
    print("🚀 Testing API endpoints...\n")

    if not wait_for_server():
        exit(1)

    for name, method, url, data in ENDPOINTS:
        test_endpoint(name, method, url, data)
import requests
import time

BASE_URL = "http://127.0.0.1:8000"

# Endpoints to test
ENDPOINTS = [
    ("Refresh Country Data (POST)", "POST", f"{BASE_URL}/countries/refresh", None),
    ("Get All Countries (GET)", "GET", f"{BASE_URL}/countries", None),
    ("Get African Countries (GET)", "GET", f"{BASE_URL}/countries?region=Africa", None),
    ("Get Countries Sorted by GDP (GET)", "GET", f"{BASE_URL}/countries?sort=gdp_desc", None),
    ("Get Specific Country (Nigeria)", "GET", f"{BASE_URL}/countries/Nigeria", None),
    ("Get API Status", "GET", f"{BASE_URL}/status", None),
    ("Get Summary Image", "GET", f"{BASE_URL}/countries/image", None),
]


def wait_for_server(max_attempts=30, delay=2):
    """Wait until the Django server starts responding."""
    print("⏳ Waiting for server to start...")
    for i in range(max_attempts):
        try:
            res = requests.get(f"{BASE_URL}/status", timeout=3)
            if res.status_code == 200:
                print("✅ Server is ready!\n")
                return True
        except requests.exceptions.RequestException:
            pass
        print(f"Still waiting... ({i+1}/{max_attempts})")
        time.sleep(delay)
    print("❌ Server did not start in time.")
    return False


def test_endpoint(name, method, url, data=None):
    print(f"🔹 Testing: {name}")
    try:
        if method == "GET":
            res = requests.get(url, timeout=10)
        elif method == "POST":
            res = requests.post(url, json=data or {}, timeout=15)
        else:
            print(f"⚠️ Unsupported method {method}")
            return

        print(f"   Status: {res.status_code}")
        if "image" in url:
            print("   ✅ Image response received.")
            with open("summary.png", "wb") as f:
                f.write(res.content)
        else:
            try:
                print("   ✅ Success:", res.json())
            except Exception:
                print("   ⚠️ Non-JSON Response:", res.text[:100])
        print()
    except Exception as e:
        print(f"   ❌ Error testing {name}: {e}\n")


if __name__ == "__main__":
    print("🚀 Testing API endpoints...\n")

    if not wait_for_server():
        exit(1)

    for name, method, url, data in ENDPOINTS:
        test_endpoint(name, method, url, data)
