from browser_manager import BrowserManager


def get_blinkit_price(product: str):
    """
    Fetch product data from Blinkit using Playwright network interception
    """

    page = BrowserManager.new_page()

    try:
        search_url = f"https://blinkit.com/s/?q={product}"

        captured = []

        def handle_response(response):
            print(response.url)
            if "/v1/layout/search" in response.url:
                try:
                    captured.append(response.json())
                except:
                    pass

        page.on("response", handle_response)
        page.goto(search_url, timeout=60000)
        page.wait_for_timeout(5000)  # Wait for potential late responses

        data = captured[0] if captured else {}  

        if data:
            print("✅ Blinkit API response captured")
        else:
            print("⚠️ Blinkit API response not captured")


        products = []

        if "data" in data and "products" in data["data"]:
            for item in data["data"]["products"]:

                name = item.get("name")
                price = item.get("price")

                products.append({
                    "provider": "blinkit",
                    "name": name,
                    "price": price
                })

        return products

    except Exception as e:
        print(f"Blinkit error: {e}")
        return []

    finally:
        page.close()