from django.contrib.admin.views.decorators import staff_member_required
from django.shortcuts import render
from django.http import HttpResponse
from django.http import JsonResponse
from app.tasks import amazon_compare_prices
from app.models import Book
from services.utils import chunk_list
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
        return JsonResponse({"message": "Feature One has been enqueued successfully!"})
