from services.amazon.client_amazon import Amazon
from sp_api.base import SellingApiException
from sp_api.base import Marketplaces


def get_inventory_marketplace(marketplace_id: str, inventory_items: list = []):
    data = {
        "details": False,
        "granularityId": marketplace_id,
        "nextToken": None,
    }
    co = 0
    try:
        while True:
            res = Amazon().get_inventory(**data)
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


def read_black_list():
    import re

    file_path = "restirected_books/black_asin_list.txt"

    black_list, res = [], []

    with open(file_path, "r", encoding="utf-8") as file:
        black_list = file.readlines()

        for line in black_list:
            cleaned_content = (
                re.sub(r"[\u0000-\u001F\u2060]", "", line).replace(" ", "").upper()
            )
            res.append(cleaned_content)

    return res


def run_app():
    black_list = read_black_list()

    result_list = list()
    result_list = get_inventory_marketplace(Marketplaces.CA.marketplace_id, result_list)
    result_list = get_inventory_marketplace(Marketplaces.US.marketplace_id, result_list)

    set_black = set(black_list)
    set_inventory = set(result_list)
    common_items = set_black.intersection(set_inventory)

    if common_items:

        with open("restirected_books/inventory_asins.txt", "w") as file:
            for i in common_items:
                file.write(str(i) + "\n")

        send_mail(
            subject="Black List ASINs",
            attachments=["restirected_books/inventory_asins.txt"],
        )

        print("Email sent!")
    
    else:
        print("There is no ASINs to send!")
    
    return common_items
