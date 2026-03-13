#!/usr/bin/env python3
"""
Zepto API Discovery - Playwright Script

This script mirrors the Blinkit fetcher but for Zepto.
It:
1. Launches a Chromium browser
2. Navigates to Zepto
3. Opens the Zepto search page for the given query
4. Intercepts the Zepto search API response
5. Saves the JSON response
6. Prints normalized products in a human-readable format
"""

import json
import sys
import shutil
from pathlib import Path
from datetime import datetime
from playwright.sync_api import sync_playwright, Page, Response

from providers.zepto import ZeptoProvider


class ZeptoPlaywrightFetcher:
    """Handles Zepto API discovery using Playwright"""

    ZEPTO_HOME = "https://www.zeptonow.com"
    SEARCH_PAGE_URL = "https://www.zeptonow.com/search"
    OUTPUT_DIR = Path(__file__).parent / "sample_responses"

    def __init__(self, headless: bool = True, timeout: int = 15000):
        self.headless = headless
        self.timeout = timeout
        self.captured_response = None
        self.captured_url = None
        self.api_response_received = False

    @staticmethod
    def _is_zepto_search_response(response: Response) -> bool:
        try:
            if "application/json" not in (response.headers.get("content-type", "") or ""):
                return False

            data = response.json()

            #detect product structures commonly used by zepto
            text = json.dumps(data).lower()

            if "product" in text or "products" in text:
                return True

        except:
            return False

        return False    


    @staticmethod
    def _print_products_from_response(response_data: dict) -> None:
        """Parse and print products from a Zepto API response."""
        try:
            products = ZeptoProvider.search(response_data)
        except Exception as e:
            print(f"\n⚠️ Failed to parse products from response: {e}")
            return

        if not products:
            print("\n❌ No products found in captured response")
            return

        print(f"\n✅ Parsed {len(products)} products from captured response")
        print("-" * 80)

        for idx, product in enumerate(products, 1):
            name = product.get("name", "") or "Unknown product"
            brand = product.get("brand", "")
            size = product.get("size", "")
            price_raw = product.get("price_raw", "") or product.get("price", "")
            store_id = product.get("store_id", "")
            product_id = product.get("product_id", "")
            image = product.get("image", "")

            print(f"\n{idx}. {name}")
            if brand:
                print(f"   Brand: {brand}")
            if size:
                print(f"   Size: {size}")
            if price_raw:
                print(f"   Price: {price_raw}")
            if store_id:
                print(f"   Store ID: {store_id}")
            if product_id:
                print(f"   Product ID: {product_id}")
            if image:
                print(f"   Image: {image[:60]}...")

        print("\n" + "-" * 80)

    def on_response(self, response: Response) -> None:
        """Callback to intercept potential Zepto search responses."""
        if self.api_response_received:
            return

        if not self._is_zepto_search_response(response):
            return

        self.captured_url = response.url
        self.api_response_received = True
        print(f"\n✅ Captured Zepto API URL: {response.url}")

        try:
            self.captured_response = response.json()
            print(f"✅ Response size: {len(json.dumps(self.captured_response))} bytes")
        except Exception as e:
            print(f"⚠️ Could not parse Zepto response as JSON: {e}")

    def fetch(self, query: str = "milk", output_file: str = None) -> bool:
        """Main fetch function."""
        if output_file is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_file = self.OUTPUT_DIR / f"zeptoLiveResponse_{timestamp}.json"
        else:
            output_file = Path(output_file)

        output_file.parent.mkdir(parents=True, exist_ok=True)

        print("🚀 Starting Zepto API discovery")
        print(f"📍 Target: {self.ZEPTO_HOME}")
        print(f"🔍 Search query: {query}")
        print(f"💾 Output file: {output_file}")
        print("-" * 80)

        try:
            with sync_playwright() as p:
                print("📱 Launching Chromium browser...")
                browser = p.chromium.launch(
                    headless=self.headless,
                    args=["--disable-blink-features=AutomationControlled"],
                )

                context = browser.new_context()
                page = context.new_page()
                page.set_default_timeout(self.timeout)
                page.on("response", self.on_response)

                # Navigate to Zepto homepage first (session warm-up)
                print(f"🌐 Navigating to Zepto homepage: {self.ZEPTO_HOME}")
                try:
                    page.goto(self.ZEPTO_HOME, wait_until="domcontentloaded", timeout=self.timeout)
                except Exception as e:
                    print(f"⚠️ Navigation warning (homepage): {e}")

                # Then navigate directly to search page with query parameter
                search_url = f"{self.SEARCH_PAGE_URL}?query={query.replace(' ', '%20')}"
                print(f"🔎 Navigating to Zepto search page: {search_url}")
                try:
                    page.goto(search_url, wait_until="domcontentloaded", timeout=self.timeout)
                except Exception as e:
                    print(f"⚠️ Navigation warning (search page): {e}")

                # Allow some time for the search API to fire and be intercepted
                page.wait_for_timeout(5000)

                print("⏳ Waiting for Zepto API response...")
                wait_count = 0
                max_wait = 20  # 20 * 300ms = 6 seconds
                while wait_count < max_wait and not self.api_response_received:
                    page.wait_for_timeout(300)
                    wait_count += 1

                if self.api_response_received:
                    print("✅ Zepto API response captured")
                else:
                    print("⚠️ Zepto API response not received within timeout")

                context.close()
                browser.close()

                if self.captured_response:
                    print("\n" + "=" * 80)
                    print("✅ SUCCESS - Zepto API Response captured!")
                    print("=" * 80)

                    with open(output_file, "w", encoding="utf-8") as f:
                        json.dump(self.captured_response, f, indent=2, ensure_ascii=False)

                    print(f"💾 Response saved to: {output_file}")

                    # Also create/update the latest response copy
                    latest_file = self.OUTPUT_DIR / "zeptoLiveResponse.json"
                    try:
                        if latest_file.exists():
                            latest_file.unlink()
                        shutil.copy(output_file, latest_file)
                        print(f"📄 Latest response copied to: {latest_file}")
                    except Exception as e:
                        print(f"⚠️ Could not create latest response copy: {e}")

                    # Pretty-print parsed products
                    self._print_products_from_response(self.captured_response)

                    return True
                else:
                    print("\n⚠️ No Zepto API response captured")
                    return False

        except Exception as e:
            print(f"\n❌ Error during Zepto fetch: {e}")
            import traceback

            traceback.print_exc()
            return False


def main():
    """Main entry point."""
    import argparse

    parser = argparse.ArgumentParser(
        description="Fetch Zepto API responses using Playwright"
    )
    parser.add_argument(
        "-q",
        "--query",
        default=None,
        help="Search query (if not provided, you will be prompted)",
    )
    parser.add_argument(
        "-o",
        "--output",
        help="Output file path (optional)",
    )
    parser.add_argument(
        "--no-headless",
        action="store_true",
        help="Run browser in non-headless mode (for debugging)",
    )

    args = parser.parse_args()

    if args.query is None:
        user_input = input("Enter product to search: ").strip()
        if user_input:
            args.query = user_input
        else:
            args.query = "milk"
            print("Using default query: milk")

    print(f"\n🔍 Searching Zepto for: {args.query}")
    print("-" * 80)

    fetcher = ZeptoPlaywrightFetcher(headless=not args.no_headless)
    success = fetcher.fetch(query=args.query, output_file=args.output)

    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()

