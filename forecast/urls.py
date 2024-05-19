from django.urls import path
from .views import forecast_view, result_view, main_view

urlpatterns = [
    path('make_forecast/', forecast_view, name='forecast_view'),
    path('result/<int:result_id>/', result_view, name='result_view'),
    path('main/', main_view, name='main_view'),
]