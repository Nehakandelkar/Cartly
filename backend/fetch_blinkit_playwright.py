#!/usr/bin/env python3
"""
Blinkit API Discovery - Playwright Script
Phase 0: Reverse engineering Blinkit's search API

This script uses Playwright to:
1. Launch a headless browser
2. Navigate to Blinkit
3. Perform a search query
4. Intercept the /v1/layout/search API response
5. Save the JSON response for parsing

The script bypasses Cloudflare protection by using a real browser session.
"""

import json
import sys
import shutil
from pathlib import Path
from datetime import datetime
from playwright.sync_api import sync_playwright, Page, Response
from providers.blinkit import BlinkitProvider


class BlinkitPlaywrightFetcher:
    """Handles Blinkit API discovery using Playwright"""
    
    BLINKIT_URL = "https://blinkit.com"
    SEARCH_API_PATH = "/v1/layout/search"
    OUTPUT_DIR = Path(__file__).parent / "sample_responses"
    
    def __init__(self, headless: bool = True, timeout: int = 15000):
        """
        Initialize the fetcher
        
        Args:
            headless: Run browser in headless mode
            timeout: Page navigation timeout in milliseconds
        """
        self.headless = headless
        self.timeout = timeout
        self.captured_response = None
        self.captured_url = None
        self.api_response_received = False
    
    @staticmethod
    def _print_products_from_response(response_data: dict) -> None:
        """
        Parse and print products from a Blinkit API response using BlinkitProvider.
        """
        try:
            products = BlinkitProvider.search(response_data)
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
                # Print a truncated image URL to keep output readable
                print(f"   Image: {image[:60]}...")

        print("\n" + "-" * 80)
    
    def on_response(self, response: Response) -> None:
        """
        Callback function to intercept network responses
        
        Args:
            response: The network response object
        """
        # Check if this is the search API response we're looking for
        if self.SEARCH_API_PATH in response.url:
            self.captured_url = response.url
            self.api_response_received = True
            print(f"\n✅ Captured API URL: {response.url}")
            
            try:
                # Try to get the JSON response
                self.captured_response = response.json()
                print(f"✅ Response size: {len(json.dumps(self.captured_response))} bytes")
            except Exception as e:
                print(f"⚠️ Could not parse response as JSON: {e}")
    
    # Method removed - now using direct URL navigation instead of UI selector interaction
    # def find_search_input(self, page: Page) -> bool:
    #     """
    #     Find and interact with the search input on Blinkit
    #     
    #     Args:
    #         page: Playwright page object
    #         
    #     Returns:
    #         True if search input found and query typed, False otherwise
    #     """
    #     try:
    #         # Common selectors for search input on Blinkit
    #         search_selectors = [
    #             'input[placeholder*="Search"]',
    #             'input[placeholder*="search"]',
    #             'input[type="text"]',
    #             '[data-testid="search-input"]',
    #             '.search-input',
    #         ]
    #         
    #         for selector in search_selectors:
    #             try:
    #                 element = page.query_selector(selector)
    #                 if element:
    #                     print(f"✅ Found search input: {selector}")
    #                     return True, selector
    #             except Exception:
    #                 continue
    #         
    #         return False, None
    #     except Exception as e:
    #         print(f"❌ Error finding search input: {e}")
    #         return False, None
    
    def fetch(self, query: str = "amul milk", output_file: str = None) -> bool:
        """
        Main fetch function
        
        Args:
            query: Search query to use
            output_file: Optional custom output file path
            
        Returns:
            True if successful, False otherwise
        """
        if output_file is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_file = self.OUTPUT_DIR / f"blinkitLiveResponse_{timestamp}.json"
        else:
            output_file = Path(output_file)
        
        # Ensure output directory exists
        output_file.parent.mkdir(parents=True, exist_ok=True)
        
        print(f"🚀 Starting Blinkit API discovery")
        print(f"📍 Target: {self.BLINKIT_URL}")
        print(f"🔍 Search query: {query}")
        print(f"💾 Output file: {output_file}")
        print("-" * 80)
        
        try:
            with sync_playwright() as p:
                # Launch browser with optimized settings
                print("📱 Launching Chromium browser...")
                browser = p.chromium.launch(
                    headless=self.headless,
                    args=["--disable-blink-features=AutomationControlled"]
                )
                
                # Create context with reasonable defaults and allow geolocation
                context = browser.new_context(
                    geolocation={"latitude": 19.0760, "longitude": 72.8777},  # Mumbai coordinates as default
                    permissions=["geolocation"],
                )
                page = context.new_page()
                page.set_default_timeout(self.timeout)
                page.on("response", self.on_response)
                
                # Navigate to the Blinkit homepage instead of direct search URL
                print(f"🌐 Navigating to Blinkit homepage: {self.BLINKIT_URL}")
                try:
                    page.goto(self.BLINKIT_URL, wait_until="domcontentloaded", timeout=self.timeout)
                except Exception as e:
                    print(f"⚠️ Navigation warning: {e}")
                
                print("✅ Homepage loaded, handling location and search flow...")
                
                try:
                    # STEP 1: Handle delivery location popup / bar if present
                    try:
                        # Prefer "Detect my location" style flows so the site uses geolocation
                        detect_selectors = [
                            'button:has-text("Detect my location")',
                            'button:has-text("Detect location")',
                            'text="Detect my location"',
                            'text="Detect location"',
                        ]
                        clicked_detect = False
                        for selector in detect_selectors:
                            try:
                                page.wait_for_selector(selector, timeout=5000)
                                page.click(selector)
                                clicked_detect = True
                                print(f"📍 Clicked detect location button using selector: {selector}")
                                # Wait for Blinkit to resolve location, load nearest store, and finish rendering
                                page.wait_for_load_state("networkidle")
                                page.wait_for_timeout(2000)
                                break
                            except Exception:
                                continue
                        
                        # Fallback: if detect-location button not found, use location text input as before
                        if not clicked_detect:
                            location_selectors = [
                                'input[placeholder*="Enter your delivery location"]',
                                'input[placeholder*="Enter delivery location"]',
                                'input[placeholder*="Search for area"]',
                                'input[placeholder*="Search your area"]',
                            ]
                            found_location_selector = None
                            for selector in location_selectors:
                                try:
                                    page.wait_for_selector(selector, timeout=5000)
                                    found_location_selector = selector
                                    print(f"✅ Found location input using selector: {selector}")
                                    break
                                except Exception:
                                    continue
                            
                            if found_location_selector:
                                default_location = "Mumbai"  # stable fallback area
                                page.click(found_location_selector)
                                page.fill(found_location_selector, default_location)
                                page.keyboard.press("Enter")
                                print(f"📍 Set delivery location to: {default_location}")
                                # Wait for Blinkit to load store for this location and finish rendering
                                page.wait_for_load_state("networkidle")
                                page.wait_for_timeout(2000)
                    except Exception as e_loc:
                        print(f"⚠️ Skipping location handling due to error: {e_loc}")
                    
                    # Ensure any location popup has time to close before searching for products
                    page.wait_for_timeout(3000)
                    
                    # STEP 2: Instead of typing into the search bar, navigate directly
                    # to the search results URL so Blinkit loads the search page and
                    # triggers the /v1/layout/search API, which our response listener captures.
                    search_url = f"https://blinkit.com/s/?q={query.replace(' ', '%20')}"
                    print(f"🔎 Navigating to search page: {search_url}")
                    page.goto(search_url, wait_until="domcontentloaded", timeout=self.timeout)
                    
                    # Allow a few seconds for the search API to be triggered and response intercepted
                    page.wait_for_timeout(5000)
                except Exception as e:
                    print(f"❌ Error interacting with search / location inputs: {e}")
                    context.close()
                    browser.close()
                    return False
                
                # Wait for API response using polling (sync API compatible)
                print(f"⏳ Waiting for API response...")
                wait_count = 0
                max_wait = 20  # 20 * 300ms = 6 seconds total
                
                while wait_count < max_wait and not self.api_response_received:
                    page.wait_for_timeout(300)
                    wait_count += 1
                
                if self.api_response_received:
                    print("✅ API response captured")
                else:
                    print("⚠️ API response not received within timeout")
                
                # Close browser
                context.close()
                browser.close()
                
                # Check if we captured a response
                if self.captured_response:
                    print("\n" + "=" * 80)
                    print("✅ SUCCESS - API Response captured!")
                    print("=" * 80)
                    
                    # Save to file
                    with open(output_file, "w", encoding="utf-8") as f:
                        json.dump(self.captured_response, f, indent=2, ensure_ascii=False)
                    
                    print(f"💾 Response saved to: {output_file}")
                    
                    # Also create/update the latest response copy
                    latest_file = self.OUTPUT_DIR / "blinkitLiveResponse.json"
                    try:
                        if latest_file.exists():
                            latest_file.unlink()
                        shutil.copy(output_file, latest_file)
                        print(f"📄 Latest response copied to: {latest_file}")
                    except Exception as e:
                        print(f"⚠️ Could not create latest response copy: {e}")
                    
                    # Additionally, pretty-print parsed product information to the terminal
                    self._print_products_from_response(self.captured_response)
                    
                    return True
                else:
                    print("\n⚠️ No API response captured")
                    print("💡 This might happen if:")
                    print("   - The API response format has changed")
                    print("   - Network request was blocked or intercepted")
                    print("   - Blinkit's search endpoint URL has changed")
                    return False
        
        except Exception as e:
            print(f"\n❌ Error during fetch: {e}")
            import traceback
            traceback.print_exc()
            return False


def main():
    """Main entry point"""
    import argparse
    
    parser = argparse.ArgumentParser(
        description="Fetch Blinkit API responses using Playwright"
    )
    parser.add_argument(
        "-q", "--query",
        default=None,
        help="Search query (if not provided, you will be prompted)"
    )
    parser.add_argument(
        "-o", "--output",
        help="Output file path (optional)"
    )
    parser.add_argument(
        "--no-headless",
        action="store_true",
        help="Run browser in non-headless mode (for debugging)"
    )
    
    args = parser.parse_args()
    
    # If no query provided via CLI, prompt the user
    if args.query is None:
        user_input = input("Enter product to search: ").strip()
        if user_input:
            args.query = user_input
        else:
            # Fallback to default if user provides empty input
            args.query = "amul milk"
            print("Using default query: amul milk")
    
    # Print the search query being used
    print(f"\n🔍 Searching Blinkit for: {args.query}")
    print("-" * 80)
    
    # Create fetcher and run
    fetcher = BlinkitPlaywrightFetcher(headless=not args.no_headless)
    success = fetcher.fetch(query=args.query, output_file=args.output)
    
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
