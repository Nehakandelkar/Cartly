from playwright.sync_api import sync_playwright
import json
import time


def scrape_zepto(query: str):
    with sync_playwright() as p:
        # IMPORTANT: non-headless so Zepto actually renders products
        browser = p.chromium.launch(headless=False)

        page = browser.new_page(
            viewport={"width": 390, "height": 844},
            user_agent="Mozilla/5.0 (iPhone; CPU iPhone OS 16_0 like Mac OS X)"
        )

        # ---- LOAD PAGE ----
        page.goto(
            f"https://www.zepto.in/search?query={query}",
            timeout=60000
        )

        # wait for JS + network
        page.wait_for_load_state("networkidle")
        page.wait_for_timeout(3000)

        # trigger lazy loading (very important)
        page.mouse.wheel(0, 4000)
        time.sleep(2)

        products = []

        # ---- DOM SCRAPING ----
        # Generic approach: look for price anchors (₹) and nearby text
        cards = page.query_selector_all("div")

        for card in cards:
            try:
                price_el = card.query_selector('text=/₹\\d+/')
                name_el = card.query_selector("h5")

                if not price_el or not name_el:
                    continue

                price = int(
                    price_el.inner_text()
                    .replace("₹", "")
                    .strip()
                )

                name = name_el.inner_text().strip()

                qty_el = card.query_selector("p")
                quantity = qty_el.inner_text().strip() if qty_el else None

                products.append({
                    "platform": "ZEPTO",
                    "name": name,
                    "price": price,
                    "quantity": quantity
                })

            except:
                continue

        browser.close()
        return products


if __name__ == "__main__":
    result = scrape_zepto("milk")
    print(json.dumps(result[:5], indent=2))
