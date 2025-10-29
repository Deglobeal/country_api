import requests
import json
import sys
import os

class CountryAPIGrader:
    def __init__(self, base_url):
        self.base_url = base_url.rstrip('/')
        self.session = requests.Session()
        self.total_score = 0
        self.max_score = 100
        self.results = {}
        
    def log_test(self, test_name, points, success, details=""):
        status = "✓ PASS" if success else "✗ FAIL"
        if success:
            self.total_score += points
            
        self.results[test_name] = {
            "status": status,
            "points": points if success else 0,
            "max_points": points,
            "details": details
        }
        
        print(f"{status} - {test_name}: {points if success else 0}/{points} pts")
        if details:
            print(f"  Details: {details}")
        print()
        
    def test_1_refresh_endpoint(self):
        """TEST 1: POST /countries/refresh (25 points)"""
        print("=" * 50)
        print("TEST 1: POST /countries/refresh (25 points)")
        print("=" * 50)
        
        try:
            response = self.session.post(f"{self.base_url}/countries/refresh")
            
            # Should return 200 (success) or 503 (external API down) but NOT 403
            if response.status_code == 403:
                self.log_test("Refresh endpoint", 25, False, 
                            f"Failed with status 403 (Forbidden) - Check authentication/CSRF")
                return
            
            if response.status_code in [200, 503]:
                # Check if response is JSON
                try:
                    data = response.json()
                    if response.status_code == 200:
                        self.log_test("Refresh endpoint", 25, True, 
                                    f"Success - Created: {data.get('created', 0)}, Updated: {data.get('updated', 0)}")
                    else:
                        self.log_test("Refresh endpoint", 25, True, 
                                    f"External API unavailable but proper 503 response - {data.get('error', '')}")
                except json.JSONDecodeError:
                    self.log_test("Refresh endpoint", 25, False, 
                                "Response is not valid JSON")
            else:
                self.log_test("Refresh endpoint", 25, False, 
                            f"Unexpected status: {response.status_code}")
                
        except Exception as e:
            self.log_test("Refresh endpoint", 25, False, f"Exception: {str(e)}")
    
    def test_2_countries_list_filters_sorting(self):
        """TEST 2: GET /countries (filters & sorting) (25 points)"""
        print("=" * 50)
        print("TEST 2: GET /countries (filters & sorting) (25 points)")
        print("=" * 50)
        
        # Test basic countries list
        try:
            response = self.session.get(f"{self.base_url}/countries")
            
            if response.status_code == 500:
                self.log_test("GET /countries basic", 10, False, "Failed with status 500")
                return
                
            if response.status_code != 200:
                self.log_test("GET /countries basic", 10, False, f"Status: {response.status_code}")
                return
            
            # Check JSON response
            try:
                data = response.json()
                if not isinstance(data, list):
                    self.log_test("GET /countries basic", 10, False, "Response is not a list")
                    return
                    
                self.log_test("GET /countries basic", 10, True, f"Found {len(data)} countries")
                
            except json.JSONDecodeError:
                self.log_test("GET /countries basic", 10, False, "Response is not valid JSON")
                return
        
        except Exception as e:
            self.log_test("GET /countries basic", 10, False, f"Exception: {str(e)}")
            return
        
        # Test region filter
        try:
            response = self.session.get(f"{self.base_url}/countries?region=Africa")
            if response.status_code == 200:
                data = response.json()
                self.log_test("Region filter", 5, True, f"Found {len(data)} African countries")
            else:
                self.log_test("Region filter", 5, False, f"Status: {response.status_code}")
        except Exception as e:
            self.log_test("Region filter", 5, False, f"Exception: {str(e)}")
        
        # Test currency filter
        try:
            response = self.session.get(f"{self.base_url}/countries?currency=USD")
            if response.status_code == 200:
                data = response.json()
                self.log_test("Currency filter", 5, True, f"Found {len(data)} countries with USD")
            else:
                self.log_test("Currency filter", 5, False, f"Status: {response.status_code}")
        except Exception as e:
            self.log_test("Currency filter", 5, False, f"Exception: {str(e)}")
        
        # Test GDP sorting
        try:
            response = self.session.get(f"{self.base_url}/countries?sort=gdp_desc")
            if response.status_code == 200:
                data = response.json()
                # Check if sorting works (first item should have highest GDP)
                if len(data) > 1:
                    gdp_values = [c.get('estimated_gdp') or 0 for c in data if c.get('estimated_gdp') is not None]
                    if gdp_values == sorted(gdp_values, reverse=True):
                        self.log_test("GDP sorting", 5, True, "GDP descending sort working")
                    else:
                        self.log_test("GDP sorting", 5, False, "GDP sorting not working correctly")
                else:
                    self.log_test("GDP sorting", 5, True, "Not enough data to verify sort")
            else:
                self.log_test("GDP sorting", 5, False, f"Status: {response.status_code}")
        except Exception as e:
            self.log_test("GDP sorting", 5, False, f"Exception: {str(e)}")
    
    def test_3_get_country_by_name(self):
        """TEST 3: GET /countries/:name (10 points)"""
        print("=" * 50)
        print("TEST 3: GET /countries/:name (10 points)")
        print("=" * 50)
        
        # First get a real country to test with
        try:
            list_response = self.session.get(f"{self.base_url}/countries")
            if list_response.status_code != 200:
                self.log_test("Get countries list for testing", 5, False, "Could not fetch countries list")
                return
                
            countries = list_response.json()
            if not countries:
                self.log_test("Get existing country", 5, False, "No countries available for testing")
                return
                
            real_country = countries[0]['name']
            
            # Test getting existing country
            response = self.session.get(f"{self.base_url}/countries/{real_country}")
            if response.status_code == 200:
                try:
                    data = response.json()
                    if data.get('name') == real_country:
                        self.log_test("Get existing country", 5, True, f"Successfully fetched {real_country}")
                    else:
                        self.log_test("Get existing country", 5, False, "Country data mismatch")
                except json.JSONDecodeError:
                    self.log_test("Get existing country", 5, False, "Response is not valid JSON")
            else:
                self.log_test("Get existing country", 5, False, f"Status: {response.status_code}")
                
        except Exception as e:
            self.log_test("Get existing country", 5, False, f"Exception: {str(e)}")
        
        # Test 404 for non-existent country
        try:
            response = self.session.get(f"{self.base_url}/countries/NonExistentCountryXYZ123")
            
            if response.status_code == 500:
                self.log_test("404 for non-existent country", 5, False, "Got 500 instead of 404")
                return
                
            if response.status_code == 404:
                # Check if error response is proper JSON
                try:
                    data = response.json()
                    if 'error' in data:
                        self.log_test("404 for non-existent country", 5, True, "Correct 404 with JSON error")
                    else:
                        self.log_test("404 for non-existent country", 5, False, "404 but missing error field")
                except json.JSONDecodeError:
                    self.log_test("404 for non-existent country", 5, False, "404 but response not JSON")
            else:
                self.log_test("404 for non-existent country", 5, False, f"Got {response.status_code} instead of 404")
                
        except Exception as e:
            self.log_test("404 for non-existent country", 5, False, f"Exception: {str(e)}")
    
    def test_4_delete_country(self):
        """TEST 4: DELETE /countries/:name (10 points)"""
        print("=" * 50)
        print("TEST 4: DELETE /countries/:name (10 points)")
        print("=" * 50)
        
        # First ensure we have countries list
        try:
            list_response = self.session.get(f"{self.base_url}/countries")
            if list_response.status_code != 200:
                self.log_test("Get countries list for deletion test", 5, False, "Could not fetch countries list")
                return
                
            self.log_test("Get countries list for deletion test", 5, True, "Countries list available")
            
        except Exception as e:
            self.log_test("Get countries list for deletion test", 5, False, f"Exception: {str(e)}")
            return
        
        # Test 404 for non-existent country deletion
        try:
            response = self.session.delete(f"{self.base_url}/countries/NonExistentCountryXYZ123")
            
            if response.status_code == 403:
                self.log_test("DELETE non-existent country", 5, False, "Got 403 instead of 404")
                return
                
            if response.status_code == 404:
                # Should return JSON error
                try:
                    data = response.json()
                    if 'error' in data:
                        self.log_test("DELETE non-existent country", 5, True, "Correct 404 with JSON error")
                    else:
                        self.log_test("DELETE non-existent country", 5, False, "404 but missing error field")
                except json.JSONDecodeError:
                    self.log_test("DELETE non-existent country", 5, False, "404 but response not JSON")
            elif response.status_code == 204:
                self.log_test("DELETE non-existent country", 5, False, "Got 204 for non-existent country")
            else:
                self.log_test("DELETE non-existent country", 5, False, f"Got {response.status_code} instead of 404")
                
        except Exception as e:
            self.log_test("DELETE non-existent country", 5, False, f"Exception: {str(e)}")
    
    def test_5_status_endpoint(self):
        """TEST 5: GET /status (10 points)"""
        print("=" * 50)
        print("TEST 5: GET /status (10 points)")
        print("=" * 50)
        
        try:
            response = self.session.get(f"{self.base_url}/status")
            
            if response.status_code == 500:
                self.log_test("Status endpoint", 10, False, "Failed with status 500")
                return
                
            if response.status_code != 200:
                self.log_test("Status endpoint", 10, False, f"Status: {response.status_code}")
                return
            
            # Check JSON response structure
            try:
                data = response.json()
                required_fields = ['total_countries']
                missing_fields = [field for field in required_fields if field not in data]
                
                if not missing_fields:
                    self.log_test("Status endpoint", 10, True, 
                                f"Total countries: {data['total_countries']}, "
                                f"Last refresh: {data.get('last_refreshed_at', 'N/A')}")
                else:
                    self.log_test("Status endpoint", 10, False, 
                                f"Missing fields: {missing_fields}")
                    
            except json.JSONDecodeError:
                self.log_test("Status endpoint", 10, False, "Response is not valid JSON")
                
        except Exception as e:
            self.log_test("Status endpoint", 10, False, f"Exception: {str(e)}")
    
    def test_6_countries_image(self):
        """TEST 6: GET /countries/image (10 points)"""
        print("=" * 50)
        print("TEST 6: GET /countries/image (10 points)")
        print("=" * 50)
        
        try:
            response = self.session.get(f"{self.base_url}/countries/image")
            
            if response.status_code == 500:
                self.log_test("Image endpoint", 10, False, "Failed with status 500")
                return
            
            # Can be 200 (image exists) or 404 (no image) - both are valid
            if response.status_code == 200:
                content_type = response.headers.get('content-type', '')
                if 'image' in content_type:
                    self.log_test("Image endpoint", 10, True, "Image served successfully")
                else:
                    self.log_test("Image endpoint", 10, False, f"Wrong content-type: {content_type}")
                    
            elif response.status_code == 404:
                # Should return JSON error
                try:
                    data = response.json()
                    if 'error' in data and 'image' in data['error'].lower():
                        self.log_test("Image endpoint", 10, True, "Correct 404 for missing image")
                    else:
                        self.log_test("Image endpoint", 10, False, "404 but wrong error message")
                except json.JSONDecodeError:
                    self.log_test("Image endpoint", 10, False, "404 but response not JSON")
            else:
                self.log_test("Image endpoint", 10, False, f"Unexpected status: {response.status_code}")
                
        except Exception as e:
            self.log_test("Image endpoint", 10, False, f"Exception: {str(e)}")
    
    def test_7_error_handling_validation(self):
        """TEST 7: Error Handling & Validation (10 points)"""
        print("=" * 50)
        print("TEST 7: Error Handling & Validation (10 points)")
        print("=" * 50)
        
        # Test various error scenarios for JSON format
        
        # Test 404 error format
        try:
            response = self.session.get(f"{self.base_url}/countries/NonExistentCountryXYZ")
            
            if response.status_code == 404:
                content_type = response.headers.get('content-type', '')
                if 'application/json' not in content_type:
                    self.log_test("404 JSON format", 5, False, f"Wrong content-type: {content_type}")
                    return
                    
                try:
                    data = response.json()
                    if 'error' in data:
                        self.log_test("404 JSON format", 5, True, "Correct JSON error format for 404")
                    else:
                        self.log_test("404 JSON format", 5, False, "JSON response missing 'error' field")
                except json.JSONDecodeError:
                    self.log_test("404 JSON format", 5, False, "404 response is not valid JSON")
            else:
                self.log_test("404 JSON format", 5, False, f"Got {response.status_code} instead of 404")
                
        except Exception as e:
            self.log_test("404 JSON format", 5, False, f"Exception: {str(e)}")
        
        # Test other error formats (400, 500, etc.)
        try:
            # Try to trigger a 400 by sending invalid data to refresh (if possible)
            response = self.session.post(f"{self.base_url}/countries/refresh", data="invalid json")
            
            # We don't care about the status code here, just check if it's JSON
            content_type = response.headers.get('content-type', '')
            if 'application/json' in content_type:
                try:
                    data = response.json()
                    self.log_test("Error response JSON format", 5, True, "All error responses in JSON format")
                except json.JSONDecodeError:
                    self.log_test("Error response JSON format", 5, False, "Error response not valid JSON")
            else:
                self.log_test("Error response JSON format", 5, False, f"Error response not JSON, content-type: {content_type}")
                
        except Exception as e:
            self.log_test("Error response JSON format", 5, False, f"Exception: {str(e)}")
    
    def run_all_tests(self):
        """Run all test suites"""
        print("🚀 COUNTRY API COMPREHENSIVE TEST SUITE")
        print("=" * 60)
        print(f"Testing API: {self.base_url}")
        print("=" * 60)
        print()
        
        self.test_1_refresh_endpoint()
        self.test_2_countries_list_filters_sorting()
        self.test_3_get_country_by_name()
        self.test_4_delete_country()
        self.test_5_status_endpoint()
        self.test_6_countries_image()
        self.test_7_error_handling_validation()
        
        # Print final results
        print("=" * 60)
        print("FINAL RESULTS")
        print("=" * 60)
        
        for test_name, result in self.results.items():
            print(f"{result['status']} - {test_name}: {result['points']}/{result['max_points']}")
            if result['details']:
                print(f"  {result['details']}")
        
        print("=" * 60)
        print(f"TOTAL SCORE: {self.total_score}/{self.max_score} ({self.total_score/self.max_score*100:.1f}%)")
        
        # Pass/Fail determination
        pass_mark = 70
        if self.total_score >= pass_mark:
            print(f"STATUS: PASSED ✓ (Need {pass_mark}+ to pass)")
        else:
            print(f"STATUS: FAILED ✗ (Need {pass_mark}+ to pass)")
        
        print("=" * 60)
        
        return self.total_score

def main():
    if len(sys.argv) > 1:
        base_url = sys.argv[1]
    else:
        base_url = "http://localhost:8000"
    
    grader = CountryAPIGrader(base_url)
    score = grader.run_all_tests()
    
    # Exit with code 0 if passed, 1 if failed
    sys.exit(0 if score >= 70 else 1)

if __name__ == "__main__":
    main()