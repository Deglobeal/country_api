import requests
import random
from datetime import datetime
import os
from PIL import Image, ImageDraw, ImageFont
import io
from django.conf import settings
from django.utils import timezone
from .models import Country

def fetch_countries_data():
    """Fetch country data from restcountries API"""
    try:
        url = 'https://restcountries.com/v2/all?fields=name,capital,region,population,flag,currencies'
        print(f"Fetching from: {url}")
        response = requests.get(url, timeout=30)
        print(f"Response status: {response.status_code}")
        response.raise_for_status()
        data = response.json()
        print(f"Received {len(data)} countries")
        return data
    except requests.RequestException as e:
        print(f"Countries API error: {str(e)}")
        raise Exception(f"Could not fetch data from Countries API: {str(e)}")

def fetch_exchange_rates():
    """Fetch exchange rates from open.er-api.com"""
    try:
        url = 'https://open.er-api.com/v6/latest/USD'
        print(f"Fetching from: {url}")
        response = requests.get(url, timeout=30)
        print(f"Response status: {response.status_code}")
        response.raise_for_status()
        data = response.json()
        print(f"Exchange API result: {data.get('result')}")
        if data.get('result') == 'success':
            return data['rates']
        else:
            raise Exception("Exchange rate API returned unsuccessful result")
    except requests.RequestException as e:
        print(f"Exchange API error: {str(e)}")
        raise Exception(f"Could not fetch data from Exchange Rates API: {str(e)}")
def calculate_estimated_gdp(population, exchange_rate):
    """Calculate estimated GDP using population and exchange rate"""
    if not exchange_rate:
        return None
    
    try:
        population_val = float(population)
        exchange_rate_val = float(exchange_rate)
        
        if exchange_rate_val == 0:
            return None
            
        multiplier = random.randint(1000, 2000)
        gdp = (population_val * multiplier) / exchange_rate_val
        return float(gdp)
    except (TypeError, ValueError, ZeroDivisionError):
        return None



def refresh_countries_data():
    """Main function to refresh countries data"""
    from .models import Country
    
    try:
        # Fetch data from external APIs
        print("Fetching countries data...")
        countries_data = fetch_countries_data()
        print(f"Fetched {len(countries_data)} countries")
        
        print("Fetching exchange rates...")
        exchange_rates = fetch_exchange_rates()
        print("Exchange rates fetched successfully")
        
        created_count = 0
        updated_count = 0
        error_count = 0
        
        # Clear existing data to avoid duplicates
        Country.objects.all().delete()
        print("Cleared existing countries data")
        
        for country_data in countries_data:
            try:
                # Extract currency code (first one if multiple)
                currency_code = None
                currencies = country_data.get('currencies', [])
                if currencies and len(currencies) > 0:
                    currency_code = currencies[0].get('code')
                
                # Get exchange rate
                exchange_rate = None
                if currency_code and currency_code in exchange_rates:
                    exchange_rate = exchange_rates[currency_code]
                
                # Calculate estimated GDP
                estimated_gdp = calculate_estimated_gdp(
                    country_data.get('population', 0), 
                    exchange_rate
                )
                
                # Create country record
                Country.objects.create(
                    name=country_data['name'],
                    capital=country_data.get('capital'),
                    region=country_data.get('region'),
                    population=int(country_data.get('population', 0)),
                    currency_code=currency_code,
                    exchange_rate=exchange_rate,
                    estimated_gdp=estimated_gdp,
                    flag_url=country_data.get('flag'),
                )
                created_count += 1
                    
            except Exception as e:
                print(f"Error processing country {country_data.get('name')}: {e}")
                error_count += 1
                continue
        
        # Ensure cache directory exists
        os.makedirs(settings.CACHE_DIR, exist_ok=True)
        
        # Generate summary image
        print("Generating summary image...")
        try:
            generate_summary_image()
            print("Summary image generated")
        except Exception as e:
            print(f"Error generating image: {e}")
        
        return {
            'message': f'Successfully refreshed {created_count} countries',
            'total_countries': created_count,
            'errors': error_count
        }
        
    except Exception as e:
        print(f"Error in refresh_countries_data: {e}")
        raise e





def generate_summary_image():
    """Generate summary image with countries data"""
    from .models import Country
    
    try:
        # Get top 5 countries by GDP
        top_countries = Country.objects.exclude(estimated_gdp__isnull=True)\
                                     .order_by('-estimated_gdp')[:5]
        
        # Create image
        img_width = 800
        img_height = 600
        image = Image.new('RGB', (img_width, img_height), color='white')
        draw = ImageDraw.Draw(image)
        
        # Use default font
        try:
            font_large = ImageFont.truetype("arial.ttf", 24)
            font_medium = ImageFont.truetype("arial.ttf", 18)
            font_small = ImageFont.truetype("arial.ttf", 14)
        except:
            font_large = ImageFont.load_default()
            font_medium = ImageFont.load_default()
            font_small = ImageFont.load_default()
        
        # Draw content
        y_position = 30
        
        # Title
        draw.text((img_width//2 - 100, y_position), "Countries Summary", fill='black', font=font_large)
        y_position += 50
        
        # Total countries
        total_countries = Country.objects.count()
        draw.text((50, y_position), f"Total Countries: {total_countries}", fill='black', font=font_medium)
        y_position += 40
        
        # Top countries by GDP
        draw.text((50, y_position), "Top 5 Countries by GDP:", fill='black', font=font_medium)
        y_position += 40
        
        for i, country in enumerate(top_countries, 1):
            gdp_str = f"${country.estimated_gdp:,.2f}" if country.estimated_gdp else "N/A"
            text = f"{i}. {country.name}: {gdp_str}"
            draw.text((70, y_position), text, fill='black', font=font_small)
            y_position += 30
        
        y_position += 30
        
        # Last refresh time
        latest_country = Country.objects.order_by('-last_refreshed_at').first()
        if latest_country:
            refresh_time = latest_country.last_refreshed_at.strftime("%Y-%m-%d %H:%M:%S UTC")
            draw.text((50, y_position), f"Last Refresh: {refresh_time}", fill='black', font=font_small)
        
        # Ensure cache directory exists
        os.makedirs(settings.CACHE_DIR, exist_ok=True)
        
        # Save image
        image_path = os.path.join(settings.CACHE_DIR, 'summary.png')
        image.save(image_path)
        print(f"Image saved to: {image_path}")
        
        return image_path
    except Exception as e:
        print(f"Error generating image: {e}")
        # Create a simple error image
        try:
            img = Image.new('RGB', (400, 200), color='red')
            draw = ImageDraw.Draw(img)
            draw.text((50, 80), "Error generating summary", fill='white')
            error_path = os.path.join(settings.CACHE_DIR, 'summary.png')
            img.save(error_path)
            return error_path
        except:
            return None





def custom_exception_handler(exc, context):
    """Custom exception handler for consistent error responses"""
    from rest_framework.views import exception_handler as drf_exception_handler
    from rest_framework import status
    
    # Call REST framework's default exception handler first
    response = drf_exception_handler(exc, context)
    
    if response is not None:
        if isinstance(response.data, dict):
            if 'error' not in response.data:
                if response.status_code == status.HTTP_404_NOT_FOUND:
                    response.data = {'error': 'Country not found'}
                elif response.status_code == status.HTTP_400_BAD_REQUEST:
                    response.data = {'error': 'Validation failed', 'details': response.data}
                elif response.status_code == status.HTTP_405_METHOD_NOT_ALLOWED:
                    response.data = {'error': 'Method not allowed'}
                else:
                    response.data = {'error': response.data.get('detail', 'An error occurred')}
        else:
            response.data = {'error': 'Validation failed', 'details': response.data}
    else:
        response = Response( # type: ignore
            {'error': 'Internal server error'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )
    
    return response


