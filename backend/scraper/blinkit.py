from playwright.sync_api import sync_playwright
import json
import time


def scrape_blinkit(query: str):
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)

        page = browser.new_page(
            viewport={"width": 390, "height": 844},
            user_agent="Mozilla/5.0 (iPhone; CPU iPhone OS 16_0 like Mac OS X)"
        )

        captured = []

        def handle_response(response):
            if "layout/search" in response.url:
                try:
                    captured.append(response.json())
                    print("✅ Captured:", response.url)
                except:
                    pass

        page.on("response", handle_response)

        page.goto(
            f"https://blinkit.com/s/?q={query}",
            timeout=60000
        )

        time.sleep(6)
        browser.close()

        # -------- GENERALISED CHEAPEST LOGIC --------
        keyword = query.lower()
        cheapest = None

        for block in captured:
            snippets = block.get("response", {}).get("snippets", [])

            for snippet in snippets:
                data = snippet.get("data", {})

                name_text = data.get("name", {}).get("text", "")
                name_lower = name_text.lower()

                quantity = data.get("variant", {}).get("text")

                cart_item = (
                    data.get("atc_action", {})
                        .get("add_to_cart", {})
                        .get("cart_item", {})
                )

                price = cart_item.get("price")

                # match any product based on user input keyword
                if keyword in name_lower and isinstance(price, (int, float)):
                    product = {
                        "platform": "BLINKIT",
                        "name": name_text,
                        "price": price,
                        "quantity": quantity
                    }

                    if cheapest is None or price < cheapest["price"]:
                        cheapest = product

        return cheapest if cheapest else {
            "platform": "BLINKIT",
            "error": f"NO_PRODUCT_FOUND_FOR_{query.upper()}"
        }


if __name__ == "__main__":
    # try changing this to rice / curd / sugar / bread etc.
    result = scrape_blinkit("milk")
    print(json.dumps(result, indent=2))
