# test_bot_grading.py
import os
import django
import sys
import time

# Add the project directory to the Python path
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.append(project_root)

# Set the Django settings module
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'country_api.settings')

# Setup Django
try:
    django.setup()
except Exception as e:
    print(f"Error setting up Django: {e}")
    print("Make sure your Django project is properly configured.")
    sys.exit(1)

# Now import Django components
import json
import tempfile
import io
from decimal import Decimal
from unittest.mock import patch, MagicMock
from django.test import TestCase, Client, TransactionTestCase
from django.urls import reverse
from django.core.files.uploadedfile import SimpleUploadedFile
from django.utils import timezone

# Import your app components
try:
    from countries.models import Country
    from countries.services import ExternalAPIService, CountryDataProcessor
    from countries.image_service import SummaryImageGenerator
except ImportError as e:
    print(f"Error importing app components: {e}")
    print("Make sure your 'countries' app is properly installed in INSTALLED_APPS")
    sys.exit(1)

class BotGradingTestCase(TransactionTestCase):
    """
    Test case that matches the exact grading criteria from the bot
    """
    reset_sequences = True
    
    def setUp(self):
        # Set up the test client with proper host
        self.client = Client(SERVER_NAME='localhost')
        
        # Clear any existing countries first
        Country.objects.all().delete()
        
        # Create test countries with proper GDP ordering for sorting tests
        self.country1 = Country.objects.create(
            name="Nigeria",
            capital="Abuja",
            region="Africa",
            population=206139589,
            currency_code="NGN",
            exchange_rate=Decimal('1600.23'),
            estimated_gdp=Decimal('25767448125.20'),  # Medium GDP
            flag_url="https://flagcdn.com/ng.svg",
            last_refreshed_at=timezone.now()
        )
        
        self.country2 = Country.objects.create(
            name="Ghana",
            capital="Accra",
            region="Africa",
            population=31072940,
            currency_code="GHS",
            exchange_rate=Decimal('15.34'),
            estimated_gdp=Decimal('3029834520.60'),  # Lowest GDP
            flag_url="https://flagcdn.com/gh.svg",
            last_refreshed_at=timezone.now()
        )
        
        self.country3 = Country.objects.create(
            name="United States",
            capital="Washington D.C.",
            region="Americas",
            population=331002651,
            currency_code="USD",
            exchange_rate=Decimal('1.0'),
            estimated_gdp=Decimal('662005302000.00'),  # Highest GDP
            flag_url="https://flagcdn.com/us.svg",
            last_refreshed_at=timezone.now()
        )

        # Country without currency for edge case testing
        self.country_no_currency = Country.objects.create(
            name="CountryWithoutCurrency",
            capital="Capital",
            region="Region",
            population=1000000,
            currency_code=None,
            exchange_rate=None,
            estimated_gdp=0,
            flag_url="https://flagcdn.com/test.svg",
            last_refreshed_at=timezone.now()
        )

    # ============================================================
    # TEST 1: POST /countries/refresh (25 points)
    # ============================================================
    def test_1_post_countries_refresh_25_points(self):
        """TEST 1: POST /countries/refresh (25 points)"""
        print("\n" + "="*60)
        print("TEST 1: POST /countries/refresh (25 points)")
        print("="*60)
        
        points_earned = 0
        max_points = 25
        
        # Mock external APIs to avoid timeout and ensure consistent testing
        mock_countries_data = [
            {
                "name": "Nigeria",
                "capital": "Abuja",
                "region": "Africa",
                "population": 206139589,
                "flag": "https://flagcdn.com/ng.svg",
                "currencies": [{"code": "NGN", "name": "Nigerian Naira", "symbol": "₦"}]
            },
            {
                "name": "Ghana",
                "capital": "Accra",
                "region": "Africa",
                "population": 31072940,
                "flag": "https://flagcdn.com/gh.svg",
                "currencies": [{"code": "GHS", "name": "Ghanaian Cedi", "symbol": "₵"}]
            },
            {
                "name": "United States",
                "capital": "Washington D.C.",
                "region": "Americas",
                "population": 331002651,
                "flag": "https://flagcdn.com/us.svg",
                "currencies": [{"code": "USD", "name": "United States Dollar", "symbol": "$"}]
            }
        ]
        
        mock_exchange_data = {
            "NGN": 1600.23,
            "GHS": 15.34,
            "USD": 1.0
        }
        
        try:
            with patch('countries.views.ExternalAPIService.fetch_countries_data') as mock_fetch_countries, \
                 patch('countries.views.ExternalAPIService.fetch_exchange_rates') as mock_fetch_rates, \
                 patch('countries.views.SummaryImageGenerator.generate_summary_image') as mock_generate_image:
                
                mock_fetch_countries.return_value = mock_countries_data
                mock_fetch_rates.return_value = mock_exchange_data
                mock_generate_image.return_value = "/path/to/summary.png"
                
                # Make POST request to refresh endpoint
                response = self.client.post(
                    reverse('refresh-countries'),
                    content_type='application/json'
                )
                
                print(f"✓ Refresh endpoint called")
                
                # Check response status
                if response.status_code == 200:
                    points_earned += 25
                    print(f"✓ Refresh endpoint completed successfully (25 pts)")
                    
                    # Verify response structure
                    response_data = response.json()
                    required_fields = ['message', 'created', 'updated']
                    if all(field in response_data for field in required_fields):
                        print(f"✓ Returns correct response structure")
                    else:
                        print(f"✗ Missing required fields in response")
                else:
                    print(f"✗ Refresh endpoint failed with status {response.status_code} (0 pts)")
                    
        except Exception as e:
            print(f"✗ Refresh endpoint timed out or crashed: {e} (0 pts)")
        
        print(f"TEST 1 SCORE: {points_earned}/{max_points}")
        return points_earned

    # ============================================================
    # TEST 2: GET /countries (filters & sorting) (25 points)
    # ============================================================
    def test_2_get_countries_filters_sorting_25_points(self):
        """TEST 2: GET /countries (filters & sorting) (25 points)"""
        print("\n" + "="*60)
        print("TEST 2: GET /countries (filters & sorting) (25 points)")
        print("="*60)
        
        points_earned = 0
        max_points = 25
        
        # 2.1 Basic GET /countries works (5 pts)
        response = self.client.get(reverse('list-countries'))
        if response.status_code == 200:
            points_earned += 5
            print(f"✓ Basic GET /countries works (5 pts)")
        else:
            print(f"✗ Basic GET /countries failed with status {response.status_code} (0 pts)")
        
        # 2.2 Returns correct structure (5 pts)
        if response.status_code == 200:
            data = response.json()
            if (isinstance(data, list) and len(data) > 0 and 
                all(isinstance(item, dict) for item in data) and
                all('name' in item and 'population' in item for item in data)):
                points_earned += 5
                print(f"✓ Returns correct structure (5 pts)")
            else:
                print(f"✗ Returns incorrect structure (0 pts)")
        
        # 2.3 Filter by region works (5 pts)
        response = self.client.get(reverse('list-countries') + '?region=Africa')
        if response.status_code == 200:
            data = response.json()
            if all(country['region'] == 'Africa' for country in data):
                points_earned += 5
                print(f"✓ Filter by region works (5 pts)")
            else:
                print(f"✗ Filter by region returns incorrect data (0 pts)")
        else:
            print(f"✗ Filter by region failed with status {response.status_code} (0 pts)")
        
        # 2.4 Filter by currency works (5 pts)
        response = self.client.get(reverse('list-countries') + '?currency=NGN')
        if response.status_code == 200:
            data = response.json()
            if len(data) > 0 and all(country['currency_code'] == 'NGN' for country in data):
                points_earned += 5
                print(f"✓ Filter by currency works (5 pts)")
            else:
                print(f"✗ Filter by currency returns incorrect data (0 pts)")
        else:
            print(f"✗ Filter by currency failed with status {response.status_code} (0 pts)")
        
        # 2.5 Sorting by GDP returns correct order (5 pts)
        response = self.client.get(reverse('list-countries') + '?sort=gdp_desc')
        if response.status_code == 200:
            data = response.json()
            # Filter out countries with None GDP for sorting test
            countries_with_gdp = [c for c in data if c.get('estimated_gdp') is not None]
            gdp_values = [float(c['estimated_gdp']) for c in countries_with_gdp]
            
            # Check if sorted in descending order
            if gdp_values == sorted(gdp_values, reverse=True) and len(gdp_values) >= 2:
                points_earned += 5
                print(f"✓ Sorting by GDP returns correct order (5 pts)")
            else:
                print(f"✗ Sorting by GDP returns incorrect order (0 pts)")
                print(f"  GDP values: {gdp_values}")
                print(f"  Expected descending: {sorted(gdp_values, reverse=True)}")
        else:
            print(f"✗ Sorting by GDP failed with status {response.status_code} (0 pts)")
        
        print(f"TEST 2 SCORE: {points_earned}/{max_points}")
        return points_earned

    # ============================================================
    # TEST 3: GET /countries/:name (10 points)
    # ============================================================
    def test_3_get_country_by_name_10_points(self):
        """TEST 3: GET /countries/:name (10 points)"""
        print("\n" + "="*60)
        print("TEST 3: GET /countries/:name (10 points)")
        print("="*60)
        
        points_earned = 0
        max_points = 10
        
        # 3.1 Get specific country works (5 pts)
        response = self.client.get(reverse('country-detail', kwargs={'name': 'Nigeria'}))
        if response.status_code == 200:
            points_earned += 5
            print(f"✓ Get specific country works (5 pts)")
        else:
            print(f"✗ Get specific country failed with status {response.status_code} (0 pts)")
        
        # 3.2 Returns correct country data (3 pts)
        if response.status_code == 200:
            data = response.json()
            if (data.get('name') == 'Nigeria' and 
                data.get('capital') == 'Abuja' and 
                data.get('region') == 'Africa'):
                points_earned += 3
                print(f"✓ Returns correct country data (3 pts)")
            else:
                print(f"✗ Returns incorrect country data (0 pts)")
        
        # 3.3 Returns 404 for non-existent country (2 pts)
        response = self.client.get(reverse('country-detail', kwargs={'name': 'NonExistentCountry'}))
        if response.status_code == 404:
            points_earned += 2
            print(f"✓ Returns 404 for non-existent country (2 pts)")
        else:
            print(f"✗ Should return 404 for non-existent country, got {response.status_code} (0 pts)")
        
        print(f"TEST 3 SCORE: {points_earned}/{max_points}")
        return points_earned

    # ============================================================
    # TEST 4: DELETE /countries/:name (10 points)
    # ============================================================
    def test_4_delete_country_by_name_10_points(self):
        """TEST 4: DELETE /countries/:name (10 points)"""
        print("\n" + "="*60)
        print("TEST 4: DELETE /countries/:name (10 points)")
        print("="*60)
        
        points_earned = 0
        max_points = 10
        
        # 4.1 Delete existing country (main test)
        initial_count = Country.objects.count()
        response = self.client.delete(reverse('country-detail', kwargs={'name': 'Ghana'}))
        
        # Accept either 200 or 204 for successful deletion
        if response.status_code in [200, 204]:
            points_earned += 5  # This covers the main delete functionality
            print(f"✓ Delete endpoint works (status {response.status_code})")
            
            # Verify country was actually deleted
            if Country.objects.count() == initial_count - 1:
                points_earned += 3
                print(f"✓ Country actually deleted from database (3 pts)")
            else:
                print(f"✗ Country not deleted from database (0 pts)")
        else:
            print(f"✗ Delete failed with status {response.status_code} (0 pts)")
        
        # 4.2 Returns 404 for non-existent country (2 pts)
        response = self.client.delete(reverse('country-detail', kwargs={'name': 'NonExistentCountry'}))
        if response.status_code == 404:
            points_earned += 2
            print(f"✓ Returns 404 for non-existent country (2 pts)")
        else:
            print(f"✗ Should return 404 for non-existent country, got {response.status_code} (0 pts)")
        
        print(f"TEST 4 SCORE: {points_earned}/{max_points}")
        return points_earned

    # ============================================================
    # TEST 5: GET /status (10 points)
    # ============================================================
    def test_5_get_status_10_points(self):
        """TEST 5: GET /status (10 points)"""
        print("\n" + "="*60)
        print("TEST 5: GET /status (10 points)")
        print("="*60)
        
        points_earned = 0
        max_points = 10
        
        response = self.client.get(reverse('get-status'))
        
        # 5.1 Status endpoint accessible (3 pts)
        if response.status_code == 200:
            points_earned += 3
            print(f"✓ Status endpoint accessible (3 pts)")
        else:
            print(f"✗ Status endpoint failed with status {response.status_code} (0 pts)")
            return points_earned
        
        data = response.json()
        
        # 5.2 Returns total_countries field (3 pts)
        if 'total_countries' in data:
            points_earned += 3
            print(f"✓ Returns total_countries field (3 pts)")
        else:
            print(f"✗ Missing total_countries field (0 pts)")
        
        # 5.3 Returns last_refreshed_at field (2 pts)
        if 'last_refreshed_at' in data:
            points_earned += 2
            print(f"✓ Returns last_refreshed_at field (2 pts)")
        else:
            print(f"✗ Missing last_refreshed_at field (0 pts)")
        
        # 5.4 Valid timestamp format (2 pts)
        if (data.get('last_refreshed_at') and 
            (isinstance(data['last_refreshed_at'], str) or data['last_refreshed_at'] is None)):
            points_earned += 2
            print(f"✓ Valid timestamp format (2 pts)")
        else:
            print(f"✗ Invalid timestamp format (0 pts)")
        
        print(f"TEST 5 SCORE: {points_earned}/{max_points}")
        return points_earned

    # ============================================================
    # TEST 6: GET /countries/image (10 points)
    # ============================================================
    def test_6_get_countries_image_10_points(self):
        """TEST 6: GET /countries/image (10 points)"""
        print("\n" + "="*60)
        print("TEST 6: GET /countries/image (10 points)")
        print("="*60)
        
        points_earned = 0
        max_points = 10
        
        # First, ensure the cache directory exists and create a test image
        from django.conf import settings
        cache_dir = getattr(settings, 'CACHE_DIR', 'cache')
        os.makedirs(cache_dir, exist_ok=True)
        
        # Create a test image
        try:
            from PIL import Image
            img = Image.new('RGB', (100, 100), color='red')
            img_io = io.BytesIO()
            img.save(img_io, 'PNG')
            img_io.seek(0)
            
            # Save the image
            image_path = os.path.join(cache_dir, 'summary.png')
            with open(image_path, 'wb') as f:
                f.write(img_io.getvalue())
            
            # Test image endpoint
            response = self.client.get(reverse('get-country-image'))
            
            # Check if returns actual image file
            if response.status_code == 200 and response['Content-Type'] == 'image/png':
                points_earned += 10
                print(f"✓ Image endpoint returns actual image file (10 pts)")
            else:
                print(f"✗ Image endpoint failed - status: {response.status_code}, content-type: {response.get('Content-Type')} (0 pts)")
            
            # Clean up
            try:
                if os.path.exists(image_path):
                    os.remove(image_path)
            except PermissionError:
                print("  Note: Could not clean up test image file (locked)")
                
        except ImportError:
            print("✗ PIL not available, cannot test image generation (0 pts)")
        except Exception as e:
            print(f"✗ Image test failed: {e} (0 pts)")
        
        print(f"TEST 6 SCORE: {points_earned}/{max_points}")
        return points_earned

    # ============================================================
    # TEST 7: Error Handling & Validation (10 points)
    # ============================================================
    def test_7_error_handling_validation_10_points(self):
        """TEST 7: Error Handling & Validation (10 points)"""
        print("\n" + "="*60)
        print("TEST 7: Error Handling & Validation (10 points)")
        print("="*60)
        
        points_earned = 0
        max_points = 10
        
        # 7.1 404 errors return proper JSON format (3 pts)
        response = self.client.get(reverse('country-detail', kwargs={'name': 'NonExistentCountry'}))
        if (response.status_code == 404 and 
            response['Content-Type'] == 'application/json' and
            'error' in response.json()):
            points_earned += 3
            print(f"✓ 404 errors return proper JSON format (3 pts)")
        else:
            print(f"✗ 404 errors not in proper JSON format (0 pts)")
        
        # 7.2 Consistent error response structure (JSON) (4 pts)
        # Test multiple error scenarios
        error_endpoints = [
            reverse('country-detail', kwargs={'name': 'NonExistentCountry'}),
        ]
        
        all_json_errors = True
        for endpoint in error_endpoints:
            response = self.client.get(endpoint)
            if response.status_code >= 400:
                if (response['Content-Type'] != 'application/json' or 
                    'error' not in response.json()):
                    all_json_errors = False
                    break
        
        if all_json_errors:
            points_earned += 4
            print(f"✓ Consistent error response structure (JSON) (4 pts)")
        else:
            print(f"✗ Inconsistent error response structure (0 pts)")
        
        # 7.3 Error handling implemented (3 pts)
        # Test that various error conditions are handled gracefully
        try:
            # Test invalid method
            response = self.client.put(reverse('refresh-countries'))
            if response.status_code >= 400 and response['Content-Type'] == 'application/json':
                points_earned += 3
                print(f"✓ Error handling implemented (3 pts)")
            else:
                print(f"✗ Error handling not properly implemented (0 pts)")
        except Exception as e:
            print(f"✗ Error handling test crashed: {e} (0 pts)")
        
        print(f"TEST 7 SCORE: {points_earned}/{max_points}")
        return points_earned

def run_bot_grading_tests():
    """Run all bot tests and return total score"""
    print("🚀 RUNNING BOT GRADING TESTS")
    print("="*60)
    
    # Create test instance and run all tests
    test_instance = BotGradingTestCase()
    
    # Manually call setUp to initialize the test client
    test_instance.setUp()
    
    total_score = 0
    max_total = 100
    
    # Run each test method
    test_methods = [
        test_instance.test_1_post_countries_refresh_25_points,
        test_instance.test_2_get_countries_filters_sorting_25_points,
        test_instance.test_3_get_country_by_name_10_points,
        test_instance.test_4_delete_country_by_name_10_points,
        test_instance.test_5_get_status_10_points,
        test_instance.test_6_get_countries_image_10_points,
        test_instance.test_7_error_handling_validation_10_points,
    ]
    
    for test_method in test_methods:
        try:
            score = test_method()
            total_score += score
        except Exception as e:
            print(f"❌ Test {test_method.__name__} failed: {e}")
    
    print("\n" + "="*60)
    print("🏁 FINAL BOT GRADING RESULTS")
    print("="*60)
    print(f"TOTAL SCORE: {total_score}/{max_total}")
    print(f"PASS MARK: 70/100")
    print(f"STATUS: {'PASSED ✅' if total_score >= 70 else 'FAILED ❌'}")
    print("="*60)
    
    return total_score

# Additional model tests
class CountryModelTest(TestCase):
    def test_country_creation(self):
        """Test Country model creation and string representation"""
        country = Country.objects.create(
            name="Test Country",
            capital="Test Capital",
            region="Test Region",
            population=1000000,
            currency_code="TEST",
            exchange_rate=Decimal('1.0'),
            estimated_gdp=Decimal('1000000.0'),
            flag_url="https://flagcdn.com/test.svg"
        )
        
        self.assertEqual(str(country), "Test Country")
        self.assertTrue(isinstance(country, Country))
        
    def test_required_fields(self):
        """Test that required fields are enforced"""
        # Test missing name
        with self.assertRaises(Exception):
            Country.objects.create(
                name=None,  # Required field
                population=1000000,
                currency_code="TEST"
            )

if __name__ == '__main__':
    # Run the bot grading tests
    total_score = run_bot_grading_tests()
    
    # Exit with appropriate code (0 for success, 1 for failure)
    sys.exit(0 if total_score >= 70 else 1)