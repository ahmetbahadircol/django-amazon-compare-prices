from django.urls import path
from .views import run_amazon_compare_prices_task, services_page

urlpatterns = [
    path("", services_page, name="services_page"),
    path("feature-one/", run_amazon_compare_prices_task, name="amazon_compare_prices_feature"),
]
