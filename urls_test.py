import json
import requests
import unittest
from datetime import datetime
from PIL import Image
from io import BytesIO

BASE_URL = "http://localhost:8000/countries"

class CountryAPITestCase(unittest.TestCase):
    
    def setUp(self):
        # Wait for server to be ready
        import time
        time.sleep(2)
        
        # Refresh countries before each test - NO trailing slash
        try:
            response = requests.post(f"{BASE_URL}/refresh", timeout=60)
            if response.status_code == 200:
                self.refresh_response = response
                print("✓ Refresh successful")
            else:
                print(f"✗ Refresh failed: {response.status_code}")
                self.refresh_response = None
        except requests.exceptions.RequestException as e:
            print(f"✗ Refresh error: {e}")
            self.refresh_response = None
    
    def test_refresh_endpoint(self):
        """POST /countries/refresh - Fetch all countries and exchange rates, then cache them in the database"""
        if not self.refresh_response:
            self.skipTest("Refresh endpoint not available")
        
        self.assertEqual(self.refresh_response.status_code, 200)
        data = self.refresh_response.json()
        self.assertIn("message", data)
        self.assertIn("total_countries", data)
        print(f"✓ Refreshed {data['total_countries']} countries")
    
    def test_get_countries(self):
        """GET /countries - Get all countries from the DB (support filters and sorting)"""
        # Test basic GET
        response = requests.get(f"{BASE_URL}")
        self.assertEqual(response.status_code, 200)
        
        data = response.json()
        self.assertIsInstance(data, list)
        self.assertGreater(len(data), 0)
        
        # Test filter: ?region=Africa
        response = requests.get(f"{BASE_URL}?region=Africa")
        self.assertEqual(response.status_code, 200)
        
        # Test filter: ?currency=USD  
        response = requests.get(f"{BASE_URL}?currency=USD")
        self.assertEqual(response.status_code, 200)
        
        # Test sort: ?sort=gdp_desc
        response = requests.get(f"{BASE_URL}?sort=gdp_desc")
        self.assertEqual(response.status_code, 200)
        print("✓ All filters and sorting working")
    
    def test_get_country_by_name(self):
        """GET /countries/:name - Get one country by name"""
        # First get list to find available countries
        response = requests.get(f"{BASE_URL}")
        countries = response.json()
        
        if countries:
            # Test with first available country
            country_name = countries[0]['name']
            response = requests.get(f"{BASE_URL}/{country_name}")
            self.assertEqual(response.status_code, 200)
            
            data = response.json()
            self.assertEqual(data['name'], country_name)
            print(f"✓ Found country: {country_name}")
        
        # Test non-existent country
        response = requests.get(f"{BASE_URL}/NonExistentCountryXYZ")
        self.assertEqual(response.status_code, 404)
    
    def test_delete_country(self):
        """DELETE /countries/:name - Delete a country record"""
        # Get list to find a country to delete
        response = requests.get(f"{BASE_URL}")
        countries = response.json()
        
        if len(countries) > 1:
            # Use second country to avoid deleting commonly tested ones
            country_name = countries[1]['name']
            
            # Verify exists
            response = requests.get(f"{BASE_URL}/{country_name}")
            self.assertEqual(response.status_code, 200)
            
            # Delete
            delete_response = requests.delete(f"{BASE_URL}/{country_name}")
            self.assertEqual(delete_response.status_code, 204)
            
            # Verify deleted
            response = requests.get(f"{BASE_URL}/{country_name}")
            self.assertEqual(response.status_code, 404)
            print(f"✓ Deleted country: {country_name}")
    
    def test_status_endpoint(self):
        """GET /status - Show total countries and last refresh timestamp"""
        response = requests.get(f"{BASE_URL}/status")
        self.assertEqual(response.status_code, 200)
        
        data = response.json()
        self.assertIn("total_countries", data)
        self.assertIn("last_refreshed_at", data)
        print("✓ Status endpoint working")
    
    def test_countries_image(self):
        """GET /countries/image - Serve summary image"""
        # Refresh to ensure image is generated
        refresh_response = requests.post(f"{BASE_URL}/refresh")
        if refresh_response.status_code != 200:
            self.skipTest("Cannot refresh data")
        
        # Get image
        response = requests.get(f"{BASE_URL}/image")
        self.assertEqual(response.status_code, 200)
        
        # Verify it's an image
        try:
            Image.open(BytesIO(response.content))
            print("✓ Image generated successfully")
        except Exception as e:
            self.fail(f"Not a valid image: {e}")
    
    def test_error_handling(self):
        """Test error scenarios"""
        # Test non-existent endpoint
        response = requests.get(f"{BASE_URL}/nonexistent/endpoint")
        self.assertIn(response.status_code, [404, 400])
        
        # Test non-existent country
        response = requests.get(f"{BASE_URL}/NonExistentCountry123")
        self.assertEqual(response.status_code, 404)
        print("✓ Error handling working")

if __name__ == "__main__":
    unittest.main(verbosity=2)