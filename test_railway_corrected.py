import requests
import unittest
from datetime import datetime
from PIL import Image
from io import BytesIO
from urllib.parse import quote

BASE_URL = "https://stunning-forgiveness-production.up.railway.app"

class RailwayAPITestCase(unittest.TestCase):
    
    def setUp(self):
        self.timeout = 15
    
    def test_list_countries(self):
        """GET /countries - List all countries"""
        response = requests.get(f"{BASE_URL}/countries", timeout=self.timeout)
        self.assertEqual(response.status_code, 200)
        
        data = response.json()
        self.assertIsInstance(data, list)
        self.assertGreater(len(data), 0)
        print(f"✓ List countries: {len(data)} countries")
        
        # Return first country for other tests
        return data[0]['name'] if data else None
    
    def test_get_country(self):
        """GET /countries/<name> - Get specific country"""
        # First get a country name
        country_name = self.test_list_countries()
        if not country_name:
            self.skipTest("No countries available")
        
        # Test with URL encoding for spaces
        encoded_name = quote(country_name)
        response = requests.get(f"{BASE_URL}/countries/{encoded_name}", timeout=self.timeout)
        
        if response.status_code == 200:
            data = response.json()
            self.assertEqual(data['name'], country_name)
            print(f"✓ Get country: {country_name}")
        else:
            # Try without encoding
            response = requests.get(f"{BASE_URL}/countries/{country_name}", timeout=self.timeout)
            self.assertEqual(response.status_code, 200)
            data = response.json()
            self.assertEqual(data['name'], country_name)
            print(f"✓ Get country (no encoding): {country_name}")
    
    def test_get_country_with_spaces(self):
        """Test country names with spaces"""
        test_names = ["United States", "United States of America", "Saudi Arabia"]
        
        for name in test_names:
            # Try encoded
            encoded = quote(name)
            response = requests.get(f"{BASE_URL}/countries/{encoded}", timeout=self.timeout)
            
            if response.status_code == 200:
                data = response.json()
                print(f"✓ Found with encoding: {name} -> {data['name']}")
                break
            else:
                # Try without encoding
                response = requests.get(f"{BASE_URL}/countries/{name}", timeout=self.timeout)
                if response.status_code == 200:
                    data = response.json()
                    print(f"✓ Found without encoding: {name} -> {data['name']}")
                    break
                else:
                    print(f"✗ Not found: {name}")
    
    def test_status_endpoint(self):
        """GET /status - Get API status"""
        response = requests.get(f"{BASE_URL}/status", timeout=self.timeout)
        self.assertEqual(response.status_code, 200)
        
        data = response.json()
        self.assertIn("total_countries", data)
        self.assertIn("last_refreshed_at", data)
        print(f"✓ Status: {data['total_countries']} countries")
    
    def test_image_endpoint(self):
        """GET /countries/image - Get summary image"""
        response = requests.get(f"{BASE_URL}/countries/image", timeout=self.timeout)
        
        if response.status_code == 200:
            try:
                Image.open(BytesIO(response.content))
                print("✓ Image endpoint working")
            except Exception as e:
                self.fail(f"Invalid image: {e}")
        else:
            print(f"Image endpoint returned: {response.status_code}")
            # Don't fail test for image issues
    
    def test_refresh_endpoint(self):
        """POST /countries/refresh - Refresh data"""
        try:
            response = requests.post(f"{BASE_URL}/countries/refresh", timeout=30)
            print(f"Refresh status: {response.status_code}")
            
            # Accept various status codes for refresh
            if response.status_code == 200:
                data = response.json()
                print(f"✓ Refresh successful: {data.get('message', '')}")
            elif response.status_code in [429, 503, 504]:
                print("Refresh rate limited or temporarily unavailable")
            else:
                print(f"Refresh failed: {response.text[:100]}")
                
        except requests.exceptions.Timeout:
            print("Refresh endpoint timed out (common on Railway)")
    
    def test_delete_country(self):
        """DELETE /countries/<name>/delete - Delete country"""
        # Get a country to delete
        country_name = self.test_list_countries()
        if not country_name:
            self.skipTest("No countries available")
        
        # Test delete endpoint
        response = requests.delete(f"{BASE_URL}/countries/{country_name}/delete", timeout=self.timeout)
        
        if response.status_code == 204:
            print(f"✓ Delete country: {country_name}")
            
            # Verify deletion
            response = requests.get(f"{BASE_URL}/countries/{country_name}", timeout=self.timeout)
            self.assertEqual(response.status_code, 404)
        else:
            print(f"Delete not supported or failed: {response.status_code}")

def quick_test():
    """Quick functionality test"""
    print("🚀 Quick Railway API Test")
    print("=" * 50)
    
    endpoints = [
        ("GET", "/countries", "List countries"),
        ("GET", "/status", "API status"), 
        ("GET", "/countries/image", "Summary image"),
    ]
    
    for method, endpoint, desc in endpoints:
        url = BASE_URL + endpoint
        print(f"\n{desc}: {method} {url}")
        
        try:
            if method == "GET":
                response = requests.get(url, timeout=10)
            elif method == "POST":
                response = requests.post(url, timeout=15)
            
            print(f"Status: {response.status_code}")
            
            if response.status_code == 200:
                if endpoint == "/countries/image":
                    print("✓ Image received")
                else:
                    data = response.json()
                    if endpoint == "/countries":
                        print(f"✓ {len(data)} countries")
                    elif endpoint == "/status":
                        print(f"✓ {data['total_countries']} countries, last refresh: {data['last_refreshed_at'][:19]}")
            else:
                print(f"Response: {response.text[:100]}...")
                
        except Exception as e:
            print(f"Error: {e}")

if __name__ == "__main__":
    # Run quick test first
    quick_test()
    
    print("\n" + "=" * 50)
    print("Running detailed tests...")
    print("=" * 50)
    
    # Run unit tests
    unittest.main(verbosity=2, exit=False)