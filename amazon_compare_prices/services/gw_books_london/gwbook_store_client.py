from bs4 import BeautifulSoup
import requests

from app.models import Book
from app.enums import BookType
from services.amazon.client_amazon import Amazon
from services.amazon.functions import get_book_type_from_asin

import os
from dotenv import load_dotenv
import requests
from bs4 import BeautifulSoup

from services.utils import chunk_dict

# from compare_prices.compare_prices import get_us_and_ca_infos
# from helpers.enums import BookType
# from helpers.send_email import send_mail
# from helpers.db import MySQLHandler

load_dotenv()

AMAZON_SHARE = int(os.getenv("AMAZON_SHARE"))
MAX_RANK_CA = int(os.getenv("MAX_RANK_CA"))
MAX_RANK_US = int(os.getenv("MAX_RANK_US"))
USD_CA_RATE = float(os.getenv("USD_CA_RATE"))
CATROSE_PROFIT_RATE = float(os.getenv("CATROSE_PROFIT_RATE")) + float(1)
GBOOKS_STORE_PROFIT_SHARE = int(os.getenv("GBOOKS_STORE_PROFIT_SHARE"))


class GWBookStoreClient:
    MAIN_URL = "https://gwbookstore-london.myshopify.com"

    def _request(self, url, headers=None) -> BeautifulSoup:
        # header = header or {
        #     "User-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36",
        #     "x-user-agent": "grpc-web-javascript/0.1",
        #     "sec-ch-ua-full-version-list": '"Google Chrome";v="131.0.6778.110", "Chromium";v="131.0.6778.110", "Not_A Brand";v="24.0.0.0"',
        # }
        response = requests.get(url, headers=headers)
        return BeautifulSoup(response.text, "html.parser")

    def search_google(self, query: str, pgn=0) -> str:
        url = f"https://www.google.com/search?q={query.replace(' ', '+')}&start={str(pgn)}"
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        }
        soup = self._request(url, headers=headers)
        from googlesearch import search

        for uuu in search(query=query, num=5):
            print(uuu)

        import ipdb

        ipdb.set_trace()
        print("breakpoint")
        for result in soup.find_all("a"):
            link = result.get("href")
            if link and "/url?q=" in link:
                temp = link.split("/url?q=")[1].split("&")[0]
                if "amazon" in temp:
                    if asin := temp.split("/dp/")[-1]:
                        return asin.split("&")[0] 
        if pgn == 30:
            return
        self.search_google(query=query, pgn=pgn + 10)

    def compare_gbooks_us_and_ca(self, gbooks_infos: dict) -> None:
        amazon_client = Amazon(gbooks_infos.keys())
        amazon_ca_infos, amazon_us_infos = amazon_client.parse_fetched_book_data(
            "CA"
        ), amazon_client.parse_fetched_book_data("US")
        for asin, gbooks_price_title in gbooks_infos.items():
            gbooks_title = gbooks_price_title[0]
            gbooks_price = gbooks_price_title[1]
            gbooks_book_type = gbooks_price_title[2]
            info_us = amazon_us_infos.get(asin)
            info_ca = amazon_ca_infos.get(asin)
            if not info_us or not info_ca:
                continue

            lowest_price_ca = info_ca["list_price"]
            rank_ca = info_ca["rank"]
            lowest_price_us = round(
                info_us["list_price"] * USD_CA_RATE, 2
            )  # CONVERT TO CAD
            rank_us = info_us["rank"]
            amazon_book_type = get_book_type_from_asin(asin)

            if gbooks_book_type != amazon_book_type:
                continue

            # Sell at Canada
            if lowest_price_ca > lowest_price_us:
                if all(
                    [
                        (gbooks_price + GBOOKS_STORE_PROFIT_SHARE) < lowest_price_ca,
                        rank_ca < MAX_RANK_CA,
                    ]
                ):
                    print(f"ADDED {asin} in CA file")
                    with open(
                        f"services/gw_books_london/gwbook_store_client.py/sell_CA.txt",
                        "a",
                    ) as file_ca:
                        file_ca.write(
                            f"{gbooks_title}\t{gbooks_price}\t{rank_ca}\t{lowest_price_ca}\n"
                        )
            else:  # Sell at US
                if all(
                    [
                        (gbooks_price + GBOOKS_STORE_PROFIT_SHARE) < lowest_price_us,
                        rank_us < MAX_RANK_US,
                    ]
                ):
                    print(f"ADDED {asin} in US file")
                    with open(
                        f"services/gw_books_london/gwbook_store_client.py/sell_US.txt",
                        "a",
                    ) as file_us:
                        file_us.write(
                            f"{gbooks_title}\t{gbooks_price}\t{rank_us}\t{lowest_price_us}\n"
                        )

    def search_pages(self, page: int):
        print("search pages " + str(page))
        gw_books_info = dict()
        url = f"{GWBookStoreClient.MAIN_URL}/collections/all-items?page={page}"
        soup = self._request(url=url)

        # Find the book titles (based on inspection of the page structure)
        books = soup.find_all(
            "li",
            class_="grid__item grid__item--collection-template small--one-half medium-up--one-fifth",
        )  # Adjust the class based on the webpage structure

        for book in books:

            title = book.find(
                "div", class_="h4 grid-view-item__title product-card__title"
            ).text.strip()
            price = float(
                book.find("span", class_="price-item price-item--regular")
                .text.strip()
                .split("$")[-1]
            )
            det_link = GWBookStoreClient.MAIN_URL + book.find(
                "a",
                class_="grid-view-item__link grid-view-item__image-container full-width-link",
            ).get("href")
            soup_detail = self._request(det_link)
            book_type = (
                soup_detail.find("div", class_="product-single__description rte")
                .find("p")
                .text
            )
            if book_type:
                if "Paperback" in book_type:
                    book_type = BookType.PAPER.value
                elif "Hardcover" in book_type:
                    book_type = BookType.HARD.value
                else:
                    continue
            asin = self.search_google(title)
            if asin:
                print(asin, title, book_type, price)
                gw_books_info[asin] = [title, price, book_type]
                Book.objects.create(asin=asin, price=price, book_type=book_type)

        for chunk in chunk_dict(gw_books_info):
            self.compare_gbooks_us_and_ca(chunk)

    def run_app(self, page: int = 30):
        print("Ananın amı!!!!!")
        for i in range(1, page + 1):
            self.search_pages(i)
