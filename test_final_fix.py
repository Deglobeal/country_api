import json
import requests
import unittest
from datetime import datetime
from PIL import Image
from io import BytesIO

BASE_URL = "http://localhost:8000/countries"

class CountryAPITestCase(unittest.TestCase):
    
    def setUp(self):
        # Refresh countries before each test
        try:
            response = requests.post(f"{BASE_URL}/refresh/", timeout=30)
            self.refresh_response = response
        except requests.exceptions.RequestException as e:
            self.refresh_response = None
            print(f"Failed to refresh countries: {e}")
    
    # TEST 1: POST /countries/refresh
    def test_refresh_endpoint(self):
        if not self.refresh_response:
            self.fail("Refresh endpoint failed to respond")
        
        self.assertEqual(self.refresh_response.status_code, 200, "Refresh endpoint should return 200 OK")
        self.assertLess(self.refresh_response.elapsed.total_seconds(), 30, "Refresh should complete within 30 seconds")
        
        response_data = self.refresh_response.json()
        self.assertIn("message", response_data, "Refresh response should contain a message")
        self.assertIn("total_countries", response_data, "Refresh response should contain total_countries")
    
    # TEST 2: GET /countries (filters & sorting)
    def test_get_countries(self):
        # Basic GET
        response = requests.get(f"{BASE_URL}/")
        self.assertEqual(response.status_code, 200, "GET /countries should return 200 OK")
        
        # Check response structure
        data = response.json()
        self.assertIsInstance(data, list, "Response should be a list of countries")
        if data:
            country = data[0]
            required_fields = ['id', 'name', 'capital', 'region', 'population', 
                              'currency_code', 'exchange_rate', 'estimated_gdp', 
                              'flag_url', 'last_refreshed_at']
            missing_fields = [field for field in required_fields if field not in country]
            self.assertEqual(len(missing_fields), 0, f"Missing fields: {missing_fields}")
        
        # Filter by region
        response = requests.get(f"{BASE_URL}/?region=Africa")
        self.assertEqual(response.status_code, 200, "Filter by region should return 200 OK")
        data = response.json()
        if data:
            regions = [country.get('region') for country in data]
            self.assertTrue(all(region == "Africa" for region in regions if region), "All countries should be from Africa")
        
        # Filter by currency
        response = requests.get(f"{BASE_URL}/?currency=USD")
        self.assertEqual(response.status_code, 200, "Filter by currency should return 200 OK")
        data = response.json()
        if data:
            currencies = [country.get('currency_code') for country in data]
            self.assertTrue(all(currency == "USD" for currency in currencies if currency), "All countries should use USD")
        
        # Sort by GDP
        response = requests.get(f"{BASE_URL}/?sort=gdp_desc")
        self.assertEqual(response.status_code, 200, "Sorting by GDP should return 200 OK")
        data = response.json()
        if len(data) >= 2:
            gdps = [country.get('estimated_gdp') for country in data if country.get('estimated_gdp') is not None]
            self.assertTrue(all(gdps[i] >= gdps[i+1] for i in range(len(gdps)-1)), "GDP values should be in descending order")
    
    # TEST 3: GET /countries/:name
    def test_get_country_by_name(self):
        # Get existing country - USE THE CORRECT NAME
        response = requests.get(f"{BASE_URL}/United States of America/")
        self.assertEqual(response.status_code, 200, "Should return 200 OK for existing country")
        
        # Check response structure
        data = response.json()
        required_fields = ['id', 'name', 'capital', 'region', 'population', 
                          'currency_code', 'exchange_rate', 'estimated_gdp', 
                          'flag_url', 'last_refreshed_at']
        missing_fields = [field for field in required_fields if field not in data]
        self.assertEqual(len(missing_fields), 0, f"Missing fields: {missing_fields}")
        
        # Get non-existent country
        response = requests.get(f"{BASE_URL}/NonExistentCountry/")
        self.assertEqual(response.status_code, 404, "Should return 404 for non-existent country")
        data = response.json()
        self.assertIn("error", data, "Response should contain error message")
        self.assertEqual(data["error"], "Country not found", "Error message should be 'Country not found'")
    
    # TEST 4: DELETE /countries/:name
    def test_delete_country(self):
        # Use a different country for deletion test to avoid conflicts
        country_name = "Albania"
        
        # First, ensure the country exists
        response = requests.get(f"{BASE_URL}/{country_name}/")
        self.assertEqual(response.status_code, 200, f"{country_name} should exist before deletion")
        
        # Delete the country
        delete_response = requests.delete(f"{BASE_URL}/{country_name}/")
        self.assertEqual(delete_response.status_code, 204, "DELETE should return 204 No Content")
        
        # Verify deletion
        response = requests.get(f"{BASE_URL}/{country_name}/")
        self.assertEqual(response.status_code, 404, "Should return 404 after deletion")
        data = response.json()
        self.assertIn("error", data, "Response should contain error message")
        self.assertEqual(data["error"], "Country not found", "Error message should be 'Country not found'")
        
        # Try to delete non-existent country
        response = requests.delete(f"{BASE_URL}/NonExistentCountry/")
        self.assertEqual(response.status_code, 404, "Should return 404 for non-existent country")
        data = response.json()
        self.assertIn("error", data, "Response should contain error message")
        self.assertEqual(data["error"], "Country not found", "Error message should be 'Country not found'")
    
    # TEST 5: GET /status
    def test_status_endpoint(self):
        response = requests.get(f"{BASE_URL}/status/")
        self.assertEqual(response.status_code, 200, "Status endpoint should return 200 OK")
        
        data = response.json()
        self.assertIn("total_countries", data, "Response should contain total_countries")
        self.assertIn("last_refreshed_at", data, "Response should contain last_refreshed_at")
        
        # Check timestamp format
        try:
            datetime.fromisoformat(data["last_refreshed_at"].replace('Z', '+00:00'))
        except ValueError:
            self.fail("last_refreshed_at should be in valid ISO 8601 format")
    
    # TEST 6: GET /countries/image
    def test_countries_image(self):
        # Generate image by refreshing countries
        response = requests.post(f"{BASE_URL}/refresh/")
        self.assertEqual(response.status_code, 200, "Refresh should succeed to generate image")
        
        # Get image
        response = requests.get(f"{BASE_URL}/image/")
        self.assertEqual(response.status_code, 200, "Image endpoint should return 200 OK")
        
        # Verify it's an image
        try:
            Image.open(BytesIO(response.content))
        except Exception as e:
            self.fail(f"Response is not a valid image: {e}")
    
    # TEST 7: Error Handling & Validation
    def test_error_handling(self):
        # Test 404 error
        response = requests.get(f"{BASE_URL}/nonexistentendpoint")
        self.assertEqual(response.status_code, 404, "Should return 404 for non-existent endpoint")
        data = response.json()
        self.assertIn("error", data, "Response should contain error message")
        
        # Test 400 error
        response = requests.get(f"{BASE_URL}/?invalidparam=1")
        self.assertEqual(response.status_code, 400, "Should return 400 for invalid parameters")
        data = response.json()
        self.assertIn("error", data, "Response should contain error message")

if __name__ == "__main__":
    unittest.main()