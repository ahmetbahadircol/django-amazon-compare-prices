from celery import shared_task
from app.models import Book
from services.utils import chunk_list, send_mail
from services.amazon.client_amazon import Amazon, create_txt


@shared_task
def amazon_compare_prices(user_email):
    all_books = Book.objects.values_list("asin", flat=True)
    if all_books:
        for chunk in chunk_list(all_books):
            Amazon(chunk).run_app()
        send_mail(
            subject="Amazon US and Canada Buy & Sell Lists",
            attachments=[
                "services/amazon/email_attachments/buy_CA_sell_US.txt",
                "services/amazon/email_attachments/buy_US_sell_CA.txt",
            ],
            recipient_emails=[user_email],
        )
    return "Feature One executed successfully!"
