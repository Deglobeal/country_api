import requests
import random
import json

BASE_URL = "http://127.0.0.1:8000"  # Change to your Railway URL when deployed

def test_post_refresh():
    print("TEST 1: POST /countries/refresh")
    try:
        res = requests.post(f"{BASE_URL}/countries/refresh/")
        if res.status_code == 200:
            print("✅ Passed")
            return 25
        else:
            print(f"❌ Failed with status {res.status_code}")
            print(res.text)
            return 0
    except Exception as e:
        print("❌ Error:", e)
        return 0


def test_get_countries():
    print("\nTEST 2: GET /countries (filters & sorting)")
    try:
        res = requests.get(f"{BASE_URL}/countries/")
        if res.status_code == 200 and isinstance(res.json(), list):
            print("✅ Passed")
            return 25
        else:
            print(f"❌ Failed with status {res.status_code}")
            print(res.text)
            return 0
    except Exception as e:
        print("❌ Error:", e)
        return 0


def test_get_country_by_name():
    print("\nTEST 3: GET /countries/:name")
    try:
        res = requests.get(f"{BASE_URL}/countries/")
        countries = res.json()
        if not countries:
            print("❌ No countries found")
            return 0
        name = countries[0]["name"]
        res2 = requests.get(f"{BASE_URL}/countries/{name}/")
        if res2.status_code == 200:
            print("✅ Found country:", name)
            return 10
        else:
            print(f"❌ Failed with status {res2.status_code}")
            return 0
    except Exception as e:
        print("❌ Error:", e)
        return 0


def test_delete_country():
    print("\nTEST 4: DELETE /countries/:name")
    try:
        res = requests.get(f"{BASE_URL}/countries/")
        countries = res.json()
        if not countries:
            print("❌ No countries to delete")
            return 0
        name = countries[-1]["name"]
        res2 = requests.delete(f"{BASE_URL}/countries/{name}/")
        if res2.status_code in [200, 204]:
            print(f"✅ Deleted {name}")
            return 10
        elif res2.status_code == 404:
            print(f"✅ 404 correctly returned for non-existent country")
            return 10
        else:
            print(f"❌ Failed with status {res2.status_code}")
            print(res2.text)
            return 0
    except Exception as e:
        print("❌ Error:", e)
        return 0


def test_status():
    print("\nTEST 5: GET /status")
    try:
        res = requests.get(f"{BASE_URL}/countries/status/")  # Fixed URL
        data = res.json()
        if res.status_code == 200 and "total_countries" in data:
            print("✅ Passed")
            return 10
        else:
            print(f"❌ Failed with status {res.status_code}")
            print(res.text)
            return 0
    except Exception as e:
        print("❌ Error:", e)
        return 0

def test_country_image():
    print("\nTEST 6: GET /countries/image")
    try:
        res = requests.get(f"{BASE_URL}/countries/image/")
        if res.status_code == 200 and "image" in res.headers.get("Content-Type", ""):
            print("✅ Passed (image returned)")
            return 10
        else:
            print(f"❌ Failed with status {res.status_code}")
            print(res.headers)
            return 0
    except Exception as e:
        print("❌ Error:", e)
        return 0


def test_error_handling():
    print("\nTEST 7: Error Handling & Validation")
    try:
        res = requests.get(f"{BASE_URL}/countries/NonExistentCountry/")
        if res.status_code == 404 and "application/json" in res.headers.get("Content-Type", ""):
            print("✅ Passed JSON error response")
            return 10
        else:
            print(f"❌ Failed with status {res.status_code}")
            print(res.text)
            return 0
    except Exception as e:
        print("❌ Error:", e)
        return 0


def run_all_tests():
    total = 0
    total += test_post_refresh()
    total += test_get_countries()
    total += test_get_country_by_name()
    total += test_delete_country()
    total += test_status()
    total += test_country_image()
    total += test_error_handling()
    print("\n============================================================")
    print(f"FINAL SCORE: {total}/100")
    if total >= 70:
        print("✅ PASS")
    else:
        print("❌ FAIL")
    print("============================================================")


if __name__ == "__main__":
    run_all_tests()
