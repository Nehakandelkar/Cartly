#!/usr/bin/env python3
"""
Instamart API Discovery - Playwright Script

This script mirrors the Blinkit fetcher but for Instamart (Swiggy Instamart).
It:
1. Launches a Chromium browser
2. Navigates to Instamart
3. Opens the Instamart search page for the given query
4. Intercepts the Instamart search API response
5. Saves the JSON response
6. Prints normalized products in a human-readable format
"""

import json
import sys
import shutil
from pathlib import Path
from datetime import datetime
from playwright.sync_api import sync_playwright, Page, Response

from providers.instamart import InstamartProvider


class InstamartPlaywrightFetcher:
    """Handles Instamart API discovery using Playwright"""

    INSTAMART_HOME = "https://www.swiggy.com/instamart"
    SEARCH_PAGE_URL = "https://www.swiggy.com/instamart/search"
    # URL substrings that identify the Instamart search API response
    SEARCH_API_PATHS = ("/api/instamart/search", "/dapi/instamart/search")
    OUTPUT_DIR = Path(__file__).parent / "sample_responses"

    def __init__(self, headless: bool = True, timeout: int = 30000):
        self.headless = headless
        self.timeout = timeout
        self.captured_response = None
        self.captured_url = None
        self.api_response_received = False

    @staticmethod
    def _print_products_from_response(response_data: dict) -> None:
        """Parse and print products from an Instamart API response."""
        try:
            products = InstamartProvider.search(response_data)
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
        """Callback to intercept Instamart search API responses by URL."""
        if self.api_response_received:
            return

        url = response.url
        if not any(path in url for path in self.SEARCH_API_PATHS):
            return

        self.captured_url = url
        self.api_response_received = True
        print(f"\n✅ Captured Instamart API URL: {url}")

        try:
            self.captured_response = response.json()
            print(f"✅ Response size: {len(json.dumps(self.captured_response))} bytes")
        except Exception as e:
            print(f"⚠️ Could not parse Instamart response as JSON: {e}")

    def fetch(self, query: str = "milk", output_file: str = None) -> bool:
        """Main fetch function."""
        if output_file is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_file = self.OUTPUT_DIR / f"instamartLiveResponse_{timestamp}.json"
        else:
            output_file = Path(output_file)

        output_file.parent.mkdir(parents=True, exist_ok=True)

        print("🚀 Starting Instamart API discovery")
        print(f"📍 Target: {self.INSTAMART_HOME}")
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

                # Pre-set location via cookies so Instamart loads a store immediately
                try:
                    context.add_cookies(
                        [
                            {
                                "name": "lat",
                                "value": "19.0760",
                                "domain": ".swiggy.com",
                                "path": "/",
                            },
                            {
                                "name": "lng",
                                "value": "72.8777",
                                "domain": ".swiggy.com",
                                "path": "/",
                            },
                        ]
                    )
                    print("📍 Injected Instamart location cookies (Mumbai lat/lng)")
                except Exception as e:
                    print(f"⚠️ Failed to set Instamart location cookies: {e}")

                page = context.new_page()
                page.set_default_timeout(self.timeout)
                page.on("response", self.on_response)

                # Navigate to Instamart homepage (store should load using cookies)
                print(f"🌐 Navigating to Instamart homepage: {self.INSTAMART_HOME}")
                try:
                    page.goto(self.INSTAMART_HOME, wait_until="domcontentloaded", timeout=self.timeout)
                except Exception as e:
                    print(f"⚠️ Navigation warning (homepage): {e}")

                # Navigate directly to search page to trigger the search API (no UI interaction)
                search_url = f"{self.SEARCH_PAGE_URL}?query={query.replace(' ', '%20')}"
                print(f"🔎 Navigating to Instamart search page: {search_url}")
                try:
                    page.goto(search_url, wait_until="domcontentloaded", timeout=self.timeout)
                except Exception as e:
                    print(f"⚠️ Navigation warning (search page): {e}")

                # Allow time for the search API to fire and be intercepted
                page.wait_for_timeout(5000)

                print("⏳ Waiting for Instamart API response...")
                wait_count = 0
                max_wait = 20  # 20 * 300ms = 6 seconds
                while wait_count < max_wait and not self.api_response_received:
                    page.wait_for_timeout(300)
                    wait_count += 1

                if self.api_response_received:
                    print("✅ Instamart API response captured")
                else:
                    print("⚠️ Instamart API response not received within timeout")

                context.close()
                browser.close()

                if self.captured_response:
                    print("\n" + "=" * 80)
                    print("✅ SUCCESS - Instamart API Response captured!")
                    print("=" * 80)

                    with open(output_file, "w", encoding="utf-8") as f:
                        json.dump(self.captured_response, f, indent=2, ensure_ascii=False)

                    print(f"💾 Response saved to: {output_file}")

                    # Also create/update the latest response copy
                    latest_file = self.OUTPUT_DIR / "instamartLiveResponse.json"
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
                    print("\n⚠️ No Instamart API response captured")
                    return False

        except Exception as e:
            print(f"\n❌ Error during Instamart fetch: {e}")
            import traceback

            traceback.print_exc()
            return False


def main():
    """Main entry point."""
    import argparse

    parser = argparse.ArgumentParser(
        description="Fetch Instamart API responses using Playwright"
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

    print(f"\n🔍 Searching Instamart for: {args.query}")
    print("-" * 80)

    fetcher = InstamartPlaywrightFetcher(headless=not args.no_headless)
    success = fetcher.fetch(query=args.query, output_file=args.output)

    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()

