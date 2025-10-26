# tests/test_api.py
import json
from django.test import TestCase, Client
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

class APITestCase(TestCase):
    def setUp(self):
        self.client = APIClient()

    def test_refresh_endpoint(self):
        """Test POST /countries/refresh"""
        response = self.client.post(reverse('refresh-countries'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_get_countries_with_filters_and_sorting(self):
        """Test GET /countries with filters and sorting"""
        response = self.client.get(
            reverse('countries-list'),
            {'region': 'Europe', 'currency': 'EUR', 'sort_by': 'gdp', 'sort_order': 'desc'}
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIsInstance(response.json(), list)
        # Add more assertions to check filtering and sorting

    def test_get_country_by_name(self):
        """Test GET /countries/:name"""
        # Test with valid country name
        response = self.client.get(reverse('country-detail', args=['valid_country']))
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Test with invalid country name
        response = self.client.get(reverse('country-detail', args=['invalid_country']))
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_delete_country(self):
        """Test DELETE /countries/:name"""
        # Test with valid country name
        response = self.client.delete(reverse('country-detail', args=['valid_country']))
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

        # Test with invalid country name
        response = self.client.delete(reverse('country-detail', args=['invalid_country']))
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_status_endpoint(self):
        """Test GET /status"""
        response = self.client.get(reverse('status'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIsInstance(response.json(), dict)

    def test_get_country_image(self):
        """Test GET /countries/image"""
        response = self.client.get(reverse('country-image', args=['valid_country']))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('image/', response['Content-Type'])

    def test_error_handling_and_validation(self):
        """Test error responses are in JSON format"""
        # Test 404 error
        response = self.client.get(reverse('country-detail', args=['non_existent_country']))
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertIsInstance(response.json(), dict)

        # Test 400 error
        response = self.client.get(reverse('countries-list'), {'invalid_param': 'value'})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIsInstance(response.json(), dict)