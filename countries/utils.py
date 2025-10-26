import requests
from django.core.exceptions import ValidationError
from rest_framework.views import exception_handler
from rest_framework.response import Response
from rest_framework import status
import random
from PIL import Image, ImageDraw, ImageFont
import os
from django.conf import settings
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

def fetch_countries_data():
    """Fetch country data from restcountries API"""
    try:
        logger.info("Fetching countries data from API...")
        response = requests.get(
            'https://restcountries.com/v2/all?fields=name,capital,region,population,flag,currencies',
            timeout=30
        )
        response.raise_for_status()
        data = response.json()
        
        if not isinstance(data, list):
            raise Exception("Invalid response format from countries API")
            
        logger.info(f"Successfully fetched {len(data)} countries")
        return data
        
    except requests.exceptions.Timeout:
        raise Exception("Countries API timeout - service unavailable")
    except requests.exceptions.ConnectionError:
        raise Exception("Could not connect to countries API - network error")
    except requests.exceptions.RequestException as e:
        raise Exception(f"Countries API error: {str(e)}")
    except Exception as e:
        raise Exception(f"Unexpected error fetching countries: {str(e)}")

def fetch_exchange_rates():
    """Fetch exchange rates from open.er-api.com"""
    try:
        logger.info("Fetching exchange rates from API...")
        response = requests.get('https://open.er-api.com/v6/latest/USD', timeout=30)
        response.raise_for_status()
        data = response.json()
        
        if data.get('result') == 'success':
            logger.info("Successfully fetched exchange rates")
            return data['rates']
        else:
            raise Exception("Exchange rate API returned error status")
            
    except requests.exceptions.Timeout:
        raise Exception("Exchange rates API timeout - service unavailable")
    except requests.exceptions.ConnectionError:
        raise Exception("Could not connect to exchange rates API - network error")
    except requests.exceptions.RequestException as e:
        raise Exception(f"Exchange rates API error: {str(e)}")
    except Exception as e:
        raise Exception(f"Unexpected error fetching exchange rates: {str(e)}")

def get_currency_code(country_currencies):
    """Extract currency code from country currencies data"""
    if not country_currencies or len(country_currencies) == 0:
        return None
    
    # Get the first currency code
    currency = country_currencies[0]
    return currency.get('code')

def calculate_estimated_gdp(population, exchange_rate):
    """Calculate estimated GDP using random multiplier"""
    if not population or not exchange_rate or exchange_rate <= 0:
        return None
    
    random_multiplier = random.uniform(1000, 2000)
    gdp = (population * random_multiplier) / exchange_rate
    return round(gdp, 2)

def generate_summary_image(countries):
    """Generate summary image with country statistics"""
    try:
        img_width = 600
        img_height = 400
        background_color = (240, 240, 240)
        text_color = (0, 0, 0)
        highlight_color = (0, 100, 200)
        
        image = Image.new('RGB', (img_width, img_height), background_color)
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
        
        # Title
        draw.text((20, 20), "Country GDP Summary", fill=highlight_color, font=font_large)
        
        # Total countries
        total_countries = len(countries)
        draw.text((20, 60), f"Total Countries: {total_countries}", fill=text_color, font=font_medium)
        
        # Top 5 countries by GDP
        draw.text((20, 100), "Top 5 Countries by GDP:", fill=text_color, font=font_medium)
        
        top_countries = sorted(
            [c for c in countries if c.estimated_gdp is not None],
            key=lambda x: x.estimated_gdp,
            reverse=True
        )[:5]
        
        y_position = 130
        for i, country in enumerate(top_countries, 1):
            gdp_str = f"${country.estimated_gdp:,.2f}" if country.estimated_gdp else "N/A"
            text = f"{i}. {country.name}: {gdp_str}"
            draw.text((40, y_position), text, fill=text_color, font=font_small)
            y_position += 25
        
        # Timestamp
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S UTC")
        draw.text((20, img_height - 40), f"Last refresh: {timestamp}", fill=text_color, font=font_small)
        
        # Save image
        image_path = os.path.join(settings.CACHE_DIR, 'summary.png')
        image.save(image_path)
        logger.info(f"Summary image generated at {image_path}")
        return image_path
        
    except Exception as e:
        logger.error(f"Error generating summary image: {str(e)}")
        raise Exception(f"Failed to generate summary image: {str(e)}")

def custom_exception_handler(exc, context):
    """Custom exception handler for consistent JSON error responses"""
    logger.error(f"Exception: {str(exc)}")
    logger.error(f"Context: {context}")
    
    # Call REST framework's default exception handler first
    response = exception_handler(exc, context)
    
    if response is not None:
        # Convert DRF errors to consistent JSON format
        if response.status_code == status.HTTP_400_BAD_REQUEST:
            response.data = {
                "error": "Validation failed",
                "details": response.data
            }
        elif response.status_code == status.HTTP_404_NOT_FOUND:
            response.data = {
                "error": "Country not found"
            }
        elif response.status_code == status.HTTP_403_FORBIDDEN:
            response.data = {
                "error": "Permission denied"
            }
    else:
        # Handle uncaught exceptions
        if isinstance(exc, ValidationError):
            response = Response(
                {
                    "error": "Validation failed",
                    "details": str(exc)
                },
                status=status.HTTP_400_BAD_REQUEST
            )
        else:
            response = Response(
                {"error": "Internal server error"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    return response