import os
import django
import requests

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'country_api.settings')
django.setup()

from countries.models import Country

BASE_URL = "http://localhost:8000/countries"

def debug_refresh():
    print("Testing refresh endpoint...")
    response = requests.post(f"{BASE_URL}/refresh")
    print(f"Status: {response.status_code}")
    if response.status_code != 200:
        print(f"Error: {response.text}")
    else:
        print(f"Success: {response.json()}")

def debug_countries():
    print("\nTesting countries list...")
    response = requests.get(f"{BASE_URL}/")
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        countries = response.json()
        print(f"Found {len(countries)} countries")
        if countries:
            print("First country:", countries[0]['name'])
    else:
        print(f"Error: {response.text}")

def debug_specific_country():
    print("\nTesting specific country...")
    # Try a few different country names
    test_countries = ["United States", "United States of America", "Albania", "France"]
    
    for country_name in test_countries:
        response = requests.get(f"{BASE_URL}/{country_name}")
        print(f"{country_name}: Status {response.status_code}")
        if response.status_code == 200:
            print(f"Found: {response.json()['name']}")
            break

def debug_database():
    print("\nChecking database directly...")
    count = Country.objects.count()
    print(f"Total countries in database: {count}")
    if count > 0:
        first_country = Country.objects.first()
        print(f"First country: {first_country.name}")

if __name__ == "__main__":
    debug_refresh()
    debug_countries()
    debug_specific_country()
    debug_database()