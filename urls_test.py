import requests
import unittest
from PIL import Image
from io import BytesIO

BASE_URL = "https://stunning-forgiveness-production.up.railway.app/countries"

class TestFixes(unittest.TestCase):
    
    def test_1_delete_endpoint(self):
        """Test DELETE /countries/:name"""
        print("\n1. Testing DELETE endpoint...")
        
        # First get a country to delete
        response = requests.get(f"{BASE_URL}")
        countries = response.json()
        
        if len(countries) > 1:
            country_name = countries[1]['name']  # Use second country
            
            # Test delete
            delete_response = requests.delete(f"{BASE_URL}/{country_name}")
            print(f"DELETE status: {delete_response.status_code}")
            
            if delete_response.status_code == 204:
                print("✓ DELETE returns 204")
            elif delete_response.status_code == 404:
                print("✓ DELETE returns 404 (country not found)")
            else:
                print(f"✗ DELETE returns {delete_response.status_code}, expected 204 or 404")
                
            # Test delete non-existent country
            delete_response = requests.delete(f"{BASE_URL}/NonExistentCountry123")
            self.assertEqual(delete_response.status_code, 404, "Should return 404 for non-existent country")
            print("✓ DELETE returns 404 for non-existent country")
    
    def test_2_refresh_endpoint(self):
        """Test POST /countries/refresh"""
        print("\n2. Testing refresh endpoint...")
        
        try:
            response = requests.post(f"{BASE_URL}/refresh", timeout=60)
            print(f"Refresh status: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                print(f"✓ Refresh successful: {data}")
            elif response.status_code == 503:
                print("✓ Refresh returns 503 (external API unavailable)")
            else:
                print(f"✗ Refresh returns {response.status_code}, expected 200 or 503")
                print(f"Response: {response.text}")
                
        except requests.exceptions.Timeout:
            print("✗ Refresh timeout")
    
    def test_3_image_endpoint(self):
        """Test GET /countries/image"""
        print("\n3. Testing image endpoint...")
        
        # First refresh to ensure data exists
        refresh_response = requests.post(f"{BASE_URL}/refresh")
        
        response = requests.get(f"{BASE_URL}/image")
        print(f"Image status: {response.status_code}")
        
        if response.status_code == 200:
            try:
                img = Image.open(BytesIO(response.content))
                print(f"✓ Image generated: {img.size}")
            except Exception as e:
                print(f"✗ Invalid image: {e}")
        else:
            print(f"✗ Image endpoint failed: {response.text}")

if __name__ == "__main__":
    unittest.main(verbosity=2)