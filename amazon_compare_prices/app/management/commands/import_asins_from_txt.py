from django.core.management.base import BaseCommand

from app.models import Book

import os


class Command(BaseCommand):
    help = "Import books from a TXT file"

    def handle(self, *args, **kwargs):
        current_directory = os.path.dirname(os.path.realpath(__file__))
        file_path = os.path.join(
            current_directory, "asin.txt"
        )  # REQUIRES ASIN LIST IN TXT FILE IN THE SAME PATH
        with open(file_path, "r") as file:
            line = file.readline().strip()
            item_list = [item.strip().strip("'") for item in line.split(",")]
            for row in item_list:
                Book.objects.create(asin=row)
        self.stdout.write(self.style.SUCCESS("Successfully imported books from TXT"))
