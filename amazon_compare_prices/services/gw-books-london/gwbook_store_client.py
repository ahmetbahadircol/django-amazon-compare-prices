# from bs4 import BeautifulSoup
# import requests

# from amazon_compare_prices.app.enums import BookType


# class GWBookStoreClient:
#     MAIN_URL = "https://gwbookstore-london.myshopify.com"

#     def _request(self, url, hearder=None) -> BeautifulSoup:
#         header = hearder or {
#             "User-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36",
#             "x-user-agent": "grpc-web-javascript/0.1",
#             "sec-ch-ua-full-version-list": '"Google Chrome";v="131.0.6778.110", "Chromium";v="131.0.6778.110", "Not_A Brand";v="24.0.0.0"',
#         }
#         response = requests.get(url, headers=header)
#         return BeautifulSoup(response.text, "html.parser")

#     def search_google(self, query: str, pgn=0) -> str:
#         url = f"https://www.google.com/search?q={query.replace(' ', '+')}&start={str(pgn)}"
#         headers = {"User-Agent": "Mozilla/5.0"}
#         response = requests.get(url, headers=headers, timeout=10)
#         soup = BeautifulSoup(response.text, "html.parser")

#         for result in soup.find_all("a"):
#             link = result.get("href")
#             if link and "/url?q=" in link:
#                 temp = link.split("/url?q=")[1].split("&")[0]
#                 if "amazon" in temp:
#                     if asin := temp.split("/dp/")[-1]:
#                         return asin.split("&")[0]
#         if pgn == 30:
#             return
#         self.search_google(query=query, pgn=pgn + 10)

# def compare_gbooks_us_and_ca(self, gbooks_infos: dict) -> None:
#     amazon_ca_infos, amazon_us_infos = get_us_and_ca_infos(gbooks_infos.keys())
#     for asin, gbooks_price_title in gbooks_infos.items():
#         gbooks_title = gbooks_price_title[0]
#         gbooks_price = gbooks_price_title[1]
#         gbooks_book_type = gbooks_price_title[2]
#         info_us = amazon_us_infos.get(asin)
#         info_ca = amazon_ca_infos.get(asin)
#         if not info_us or not info_ca:
#             continue

#         lowest_price_ca = info_ca["list_price"]
#         rank_ca = info_ca["rank"]
#         lowest_price_us = round(
#             info_us["list_price"] * USD_CA_RATE, 2
#         )  # CONVERT TO CAD
#         rank_us = info_us["rank"]
#         amazon_book_type = get_book_type_from_asin(asin)

#         if gbooks_book_type != amazon_book_type:
#             continue

#         # Sell at Canada
#         if lowest_price_ca > lowest_price_us:
#             if all(
#                 [
#                     (gbooks_price + GBOOKS_STORE_PROFIT_SHARE) < lowest_price_ca,
#                     rank_ca < MAX_RANK_CA,
#                 ]
#             ):
#                 print(f"ADDED {asin} in CA file")
#                 with open(f"gbook_store/sell_CA.txt", "a") as file_ca:
#                     file_ca.write(
#                         f"{gbooks_title}\t{gbooks_price}\t{rank_ca}\t{lowest_price_ca}\n"
#                     )
#         else:  # Sell at US
#             if all(
#                 [
#                     (gbooks_price + GBOOKS_STORE_PROFIT_SHARE) < lowest_price_us,
#                     rank_us < MAX_RANK_US,
#                 ]
#             ):
#                 print(f"ADDED {asin} in US file")
#                 with open(f"gbook_store/sell_US.txt", "a") as file_us:
#                     file_us.write(
#                         f"{gbooks_title}\t{gbooks_price}\t{rank_us}\t{lowest_price_us}\n"
#                     )

#     def search_pages(self, page: int):
#         gw_books_info = dict()
#         url = f"{GWBookStoreClient.MAIN_URL}/collections/all-items?page={page}"
#         soup = self._request(url=url)

#         # Find the book titles (based on inspection of the page structure)
#         books = soup.find_all(
#             "li",
#             class_="grid__item grid__item--collection-template small--one-half medium-up--one-fifth",
#         )  # Adjust the class based on the webpage structure

#         for book in books:

#             title = book.find(
#                 "div", class_="h4 grid-view-item__title product-card__title"
#             ).text.strip()
#             price = float(
#                 book.find("span", class_="price-item price-item--regular")
#                 .text.strip()
#                 .split("$")[-1]
#             )
#             det_link = GWBookStoreClient.MAIN_URL + book.find(
#                 "a",
#                 class_="grid-view-item__link grid-view-item__image-container full-width-link",
#             ).get("href")
#             soup_detail = self._request(det_link)
#             book_type = (
#                 soup_detail.find("div", class_="product-single__description rte")
#                 .find("p")
#                 .text
#             )
#             if book_type:
#                 if "Paperback" in book_type:
#                     book_type = BookType.PAPER.value
#                 elif "Hardcover" in book_type:
#                     book_type = BookType.HARD.value
#                 else:
#                     continue
#             asin = search_google(title)
#             if asin:
#                 print(asin, title, book_type, price)
#                 gw_books_info[asin] = [title, price, book_type]
#                 db.insert(asin)

#         for chunk in chunk_dict(gw_books_info):
#             compare_gbooks_us_and_ca(chunk)

#         return flag

#     def run_app(self):
#         for i in range(32)
#         self.search_pages(i)
