from django.contrib.admin.views.decorators import staff_member_required
from django.shortcuts import render, redirect
from django.http import HttpResponse

from app.models import Book
from services.utils import chunk_list
from services.amazon.client_amazon import Amazon, create_txt


def custom_admin_page(request):
    if request.method == "POST":
        all_books = Book.objects.values_list("asin", flat=True)
        if all_books:
            create_txt()
            for chunk in chunk_list(all_books):
                Amazon(chunk).run_app()
            return HttpResponse("Button clicked and function executed!")

    return render(request, "admin/custom_page.html")
