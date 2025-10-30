import requests
import random
from decimal import Decimal
from django.conf import settings
from typing import Dict, List, Optional, Tuple
import logging

logger = logging.getLogger(__name__)

class ExternalAPIService:
    """Handles fetching of country and exchange rate data from external APIs."""

    @staticmethod
    def fetch_countries_data() -> List[Dict]:
        """Fetch country data from multiple fallback APIs."""
        endpoints = [
            "https://restcountries.com/v3.1/all?fields=name,capital,region,population,flags,currencies",
            "https://restcountries.com/v2/all?fields=name,capital,region,population,flag,currencies",
        ]
        for endpoint in endpoints:
            try:
                logger.info(f"Fetching countries from {endpoint}")
                response = requests.get(endpoint, timeout=15)
                response.raise_for_status()
                data = response.json()

                if isinstance(data, list) and len(data) > 0:
                    logger.info(f"✅ Fetched {len(data)} countries successfully.")
                    return data
            except Exception as e:
                logger.warning(f"⚠️ Failed endpoint {endpoint}: {e}")
                continue

        raise Exception("All country API endpoints failed")

    @staticmethod
    def fetch_exchange_rates() -> Dict:
        """Fetch exchange rates with fallback defaults."""
        endpoints = [
            "https://api.exchangerate-api.com/v4/latest/USD",
            "https://open.er-api.com/v6/latest/USD",
        ]
        for endpoint in endpoints:
            try:
                logger.info(f"Fetching exchange rates from {endpoint}")
                response = requests.get(endpoint, timeout=15)
                response.raise_for_status()
                data = response.json()
                if "rates" in data:
                    logger.info("✅ Successfully fetched exchange rates")
                    return data["rates"]
            except Exception as e:
                logger.warning(f"⚠️ Failed exchange endpoint {endpoint}: {e}")
                continue

        # Fallback rates if all endpoints fail
        logger.warning("Using fallback exchange rates")
        return {
            "USD": 1.0, "EUR": 0.93, "GBP": 0.80, "NGN": 1600.0,
            "GHS": 15.0, "JPY": 150.0, "CAD": 1.35, "AUD": 1.55
        }
class CountryDataProcessor:
    @staticmethod
    def extract_currency_code(currencies: List[Dict]) -> Optional[str]:
        """Extract currency code from currencies array"""
        if not currencies or len(currencies) == 0:
            return None
        
        # Try different possible key names
        currency = currencies[0]
        for key in ['code', 'currency_code', 'id']:
            if key in currency and currency[key]:
                return currency[key]
        
        return None

    @staticmethod
    def calculate_estimated_gdp(population: int, exchange_rate: Optional[Decimal]) -> Optional[Decimal]:
        """Calculate estimated GDP using random multiplier"""
        if not exchange_rate or exchange_rate == 0:
            return None
        
        random_multiplier = Decimal(str(random.uniform(1000, 2000)))
        population_decimal = Decimal(str(population))
        exchange_rate_decimal = Decimal(str(exchange_rate))
        
        estimated = (population_decimal * random_multiplier) / exchange_rate_decimal
        return estimated.quantize(Decimal('0.01'))

    @staticmethod
    def process_country_data(country_data: Dict, exchange_rates: Dict) -> Dict:
        """Process individual country data"""
        # Extract name with fallback for different API versions
        name = country_data.get('name')
        if isinstance(name, dict):
            name = name.get('common') or name.get('official')
        
        # Extract flag URL with fallback
        flag_url = country_data.get('flag') or country_data.get('flags', {}).get('png')
        
        # Extract currencies
        currencies = country_data.get('currencies', [])
        
        currency_code = CountryDataProcessor.extract_currency_code(currencies)
        
        exchange_rate = None
        if currency_code and currency_code in exchange_rates:
            exchange_rate = Decimal(str(exchange_rates[currency_code]))
        
        estimated_gdp = CountryDataProcessor.calculate_estimated_gdp(
            country_data.get('population', 0),
            exchange_rate
        )
        
        return {
            'name': name or 'Unknown',
            'capital': country_data.get('capital', [''])[0] if isinstance(country_data.get('capital'), list) else country_data.get('capital'),
            'region': country_data.get('region'),
            'population': country_data.get('population', 0),
            'currency_code': currency_code,
            'exchange_rate': exchange_rate,
            'estimated_gdp': estimated_gdp,
            'flag_url': flag_url
        }



    
    

    
    

   