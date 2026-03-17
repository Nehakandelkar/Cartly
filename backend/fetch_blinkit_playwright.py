#!/usr/bin/env python3

import json
from pathlib import Path
from datetime import datetime
from playwright.sync_api import sync_playwright


class BlinkitPlaywrightFetcher:

    SEARCH_URL = "https://blinkit.com/s/?q="
    OUTPUT_DIR = Path(__file__).parent / "sample_responses"

    def __init__(self, headless=True, timeout=60000):
        self.headless = headless
        self.timeout = timeout

    def fetch(self, query: str):

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_file = self.OUTPUT_DIR / f"blinkitLiveResponse_{timestamp}.json"

        print("🚀 Starting Blinkit API discovery")

        try:
            with sync_playwright() as p:

                browser = p.chromium.launch(headless=self.headless)

                context = browser.new_context(
                    geolocation={"latitude": 19.0760, "longitude": 72.8777},
                    permissions=["geolocation"]
                )

                page = context.new_page()

                search_url = f"{self.SEARCH_URL}{query}"

                print(f"🌐 Opening {search_url}")

                page.goto(search_url, wait_until="domcontentloaded", timeout=self.timeout)

                print("⏳ Waiting for search API response")

                response = page.wait_for_response(
                    lambda r: "search" in r.url and r.status == 200,
                    timeout=self.timeout
                )

                data = response.json()

                print("✅ API response captured")

                context.close()
                browser.close()

            output_file.parent.mkdir(parents=True, exist_ok=True)

            with open(output_file, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2)

            print(f"💾 Saved response to {output_file}")

            return data

        except Exception as e:
            print(f"❌ Blinkit fetch failed: {e}")
            return {}


def main():

    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("-q", "--query", default="milk")
    parser.add_argument("--no-headless", action="store_true")

    args = parser.parse_args()

    fetcher = BlinkitPlaywrightFetcher(headless=not args.no_headless)
    fetcher.fetch(args.query)


if __name__ == "__main__":
    main()