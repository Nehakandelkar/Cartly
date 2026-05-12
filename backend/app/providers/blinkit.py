import asyncio
import json
from playwright.async_api import async_playwright
from app.providers.base import BaseProvider, PriceResult


class BlinkitProvider(BaseProvider):

    BASE_URL = "https://blinkit.com"
    SEARCH_URL = "https://blinkit.com/v1/layout/search"

    async def search(self, query: str, pincode: str) -> list[PriceResult]:
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            context = await browser.new_context(
                user_agent="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
                           "AppleWebKit/537.36 (KHTML, like Gecko) "
                           "Chrome/120.0.0.0 Safari/537.36"
            )
            page = await context.new_page()

            captured_responses = []

            # Step 1: intercept the search API response
            async def handle_response(response):
                if "v1/layout/search" in response.url and response.status == 200:
                    try:
                        data = await response.json()
                        captured_responses.append(data)
                    except Exception:
                        pass

            page.on("response", handle_response)

            # Step 2: load homepage first (sets cookies, session)
            await page.goto(self.BASE_URL, wait_until="domcontentloaded")
            await asyncio.sleep(2)

            # Step 3: trigger the search (this fires the XHR we're intercepting)
            await page.goto(
                f"{self.BASE_URL}/s/?q={query}",
                wait_until="domcontentloaded"
            )
            await asyncio.sleep(3)  # wait for XHR to complete

            await browser.close()

        if not captured_responses:
            return []

        return self._parse(captured_responses[0])

    def _parse(self, data: dict) -> list[PriceResult]:
        results = []

        snippets = data.get("response", {}).get("snippets", [])

        for snippet in snippets:
            # only process product cards, skip headers/banners
            if snippet.get("widget_type") != "product_card_snippet_type_2":
                continue

            snippet_data = snippet.get("data", {})

            # the cleanest source of truth is the cart_item inside atc_action
            cart_item = (
                snippet_data
                .get("atc_action", {})
                .get("add_to_cart", {})
                .get("cart_item", {})
            )

            if not cart_item:
                continue

            results.append(PriceResult(
                platform="blinkit",
                product_name=cart_item.get("product_name", ""),
                price=float(cart_item.get("price", 0)),
                mrp=float(cart_item.get("mrp", 0)),
                unit=cart_item.get("unit", ""),
                in_stock=not snippet_data.get("is_sold_out", False),
                image_url=cart_item.get("image_url", ""),
                platform_product_id=str(cart_item.get("product_id", "")),
            ))

        return results