import asyncio
import json
from playwright.async_api import async_playwright
from app.providers.base import BaseProvider, PriceResult


class InstamartProvider(BaseProvider):

    SEARCH_API = "/api/instamart/search/v2"

    async def search(self, query: str, pincode: str) -> list[PriceResult]:

        results = []
        captured_data = None

        async with async_playwright() as p:

            browser = await p.chromium.launch(
                headless=False,
                slow_mo=300
            )

            context = await browser.new_context(
                user_agent=(
                    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                    "AppleWebKit/537.36 (KHTML, like Gecko) "
                    "Chrome/124.0.0.0 Safari/537.36"
                ),
                locale="en-IN",
            )

            page = await context.new_page()

            # ---------------------------------------------------
            # Intercept ONLY Instamart search API
            # ---------------------------------------------------
            async def handle_response(response):
                nonlocal captured_data

                try:

                    if (
                        self.SEARCH_API in response.url
                        and response.status == 200
                    ):

                        print("\n================ SEARCH API =================")
                        print("URL:", response.url)

                        text = await response.text()

                        print("\nRAW RESPONSE:")
                        print(text[:3000])

                        try:
                            data = json.loads(text)

                            captured_data = data

                            print("\n[Instamart] JSON captured successfully")

                        except Exception as e:
                            print(f"\n[Instamart] JSON parse failed: {e}")

                except Exception as e:
                    print(f"\n[Instamart] Response handling error: {e}")

            page.on("response", handle_response)

            # ---------------------------------------------------
            # STEP 1: Open homepage
            # ---------------------------------------------------
            print("\nOpening Instamart homepage...")

            await page.goto(
                "https://www.swiggy.com/instamart",
                wait_until="domcontentloaded"
            )

            await page.wait_for_load_state("networkidle")

            await asyncio.sleep(3)

            # ---------------------------------------------------
            # STEP 2: Set Bangalore location
            # ---------------------------------------------------
            print("\nSetting Bangalore location...")

            try:

                # Click location input
                location_input = page.locator("input").first

                await location_input.click()

                await asyncio.sleep(1)

                await location_input.fill("Bangalore")

                await asyncio.sleep(3)

                # Select first suggestion
                first_location = page.locator("text=Bangalore").first

                await first_location.click()

                print("[Instamart] Location selected")

            except Exception as e:
                print(f"[Instamart] Location selection failed: {e}")

            # ---------------------------------------------------
            # STEP 3: Wait for store/session initialization
            # ---------------------------------------------------
            print("\nWaiting for store initialization...")

            await asyncio.sleep(8)

            # ---------------------------------------------------
            # STEP 4: Search product
            # ---------------------------------------------------
            print(f"\nSearching for '{query}'...")

            try:

                search_input = page.locator("input[type='text']").last

                await search_input.click()

                await asyncio.sleep(1)

                await search_input.fill(query)

                await asyncio.sleep(2)

                await search_input.press("Enter")

            except Exception as e:
                print(f"[Instamart] Search interaction failed: {e}")

            # ---------------------------------------------------
            # STEP 5: Wait for search API
            # ---------------------------------------------------
            try:

                await page.wait_for_response(
                    lambda r: (
                        self.SEARCH_API in r.url
                        and r.status == 200
                    ),
                    timeout=15000
                )

                print("\n[Instamart] Search API detected")

            except Exception:
                print("\n[Instamart] Timed out waiting for search API")

            await asyncio.sleep(5)

            await browser.close()

        # ---------------------------------------------------
        # STEP 6: Validate capture
        # ---------------------------------------------------
        if not captured_data:

            print("\n[Instamart] No search data captured")

            return results

        # ---------------------------------------------------
        # DEBUG
        # ---------------------------------------------------
        # print(json.dumps(captured_data, indent=2)[:5000])

        # ---------------------------------------------------
        # STEP 7: Parse response
        # ---------------------------------------------------
        try:

            cards = captured_data.get("data", {}).get("cards", [])

            for card in cards:

                card_data = card.get("card", {}).get("card", {})

                items = (
                    card_data
                    .get("gridElements", {})
                    .get("infoWithStyle", {})
                    .get("items", [])
                )

                for item in items:

                    try:

                        variations = item.get("variations", [])

                        variant = next(
                            (
                                v for v in variations
                                if v.get("listingVariant")
                            ),
                            variations[0] if variations else None
                        )

                        if not variant:
                            continue

                        name = variant.get("displayName", "")

                        if not name:
                            continue

                        price_obj = variant.get("price", {})

                        price = float(
                            price_obj.get("offerPrice", {}).get("units", 0)
                        )

                        mrp = float(
                            price_obj.get("mrp", {}).get("units", price)
                        )

                        unit = variant.get("quantityDescription", "")

                        in_stock = (
                            variant
                            .get("inventory", {})
                            .get("inStock", True)
                        )

                        image_id = (
                            variant.get("imageIds") or [""]
                        )[0]

                        image_url = (
                            f"https://instaimg.swiggy.com/swiggy_assets/{image_id}"
                            if image_id else ""
                        )

                        product_id = variant.get("skuId", "")

                        results.append(
                            PriceResult(
                                platform="instamart",
                                product_name=name,
                                price=price,
                                mrp=mrp,
                                unit=unit,
                                in_stock=in_stock,
                                image_url=image_url,
                                platform_product_id=product_id,
                            )
                        )

                    except Exception as e:
                        print(f"[Instamart] Item parse error: {e}")

        except Exception as e:
            print(f"[Instamart] Parse error: {e}")

        return results