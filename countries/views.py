from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from django.db.models import Q
from .models import Country
from .serializers import CountrySerializer, StatusSerializer
from .utils import (
    fetch_countries_data, 
    fetch_exchange_rates, 
    get_currency_code,
    generate_summary_image
)
import os
from django.conf import settings
from django.http import FileResponse, HttpResponse
import random

@api_view(['POST'])
def refresh_countries(request):
    """Fetch and update country data from external APIs"""
    try:
        # Fetch data from external APIs
        countries_data = fetch_countries_data()
        exchange_rates = fetch_exchange_rates()
        
        updated_count = 0
        created_count = 0
        
        for country_data in countries_data:
            currency_code = get_currency_code(country_data.get('currencies', []))
            exchange_rate = exchange_rates.get(currency_code) if currency_code else None
            
            # Calculate estimated GDP
            population = country_data.get('population')
            estimated_gdp = None
            
            if population and exchange_rate and exchange_rate > 0:
                random_multiplier = random.uniform(1000, 2000)
                estimated_gdp = (population * random_multiplier) / exchange_rate
            
            country_obj, created = Country.objects.update_or_create(
                name=country_data['name'],
                defaults={
                    'capital': country_data.get('capital'),
                    'region': country_data.get('region'),
                    'population': population,
                    'currency_code': currency_code,
                    'exchange_rate': exchange_rate,
                    'estimated_gdp': estimated_gdp,
                    'flag_url': country_data.get('flag')
                }
            )
            
            if created:
                created_count += 1
            else:
                updated_count += 1
        
        # Generate summary image
        all_countries = Country.objects.all()
        generate_summary_image(all_countries)
        
        return Response({
            "message": "Refresh completed successfully",
            "created": created_count,
            "updated": updated_count,
            "total": len(countries_data)
        })
        
    except Exception as e:
        return Response(
            {
                "error": "External data source unavailable",
                "details": str(e)
            },
            status=status.HTTP_503_SERVICE_UNAVAILABLE
        )

@api_view(['GET'])
def list_countries(request):
    """Get all countries with filtering and sorting"""
    queryset = Country.objects.all()
    
    # Filter by region
    region = request.GET.get('region')
    if region:
        queryset = queryset.filter(region__icontains=region)
    
    # Filter by currency
    currency = request.GET.get('currency')
    if currency:
        queryset = queryset.filter(currency_code__iexact=currency)
    
    # Sorting
    sort = request.GET.get('sort')
    if sort == 'gdp_desc':
        queryset = queryset.filter(estimated_gdp__isnull=False).order_by('-estimated_gdp')
    elif sort == 'gdp_asc':
        queryset = queryset.filter(estimated_gdp__isnull=False).order_by('estimated_gdp')
    elif sort == 'name_asc':
        queryset = queryset.order_by('name')
    elif sort == 'name_desc':
        queryset = queryset.order_by('-name')
    elif sort == 'population_desc':
        queryset = queryset.order_by('-population')
    elif sort == 'population_asc':
        queryset = queryset.order_by('population')
    else:
        queryset = queryset.order_by('name')
    
    serializer = CountrySerializer(queryset, many=True)
    return Response(serializer.data)

@api_view(['GET'])
def get_country_by_name(request, name):
    """Get single country by name (case-insensitive)"""
    country = get_object_or_404(Country, name__iexact=name)
    serializer = CountrySerializer(country)
    return Response(serializer.data)

@api_view(['DELETE'])
def delete_country(request, name):
    """Delete country by name (case-insensitive)"""
    country = get_object_or_404(Country, name__iexact=name)
    country.delete()
    return Response({"message": "Country deleted successfully"})

@api_view(['GET'])
def get_status(request):
    """Get total countries and last refresh timestamp"""
    total_countries = Country.objects.count()
    
    # Get the most recent refresh timestamp
    latest_country = Country.objects.order_by('-last_refreshed_at').first()
    last_refreshed_at = latest_country.last_refreshed_at if latest_country else None
    
    data = {
        "total_countries": total_countries,
        "last_refreshed_at": last_refreshed_at
    }
    
    serializer = StatusSerializer(data)
    return Response(serializer.data)

@api_view(['GET'])
def serve_summary_image(request):
    """Serve the generated summary image"""
    image_path = os.path.join(settings.CACHE_DIR, 'summary.png')
    
    if os.path.exists(image_path):
        return FileResponse(open(image_path, 'rb'), content_type='image/png')
    else:
        return Response(
            {"error": "Summary image not found"},
            status=status.HTTP_404_NOT_FOUND
        )
    

@api_view(['GET', 'DELETE'])
def country_detail(request, name):
    """Get or delete a specific country by name"""
    country = get_object_or_404(Country, name__iexact=name)
    
    if request.method == 'GET':
        serializer = CountrySerializer(country)
        return Response(serializer.data)
    
    elif request.method == 'DELETE':
        country.delete()
        return Response({"message": "Country deleted successfully"})