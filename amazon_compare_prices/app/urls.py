from django.urls import path
from .views import (
    run_amazon_compare_prices_task,
    services_page,
    run_black_list_restirected_books_task,
)

urlpatterns = [
    path("", services_page, name="services_page"),
    path(
        "amazon/",
        run_amazon_compare_prices_task,
        name="amazon_compare_prices_feature",
    ),
    path(
        "black-list/",
        run_black_list_restirected_books_task,
        name="black_list_restirected_books_feature",
    ),
]
