from django.urls import path
from . import views

urlpatterns = [
    path('refresh/', views.refresh_countries, name='refresh_countries'),
    path('image/', views.serve_summary_image, name='serve_summary_image'),
    path('status/', views.get_status, name='get_status'),
    path('', views.list_countries, name='list_countries'),
    # Single endpoint that handles both GET and DELETE for a country
    path('<str:name>/', views.country_detail, name='country_detail'),
]