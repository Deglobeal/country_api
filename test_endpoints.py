import requests
import json
import time
import sys

class CountryAPITester:
    def __init__(self, base_url):
        self.base_url = base_url.rstrip('/')
        self.session = requests.Session()
        
    def print_result(self, test_name, success, response=None, expected_code=None):
        status = "✓ PASS" if success else "✗ FAIL"
        color = "\033[92m" if success else "\033[91m"
        reset = "\033[0m"
        
        print(f"{color}{status}{reset} - {test_name}")
        
        if response is not None:
            print(f"  Status Code: {response.status_code} (Expected: {expected_code})")
            if not success:
                print(f"  Response: {response.text}")
        print()

    def test_refresh_endpoint(self):
        """Test POST /countries/refresh"""
        print("Testing POST /countries/refresh...")
        try:
            response = self.session.post(f"{self.base_url}/countries/refresh")
            success = response.status_code in [200, 503]  # 503 if external APIs are down
            self.print_result("Refresh countries", success, response, 200)
            return response
        except Exception as e:
            self.print_result("Refresh countries", False)
            print(f"  Exception: {e}")
            return None

    def test_list_countries(self):
        """Test GET /countries"""
        print("Testing GET /countries...")
        try:
            response = self.session.get(f"{self.base_url}/countries")
            success = response.status_code == 200
            self.print_result("List all countries", success, response, 200)
            
            if success:
                data = response.json()
                print(f"  Found {len(data)} countries")
                if len(data) > 0:
                    print(f"  Sample country: {data[0]['name']}")
            return response
        except Exception as e:
            self.print_result("List all countries", False)
            print(f"  Exception: {e}")
            return None

    def test_list_countries_with_filters(self):
        """Test GET /countries with filters"""
        print("Testing GET /countries with filters...")
        
        # Test region filter
        try:
            response = self.session.get(f"{self.base_url}/countries?region=Africa")
            success = response.status_code == 200
            self.print_result("Filter by region (Africa)", success, response, 200)
            
            if success:
                data = response.json()
                print(f"  Found {len(data)} African countries")
        except Exception as e:
            self.print_result("Filter by region", False)
            print(f"  Exception: {e}")

        # Test sorting
        try:
            response = self.session.get(f"{self.base_url}/countries?sort=gdp_desc")
            success = response.status_code == 200
            self.print_result("Sort by GDP descending", success, response, 200)
        except Exception as e:
            self.print_result("Sort by GDP", False)
            print(f"  Exception: {e}")

    def test_get_country(self):
        """Test GET /countries/:name"""
        print("Testing GET /countries/:name...")
        
        # First get a real country name from the list
        list_response = self.session.get(f"{self.base_url}/countries")
        if list_response.status_code == 200:
            countries = list_response.json()
            if len(countries) > 0:
                real_country = countries[0]['name']
                
                # Test existing country
                try:
                    response = self.session.get(f"{self.base_url}/countries/{real_country}")
                    success = response.status_code == 200
                    self.print_result(f"Get existing country ({real_country})", success, response, 200)
                except Exception as e:
                    self.print_result("Get existing country", False)
                    print(f"  Exception: {e}")
        
        # Test non-existent country
        try:
            response = self.session.get(f"{self.base_url}/countries/NonExistentCountryXYZ")
            success = response.status_code == 404
            self.print_result("Get non-existent country (404 test)", success, response, 404)
            
            if success:
                data = response.json()
                if 'error' in data and data['error'] == 'Country not found':
                    print("  ✓ Correct error message")
                else:
                    print("  ✗ Wrong error message format")
        except Exception as e:
            self.print_result("Get non-existent country", False)
            print(f"  Exception: {e}")

    def test_delete_country(self):
        """Test DELETE /countries/:name"""
        print("Testing DELETE /countries/:name...")
        
        # Note: This might fail if authentication is required
        try:
            response = self.session.delete(f"{self.base_url}/countries/TestCountry")
            # Accept 204 (success), 404 (not found), or 403 (forbidden) as expected behaviors
            success = response.status_code in [204, 404, 403]
            self.print_result("Delete country", success, response, "204/404/403")
            
            if response.status_code == 404:
                data = response.json()
                if 'error' in data and data['error'] == 'Country not found':
                    print("  ✓ Correct 404 error message")
            elif response.status_code == 403:
                print("  ✓ 403 Forbidden (expected if auth required)")
            elif response.status_code == 204:
                print("  ✓ Country deleted successfully")
                
        except Exception as e:
            self.print_result("Delete country", False)
            print(f"  Exception: {e}")

    def test_status_endpoint(self):
        """Test GET /status"""
        print("Testing GET /status...")
        try:
            response = self.session.get(f"{self.base_url}/status")
            success = response.status_code == 200
            self.print_result("Get status", success, response, 200)
            
            if success:
                data = response.json()
                required_fields = ['total_countries', 'last_refreshed_at']
                missing_fields = [field for field in required_fields if field not in data]
                
                if not missing_fields:
                    print("  ✓ All required fields present")
                    print(f"  Total countries: {data['total_countries']}")
                    print(f"  Last refreshed: {data['last_refreshed_at']}")
                else:
                    print(f"  ✗ Missing fields: {missing_fields}")
        except Exception as e:
            self.print_result("Get status", False)
            print(f"  Exception: {e}")

    def test_countries_image(self):
        """Test GET /countries/image"""
        print("Testing GET /countries/image...")
        try:
            response = self.session.get(f"{self.base_url}/countries/image")
            
            # Could be 200 (image) or 404 (no image)
            if response.status_code == 200:
                self.print_result("Get countries image", True, response, 200)
                print("  ✓ Image returned successfully")
                print(f"  Content-Type: {response.headers.get('content-type')}")
            elif response.status_code == 404:
                data = response.json()
                if 'error' in data and data['error'] == 'Summary image not found':
                    self.print_result("Get countries image", True, response, 404)
                    print("  ✓ Correct error for missing image")
                else:
                    self.print_result("Get countries image", False, response, 404)
            else:
                self.print_result("Get countries image", False, response, "200/404")
                
        except Exception as e:
            self.print_result("Get countries image", False)
            print(f"  Exception: {e}")

    def test_error_responses_format(self):
        """Test that error responses are in JSON format"""
        print("Testing error responses format...")
        
        # Test 404 error format
        try:
            response = self.session.get(f"{self.base_url}/countries/NonExistentCountryXYZ")
            if response.status_code == 404:
                content_type = response.headers.get('content-type', '')
                if 'application/json' in content_type:
                    try:
                        data = response.json()
                        if 'error' in data:
                            self.print_result("404 JSON error format", True, response, 404)
                            print("  ✓ Correct JSON error format")
                        else:
                            self.print_result("404 JSON error format", False, response, 404)
                    except json.JSONDecodeError:
                        self.print_result("404 JSON error format", False, response, 404)
                        print("  ✗ Response is not valid JSON")
                else:
                    self.print_result("404 JSON error format", False, response, 404)
                    print(f"  ✗ Wrong content-type: {content_type}")
        except Exception as e:
            self.print_result("404 error format", False)
            print(f"  Exception: {e}")

    def run_all_tests(self):
        """Run all tests"""
        print("=" * 60)
        print("COUNTRY API TEST SUITE")
        print("=" * 60)
        print(f"Testing base URL: {self.base_url}")
        print()
        
        # Run tests in logical order
        self.test_refresh_endpoint()
        time.sleep(2)  # Wait for refresh to complete
        
        self.test_list_countries()
        self.test_list_countries_with_filters()
        self.test_get_country()
        self.test_delete_country()
        self.test_status_endpoint()
        self.test_countries_image()
        self.test_error_responses_format()
        
        print("=" * 60)
        print("TESTING COMPLETE")
        print("=" * 60)

if __name__ == "__main__":
    # Get base URL from command line or use default
    if len(sys.argv) > 1:
        base_url = sys.argv[1]
    else:
        base_url = "http://localhost:8000"  # Default Django development server
    
    tester = CountryAPITester(base_url)
    tester.run_all_tests()