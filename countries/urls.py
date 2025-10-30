from django.urls import path
from . import views




urlpatterns = [
    path('refresh', views.refresh_countries, name='refresh-countries'),
    path('', views.CountryListView.as_view(), name='country-list'),
    path('image', views.countries_image, name='countries-image'),
    path('status', views.status_view, name='status'),
    path('<str:name>', views.CountryDetailView.as_view(), name='country-detail'),
]