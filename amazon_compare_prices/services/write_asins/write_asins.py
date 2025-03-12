from sp_api.api import Orders
from sp_api.base import Marketplaces
from datetime import datetime, timedelta

import time
from dotenv import load_dotenv
import os

from app.models import Book
from services.amazon.decorators import reauth, retry_on_throttling

load_dotenv()

PULL_DAYS_ASIN = int(os.getenv("PULL_DAYS_ASIN"))

created_after = (
    (datetime.now() - timedelta(days=PULL_DAYS_ASIN))
    .replace(hour=0, minute=0, second=0, microsecond=0)
    .isoformat()
)


class WriteAsin:

    @retry_on_throttling(delay=1, max_retries=10)
    @reauth
    def get_orders(
        self, market_place, created_after, orders_list=None, next_token=None
    ):
        if orders_list is None:
            orders_list = []
        if next_token:
            response = Orders(market_place).get_orders(NextToken=next_token)
        else:
            response = Orders(market_place).get_orders(CreatedAfter=created_after)

        orders_list.extend(response.payload.get("Orders", []))

        next_token = response.payload.get("NextToken")

        if next_token:
            return self.get_orders(market_place, created_after, orders_list, next_token)
        else:
            return orders_list

    @retry_on_throttling(delay=1, max_retries=5)
    @reauth
    def get_items(self, order_id):
        return Orders().get_order_items(order_id=order_id).payload.get("OrderItems", [])

    def run_app(self) -> None:
        orders = self.get_orders(Marketplaces.CA, created_after) + self.get_orders(
            Marketplaces.US, created_after
        )
        order, item = None, None
        try:
            for idx, order in enumerate(orders):
                order_id = order.get("AmazonOrderId")
                sales_channel = order.get("SalesChannel")
                if sales_channel[-3:] == "com":
                    market_place = "US"
                else:
                    market_place = "CA"
                items = self.get_items(order_id)
                for item in items:
                    asin = item.get("ASIN")
                    Book.objects.create(asin=asin, title=item["Title"])
                    print(asin + "---" + sales_channel)
                time.sleep(1)
        except KeyError as e:
            print("----- KEY ERROR ------")
            print(e)
            print(order)
            print(item)
