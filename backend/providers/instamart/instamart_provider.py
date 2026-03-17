from browser_manager import BrowserManager


def get_instamart_price(product: str):
    """
    Fetch product data from Swiggy Instamart
    """

    page = BrowserManager.new_page()

    try:
        search_url = f"https://www.swiggy.com/instamart/search?query={product}"

        captured = []

        def handle_response(response):
            print(response.url)
            if "swiggy.com/api/instamart" in response.url:
                try:
                    captured.append(response.json())
                except:
                    pass

        page.on("response", handle_response)
        page.goto(search_url, timeout=60000)
        page.wait_for_timeout(5000)  # Wait for potential late responses

        data = captured[0] if captured else {}  

        if data:
            print("✅ Instamart API response captured")
        else:
            print("⚠️ Instamart API response not captured")            
                
        


        products = []

        if "data" in data and "items" in data["data"]:

            for item in data["data"]["items"]:

                name = item.get("name")
                price = item.get("price")

                products.append({
                    "provider": "instamart",
                    "name": name,
                    "price": price
                })

        return products

    except Exception as e:
        print(f"Instamart error: {e}")
        return []

    finally:
        page.close()