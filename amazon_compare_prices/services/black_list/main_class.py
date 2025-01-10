from services.utils import send_mail
from services.amazon.client_amazon import Amazon
from sp_api.base import SellingApiException
from sp_api.base import Marketplaces


class BlackList:

    def get_inventory_marketplace(
        self, marketplace_id: str, inventory_items: list = []
    ):
        data = {
            "details": False,
            "granularityId": marketplace_id,
            "nextToken": None,
        }
        co = 0
        try:
            while True:
                res = Amazon.get_inventory(**data)
                temp = res.payload.get("inventorySummaries", [])

                for book in temp:
                    if book.get("totalQuantity") >= 1:
                        inventory_items.append(book["asin"])

                if pgn := getattr(res, "pagination"):
                    data["nextToken"] = pgn.get("nextToken")
                else:
                    data["nextToken"] = None

                if not data["nextToken"]:
                    break
                co += 1
                print(f"---Try: {co}---")

        except SellingApiException as ex:
            print(f"Error: {ex}")

        print(len(inventory_items))
        return inventory_items

    def read_black_list(self):
        import re

        file_path = "services/black_list/restirected_books/input_black_asin_list.txt"

        black_list, res = [], []

        with open(file_path, "r", encoding="utf-8") as file:
            black_list = file.readlines()

            for line in black_list:
                cleaned_content = (
                    re.sub(r"[\u0000-\u001F\u2060]", "", line).replace(" ", "").upper()
                )
                res.append(cleaned_content)

        return res

    def run_app(self):
        black_list = self.read_black_list()

        result_list = list()
        result_list = self.get_inventory_marketplace(
            Marketplaces.CA.marketplace_id, result_list
        )
        result_list = self.get_inventory_marketplace(
            Marketplaces.US.marketplace_id, result_list
        ).extend(result_list)

        set_black = set(black_list)
        set_inventory = set(result_list)
        return set_black.intersection(set_inventory)

