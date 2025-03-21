from django.urls import path
from .views import (
    run_amazon_compare_prices_task,
    run_gw_book_store_compare_prices_task,
    run_write_asin_task,
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
    path(
        "gw-book-store/",
        run_gw_book_store_compare_prices_task,
        name="gw_book_store_compare_prices_feature",
    ),
    path(
        "write-asin/",
        run_write_asin_task,
        name="gw_book_store_compare_prices_feature",
    ),
]
