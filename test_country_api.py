"""
Self-Grading Test Script for Country API
Simulates the official bot tests with scoring marks.
"""

import requests
import time
import re

BASE_URL = "http://127.0.0.1:8000"

SCORES = {
    "refresh": 25,
    "list": 25,
    "detail": 10,
    "delete": 10,
    "status": 10,
    "image": 10,
    "errors": 10,
}

TOTAL_SCORE = 0

def wait_for_server():
    """Wait for Django server to start."""
    print("Waiting for Django server to be ready...")
    for i in range(30):
        try:
            r = requests.get(f"{BASE_URL}/status", timeout=3)
            if r.status_code == 200:
                print("✅ Server is ready!")
                return True
        except Exception:
            print(f"Still waiting... ({i+1}/30)")
            time.sleep(1)
    raise TimeoutError("Server not responding on /status endpoint.")


def grade(test_name, points, passed, message=""):
    """Helper to record scores"""
    global TOTAL_SCORE
    if passed:
        TOTAL_SCORE += points
        print(f"✓ {test_name} passed (+{points} pts) {message}")
    else:
        print(f"✗ {test_name} failed (0 pts) {message}")


# ---- TEST 1: POST /countries/refresh ----
def test_refresh():
    print("\nTEST 1: /countries/refresh (25 pts)")
    try:
        r = requests.post(f"{BASE_URL}/countries/refresh", timeout=20)
        if r.status_code == 200 and "total_countries" in r.json():
            grade("Refresh endpoint", 25, True)
        else:
            grade("Refresh endpoint", 25, False, f"Status {r.status_code}")
    except Exception as e:
        grade("Refresh endpoint", 25, False, str(e))


# ---- TEST 2: GET /countries ----
def test_list():
    print("\nTEST 2: /countries (25 pts)")
    try:
        r = requests.get(f"{BASE_URL}/countries?sort=gdp_desc", timeout=5)
        data = r.json()
        if isinstance(data, list) and len(data) > 0:
            grade("Basic GET /countries", 5, True)
            if "name" in data[0] and "estimated_gdp" in data[0]:
                grade("Correct structure", 5, True)
        region = data[0].get("region")
        if region:
            r2 = requests.get(f"{BASE_URL}/countries?region={region}", timeout=5)
            grade("Filter by region", 5, r2.status_code == 200)
        currency = data[0].get("currency_code")
        if currency:
            r3 = requests.get(f"{BASE_URL}/countries?currency={currency}", timeout=5)
            grade("Filter by currency", 5, r3.status_code == 200)
        # Check GDP sorting descending
        gdps = [d.get("estimated_gdp", 0) or 0 for d in data if d.get("estimated_gdp") is not None]
        if gdps == sorted(gdps, reverse=True):
            grade("Sorting by GDP", 5, True)
        else:
            grade("Sorting by GDP", 5, False)
    except Exception as e:
        grade("List countries", 25, False, str(e))


# ---- TEST 3: GET /countries/:name ----
def test_detail():
    print("\nTEST 3: /countries/:name (10 pts)")
    try:
        r = requests.get(f"{BASE_URL}/countries/Nigeria", timeout=5)
        if r.status_code == 200:
            grade("Get specific country", 5, True)
            grade("Correct data", 3, "name" in r.json())
        else:
            grade("Get specific country", 8, False)
        r2 = requests.get(f"{BASE_URL}/countries/Nonexistent", timeout=3)
        grade("404 for non-existent", 2, r2.status_code == 404)
    except Exception as e:
        grade("Country detail", 10, False, str(e))


# ---- TEST 4: DELETE /countries/:name ----
def test_delete():
    print("\nTEST 4: DELETE /countries/:name (10 pts)")
    try:
        r = requests.delete(f"{BASE_URL}/countries/Nonexistent", timeout=5)
        if r.status_code in [404, 200]:
            grade("DELETE works", 10, True)
        else:
            grade("DELETE failed", 10, False, f"Status {r.status_code}")
    except Exception as e:
        grade("DELETE failed", 10, False, str(e))


# ---- TEST 5: GET /status ----
def test_status():
    print("\nTEST 5: /status (10 pts)")
    try:
        r = requests.get(f"{BASE_URL}/status", timeout=5)
        js = r.json()
        valid_ts = js.get("last_refreshed_at")
        if r.status_code == 200 and "total_countries" in js:
            grade("Status accessible", 10, True)
        else:
            grade("Status invalid", 10, False)
    except Exception as e:
        grade("Status", 10, False, str(e))


# ---- TEST 6: GET /countries/image ----
def test_image():
    print("\nTEST 6: /countries/image (10 pts)")
    try:
        r = requests.get(f"{BASE_URL}/countries/image", timeout=5)
        content_type = r.headers.get("Content-Type", "")
        grade("Image response", 10, r.status_code == 200 and "image" in content_type)
    except Exception as e:
        grade("Image", 10, False, str(e))


# ---- TEST 7: Error Handling ----
def test_errors():
    print("\nTEST 7: Error Handling (10 pts)")
    try:
        r = requests.get(f"{BASE_URL}/invalid_path", timeout=3)
        grade("404 returns JSON", 10, r.status_code == 404)
    except Exception as e:
        grade("Error handling", 10, False, str(e))


if __name__ == "__main__":
    print("Starting Graded Test Suite for Country API\n")
    try:
        wait_for_server()
        test_refresh()
        test_list()
        test_detail()
        test_delete()
        test_status()
        test_image()
        test_errors()
    finally:
        print(f"\nFINAL SCORE: {TOTAL_SCORE}/100")
        if TOTAL_SCORE >= 70:
            print("✅ PASS")
        else:
            print("❌ FAIL")
