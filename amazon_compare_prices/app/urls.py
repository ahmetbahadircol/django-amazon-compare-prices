from django.urls import path
from .views import run_feature_one, services_page

urlpatterns = [
    path("", services_page, name="services_page"),
    path("feature-one/", run_feature_one, name="services_feature_one"),
]
