from django.contrib.admin.views.decorators import staff_member_required
from django.shortcuts import render
from django.http import JsonResponse
from app.tasks import amazon_compare_prices, black_list_restirected_books
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
        black_list_restirected_books.delay()
        return JsonResponse(
            {
                "message": "Black List Restirected Books App has been enqueued successfully!"
            }
        )
