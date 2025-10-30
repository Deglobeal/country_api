import requests
import json
import time
import os
from PIL import Image
import io

# Configuration
BASE_URL = "http://localhost:8000"  # Change to your production URL
TEST_COUNTRY_NAME = "Nigeria"  # A country that exists in the API

def print_test_result(test_name, passed, message=""):
    """Helper function to print test results"""
    status = "✓ PASS" if passed else "✗ FAIL"
    print(f"{status}: {test_name}")
    if message:
        print(f"   {message}")

def test_refresh_endpoint():
    """Test 1: POST /countries/refresh"""
    print("\n" + "="*50)
    print("TEST 1: POST /countries/refresh")
    print("="*50)
    
    try:
        start_time = time.time()
        response = requests.post(f"{BASE_URL}/countries/refresh", timeout=60)
        end_time = time.time()
        
        response_time = end_time - start_time
        
        # Check if request didn't timeout
        if response_time > 30:
            print_test_result("Refresh endpoint timed out", False, f"Response time: {response_time:.2f}s")
            return False
        
        # Check status code
        if response.status_code == 200:
            data = response.json()
            print_test_result("Refresh endpoint completed successfully", True, 
                           f"Response: {data.get('message', 'Unknown')}")
            return True
        elif response.status_code == 503:
            print_test_result("External API unavailable", False, 
                           "Countries or Exchange API is down")
            return False
        else:
            print_test_result(f"Unexpected status code: {response.status_code}", False,
                           f"Response: {response.text}")
            return False
            
    except requests.exceptions.Timeout:
        print_test_result("Refresh endpoint timed out", False, "Request took longer than 60 seconds")
        return False
    except Exception as e:
        print_test_result(f"Refresh endpoint failed: {str(e)}", False)
        return False

def test_get_countries_filters_sorting():
    """Test 2: GET /countries with filters and sorting"""
    print("\n" + "="*50)
    print("TEST 2: GET /countries (filters & sorting)")
    print("="*50)
    
    tests_passed = 0
    total_tests = 5
    
    try:
        # Test basic GET
        response = requests.get(f"{BASE_URL}/countries")
        if response.status_code == 200:
            data = response.json()
            if isinstance(data, list) and len(data) > 0:
                print_test_result("Basic GET /countries works", True)
                tests_passed += 1
            else:
                print_test_result("Basic GET /countries works", False, "Invalid response format")
        else:
            print_test_result("Basic GET /countries works", False, f"Status: {response.status_code}")
        
        # Test response structure
        if tests_passed > 0:
            country = data[0] # type: ignore
            required_fields = ['id', 'name', 'capital', 'region', 'population', 
                             'currency_code', 'exchange_rate', 'estimated_gdp', 
                             'flag_url', 'last_refreshed_at']
            missing_fields = [field for field in required_fields if field not in country]
            if not missing_fields:
                print_test_result("Returns correct structure", True)
                tests_passed += 1
            else:
                print_test_result("Returns correct structure", False, f"Missing fields: {missing_fields}")
        
        # Test filter by region
        response = requests.get(f"{BASE_URL}/countries?region=Africa")
        if response.status_code == 200:
            data = response.json()
            if all(country.get('region') == 'Africa' for country in data if data):
                print_test_result("Filter by region works", True)
                tests_passed += 1
            else:
                print_test_result("Filter by region works", False, "Not all countries are from Africa")
        else:
            print_test_result("Filter by region works", False, f"Status: {response.status_code}")
        
        # Test filter by currency
        response = requests.get(f"{BASE_URL}/countries?currency=USD")
        if response.status_code == 200:
            data = response.json()
            if all(country.get('currency_code') == 'USD' for country in data if data):
                print_test_result("Filter by currency works", True)
                tests_passed += 1
            else:
                print_test_result("Filter by currency works", False, "Not all countries use USD")
        else:
            print_test_result("Filter by currency works", False, f"Status: {response.status_code}")
        
        # Test sorting by GDP
        response = requests.get(f"{BASE_URL}/countries?sort=gdp_desc")
        if response.status_code == 200:
            data = response.json()
            # Filter out countries with null GDP
            countries_with_gdp = [c for c in data if c.get('estimated_gdp') is not None]
            
            if len(countries_with_gdp) >= 2:
                # Check if GDPs are in descending order
                gdps = [c['estimated_gdp'] for c in countries_with_gdp]
                is_descending = all(gdps[i] >= gdps[i+1] for i in range(len(gdps)-1))
                
                if is_descending:
                    print_test_result("Sorting by GDP returns correct order", True)
                    tests_passed += 1
                else:
                    print_test_result("Sorting by GDP returns correct order", False, 
                                   "GDP values not in descending order")
            else:
                print_test_result("Sorting by GDP returns correct order", False, 
                               "Not enough countries with GDP data")
        else:
            print_test_result("Sorting by GDP returns correct order", False, 
                           f"Status: {response.status_code}")
        
        print(f"\nScore: {tests_passed}/{total_tests}")
        return tests_passed >= 4  # At least 4/5 tests should pass
        
    except Exception as e:
        print_test_result(f"GET countries tests failed: {str(e)}", False)
        return False

def test_get_country_by_name():
    """Test 3: GET /countries/:name"""
    print("\n" + "="*50)
    print("TEST 3: GET /countries/:name")
    print("="*50)
    
    tests_passed = 0
    total_tests = 3
    
    try:
        # Test get specific country
        response = requests.get(f"{BASE_URL}/countries/{TEST_COUNTRY_NAME}")
        if response.status_code == 200:
            data = response.json()
            if data.get('name', '').lower() == TEST_COUNTRY_NAME.lower():
                print_test_result("Get specific country works", True)
                tests_passed += 1
            else:
                print_test_result("Get specific country works", False, "Country name doesn't match")
        else:
            print_test_result("Get specific country works", False, f"Status: {response.status_code}")
        
        # Test returns correct country data
        if tests_passed > 0:
            required_fields = ['name', 'population', 'currency_code', 'exchange_rate', 'estimated_gdp']
            missing_fields = [field for field in required_fields if field not in data] # type: ignore
            if not missing_fields:
                print_test_result("Returns correct country data", True)
                tests_passed += 1
            else:
                print_test_result("Returns correct country data", False, f"Missing: {missing_fields}")
        
        # Test 404 for non-existent country
        response = requests.get(f"{BASE_URL}/countries/NonExistentCountry12345")
        if response.status_code == 404:
            data = response.json()
            if data.get('error') == 'Country not found':
                print_test_result("Returns 404 for non-existent country", True)
                tests_passed += 1
            else:
                print_test_result("Returns 404 for non-existent country", False, 
                               "Wrong error message")
        else:
            print_test_result("Returns 404 for non-existent country", False, 
                           f"Status: {response.status_code}")
        
        print(f"\nScore: {tests_passed}/{total_tests}")
        return tests_passed == total_tests
        
    except Exception as e:
        print_test_result(f"Get country by name tests failed: {str(e)}", False)
        return False

def test_delete_country():
    """Test 4: DELETE /countries/:name"""
    print("\n" + "="*50)
    print("TEST 4: DELETE /countries/:name")
    print("="*50)
    
    tests_passed = 0
    total_tests = 2
    
    try:
        # First, ensure the country exists by refreshing data
        requests.post(f"{BASE_URL}/countries/refresh", timeout=60)
        time.sleep(2)  # Wait for refresh to complete
        
        # Test delete country
        response = requests.delete(f"{BASE_URL}/countries/{TEST_COUNTRY_NAME}")
        
        if response.status_code == 204:
            print_test_result("Delete country works", True)
            tests_passed += 1
        elif response.status_code == 405:
            print_test_result("Delete country works", False, "Method not allowed (405)")
        else:
            print_test_result("Delete country works", False, f"Status: {response.status_code}")
        
        # Test 404 for non-existent country after deletion
        response = requests.delete(f"{BASE_URL}/countries/{TEST_COUNTRY_NAME}")
        if response.status_code == 404:
            data = response.json()
            if data.get('error') == 'Country not found':
                print_test_result("Returns 404 after deletion", True)
                tests_passed += 1
            else:
                print_test_result("Returns 404 after deletion", False, "Wrong error message")
        else:
            print_test_result("Returns 404 after deletion", False, f"Status: {response.status_code}")
        
        print(f"\nScore: {tests_passed}/{total_tests}")
        return tests_passed == total_tests
        
    except Exception as e:
        print_test_result(f"Delete country tests failed: {str(e)}", False)
        return False

def test_status_endpoint():
    """Test 5: GET /status"""
    print("\n" + "="*50)
    print("TEST 5: GET /status")
    print("="*50)
    
    tests_passed = 0
    total_tests = 4
    
    try:
        response = requests.get(f"{BASE_URL}/status")
        
        # Test endpoint accessible
        if response.status_code == 200:
            print_test_result("Status endpoint accessible", True)
            tests_passed += 1
        else:
            print_test_result("Status endpoint accessible", False, f"Status: {response.status_code}")
            return False
        
        data = response.json()
        
        # Test total_countries field
        if 'total_countries' in data:
            print_test_result("Returns total_countries field", True)
            tests_passed += 1
        else:
            print_test_result("Returns total_countries field", False, "Missing field")
        
        # Test last_refreshed_at field
        if 'last_refreshed_at' in data:
            print_test_result("Returns last_refreshed_at field", True)
            tests_passed += 1
        else:
            print_test_result("Returns last_refreshed_at field", False, "Missing field")
        
        # Test timestamp format (basic check)
        if data.get('last_refreshed_at'):
            try:
                # Just check if it's a string that looks like a timestamp
                timestamp = data['last_refreshed_at']
                if 'T' in timestamp and 'Z' in timestamp:
                    print_test_result("Valid timestamp format", True)
                    tests_passed += 1
                else:
                    print_test_result("Valid timestamp format", False, "Invalid format")
            except:
                print_test_result("Valid timestamp format", False, "Invalid timestamp")
        else:
            print_test_result("Valid timestamp format", False, "No timestamp")
        
        print(f"\nScore: {tests_passed}/{total_tests}")
        return tests_passed == total_tests
        
    except Exception as e:
        print_test_result(f"Status endpoint tests failed: {str(e)}", False)
        return False

def test_countries_image():
    """Test 6: GET /countries/image"""
    print("\n" + "="*50)
    print("TEST 6: GET /countries/image")
    print("="*50)
    
    try:
        # First refresh to generate image
        requests.post(f"{BASE_URL}/countries/refresh", timeout=60)
        time.sleep(2)  # Wait for image generation
        
        response = requests.get(f"{BASE_URL}/countries/image")
        
        if response.status_code == 200:
            # Check if it's actually an image
            content_type = response.headers.get('content-type', '')
            if 'image' in content_type:
                # Try to open with PIL to verify it's a valid image
                try:
                    image = Image.open(io.BytesIO(response.content))
                    print_test_result("Image endpoint returns valid image", True)
                    return True
                except:
                    print_test_result("Image endpoint returns valid image", False, 
                                   "Invalid image data")
                    return False
            else:
                print_test_result("Image endpoint returns image", False, 
                               f"Wrong content type: {content_type}")
                return False
        else:
            print_test_result("Image endpoint accessible", False, 
                           f"Status: {response.status_code}, Response: {response.text}")
            return False
            
    except Exception as e:
        print_test_result(f"Image endpoint test failed: {str(e)}", False)
        return False

def test_error_handling():
    """Test 7: Error Handling & Validation"""
    print("\n" + "="*50)
    print("TEST 7: Error Handling & Validation")
    print("="*50)
    
    tests_passed = 0
    total_tests = 3
    
    try:
        # Test 404 error format
        response = requests.get(f"{BASE_URL}/countries/NonExistentCountryXYZ")
        if response.status_code == 404:
            data = response.json()
            if data.get('error') == 'Country not found':
                print_test_result("404 errors return proper JSON format", True)
                tests_passed += 1
            else:
                print_test_result("404 errors return proper JSON format", False, 
                               "Wrong error structure")
        else:
            print_test_result("404 errors return proper JSON format", False, 
                           f"Status: {response.status_code}")
        
        # Test consistent error response structure
        response = requests.get(f"{BASE_URL}/invalid-endpoint")
        if response.status_code == 404:
            data = response.json()
            if 'error' in data:
                print_test_result("Consistent error response structure", True)
                tests_passed += 1
            else:
                print_test_result("Consistent error response structure", False, 
                               "Missing 'error' field")
        else:
            # Some other error, but should still have consistent structure
            data = response.json()
            if 'error' in data:
                print_test_result("Consistent error response structure", True)
                tests_passed += 1
            else:
                print_test_result("Consistent error response structure", False, 
                               "No consistent error structure")
        
        # Test error handling implemented
        # Try to access with invalid method
        response = requests.patch(f"{BASE_URL}/countries")
        data = response.json()
        if 'error' in data:
            print_test_result("Error handling implemented", True)
            tests_passed += 1
        else:
            print_test_result("Error handling implemented", False, "No error response")
        
        print(f"\nScore: {tests_passed}/{total_tests}")
        return tests_passed == total_tests
        
    except Exception as e:
        print_test_result(f"Error handling tests failed: {str(e)}", False)
        return False

def run_all_tests():
    """Run all tests and calculate final score"""
    print("🚀 STARTING BOT CHECK TESTS")
    print("="*60)
    
    test_results = []
    
    # Run all tests
    test_results.append(("POST /countries/refresh", test_refresh_endpoint()))
    test_results.append(("GET /countries (filters & sorting)", test_get_countries_filters_sorting()))
    test_results.append(("GET /countries/:name", test_get_country_by_name()))
    test_results.append(("DELETE /countries/:name", test_delete_country()))
    test_results.append(("GET /status", test_status_endpoint()))
    test_results.append(("GET /countries/image", test_countries_image()))
    test_results.append(("Error Handling & Validation", test_error_handling()))
    
    # Calculate scores (matching bot scoring)
    scores = {
        "POST /countries/refresh": 25,
        "GET /countries (filters & sorting)": 25, 
        "GET /countries/:name": 10,
        "DELETE /countries/:name": 10,
        "GET /status": 10,
        "GET /countries/image": 10,
        "Error Handling & Validation": 10
    }
    
    total_score = 0
    max_score = 100
    
    print("\n" + "="*60)
    print("FINAL RESULTS")
    print("="*60)
    
    for test_name, passed in test_results:
        score = scores[test_name] if passed else 0
        total_score += score
        status = "✓ PASS" if passed else "✗ FAIL"
        print(f"{status}: {test_name} - {score}/{scores[test_name]} points")
    
    print("\n" + "="*60)
    print(f"TOTAL SCORE: {total_score}/{max_score} ({total_score}%)")
    
    if total_score >= 70:
        print("🎉 STATUS: PASSED - Ready for submission!")
        return True
    else:
        print("❌ STATUS: FAILED - Fix issues before submission")
        return False

def test_gdp_calculation():
    """Additional test: Verify GDP calculation formula"""
    print("\n" + "="*50)
    print("ADDITIONAL TEST: GDP Calculation")
    print("="*50)
    
    try:
        # Get a country with GDP data
        response = requests.get(f"{BASE_URL}/countries?currency=USD")
        if response.status_code == 200:
            countries = response.json()
            if countries:
                country = countries[0]
                population = country.get('population')
                exchange_rate = country.get('exchange_rate')
                estimated_gdp = country.get('estimated_gdp')
                
                if all([population, exchange_rate, estimated_gdp]):
                    # The GDP should be roughly: population × (1000-2000) ÷ exchange_rate
                    # Since we don't know the exact random multiplier, check if it's in reasonable range
                    min_possible = (population * 1000) / exchange_rate
                    max_possible = (population * 2000) / exchange_rate
                    
                    if min_possible <= estimated_gdp <= max_possible:
                        print_test_result("GDP calculation formula correct", True)
                        return True
                    else:
                        print_test_result("GDP calculation formula correct", False,
                                       f"GDP {estimated_gdp} outside expected range [{min_possible}, {max_possible}]")
                        return False
                else:
                    print_test_result("GDP calculation formula correct", False, "Missing required fields")
                    return False
            else:
                print_test_result("GDP calculation formula correct", False, "No countries with GDP data")
                return False
        else:
            print_test_result("GDP calculation formula correct", False, f"Status: {response.status_code}")
            return False
    except Exception as e:
        print_test_result(f"GDP calculation test failed: {str(e)}", False)
        return False

if __name__ == "__main__":
    # Check if server is running
    try:
        response = requests.get(f"{BASE_URL}/status", timeout=5)
        print("✅ Server is running")
    except:
        print("❌ Server is not running. Please start the Django server first.")
        print(f"   Command: python manage.py runserver")
        exit(1)
    
    # Run main tests
    success = run_all_tests()
    
    # Run additional GDP test
    test_gdp_calculation()
    
    if success:
        print("\n🎯 All bot checks passed! You can now submit your application.")
    else:
        print("\n🔧 Fix the failing tests before submission.")
        print("\nCommon issues to check:")
        print("1. POST /countries/refresh - Ensure external APIs are accessible")
        print("2. GDP sorting - Make sure null GDP values are handled correctly")
        print("3. DELETE method - Implement proper DELETE view method")
        print("4. Image generation - Ensure PIL/Pillow is installed and working")
        print("5. Error responses - All errors should return consistent JSON format")