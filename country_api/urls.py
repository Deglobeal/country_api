from django.contrib import admin
from django.urls import path, include
from django.conf.urls import handler404, handler500, handler400
from countries.views import status_view
from django.http import JsonResponse


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


# Custom error handlers
# Custom error handlers (these will work with the middleware)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('countries/', include('countries.urls')),
    path('status/', status_view, name='status'),
] 