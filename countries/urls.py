from django.urls import path
from . import views

urlpatterns = [
    path('countries/refresh', views.refresh_countries, name='refresh-countries'),
    path('countries', views.list_countries, name='list-countries'),
    path('countries/image', views.get_country_image, name='get-country-image'),  # This MUST come before the dynamic pattern
    path('countries/<str:name>', views.country_detail, name='country-detail'),  # Combined GET and DELETE
    path('status', views.get_status, name='get-status'),
]