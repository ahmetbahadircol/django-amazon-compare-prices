from __future__ import absolute_import, unicode_literals
import os
from celery import Celery

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'amazon_compare_prices.settings')

app = Celery(
    'amazon_compare_prices',
    broker='redis://redis:6379/0',  # Broker URL
    backend='redis://redis:6379/1'  # Result backend URL
)

app.config_from_object('django.conf:settings', namespace='CELERY')

app.autodiscover_tasks()
