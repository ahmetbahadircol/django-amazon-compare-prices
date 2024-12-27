from django.db import models

from .enums import BookType, Currencies


# Create your models here.
class Book(models.Model):
    asin = models.CharField(db_index=False, max_length=20)
    title = models.CharField(null=True, max_length=200)
    book_type = models.CharField(choices=BookType.choices(), max_length=10)
    price = models.FloatField(null=True)
    shipping_price = models.FloatField(null=True)
    currency = models.CharField(choices=Currencies.choices(), max_length=3)

    def __str__(self):
        return f"{self.asin} - {self.title}"
