from django.http import Http404, JsonResponse
from rest_framework import status, filters
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.views import APIView
from django_filters.rest_framework import DjangoFilterBackend
from django.http import FileResponse
import os
from django.conf import settings

from .models import Country
from .serializers import CountrySerializer
from .utils import refresh_countries_data, generate_summary_image

class CountryListView(APIView):
    def get_queryset(self):
        return Country.objects.all()
    
    def get(self, request):
        queryset = self.get_queryset()
        
        # Apply filters
        region = request.GET.get('region')
        currency = request.GET.get('currency')
        
        if region:
            queryset = queryset.filter(region__iexact=region)
        if currency:
            queryset = queryset.filter(currency_code__iexact=currency)
        
        # Apply sorting
        sort = request.GET.get('sort')
        if sort == 'gdp_desc':
            queryset = queryset.exclude(estimated_gdp__isnull=True).order_by('-estimated_gdp')
        elif sort == 'gdp_asc':
            queryset = queryset.exclude(estimated_gdp__isnull=True).order_by('estimated_gdp')
        elif sort and sort.endswith('_desc'):
            sort_field = sort.replace('_desc', '')
            if hasattr(Country, sort_field):
                queryset = queryset.order_by(f'-{sort_field}')
        elif sort and hasattr(Country, sort):
            queryset = queryset.order_by(sort)
        else:
            queryset = queryset.order_by('name')
        
        # Check for invalid parameters
        allowed_params = ['region', 'currency', 'sort']
        invalid_params = [key for key in request.GET.keys() if key not in allowed_params]
        if invalid_params:
            return Response(
                {"error": f"Invalid parameters: {', '.join(invalid_params)}"}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        serializer = CountrySerializer(queryset, many=True)
        return Response(serializer.data)
class CountryDetailView(APIView):
    def get_object(self, name):
        try:
            # Handle URL encoding and case sensitivity
            return Country.objects.get(name__iexact=name)
        except Country.DoesNotExist:
            raise Http404
    
    def get(self, request, name):
        try:
            country = self.get_object(name)
            serializer = CountrySerializer(country)
            return Response(serializer.data)
        except Http404:
            return Response({"error": "Country not found"}, status=status.HTTP_404_NOT_FOUND)
    
    def delete(self, request, name):
        try:
            country = self.get_object(name)
            country.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        except Http404:
            return Response({"error": "Country not found"}, status=status.HTTP_404_NOT_FOUND)


@api_view(['POST'])
def refresh_countries(request):
    """Refresh countries data from external APIs"""
    try:
        result = refresh_countries_data()
        return Response(result, status=status.HTTP_200_OK)
    except Exception as e:
        print(f"Refresh error: {str(e)}")  # Add this line
        import traceback
        traceback.print_exc()  # Add this line
        error_msg = str(e)
        if 'Countries API' in error_msg or 'Exchange Rates API' in error_msg:
            return Response(
                {
                    'error': 'External data source unavailable',
                    'details': error_msg
                },
                status=status.HTTP_503_SERVICE_UNAVAILABLE
            )
        return Response(
            {'error': 'Internal server error'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

@api_view(['GET'])
def status_view(request):
    """Get total countries and last refresh timestamp"""
    total_countries = Country.objects.count()
    
    # Get latest refresh timestamp from any country
    latest_country = Country.objects.order_by('-last_refreshed_at').first()
    last_refreshed_at = latest_country.last_refreshed_at.isoformat() if latest_country else None
    
    return Response({
        'total_countries': total_countries,
        'last_refreshed_at': last_refreshed_at
    })


@api_view(['GET'])
def countries_image(request):
    """Serve the generated summary image"""
    try:
        image_path = os.path.join(settings.CACHE_DIR, 'summary.png')
        
        if not os.path.exists(image_path):
            # Generate image if it doesn't exist
            print("Image not found, generating...")
            generate_summary_image()
        
        if os.path.exists(image_path):
            return FileResponse(open(image_path, 'rb'), content_type='image/png')
        else:
            return Response(
                {'error': 'Summary image not available'},
                status=status.HTTP_404_NOT_FOUND
            )
    except Exception as e:
        print(f"Error serving image: {e}")
        return Response(
            {'error': 'Failed to generate or serve image'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


    """Serve the generated summary image"""
    image_path = os.path.join(settings.CACHE_DIR, 'summary.png')
    
    if not os.path.exists(image_path):
        return Response(
            {'error': 'Summary image not found'},
            status=status.HTTP_404_NOT_FOUND
        )
    
    try:
        return FileResponse(open(image_path, 'rb'), content_type='image/png')
    except FileNotFoundError:
        return Response(
            {'error': 'Summary image not found'},
            status=status.HTTP_404_NOT_FOUND
        )