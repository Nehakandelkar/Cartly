from browser_manager import BrowserManager


def get_zepto_price(product: str):
    """
    Fetch product data from Zepto using Playwright (network interception)
    """

    page = BrowserManager.new_page()

    try:
        captured = []

        # ---------------- RESPONSE LISTENER ----------------
        def handle_response(response):
            url = response.url

            # DEBUG (optional)
            # print(url)

            if "bff-gateway.zepto.com" in url and "get_page" in url:
                try:
                    json_data = response.json()
                    captured.append(json_data)
                    print("✅ Zepto API captured")
                except:
                    pass

        page.on("response", handle_response)

        # ---------------- TRIGGER SEARCH ----------------
        search_url = f"https://www.zeptonow.com/search?q={product}"

        page.goto(search_url, timeout=60000)

        # VERY IMPORTANT (SPA delay)
        page.wait_for_load_state("networkidle")
        page.wait_for_timeout(5000)

        # ---------------- VALIDATE ----------------
        if not captured:
            print("⚠️ Zepto API response not captured")
            return []

        data = captured[0]

        print("✅ Zepto API response captured")

        # ---------------- PARSING ----------------
        products = []

        widgets = data.get("widgets", [])

        for widget in widgets:

            if widget.get("widgetId") != "PRODUCT_GRID":
                continue

            items = (
                widget.get("data", {})
                .get("resolver", {})
                .get("data", {})
                .get("items", [])
            )

            for item in items:

                pr = item.get("productResponse", {})

                product_data = pr.get("product", {})
                variant = pr.get("productVariant", {})
                price_data = pr.get("price", {})

                products.append({
                    "provider": "zepto",
                    "name": product_data.get("name"),
                    "brand": product_data.get("brand"),
                    "price": price_data.get("sp", 0) / 100,
                    "size": variant.get("formattedPacksize"),
                    "image": (
                        variant.get("images", [{}])[0].get("path")
                        if variant.get("images") else None
                    ),
                    "id": pr.get("id"),
                    "store_id": pr.get("storeId")
                })

        return products

    except Exception as e:
        print(f"Zepto error: {e}")
        return []

    finally:
        page.close()