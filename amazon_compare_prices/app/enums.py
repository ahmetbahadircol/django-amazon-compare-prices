from enum import Enum


class BookType(Enum):
    PAPER = "Paperback", "Paperback"
    HARD = "Hardcover", "Hardcover"

    @classmethod
    def choices(cls):
        return [(gen.value[0], gen.value[1]) for gen in cls]


class Currencies(Enum):
    CAD = "CAD", "Canada Dollars"
    USD = "USD", "United States Dollars"

    @classmethod
    def choices(cls):
        return [(gen.value[0], gen.value[1]) for gen in cls]
