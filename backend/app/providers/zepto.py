import asyncio
from playwright.async_api import async_playwright
from app.providers.base import BaseProvider, PriceResult

CDN_BASE = "https://cdn.zeptonow.com/production/"

class ZeptoProvider(BaseProvider):

    async def search(self, query: str, pincode: str) -> list[PriceResult]:
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            context = await browser.new_context(
                user_agent="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
                           "AppleWebKit/537.36 (KHTML, like Gecko) "
                           "Chrome/120.0.0.0 Safari/537.36"
            )
            page = await context.new_page()
            captured = []

            async def handle_response(response):
                if (
                    "bff-gateway.zepto.com/user-search-service/api/v3/search" in response.url
                    and response.status == 200
                ):
                    try:
                        data = await response.json()
                        captured.append(data)
                    except Exception:
                        pass

            page.on("response", handle_response)

            await page.goto("https://www.zeptonow.com", wait_until="domcontentloaded")
            await asyncio.sleep(2)

            await page.goto(
                f"https://www.zeptonow.com/search?query={query}",
                wait_until="domcontentloaded"
            )
            await asyncio.sleep(4)  # Zepto is slower to load than Blinkit

            await browser.close()

        if not captured:
            return []

        return self._parse(captured[0])

    def _parse(self, data: dict) -> list[PriceResult]:
        results = []

        for widget in data.get("layout", []):
            # only process product grids, skip title/banner widgets
            if widget.get("widgetId") != "PRODUCT_GRID":
                continue

            items = (
                widget
                .get("data", {})
                .get("resolver", {})
                .get("data", {})
                .get("items", [])
            )

            for item in items:
                pr = item.get("productResponse", {})
                if not pr:
                    continue

                product = pr.get("product", {})
                variant = pr.get("productVariant", {})

                # prices are in paise — divide by 100
                price = pr.get("discountedSellingPrice", 0) / 100
                mrp = pr.get("mrp", 0) / 100

                # build image URL
                images = variant.get("images", [])
                image_url = ""
                if images:
                    image_url = CDN_BASE + images[0].get("path", "")

                results.append(PriceResult(
                    platform="zepto",
                    product_name=product.get("name", ""),
                    price=price,
                    mrp=mrp,
                    unit=variant.get("formattedPacksize", ""),
                    in_stock=not pr.get("outOfStock", False),
                    image_url=image_url,
                    platform_product_id=variant.get("id", ""),
                ))

        return results