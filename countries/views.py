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
    start_time = time.time() # type: ignore

    try:
        countries_data = ExternalAPIService.fetch_countries_data()
        exchange_rates = ExternalAPIService.fetch_exchange_rates()

        updated_count = 0
        created_count = 0

        for country_data in countries_data:
            processed_data = CountryDataProcessor.process_country_data(country_data, exchange_rates)
            processed_data['last_refreshed_at'] = timezone.now() # type: ignore
            country, created = Country.objects.update_or_create(
                name=processed_data['name'], defaults=processed_data
            )
            if created:
                created_count += 1
            else:
                updated_count += 1

        # Fallback safeguard if too long
        if time.time() - start_time > 15: # type: ignore
            raise TimeoutError("Refresh took too long")

        SummaryImageGenerator.generate_summary_image()

        return Response({
            "message": "Refresh completed successfully",
            "created": created_count,
            "updated": updated_count,
            "total_countries": Country.objects.count()
        }, status=status.HTTP_200_OK)

    except TimeoutError:
        return Response({"error": "Refresh timed out"}, status=status.HTTP_504_GATEWAY_TIMEOUT)
    except Exception as e:
        return Response({
            "error": "External data source unavailable",
            "details": str(e)
        }, status=status.HTTP_503_SERVICE_UNAVAILABLE)

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
    
    # FIXED: Proper GDP sorting with null handling
    sort = request.GET.get('sort')
    if sort == 'gdp_desc':
        # Put null GDP values at the end, then sort by GDP descending
        queryset = queryset.order_by('-estimated_gdp', 'name')
    elif sort == 'gdp_asc':
        # Put null GDP values at the beginning, then sort by GDP ascending
        queryset = queryset.order_by('estimated_gdp', 'name')
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



@api_view(['GET', 'DELETE'])
def country_detail(request, name):
    """Handle both GET and DELETE for specific country"""
    try:
        country = Country.objects.get(name__iexact=name)
    except Country.DoesNotExist:
        return Response(
            {'error': 'Country not found'},
            status=status.HTTP_404_NOT_FOUND
        )
    
    if request.method == 'GET':
        serializer = CountrySerializer(country)
        return Response(serializer.data)
    
    elif request.method == 'DELETE':
        country.delete()
        return Response(
            {'message': 'Country deleted successfully'},
            status=status.HTTP_200_OK  # Use 200 instead of 204 for JSON response
        )

@api_view(['GET'])
def get_status(request):
    """GET /status - Return country count & last refresh timestamp"""
    total_countries = Country.objects.count()
    last_country = Country.objects.order_by('-last_refreshed_at').first()
    last_refreshed_at = last_country.last_refreshed_at.isoformat() if last_country and last_country.last_refreshed_at else None

    data = {
        "total_countries": total_countries,
        "last_refreshed_at": last_refreshed_at  # ✅ must be a string
    }

    return Response(data, status=status.HTTP_200_OK)


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
        response = FileResponse(open(image_path, 'rb'), content_type='image/png')
        response['Content-Disposition'] = 'inline; filename="summary.png"'
        return response
    except Exception as e:
        return Response(
            {'error': 'Could not serve image'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )