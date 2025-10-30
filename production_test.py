# production_test.py
import requests
import json
import time

BASE_URL = "https://stunning-forgiveness-production.up.railway.app"

def test_all_endpoints():
    print("🚀 Testing Deployed API Endpoints")
    print("=" * 60)
    print(f"Base URL: {BASE_URL}")
    print("=" * 60)
    
    total_score = 0
    max_score = 100
    
    # TEST 1: POST /countries/refresh (25 points)
    print("\n1. Testing POST /countries/refresh (25 points)")
    try:
        start_time = time.time()
        response = requests.post(f"{BASE_URL}/countries/refresh", timeout=60)
        elapsed_time = time.time() - start_time
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ PASS - Status: {response.status_code}, Time: {elapsed_time:.1f}s")
            print(f"   Response: {data}")
            total_score += 25
        else:
            print(f"❌ FAIL - Status: {response.status_code}")
            print(f"   Error: {response.text}")
    except requests.exceptions.Timeout:
        print("❌ FAIL - Request timed out (over 60 seconds)")
    except Exception as e:
        print(f"❌ FAIL - Exception: {e}")
    
    # Wait a moment for refresh to complete
    time.sleep(2)
    
    # TEST 2: GET /countries with filters & sorting (25 points)
    print("\n2. Testing GET /countries with filters & sorting (25 points)")
    tests_passed = 0
    
    # 2.1 Basic GET
    try:
        response = requests.get(f"{BASE_URL}/countries", timeout=10)
        if response.status_code == 200:
            data = response.json()
            if isinstance(data, list) and len(data) > 0:
                tests_passed += 1
                print("✅ Basic GET /countries works")
            else:
                print("❌ Basic GET returned invalid data")
        else:
            print(f"❌ Basic GET failed: {response.status_code}")
    except Exception as e:
        print(f"❌ Basic GET exception: {e}")
    
    # 2.2 Region filter
    try:
        response = requests.get(f"{BASE_URL}/countries?region=Africa", timeout=10)
        if response.status_code == 200:
            data = response.json()
            if all(country.get('region') == 'Africa' for country in data):
                tests_passed += 1
                print("✅ Region filter works")
            else:
                print("❌ Region filter returns wrong data")
        else:
            print(f"❌ Region filter failed: {response.status_code}")
    except Exception as e:
        print(f"❌ Region filter exception: {e}")
    
    # 2.3 Currency filter
    try:
        response = requests.get(f"{BASE_URL}/countries?currency=USD", timeout=10)
        if response.status_code == 200:
            data = response.json()
            if len(data) > 0 and all(country.get('currency_code') == 'USD' for country in data):
                tests_passed += 1
                print("✅ Currency filter works")
            else:
                print("❌ Currency filter returns wrong data")
        else:
            print(f"❌ Currency filter failed: {response.status_code}")
    except Exception as e:
        print(f"❌ Currency filter exception: {e}")
    
    # 2.4 GDP sorting
    try:
        response = requests.get(f"{BASE_URL}/countries?sort=gdp_desc", timeout=10)
        if response.status_code == 200:
            data = response.json()
            countries_with_gdp = [c for c in data if c.get('estimated_gdp') is not None]
            if len(countries_with_gdp) >= 2:
                gdp_values = [float(c['estimated_gdp']) for c in countries_with_gdp]
                if gdp_values == sorted(gdp_values, reverse=True):
                    tests_passed += 1
                    print("✅ GDP sorting works")
                else:
                    print("❌ GDP sorting returns wrong order")
            else:
                print("❌ Not enough countries with GDP for sorting test")
        else:
            print(f"❌ GDP sorting failed: {response.status_code}")
    except Exception as e:
        print(f"❌ GDP sorting exception: {e}")
    
    # Calculate score for test 2 (5 points per passed test)
    test_2_score = tests_passed * 5
    total_score += test_2_score
    print(f"   Test 2 Score: {test_2_score}/20")
    
    # TEST 3: GET /countries/:name (10 points)
    print("\n3. Testing GET /countries/:name (10 points)")
    tests_passed = 0
    
    # 3.1 Get existing country
    try:
        response = requests.get(f"{BASE_URL}/countries/United%20States", timeout=10)
        if response.status_code == 200:
            data = response.json()
            if data.get('name') == 'United States':
                tests_passed += 1
                print("✅ Get existing country works")
            else:
                print("❌ Get existing country returns wrong data")
        else:
            print(f"❌ Get existing country failed: {response.status_code}")
    except Exception as e:
        print(f"❌ Get existing country exception: {e}")
    
    # 3.2 Get non-existent country
    try:
        response = requests.get(f"{BASE_URL}/countries/NonExistentCountry", timeout=10)
        if response.status_code == 404:
            tests_passed += 1
            print("✅ 404 for non-existent country works")
        else:
            print(f"❌ Should return 404, got: {response.status_code}")
    except Exception as e:
        print(f"❌ 404 test exception: {e}")
    
    # Calculate score for test 3
    test_3_score = tests_passed * 5
    total_score += test_3_score
    print(f"   Test 3 Score: {test_3_score}/10")
    
    # TEST 4: DELETE /countries/:name (10 points)
    print("\n4. Testing DELETE /countries/:name (10 points)")
    tests_passed = 0
    
    # 4.1 Delete existing country (use a test country if available, or Ghana)
    try:
        response = requests.delete(f"{BASE_URL}/countries/Ghana", timeout=10)
        if response.status_code in [200, 204]:
            tests_passed += 1
            print("✅ Delete country works")
        else:
            print(f"❌ Delete country failed: {response.status_code}")
    except Exception as e:
        print(f"❌ Delete country exception: {e}")
    
    # 4.2 Delete non-existent country
    try:
        response = requests.delete(f"{BASE_URL}/countries/NonExistentCountry", timeout=10)
        if response.status_code == 404:
            tests_passed += 1
            print("✅ 404 for delete non-existent works")
        else:
            print(f"❌ Delete should return 404, got: {response.status_code}")
    except Exception as e:
        print(f"❌ Delete 404 test exception: {e}")
    
    # Calculate score for test 4
    test_4_score = tests_passed * 5
    total_score += test_4_score
    print(f"   Test 4 Score: {test_4_score}/10")
    
    # TEST 5: GET /status (10 points)
    print("\n5. Testing GET /status (10 points)")
    tests_passed = 0
    
    try:
        response = requests.get(f"{BASE_URL}/status", timeout=10)
        if response.status_code == 200:
            data = response.json()
            if 'total_countries' in data:
                tests_passed += 1
                print("✅ Status returns total_countries")
            if 'last_refreshed_at' in data:
                tests_passed += 1
                print("✅ Status returns last_refreshed_at")
            print(f"   Status data: {data}")
        else:
            print(f"❌ Status endpoint failed: {response.status_code}")
    except Exception as e:
        print(f"❌ Status endpoint exception: {e}")
    
    # Calculate score for test 5 (5 points per field)
    test_5_score = tests_passed * 5
    total_score += test_5_score
    print(f"   Test 5 Score: {test_5_score}/10")
    
    # TEST 6: GET /countries/image (10 points)
    print("\n6. Testing GET /countries/image (10 points)")
    
    try:
        response = requests.get(f"{BASE_URL}/countries/image", timeout=10)
        if response.status_code == 200 and 'image/png' in response.headers.get('content-type', ''):
            total_score += 10
            print("✅ Image endpoint returns PNG image")
        else:
            print(f"❌ Image endpoint failed - Status: {response.status_code}, Content-Type: {response.headers.get('content-type')}")
    except Exception as e:
        print(f"❌ Image endpoint exception: {e}")
    
    # TEST 7: Error Handling (10 points)
    print("\n7. Testing Error Handling (10 points)")
    tests_passed = 0
    
    # Test invalid method
    try:
        response = requests.put(f"{BASE_URL}/countries/refresh", timeout=10)
        if response.status_code == 405:
            tests_passed += 1
            print("✅ 405 for invalid method works")
        else:
            print(f"❌ Should return 405 for PUT, got: {response.status_code}")
    except Exception as e:
        print(f"❌ Invalid method test exception: {e}")
    
    # Test JSON error format
    try:
        response = requests.get(f"{BASE_URL}/countries/NonExistentCountry", timeout=10)
        if (response.status_code == 404 and 
            'application/json' in response.headers.get('content-type', '') and
            'error' in response.json()):
            tests_passed += 1
            print("✅ JSON error format works")
        else:
            print("❌ Error response not in JSON format")
    except Exception as e:
        print(f"❌ JSON error test exception: {e}")
    
    # Calculate score for test 7
    test_7_score = tests_passed * 5
    total_score += test_7_score
    print(f"   Test 7 Score: {test_7_score}/10")
    
    # FINAL RESULTS
    print("\n" + "=" * 60)
    print("🏁 FINAL PRODUCTION TEST RESULTS")
    print("=" * 60)
    print(f"TOTAL SCORE: {total_score}/{max_score}")
    print(f"PASS MARK: 70/100")
    print(f"STATUS: {'PASSED ✅' if total_score >= 70 else 'FAILED ❌'}")
    print("=" * 60)
    
    return total_score

if __name__ == '__main__':
    score = test_all_endpoints()
    
    if score >= 70:
        print("\n🎉 Your API is READY for submission!")
        print("Use this command in Slack:")
        print("/stage-two-backend")
        print("Submit: https://stunning-forgiveness-production.up.railway.app")
    else:
        print("\n⚠️  Some tests failed. Fix issues before submission.")
    
    exit(0 if score >= 70 else 1)