from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.db.models import Q
from django.shortcuts import get_object_or_404
from .models import Country
from .serializers import CountrySerializer, StatusSerializer, ErrorSerializer
from .services import ExternalAPIService, CountryDataProcessor
from .image_service import SummaryImageGenerator
import os
from django.http import FileResponse, HttpResponse
from django.conf import settings

@api_view(['POST'])
def refresh_countries(request):
    """POST /countries/refresh - Fetch and update country data"""
    try:
        # Fetch data from external APIs
        countries_data = ExternalAPIService.fetch_countries_data()
        exchange_rates = ExternalAPIService.fetch_exchange_rates()
        
        updated_count = 0
        created_count = 0
        
        # Process each country
        for country_data in countries_data:
            processed_data = CountryDataProcessor.process_country_data(
                country_data, 
                exchange_rates
            )
            
            # Update or create country
            country, created = Country.objects.update_or_create(
                name=processed_data['name'],
                defaults=processed_data
            )
            
            if created:
                created_count += 1
            else:
                updated_count += 1
        
        # Generate summary image
        SummaryImageGenerator.generate_summary_image()
        
        return Response({
            'message': 'Refresh completed successfully',
            'created': created_count,
            'updated': updated_count,
            'total': len(countries_data)
        })
        
    except Exception as e:
        return Response(
            {
                'error': 'External data source unavailable',
                'details': str(e)
            },
            status=status.HTTP_503_SERVICE_UNAVAILABLE
        )

@api_view(['GET'])
def list_countries(request):
    """GET /countries - List countries with filtering and sorting"""
    queryset = Country.objects.all()
    
    # Filter by region
    region = request.GET.get('region')
    if region:
        queryset = queryset.filter(region__iexact=region)
    
    # Filter by currency
    currency = request.GET.get('currency')
    if currency:
        queryset = queryset.filter(currency_code__iexact=currency)
    
    # Sorting
    sort = request.GET.get('sort')
    if sort == 'gdp_desc':
        queryset = queryset.exclude(estimated_gdp__isnull=True).order_by('-estimated_gdp')
    elif sort == 'gdp_asc':
        queryset = queryset.exclude(estimated_gdp__isnull=True).order_by('estimated_gdp')
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
def get_country(request, name):
    """GET /countries/:name - Get country by name"""
    country = get_object_or_404(Country, name__iexact=name)
    serializer = CountrySerializer(country)
    return Response(serializer.data)

@api_view(['DELETE'])
def delete_country(request, name):
    """DELETE /countries/:name - Delete country by name"""
    country = get_object_or_404(Country, name__iexact=name)
    country.delete()
    return Response(status=status.HTTP_204_NO_CONTENT)

@api_view(['GET'])
def get_status(request):
    """GET /status - Get total countries and last refresh timestamp"""
    total_countries = Country.objects.count()
    
    last_refresh = Country.objects.order_by('-last_refreshed_at').first()
    last_refreshed_at = last_refresh.last_refreshed_at if last_refresh else None
    
    data = {
        'total_countries': total_countries,
        'last_refreshed_at': last_refreshed_at
    }
    
    serializer = StatusSerializer(data)
    return Response(serializer.data)

@api_view(['GET'])
def get_country_image(request):
    """GET /countries/image - Serve summary image"""
    image_path = os.path.join(settings.CACHE_DIR, 'summary.png')
    
    if not os.path.exists(image_path):
        return Response(
            {'error': 'Summary image not found'},
            status=status.HTTP_404_NOT_FOUND
        )
    
    try:
        return FileResponse(open(image_path, 'rb'), content_type='image/png')
    except Exception as e:
        return Response(
            {'error': 'Could not serve image'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )