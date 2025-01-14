from celery import shared_task
from services.gw_books_london.gwbook_store_client import (
    GWBookStoreClient,
)
from app.models import Book
from services.utils import chunk_list, send_mail
from services.amazon.client_amazon import Amazon
from services.black_list.main_class import BlackList


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
    return "Feature executed successfully!"


@shared_task
def black_list_restirected_books(user_email):
    common_items = BlackList().run_app()
    with open(
        "services/black_list/restirected_books/output_inventory_asins.txt", "w"
    ) as file:
        for i in common_items:
            file.write(str(i) + "\n")

    send_mail(
        subject="Black List ASINs",
        attachments=[
            "services/black_list/restirected_books/output_inventory_asins.txt"
        ],
        recipient_emails=[user_email],
    )

    print("Email sent!")
    return "Feature executed successfully!"


@shared_task
def gw_book_store_compare_prices(user_email, page: int = None):
    print("Task başladı")
    GWBookStoreClient().run_app(page)
    print("Task bitti")
    send_mail(
        subject="GW Books London",
        attachments=[
            "services/gw_books_london/gwbook_store_client.py/sell_CA.txt",
            "services/gw_books_london/gwbook_store_client.py/sell_US.txt",
        ],
        recipient_emails=[user_email],
    )

    print("Email sent!")
    return "Feature executed successfully!"
