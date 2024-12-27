from sp_api.base import Marketplaces
from sp_api.base.exceptions import SellingApiBadRequestException
from sp_api.api import Products
from typing import Optional, Tuple

import time
from datetime import datetime
from dotenv import load_dotenv
import os
from pathlib import Path

from .decorators import reauth, retry_on_throttling

PATH = "/email_attachments"

load_dotenv()

AMAZON_SHARE = int(os.getenv("AMAZON_SHARE"))
MAX_RANK_CA = int(os.getenv("MAX_RANK_CA"))
MAX_RANK_US = int(os.getenv("MAX_RANK_US"))
USD_CA_RATE = float(os.getenv("USD_CA_RATE"))
CATROSE_PROFIT_RATE = float(os.getenv("CATROSE_PROFIT_RATE")) + float(1)


def create_txt():
    file_path_ca = os.path.join(
        "services/amazon/email_attachments", "buy_US_sell_CA.txt"
    )
    file_path_us = os.path.join(
        "services/amazon/email_attachments", "buy_CA_sell_US.txt"
    )

    with open(file_path_ca, "w") as file_ca:
        file_ca.write(
            f"ASIN  |  US PRICE(CAD)  |  RANK US  |  US PRICE\n-----------------------------------------\n"
        )
    with open(file_path_us, "w") as file_us:
        file_us.write(
            f"ASIN  |  US PRICE(CAD)  |  RANK CA  |  CA PRICE\n-----------------------------------------\n"
        )


class Amazon:
    def __init__(self, asin_list: list):
        self.books = asin_list

    def _format_time(self, t):
        return (
            datetime.fromtimestamp(t).strftime("%H:%M:%S")
            + f":{int((t % 1) * 1000):03d}"
        )

    @retry_on_throttling(delay=2, max_retries=7)
    @reauth
    def get_offers_batch(self, market_placeid: str) -> list[dict]:
        """
        returns list of offers for each book

        TODO: Make this fucntion for flexibile item condition: [new, used, ...]
        """
        requests = []
        for asin in self.books:
            request = {
                "uri": f"/products/pricing/v0/items/{asin}/offers",
                "method": "GET",
                "ItemCondition": "New",
                "MarketplaceId": market_placeid,
            }
            requests.append(request)
        try:
            res = Products().get_item_offers_batch(requests).payload["responses"]
            time.sleep(2.01)
            return res
        except SellingApiBadRequestException as e:
            print(e)

    def _find_lowest_price(
        self, offers: list, cond: list[str] = ["new"]
    ) -> Tuple[Optional[float], Optional[float]]:
        if not offers:
            return None, None
        temp = list()
        for off in offers:
            try:
                if off["SubCondition"] in cond:
                    list_p = off["ListingPrice"]["Amount"]
                    shipping_p = off["Shipping"]["Amount"]
                    temp.append(
                        (
                            list_p,
                            shipping_p,
                        )
                    )
                else:
                    continue
            except KeyError as e:
                print("----- KEY ERROR -----")
                print(e)
                continue

        return min(temp, key=sum)

    def parse_fetched_book_data(self, marketplace: str):
        offers = self.get_offers_batch(
            market_placeid=getattr(Marketplaces, marketplace).marketplace_id
        )
        result = dict()
        for offer in offers:
            try:
                list_price, shipping_price = self._find_lowest_price(
                    offer["body"]["payload"]["Offers"]
                )
                if list_price is not None or shipping_price is not None:
                    result[offer["body"]["payload"]["ASIN"]] = {
                        "rank": offer["body"]["payload"]["Summary"]["SalesRankings"][0][
                            "Rank"
                        ],
                        "list_price": list_price,
                        "shipping_price": shipping_price,
                    }
            except KeyError as e:
                print("----- KEY ERROR -----")
                print(e)
                continue
        return result

    def compare(self):
        book_info_ca, book_info_us = self.parse_fetched_book_data(
            marketplace="CA"
        ), self.parse_fetched_book_data(marketplace="US")
        for asin, info_ca in book_info_ca.items():
            info_us = book_info_us.get(asin)
            if not info_us:
                continue

            lowest_price_ca = info_ca["list_price"]
            shipping_price_ca = info_ca["shipping_price"]
            rank_ca = info_ca["rank"]
            lowest_price_us = round(info_us["list_price"] * USD_CA_RATE, 2)
            shipping_price_us = round(
                info_us["shipping_price"] * USD_CA_RATE, 2
            )  # CONVERT TO CAD
            rank_us = info_us["rank"]

            # Compare Canada and US

            # Buy from Canada and Sell in US
            if all(
                [
                    rank_us < MAX_RANK_US,
                    (lowest_price_ca + shipping_price_ca) * CATROSE_PROFIT_RATE
                    + AMAZON_SHARE
                    < lowest_price_us,
                ]
            ):
                print(f"ADDED {asin} in US file")
                with open(
                    f"services/amazon/email_attachments/buy_CA_sell_US.txt", "a"
                ) as file_us:
                    file_us.write(
                        f"{asin}\t{lowest_price_us}\t{rank_us}\t{lowest_price_ca}\n"
                    )

            # Buy from US and Sell in Canada
            if all(
                [
                    rank_ca < MAX_RANK_CA,
                    (lowest_price_us + shipping_price_us) * CATROSE_PROFIT_RATE
                    + AMAZON_SHARE
                    < lowest_price_ca,
                ]
            ):
                print(f"ADDED {asin} in CA file")
                with open(
                    f"services/amazon/email_attachments/buy_US_sell_CA.txt", "a"
                ) as file_ca:
                    file_ca.write(
                        f"{asin}\t{lowest_price_us}\t{rank_ca}\t{lowest_price_ca}\n"
                    )

        print("Data written to output.txt")

    def run_app(self):
        self.compare()
