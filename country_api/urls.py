from django.contrib import admin
from django.urls import path, include
from django.http import JsonResponse
from django.views.generic import RedirectView

# Simple API root view
def api_root(request):
    return JsonResponse({
        "message": "Country Currency & Exchange API",
        "version": "1.0",
        "endpoints": {
            "refresh_countries": "POST /countries/refresh/",
            "list_countries": "GET /countries/",
            "get_country": "GET /countries/{name}/",
            "delete_country": "DELETE /countries/{name}/",
            "status": "GET /countries/status/",
            "summary_image": "GET /countries/image/",
            "admin": "/admin/"
        },
        "documentation": "Check README for usage instructions"
    })

urlpatterns = [
    # Root endpoint
    path('', api_root, name='api-root'),
    
    # Admin
    path('admin/', admin.site.urls),
    path('', include('countries.urls')),
    
]