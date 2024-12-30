from django.contrib.admin.views.decorators import staff_member_required
from django.shortcuts import render
from django.http import HttpResponse
from django.http import JsonResponse
from app.tasks import run_feature_one_task
from app.models import Book
from services.utils import chunk_list
from services.amazon.client_amazon import Amazon, create_txt


@staff_member_required
def services_page(request):
    return render(request, "admin/services_page.html")


@staff_member_required
def run_feature_one(request):
    if request.method == "POST":
        # Enqueue the Celery task
        run_feature_one_task.delay()
        # Respond immediately
        return JsonResponse({"message": "Feature One has been enqueued successfully!"})
