import asyncio
from app.providers.blinkit import BlinkitProvider
from app.providers.zepto import ZeptoProvider
from app.providers.instamart import InstamartProvider
from app.providers.base import PriceResult


class AggregatorService:

    def __init__(self):
        self.providers = [
            BlinkitProvider(),
            ZeptoProvider(),
            InstamartProvider(),
        ]

    async def search(self, query: str, pincode: str) -> list[PriceResult]:
        tasks = [
            provider.search(query, pincode)
            for provider in self.providers
        ]

        results = await asyncio.gather(*tasks, return_exceptions=True)

        final = []
        for res in results:
            if isinstance(res, Exception):
                print(f"Provider error: {res}")
                continue
            final.extend(res)

        return final