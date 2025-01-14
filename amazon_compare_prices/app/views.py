from django.contrib.admin.views.decorators import staff_member_required
from django.shortcuts import render
from django.http import JsonResponse
from services.utils import convert_bytes_to_dict
from app.tasks import (
    amazon_compare_prices,
    black_list_restirected_books,
    gw_book_store_compare_prices,
)
from services.amazon.client_amazon import Amazon, create_txt


@staff_member_required
def services_page(request):
    return render(request, "admin/services_page.html")


@staff_member_required
def run_amazon_compare_prices_task(request):
    if request.method == "POST":
        create_txt()
        user_email = request.user.email
        amazon_compare_prices.delay(user_email)
        return JsonResponse(
            {"message": "Amazon Compare Prices App has been enqueued successfully!"}
        )


@staff_member_required
def run_black_list_restirected_books_task(request):
    if request.method == "POST":
        user_email = request.user.email
        black_list_restirected_books.delay(user_email)
        return JsonResponse(
            {
                "message": "Black List Restirected Books App has been enqueued successfully!"
            }
        )


@staff_member_required
def run_gw_book_store_compare_prices_task(request):
    if request.method == "POST":
        user_email = request.user.email
        page = int(convert_bytes_to_dict(request.body).get("gwBooksPage"))
        print(page)
        # gw_book_store_compare_prices.delay(user_email, int(page))
        gw_book_store_compare_prices(user_email, int(page))
        return JsonResponse(
            {"message": "GW Book Store London App has been enqueued successfully!"}
        )
