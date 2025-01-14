from services.amazon.decorators import reauth, retry_on_throttling
from sp_api.api import Catalog


@retry_on_throttling(delay=2, max_retries=5)
@reauth
def get_book_type_from_asin(asin: str) -> str:
    """
    returns the type of a book using ASIN:
        HARD: "Hardcover"
        PAPER: "Paperback"
    """
    return Catalog().get_item(asin=asin).payload["AttributeSets"][0]["Binding"]
