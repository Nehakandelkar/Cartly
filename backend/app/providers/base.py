from dataclasses import dataclass
from abc import ABC, abstractmethod

@dataclass
class PriceResult:
    platform: str          # "blinkit", "zepto", etc.
    product_name: str      # "Amul Taaza Milk"
    price: float           # actual selling price
    mrp: float             # original price
    unit: str              # "500 ml", "1 kg"
    in_stock: bool
    image_url: str
    platform_product_id: str   # blinkit's internal ID for this product


class BaseProvider(ABC):

    @abstractmethod
    async def search(self, query: str, pincode: str) -> list[PriceResult]:
        pass