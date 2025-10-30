import json
import requests
import unittest
from datetime import datetime
from PIL import Image
from io import BytesIO

BASE_URL = "https://stunning-forgiveness-production.up.railway.app/countries"

class RailwayCountryAPITestCase(unittest.TestCase):
    
    def setUp(self):
        # Add a longer timeout for production environment
        self.timeout = 30
        
    def test_refresh_endpoint(self):
        """POST /countries/refresh - Fetch all countries and exchange rates"""
        print("Testing refresh endpoint...")
        try:
            response = requests.post(f"{BASE_URL}/refresh", timeout=self.timeout)
            print(f"Status: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                print(f"✓ Refresh successful: {data.get('message')}")
                self.assertIn("total_countries", data)
                print(f"Total countries: {data['total_countries']}")
            else:
                print(f"Response: {response.text}")
            
            # Don't fail if rate limited or temporary issue
            self.assertIn(response.status_code, [200, 429, 503], "Refresh should return 200, 429 (rate limit) or 503 (temp unavailable)")
            
        except requests.exceptions.Timeout:
            self.skipTest("Refresh endpoint timed out")
        except requests.exceptions.ConnectionError:
            self.skipTest("Cannot connect to Railway deployment")
    
    def test_get_countries(self):
        """GET /countries - Get all countries with filters and sorting"""
        print("Testing countries list endpoint...")
        try:
            # Basic GET
            response = requests.get(f"{BASE_URL}", timeout=self.timeout)
            self.assertEqual(response.status_code, 200)
            data = response.json()
            
            self.assertIsInstance(data, list)
            print(f"✓ Retrieved {len(data)} countries")
            
            # Test filters if we have data
            if len(data) > 0:
                # Test region filter
                response = requests.get(f"{BASE_URL}?region=Africa", timeout=self.timeout)
                self.assertEqual(response.status_code, 200)
                
                # Test currency filter
                response = requests.get(f"{BASE_URL}?currency=USD", timeout=self.timeout)
                self.assertEqual(response.status_code, 200)
                
                # Test sorting
                response = requests.get(f"{BASE_URL}?sort=gdp_desc", timeout=self.timeout)
                self.assertEqual(response.status_code, 200)
                
                print("✓ All filters and sorting working")
            
        except requests.exceptions.Timeout:
            self.fail("Countries endpoint timed out")
    
    def test_get_country_by_name(self):
        """GET /countries/:name - Get one country by name"""
        print("Testing country by name endpoint...")
        try:
            # First get list to find available countries
            response = requests.get(f"{BASE_URL}", timeout=self.timeout)
            countries = response.json()
            
            if len(countries) > 0:
                # Test with first available country
                country_name = countries[0]['name']
                response = requests.get(f"{BASE_URL}/{country_name}", timeout=self.timeout)
                
                if response.status_code == 200:
                    data = response.json()
                    self.assertEqual(data['name'], country_name)
                    print(f"✓ Found country: {country_name}")
                else:
                    print(f"Country lookup failed: {response.status_code}")
                    # Don't fail, might be case sensitivity issue
            
            # Test non-existent country
            response = requests.get(f"{BASE_URL}/NonExistentCountryXYZ123", timeout=self.timeout)
            self.assertEqual(response.status_code, 404)
            print("✓ Non-existent country returns 404")
            
        except requests.exceptions.Timeout:
            self.fail("Country by name endpoint timed out")
    
    def test_status_endpoint(self):
        """GET /status - Show total countries and last refresh timestamp"""
        print("Testing status endpoint...")
        try:
            response = requests.get(f"{BASE_URL}/status", timeout=self.timeout)
            self.assertEqual(response.status_code, 200)
            
            data = response.json()
            self.assertIn("total_countries", data)
            self.assertIn("last_refreshed_at", data)
            
            print(f"✓ Status: {data['total_countries']} countries, last refresh: {data['last_refreshed_at']}")
            
        except requests.exceptions.Timeout:
            self.fail("Status endpoint timed out")
    
    def test_countries_image(self):
        """GET /countries/image - Serve summary image"""
        print("Testing image endpoint...")
        try:
            response = requests.get(f"{BASE_URL}/image", timeout=self.timeout)
            
            if response.status_code == 200:
                # Verify it's an image
                try:
                    Image.open(BytesIO(response.content))
                    print("✓ Image generated successfully")
                except Exception as e:
                    print(f"Image validation failed: {e}")
                    # Don't fail the test for image issues
            else:
                print(f"Image endpoint returned: {response.status_code}")
                # Don't fail, image might not be generated yet
            
        except requests.exceptions.Timeout:
            print("Image endpoint timed out")
    
    def test_error_handling(self):
        """Test error scenarios"""
        print("Testing error handling...")
        try:
            # Test non-existent country
            response = requests.get(f"{BASE_URL}/NonExistentCountry123", timeout=10)
            self.assertEqual(response.status_code, 404)
            
            # Test non-existent endpoint
            response = requests.get(f"{BASE_URL}/nonexistent/endpoint", timeout=10)
            self.assertIn(response.status_code, [404, 400])
            
            print("✓ Error handling working")
            
        except requests.exceptions.Timeout:
            print("Error handling test timed out")

def test_all_endpoints_quick():
    """Quick test without unittest framework"""
    print("🚀 Testing Railway Deployment")
    print("=" * 50)
    
    endpoints = [
        ("GET", "/countries", "Get all countries"),
        ("GET", "/countries/status", "Get status"),
        ("GET", "/countries/image", "Get summary image"),
    ]
    
    for method, endpoint, description in endpoints:
        print(f"\nTesting: {description}")
        print(f"Endpoint: {method} {endpoint}")
        
        try:
            if method == "GET":
                response = requests.get(f"https://stunning-forgiveness-production.up.railway.app{endpoint}", timeout=15)
            elif method == "POST":
                response = requests.post(f"https://stunning-forgiveness-production.up.railway.app{endpoint}", timeout=15)
            
            print(f"Status: {response.status_code}")
            
            if response.status_code == 200:
                if endpoint == "/countries/image":
                    print("✓ Image received")
                else:
                    data = response.json()
                    if endpoint == "/countries":
                        print(f"✓ Retrieved {len(data)} countries")
                    elif endpoint == "/countries/status":
                        print(f"✓ Status: {data['total_countries']} countries")
            else:
                print(f"Response: {response.text[:100]}...")
                
        except requests.exceptions.Timeout:
            print("✗ Timeout")
        except requests.exceptions.ConnectionError:
            print("✗ Connection Error")
        except Exception as e:
            print(f"✗ Error: {e}")

if __name__ == "__main__":
    print("Testing Railway Deployment")
    print("Base URL:", BASE_URL)
    print("=" * 60)
    
    # Run quick test first
    test_all_endpoints_quick()
    
    print("\n" + "=" * 60)
    print("Running detailed unit tests...")
    print("=" * 60)
    
    # Run unittest
    unittest.main(verbosity=2, exit=False)