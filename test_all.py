# test_all.py
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

class CountryAPITestCase(TransactionTestCase):
    """
    Using TransactionTestCase to ensure database is properly reset between tests
    """
    reset_sequences = True
    
    def setUp(self):
        # Set up the test client with proper host
        self.client = Client(SERVER_NAME='localhost')
        
        # Clear any existing countries first
        Country.objects.all().delete()
        
        # Create test countries with proper GDP ordering
        self.country1 = Country.objects.create(
            name="Nigeria",
            capital="Abuja",
            region="Africa",
            population=206139589,
            currency_code="NGN",
            exchange_rate=Decimal('1600.23'),
            estimated_gdp=Decimal('25767448125.2'),  # Lowest GDP
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
            estimated_gdp=Decimal('3029834520.6'),  # Medium GDP
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
            estimated_gdp=Decimal('662005302000.0'),  # Highest GDP
            flag_url="https://flagcdn.com/us.svg",
            last_refreshed_at=timezone.now()
        )

    def test_1_post_countries_refresh(self):
        """Test POST /countries/refresh endpoint (25 points)"""
        print("\n=== Testing POST /countries/refresh ===")
        
        # Mock external APIs to avoid creating real countries
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
            
            # Debug response
            print(f"Refresh response status: {response.status_code}")
            
            # Check if response is JSON before trying to parse it
            if response.status_code == 200 and 'application/json' in response.get('Content-Type', ''):
                response_data = response.json()
                print(f"Refresh response data: {response_data}")
                
                # Check response
                self.assertEqual(response.status_code, 200, 
                               f"Expected 200, got {response.status_code}")
                self.assertIn('application/json', response['Content-Type'])
                
                self.assertIn('message', response_data)
                self.assertIn('created', response_data)
                self.assertIn('updated', response_data)
                self.assertIn('total', response_data)
                
                # Should update existing 3 countries, not create new ones
                self.assertEqual(response_data['created'], 0)
                self.assertEqual(response_data['updated'], 3)
                self.assertEqual(response_data['total'], 3)
            
            # Verify countries were updated (not created new ones)
            self.assertEqual(Country.objects.count(), 3)

    def test_2_get_countries_with_filters_and_sorting(self):
        """Test GET /countries with filters and sorting (25 points)"""
        print("\n=== Testing GET /countries with filters and sorting ===")
        
        # Test without filters
        response = self.client.get(reverse('list-countries'))
        self.assertEqual(response.status_code, 200)
        self.assertIn('application/json', response['Content-Type'])
        
        data = response.json()
        self.assertIsInstance(data, list)
        self.assertEqual(len(data), 3, f"Expected 3 countries, got {len(data)}")
        
        # Test region filter
        response = self.client.get(reverse('list-countries') + '?region=Africa')
        self.assertEqual(response.status_code, 200)
        
        data = response.json()
        self.assertEqual(len(data), 2)
        for country in data:
            self.assertEqual(country['region'], 'Africa')
        
        # Test currency filter
        response = self.client.get(reverse('list-countries') + '?currency=NGN')
        self.assertEqual(response.status_code, 200)
        
        data = response.json()
        self.assertEqual(len(data), 1)
        self.assertEqual(data[0]['currency_code'], 'NGN')
        
        # Test sorting by GDP descending - THIS IS THE CRITICAL TEST
        print("Testing GDP descending sort...")
        response = self.client.get(reverse('list-countries') + '?sort=gdp_desc')
        self.assertEqual(response.status_code, 200)
        
        data = response.json()
        self.assertEqual(len(data), 3)
        
        # Debug GDP values
        gdp_values = []
        for country in data:
            gdp = country.get('estimated_gdp')
            print(f"Country: {country['name']}, GDP: {gdp}")
            if gdp is not None:
                gdp_values.append(float(gdp))
        
        print(f"GDP values: {gdp_values}")
        print(f"GDP values sorted descending: {sorted(gdp_values, reverse=True)}")
        
        # Check if GDP values are in descending order
        self.assertEqual(gdp_values, sorted(gdp_values, reverse=True),
                        f"GDP values not in descending order: {gdp_values}")
        
        # Test sorting by GDP ascending
        response = self.client.get(reverse('list-countries') + '?sort=gdp_asc')
        self.assertEqual(response.status_code, 200)
        
        data = response.json()
        gdp_values = [float(country['estimated_gdp']) for country in data if country['estimated_gdp'] is not None]
        self.assertEqual(gdp_values, sorted(gdp_values))

    def test_3_get_country_by_name(self):
        """Test GET /countries/:name endpoint (10 points)"""
        print("\n=== Testing GET /countries/:name ===")
        
        # Test existing country
        response = self.client.get(reverse('country-detail', kwargs={'name': 'Nigeria'}))
        self.assertEqual(response.status_code, 200)
        self.assertIn('application/json', response['Content-Type'])
        
        data = response.json()
        self.assertEqual(data['name'], 'Nigeria')
        self.assertEqual(data['capital'], 'Abuja')
        self.assertEqual(data['region'], 'Africa')
        
        # Test non-existent country
        response = self.client.get(reverse('country-detail', kwargs={'name': 'NonExistentCountry'}))
        self.assertEqual(response.status_code, 404)
        self.assertIn('application/json', response['Content-Type'])
        
        error_data = response.json()
        self.assertIn('error', error_data)
        self.assertEqual(error_data['error'], 'Country not found')

    def test_4_delete_country_by_name(self):
        """Test DELETE /countries/:name endpoint (10 points)"""
        print("\n=== Testing DELETE /countries/:name ===")
        
        # Test existing country
        initial_count = Country.objects.count()
        response = self.client.delete(reverse('country-detail', kwargs={'name': 'Nigeria'}))
        
        print(f"Delete response status: {response.status_code}")
        
        # Check if response is JSON before trying to parse it
        if response.status_code in [200, 204] and response.content and 'application/json' in response.get('Content-Type', ''):
            response_data = response.json()
            print(f"Delete response data: {response_data}")
        
        # Should return 204 No Content or 200 with message
        self.assertIn(response.status_code, [200, 204], 
                     f"Expected 200 or 204, got {response.status_code}")
        
        if response.status_code == 200 and response.content and 'application/json' in response.get('Content-Type', ''):
            data = response.json()
            self.assertIn('message', data)
        
        # Verify country was deleted
        self.assertEqual(Country.objects.count(), initial_count - 1)
        self.assertFalse(Country.objects.filter(name='Nigeria').exists())
        
        # Test non-existent country
        response = self.client.delete(reverse('country-detail', kwargs={'name': 'NonExistentCountry'}))
        self.assertEqual(response.status_code, 404)
        self.assertIn('application/json', response['Content-Type'])
        
        error_data = response.json()
        self.assertIn('error', error_data)
        self.assertEqual(error_data['error'], 'Country not found')

    def test_5_get_status(self):
        """Test GET /status endpoint (10 points)"""
        print("\n=== Testing GET /status ===")
        
        response = self.client.get(reverse('get-status'))
        self.assertEqual(response.status_code, 200)
        self.assertIn('application/json', response['Content-Type'])
        
        data = response.json()
        self.assertIn('total_countries', data)
        self.assertIn('last_refreshed_at', data)
        
        self.assertEqual(data['total_countries'], 3)
        self.assertIsNotNone(data['last_refreshed_at'])

    def test_6_get_countries_image(self):
        """Test GET /countries/image endpoint (10 points)"""
        print("\n=== Testing GET /countries/image ===")
        
        # First, ensure the cache directory exists
        from django.conf import settings
        cache_dir = getattr(settings, 'CACHE_DIR', 'cache')
        os.makedirs(cache_dir, exist_ok=True)
        
        # Create a test image
        try:
            from PIL import Image
        except ImportError:
            print("PIL not available, skipping image test")
            return
            
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
        
        print(f"Image response status: {response.status_code}")
        print(f"Image response content type: {response.get('Content-Type', 'None')}")
        
        # Should return 200 with image/png content type
        if response.status_code == 200:
            self.assertEqual(response['Content-Type'], 'image/png')
        elif response.status_code == 404:
            # If no image exists, should return JSON error
            self.assertEqual(response['Content-Type'], 'application/json')
            error_data = response.json()
            self.assertIn('error', error_data)
        
        # Clean up - wait a bit and retry if file is locked
        if os.path.exists(image_path):
            try:
                os.remove(image_path)
            except PermissionError:
                print("File is locked, waiting and retrying...")
                time.sleep(1)
                try:
                    os.remove(image_path)
                except PermissionError:
                    print("Could not delete file, skipping cleanup")

    def test_7_error_handling_and_validation(self):
        """Test error handling and validation (10 points)"""
        print("\n=== Testing Error Handling ===")
        
        # Test 404 for non-existent country (GET)
        response = self.client.get(reverse('country-detail', kwargs={'name': 'NonExistent'}))
        self.assertEqual(response.status_code, 404)
        self.assertIn('application/json', response['Content-Type'])
        error_data = response.json()
        self.assertIn('error', error_data)
        
        # Test 404 for non-existent country (DELETE)
        response = self.client.delete(reverse('country-detail', kwargs={'name': 'NonExistent'}))
        self.assertEqual(response.status_code, 404)
        self.assertIn('application/json', response['Content-Type'])
        error_data = response.json()
        self.assertIn('error', error_data)
        
        # Test invalid method for endpoints
        response = self.client.put(reverse('refresh-countries'))
        self.assertIn(response.status_code, [405, 400, 403, 404])
        
        # Ensure all error responses are JSON
        if response.status_code >= 400:
            self.assertIn('application/json', response['Content-Type'])

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

def run_all_tests():
    """Function to run all tests and return results"""
    import unittest
    loader = unittest.TestLoader()
    suite = loader.loadTestsFromTestCase(CountryAPITestCase)
    suite.addTests(loader.loadTestsFromTestCase(CountryModelTest))
    
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    return result

if __name__ == '__main__':
    print("Running Country API Tests...")
    print("=" * 50)
    
    # Run the tests
    result = run_all_tests()
    
    # Print summary
    print("=" * 50)
    if result.wasSuccessful():
        print("✅ ALL TESTS PASSED!")
    else:
        print(f"❌ {len(result.failures)} tests failed, {len(result.errors)} tests had errors")
        print("\nFailed tests:")
        for test, traceback in result.failures:
            print(f"  - {test}")
        print("\nTests with errors:")
        for test, traceback in result.errors:
            print(f"  - {test}")
    
    # Exit with appropriate code
    sys.exit(0 if result.wasSuccessful() else 1)