from celery import shared_task
from app.models import Book
from services.utils import chunk_list
from services.amazon.client_amazon import Amazon, create_txt


@shared_task
def run_feature_one_task():
    all_books = Book.objects.values_list("asin", flat=True)
    if all_books:
        create_txt()
        for chunk in chunk_list(all_books):
            Amazon(chunk).run_app()
    return "Feature One executed successfully!"
