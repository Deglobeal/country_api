import requests
import json
import sys

class BotSimulationTest:
    def __init__(self, base_url):
        self.base_url = base_url.rstrip('/')
        self.session = requests.Session()
        self.results = {
            "test1": {"name": "POST /countries/refresh", "points": 25, "passed": False, "details": ""},
            "test2": {"name": "GET /countries (filters & sorting)", "points": 25, "passed": False, "details": ""},
            "test3": {"name": "GET /countries/:name", "points": 10, "passed": False, "details": ""},
            "test4": {"name": "DELETE /countries/:name", "points": 10, "passed": False, "details": ""},
            "test5": {"name": "GET /status", "points": 10, "passed": False, "details": ""},
            "test6": {"name": "GET /countries/image", "points": 10, "passed": False, "details": ""},
            "test7": {"name": "Error Handling & Validation", "points": 10, "passed": False, "details": ""}
        }
    
    def print_result(self, test_name, passed, details=""):
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"{status}: {test_name}")
        if details:
            print(f"   Details: {details}")
        print()
    
    def test_1_refresh_endpoint(self):
        """TEST 1: POST /countries/refresh (25 points)"""
        print("=" * 60)
        print("TEST 1: POST /countries/refresh (25 points)")
        print("=" * 60)
        
        try:
            response = self.session.post(f"{self.base_url}/countries/refresh/")
            
            # Check status code (should be 200, not 403)
            if response.status_code == 403:
                self.results["test1"]["details"] = f"Failed with status 403 - CSRF/authentication issue"
                self.print_result(self.results["test1"]["name"], False, self.results["test1"]["details"])
                return
            
            # Check if response is JSON
            try:
                data = response.json()
            except:
                self.results["test1"]["details"] = "Response is not valid JSON"
                self.print_result(self.results["test1"]["name"], False, self.results["test1"]["details"])
                return
            
            # Check for success indicators
            if response.status_code == 200:
                if "created" in data or "updated" in data or "total_processed" in data:
                    self.results["test1"]["passed"] = True
                    self.results["test1"]["details"] = f"Success - {data.get('created', 0)} created, {data.get('updated', 0)} updated"
                    self.print_result(self.results["test1"]["name"], True, self.results["test1"]["details"])
                else:
                    self.results["test1"]["details"] = "Missing expected fields in response"
                    self.print_result(self.results["test1"]["name"], False, self.results["test1"]["details"])
            elif response.status_code == 503:
                self.results["test1"]["details"] = "External APIs unavailable - this might be acceptable if APIs are down"
                self.print_result(self.results["test1"]["name"], False, self.results["test1"]["details"])
            else:
                self.results["test1"]["details"] = f"Failed with status {response.status_code}: {data}"
                self.print_result(self.results["test1"]["name"], False, self.results["test1"]["details"])
                
        except Exception as e:
            self.results["test1"]["details"] = f"Exception: {str(e)}"
            self.print_result(self.results["test1"]["name"], False, self.results["test1"]["details"])
    
    def test_2_countries_list(self):
        """TEST 2: GET /countries (filters & sorting) (25 points)"""
        print("=" * 60)
        print("TEST 2: GET /countries (filters & sorting) (25 points)")
        print("=" * 60)
        
        try:
            # Test basic list
            response = self.session.get(f"{self.base_url}/countries/")
            
            if response.status_code == 500:
                self.results["test2"]["details"] = "Failed with status 500 - Internal Server Error"
                self.print_result(self.results["test2"]["name"], False, self.results["test2"]["details"])
                return
            
            if response.status_code != 200:
                self.results["test2"]["details"] = f"Failed with status {response.status_code}"
                self.print_result(self.results["test2"]["name"], False, self.results["test2"]["details"])
                return
            
            # Check if response is JSON array
            try:
                countries = response.json()
                if not isinstance(countries, list):
                    self.results["test2"]["details"] = "Response is not a JSON array"
                    self.print_result(self.results["test2"]["name"], False, self.results["test2"]["details"])
                    return
            except:
                self.results["test2"]["details"] = "Response is not valid JSON"
                self.print_result(self.results["test2"]["name"], False, self.results["test2"]["details"])
                return
            
            # Test region filter
            response_africa = self.session.get(f"{self.base_url}/countries/?region=Africa")
            if response_africa.status_code == 200:
                africa_countries = response_africa.json()
                print(f"   Region filter (Africa): Found {len(africa_countries)} countries")
            else:
                print(f"   Region filter failed: {response_africa.status_code}")
            
            # Test currency filter
            response_currency = self.session.get(f"{self.base_url}/countries/?currency=USD")
            if response_currency.status_code == 200:
                usd_countries = response_currency.json()
                print(f"   Currency filter (USD): Found {len(usd_countries)} countries")
            else:
                print(f"   Currency filter failed: {response_currency.status_code}")
            
            # Test GDP sorting
            response_gdp = self.session.get(f"{self.base_url}/countries/?sort=gdp_desc")
            if response_gdp.status_code == 200:
                gdp_countries = response_gdp.json()
                # Check if sorted by GDP (descending)
                if len(gdp_countries) > 1:
                    gdps = [c.get('estimated_gdp', 0) or 0 for c in gdp_countries if c.get('estimated_gdp') is not None]
                    if gdps == sorted(gdps, reverse=True):
                        print("   GDP sorting: ✅ Correctly sorted descending")
                    else:
                        print("   GDP sorting: ❌ Not correctly sorted")
                else:
                    print("   GDP sorting: ⚠️  Not enough countries with GDP data")
            else:
                print(f"   GDP sorting failed: {response_gdp.status_code}")
            
            # Check country data structure
            if len(countries) > 0:
                country = countries[0]
                required_fields = ['name', 'population', 'currency_code', 'exchange_rate', 'estimated_gdp']
                missing_fields = [field for field in required_fields if field not in country]
                
                if missing_fields:
                    self.results["test2"]["details"] = f"Missing fields in country data: {missing_fields}"
                    self.print_result(self.results["test2"]["name"], False, self.results["test2"]["details"])
                    return
                
                # Check GDP calculation
                if country.get('estimated_gdp') is not None:
                    population = country.get('population', 0)
                    exchange_rate = country.get('exchange_rate', 1)
                    estimated_gdp = country.get('estimated_gdp', 0)
                    
                    # Rough check: GDP should be population * (1000-2000) / exchange_rate
                    expected_min = (population * 1000) / exchange_rate
                    expected_max = (population * 2000) / exchange_rate
                    
                    if expected_min <= estimated_gdp <= expected_max:
                        print("   GDP calculation: ✅ Within expected range")
                    else:
                        print(f"   GDP calculation: ⚠️  Possibly incorrect: {estimated_gdp} not in range [{expected_min}, {expected_max}]")
                
                self.results["test2"]["passed"] = True
                self.results["test2"]["details"] = f"Success - {len(countries)} countries, filters working"
                self.print_result(self.results["test2"]["name"], True, self.results["test2"]["details"])
            else:
                self.results["test2"]["details"] = "No countries returned"
                self.print_result(self.results["test2"]["name"], False, self.results["test2"]["details"])
                
        except Exception as e:
            self.results["test2"]["details"] = f"Exception: {str(e)}"
            self.print_result(self.results["test2"]["name"], False, self.results["test2"]["details"])
    
    def test_3_country_by_name(self):
        """TEST 3: GET /countries/:name (10 points)"""
        print("=" * 60)
        print("TEST 3: GET /countries/:name (10 points)")
        print("=" * 60)
        
        try:
            # First get list to have valid country names
            response = self.session.get(f"{self.base_url}/countries/")
            if response.status_code != 200:
                self.results["test3"]["details"] = "Could not fetch countries list"
                self.print_result(self.results["test3"]["name"], False, self.results["test3"]["details"])
                return
            
            countries = response.json()
            if not countries:
                self.results["test3"]["details"] = "No countries available for testing"
                self.print_result(self.results["test3"]["name"], False, self.results["test3"]["details"])
                return
            
            # Test getting existing country
            test_country = countries[0]['name']
            response = self.session.get(f"{self.base_url}/countries/{test_country}/")
            
            if response.status_code == 200:
                country_data = response.json()
                if country_data.get('name') == test_country:
                    print(f"   Found country: {test_country}")
                    
                    # Test non-existent country
                    response_404 = self.session.get(f"{self.base_url}/countries/NonExistentCountry12345/")
                    if response_404.status_code == 404:
                        # Check if response is JSON
                        try:
                            error_data = response_404.json()
                            if 'error' in error_data:
                                print("   404 for non-existent country: ✅ Correct")
                                self.results["test3"]["passed"] = True
                                self.results["test3"]["details"] = "Success - found country and proper 404"
                                self.print_result(self.results["test3"]["name"], True, self.results["test3"]["details"])
                                return
                            else:
                                print("   404 response missing 'error' field")
                        except:
                            print("   404 response not in JSON format")
                    else:
                        print(f"   Should return 404 for non-existent country, got {response_404.status_code}")
                else:
                    print("   Country name mismatch")
            else:
                print(f"   Failed to get country: {response.status_code}")
            
            self.results["test3"]["details"] = "Did not pass all checks"
            self.print_result(self.results["test3"]["name"], False, self.results["test3"]["details"])
                
        except Exception as e:
            self.results["test3"]["details"] = f"Exception: {str(e)}"
            self.print_result(self.results["test3"]["name"], False, self.results["test3"]["details"])
    
    def test_4_delete_country(self):
        """TEST 4: DELETE /countries/:name (10 points)"""
        print("=" * 60)
        print("TEST 4: DELETE /countries/:name (10 points)")
        print("=" * 60)
        
        try:
            # First get list to have valid country names
            response = self.session.get(f"{self.base_url}/countries/")
            if response.status_code != 200:
                self.results["test4"]["details"] = "Could not fetch countries list"
                self.print_result(self.results["test4"]["name"], False, self.results["test4"]["details"])
                return
            
            countries = response.json()
            if not countries:
                self.results["test4"]["details"] = "No countries available for testing"
                self.print_result(self.results["test4"]["name"], False, self.results["test4"]["details"])
                return
            
            # Test deleting existing country (use last one to avoid breaking other tests)
            test_country = countries[-1]['name']
            response = self.session.delete(f"{self.base_url}/countries/{test_country}/")
            
            if response.status_code in [200, 204]:
                print(f"   Deleted country: {test_country}")
                
                # Verify it's gone
                response_check = self.session.get(f"{self.base_url}/countries/{test_country}/")
                if response_check.status_code == 404:
                    print("   Country successfully removed: ✅")
                else:
                    print(f"   Country still exists after delete: {response_check.status_code}")
                
                # Test deleting non-existent country
                response_404 = self.session.delete(f"{self.base_url}/countries/NonExistentCountry12345/")
                if response_404.status_code == 404:
                    # Check if response is JSON
                    try:
                        error_data = response_404.json()
                        if 'error' in error_data:
                            print("   404 for non-existent country: ✅ Correct")
                            self.results["test4"]["passed"] = True
                            self.results["test4"]["details"] = "Success - deleted country and proper 404"
                            self.print_result(self.results["test4"]["name"], True, self.results["test4"]["details"])
                            
                            # Re-add the country for subsequent tests
                            self.session.post(f"{self.base_url}/countries/refresh/")
                            return
                        else:
                            print("   404 response missing 'error' field")
                    except:
                        print("   404 response not in JSON format")
                else:
                    print(f"   Should return 404 for non-existent country, got {response_404.status_code}")
            elif response.status_code == 403:
                self.results["test4"]["details"] = "Failed with status 403 - Authentication/CSRF issue"
            else:
                print(f"   Delete failed: {response.status_code}")
            
            self.results["test4"]["details"] = "Did not pass all checks"
            self.print_result(self.results["test4"]["name"], False, self.results["test4"]["details"])
                
        except Exception as e:
            self.results["test4"]["details"] = f"Exception: {str(e)}"
            self.print_result(self.results["test4"]["name"], False, self.results["test4"]["details"])
    
    def test_5_status_endpoint(self):
        """TEST 5: GET /status (10 points)"""
        print("=" * 60)
        print("TEST 5: GET /status (10 points)")
        print("=" * 60)
        
        try:
            response = self.session.get(f"{self.base_url}/countries/status/")
            
            if response.status_code == 500:
                self.results["test5"]["details"] = "Failed with status 500 - Internal Server Error"
                self.print_result(self.results["test5"]["name"], False, self.results["test5"]["details"])
                return
            
            if response.status_code != 200:
                self.results["test5"]["details"] = f"Failed with status {response.status_code}"
                self.print_result(self.results["test5"]["name"], False, self.results["test5"]["details"])
                return
            
            # Check if response is JSON
            try:
                data = response.json()
            except:
                self.results["test5"]["details"] = "Response is not valid JSON"
                self.print_result(self.results["test5"]["name"], False, self.results["test5"]["details"])
                return
            
            # Check required fields
            required_fields = ['total_countries', 'last_refreshed_at']
            missing_fields = [field for field in required_fields if field not in data]
            
            if missing_fields:
                self.results["test5"]["details"] = f"Missing fields: {missing_fields}"
                self.print_result(self.results["test5"]["name"], False, self.results["test5"]["details"])
                return
            
            self.results["test5"]["passed"] = True
            self.results["test5"]["details"] = f"Success - {data['total_countries']} countries, last refresh: {data['last_refreshed_at']}"
            self.print_result(self.results["test5"]["name"], True, self.results["test5"]["details"])
                
        except Exception as e:
            self.results["test5"]["details"] = f"Exception: {str(e)}"
            self.print_result(self.results["test5"]["name"], False, self.results["test5"]["details"])
    
    def test_6_image_endpoint(self):
        """TEST 6: GET /countries/image (10 points)"""
        print("=" * 60)
        print("TEST 6: GET /countries/image (10 points)")
        print("=" * 60)
        
        try:
            response = self.session.get(f"{self.base_url}/countries/image/")
            
            if response.status_code == 500:
                self.results["test6"]["details"] = "Failed with status 500 - Internal Server Error"
                self.print_result(self.results["test6"]["name"], False, self.results["test6"]["details"])
                return
            
            if response.status_code != 200:
                self.results["test6"]["details"] = f"Failed with status {response.status_code}"
                self.print_result(self.results["test6"]["name"], False, self.results["test6"]["details"])
                return
            
            # Check if it's an image
            content_type = response.headers.get('Content-Type', '')
            if 'image' in content_type:
                self.results["test6"]["passed"] = True
                self.results["test6"]["details"] = f"Success - image returned ({content_type})"
                self.print_result(self.results["test6"]["name"], True, self.results["test6"]["details"])
            else:
                self.results["test6"]["details"] = f"Not an image - Content-Type: {content_type}"
                self.print_result(self.results["test6"]["name"], False, self.results["test6"]["details"])
                
        except Exception as e:
            self.results["test6"]["details"] = f"Exception: {str(e)}"
            self.print_result(self.results["test6"]["name"], False, self.results["test6"]["details"])
    
    def test_7_error_handling(self):
        """TEST 7: Error Handling & Validation (10 points)"""
        print("=" * 60)
        print("TEST 7: Error Handling & Validation (10 points)")
        print("=" * 60)
        
        try:
            # Test 404 for non-existent country
            response = self.session.get(f"{self.base_url}/countries/NonExistentCountry12345/")
            
            # Check status code
            if response.status_code != 404:
                self.results["test7"]["details"] = f"Should return 404 for non-existent country, got {response.status_code}"
                self.print_result(self.results["test7"]["name"], False, self.results["test7"]["details"])
                return
            
            # Check if response is JSON
            try:
                error_data = response.json()
            except:
                self.results["test7"]["details"] = "Error responses not in JSON format"
                self.print_result(self.results["test7"]["name"], False, self.results["test7"]["details"])
                return
            
            # Check error format
            if 'error' in error_data:
                self.results["test7"]["passed"] = True
                self.results["test7"]["details"] = f"Success - JSON error format: {error_data['error']}"
                self.print_result(self.results["test7"]["name"], True, self.results["test7"]["details"])
            else:
                self.results["test7"]["details"] = "Error response missing 'error' field"
                self.print_result(self.results["test7"]["name"], False, self.results["test7"]["details"])
                
        except Exception as e:
            self.results["test7"]["details"] = f"Exception: {str(e)}"
            self.print_result(self.results["test7"]["name"], False, self.results["test7"]["details"])
    
    def run_all_tests(self):
        """Run all tests and calculate score"""
        print("🚀 STARTING BOT SIMULATION TESTS")
        print(f"📋 Testing URL: {self.base_url}")
        print()
        
        self.test_1_refresh_endpoint()
        self.test_2_countries_list() 
        self.test_3_country_by_name()
        self.test_4_delete_country()
        self.test_5_status_endpoint()
        self.test_6_image_endpoint()
        self.test_7_error_handling()
        
        # Calculate results
        total_score = 0
        max_score = 0
        
        print("=" * 60)
        print("FINAL RESULTS")
        print("=" * 60)
        
        for test_key, test_data in self.results.items():
            points = test_data["points"] if test_data["passed"] else 0
            total_score += points
            max_score += test_data["points"]
            
            status = "✅ PASS" if test_data["passed"] else "❌ FAIL"
            print(f"{status}: {test_data['name']} ({points}/{test_data['points']} pts)")
            if test_data["details"]:
                print(f"   Details: {test_data['details']}")
            print()
        
        print("=" * 60)
        print(f"TOTAL SCORE: {total_score}/{max_score} ({total_score/max_score*100:.1f}%)")
        print(f"PASS MARK: 70/100 (70%)")
        print("=" * 60)
        
        if total_score >= 70:
            print("🎉 STATUS: PASS ✅ - Ready for submission!")
        else:
            print("💥 STATUS: FAIL ❌ - Fix issues before submission!")
        
        return total_score

if __name__ == "__main__":
    # Get base URL from command line or use default
    if len(sys.argv) > 1:
        base_url = sys.argv[1]
    else:
        base_url = "http://localhost:8000"  # Change to your Railway URL when deployed
    
    tester = BotSimulationTest(base_url)
    score = tester.run_all_tests()
    
    # Exit with code 0 if pass, 1 if fail
    sys.exit(0 if score >= 70 else 1)