from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.db import IntegrityError
from .models import Country
from .serializers import CountrySerializer, StatusSerializer
from .utils import (
    fetch_countries_data, 
    fetch_exchange_rates, 
    get_currency_code,
    calculate_estimated_gdp,
    generate_summary_image
)
import os
from django.conf import settings
from django.http import FileResponse
import random
import logging

logger = logging.getLogger(__name__)

@api_view(['POST'])
def refresh_countries(request):
    """Fetch and update country data from external APIs"""
    try:
        logger.info("Starting countries refresh...")
        
        # Fetch data from external APIs
        countries_data = fetch_countries_data()
        exchange_rates = fetch_exchange_rates()
        
        updated_count = 0
        created_count = 0
        errors = []
        
        for country_data in countries_data:
            try:
                currency_code = get_currency_code(country_data.get('currencies', []))
                exchange_rate = exchange_rates.get(currency_code) if currency_code else None
                
                # Get population
                population = country_data.get('population')
                if population is None:
                    errors.append(f"Missing population for {country_data.get('name')}")
                    continue
                
                # Calculate estimated GDP
                estimated_gdp = calculate_estimated_gdp(population, exchange_rate)
                
                # Update or create country
                country_obj, created = Country.objects.update_or_create(
                    name=country_data['name'],
                    defaults={
                        'capital': country_data.get('capital', ''),
                        'region': country_data.get('region', ''),
                        'population': population,
                        'currency_code': currency_code,
                        'exchange_rate': exchange_rate,
                        'estimated_gdp': estimated_gdp,
                        'flag_url': country_data.get('flag', '')
                    }
                )
                
                if created:
                    created_count += 1
                else:
                    updated_count += 1
                    
            except IntegrityError as e:
                errors.append(f"Integrity error for {country_data.get('name')}: {str(e)}")
            except Exception as e:
                errors.append(f"Error processing {country_data.get('name')}: {str(e)}")
        
        # Generate summary image
        try:
            all_countries = Country.objects.all()
            generate_summary_image(all_countries)
            image_generated = True
        except Exception as e:
            logger.error(f"Failed to generate summary image: {str(e)}")
            image_generated = False
            errors.append(f"Image generation failed: {str(e)}")
        
        response_data = {
            "message": "Refresh completed successfully",
            "created": created_count,
            "updated": updated_count,
            "total_processed": len(countries_data),
            "image_generated": image_generated
        }
        
        if errors:
            response_data["errors"] = errors[:10]  # Limit errors in response
        
        logger.info(f"Refresh completed: {created_count} created, {updated_count} updated")
        return Response(response_data)
        
    except Exception as e:
        logger.error(f"Refresh failed: {str(e)}")
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
    try:
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
        
    except Exception as e:
        logger.error(f"Error listing countries: {str(e)}")
        return Response(
            {"error": "Internal server error"},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

@api_view(['GET', 'DELETE'])
def country_detail(request, name):
    """Handle both GET and DELETE for a specific country"""
    try:
        country = Country.objects.get(name__iexact=name)
    except Country.DoesNotExist:
        return Response(
            {"error": "Country not found"},
            status=status.HTTP_404_NOT_FOUND
        )
    
    if request.method == 'GET':
        serializer = CountrySerializer(country)
        return Response(serializer.data)
    
    elif request.method == 'DELETE':
        country.delete()
        return Response(
            {"message": "Country deleted successfully"},
            status=status.HTTP_200_OK
        )

@api_view(['GET'])
def get_status(request):
    """Get total countries and last refresh timestamp"""
    try:
        total_countries = Country.objects.count()
        
        # Get the most recent refresh timestamp
        latest_country = Country.objects.order_by('-last_refreshed_at').first()
        last_refreshed_at = latest_country.last_refreshed_at if latest_country else None
        
        # Return simple dict instead of using serializer
        return Response({
            "total_countries": total_countries,
            "last_refreshed_at": last_refreshed_at
        })
        
    except Exception as e:
        logger.error(f"Error getting status: {str(e)}")
        return Response(
            {"error": "Internal server error"},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['GET'])
def serve_summary_image(request):
    """Serve the generated summary image"""
    try:
        image_path = os.path.join(settings.CACHE_DIR, 'summary.png')
        
        if os.path.exists(image_path):
            return FileResponse(
                open(image_path, 'rb'), 
                content_type='image/png',
                as_attachment=False
            )
        else:
            return Response(
                {"error": "Summary image not found"},
                status=status.HTTP_404_NOT_FOUND
            )
            
    except Exception as e:
        logger.error(f"Error serving image: {str(e)}")
        return Response(
            {"error": "Internal server error"},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )