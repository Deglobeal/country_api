import requests
import random
from decimal import Decimal
from django.conf import settings
from typing import Dict, List, Optional, Tuple

class ExternalAPIService:
    @staticmethod
    def fetch_countries_data() -> List[Dict]:
        """Fetch country data from restcountries API"""
        try:
            response = requests.get(
                'https://restcountries.com/v2/all?fields=name,capital,region,population,flag,currencies',
                timeout=30
            )
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            raise Exception(f"Could not fetch data from Countries API: {str(e)}")

    @staticmethod
    def fetch_exchange_rates() -> Dict:
        """Fetch exchange rates from er-api"""
        try:
            response = requests.get(
                'https://open.er-api.com/v6/latest/USD',
                timeout=30
            )
            response.raise_for_status()
            data = response.json()
            if data.get('result') != 'success':
                raise Exception("Exchange rate API returned non-success result")
            return data.get('rates', {})
        except requests.exceptions.RequestException as e:
            raise Exception(f"Could not fetch data from Exchange Rate API: {str(e)}")

class CountryDataProcessor:
    @staticmethod
    def extract_currency_code(currencies: List[Dict]) -> Optional[str]:
        """Extract currency code from currencies array"""
        if not currencies or len(currencies) == 0:
            return None
        return currencies[0].get('code')

    @staticmethod
    def calculate_estimated_gdp(population: int, exchange_rate: Optional[Decimal]) -> Optional[Decimal]:
        """Calculate estimated GDP using random multiplier"""
        if not exchange_rate or exchange_rate == 0:
            return None
        
        random_multiplier = random.randint(1000, 2000)
        estimated = (population * random_multiplier) / exchange_rate
        return Decimal(str(estimated)).quantize(Decimal('0.01'))

    @staticmethod
    def process_country_data(
        country_data: Dict, 
        exchange_rates: Dict
    ) -> Dict:
        """Process individual country data"""
        currency_code = CountryDataProcessor.extract_currency_code(
            country_data.get('currencies', [])
        )
        
        exchange_rate = None
        if currency_code and currency_code in exchange_rates:
            exchange_rate = Decimal(str(exchange_rates[currency_code]))
        
        estimated_gdp = CountryDataProcessor.calculate_estimated_gdp(
            country_data.get('population', 0),
            exchange_rate
        )
        
        return {
            'name': country_data.get('name', ''),
            'capital': country_data.get('capital'),
            'region': country_data.get('region'),
            'population': country_data.get('population', 0),
            'currency_code': currency_code,
            'exchange_rate': exchange_rate,
            'estimated_gdp': estimated_gdp,
            'flag_url': country_data.get('flag', '')
        }