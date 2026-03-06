from playwright.sync_api import sync_playwright
import json
import time

# ✅ Use the EXACT API you saw
INSTAMART_API = "https://www.swiggy.com/api/instamart/search/v2"

# ⚠️ Location-specific IDs (hardcoded for now)
STORE_ID = "1382871"
PRIMARY_STORE_ID = "1382871"
SECONDARY_STORE_ID = "1402457"


def scrape_instamart(query: str):
    with sync_playwright() as p:
        # Headed browser is IMPORTANT
        browser = p.chromium.launch(headless=False)

        context = browser.new_context(
            viewport={"width": 390, "height": 844},
            user_agent="Mozilla/5.0 (iPhone; CPU iPhone OS 16_0 like Mac OS X)"
        )

        page = context.new_page()

        # 1️⃣ Open Instamart search page (session warm-up)
        page.goto(
            f"https://www.swiggy.com/instamart/search?custom_back=true&query={query}",
            timeout=60000
        )

        # Let page fully load + JS settle
        page.wait_for_load_state("networkidle")
        time.sleep(2)

        # 2️⃣ Call Instamart API USING SAME SESSION
        response = page.request.get(
            INSTAMART_API,
            params={
                "query": query,
                "offset": 0,
                "ageConsent": "false",
                "layoutId": "4987",
                "storeId": STORE_ID,
                "primaryStoreId": PRIMARY_STORE_ID,
                "secondaryStoreId": SECONDARY_STORE_ID
            },
            headers={
                "accept": "application/json",
                "content-type": "application/json",
                "referer": "https://www.swiggy.com/instamart",
                "origin": "https://www.swiggy.com"
            }
        )

        try:
            data = response.json()
        except Exception:
            print("❌ Instamart API did not return JSON")
            print(response.text()[:300])
            browser.close()
            return []

        products = []

        # 3️⃣ Parse product cards
        cards = data.get("data", {}).get("cards", [])

        for wrapper in cards:
            card = wrapper.get("card", {}).get("card", {})

            # Product widgets
            if card.get("@type", "").endswith("ItemWidget"):
                info = card.get("info", {})

                name = info.get("name")
                price = info.get("price") or info.get("finalPrice")
                quantity = info.get("variant", {}).get("name")

                if name and price:
                    products.append({
                        "platform": "INSTAMART",
                        "name": name,
                        "price": price // 100,  # paise → rupees
                        "quantity": quantity
                    })

        browser.close()
        return products


if __name__ == "__main__":
    result = scrape_instamart("milk")
    print(json.dumps(result[:5], indent=2))
