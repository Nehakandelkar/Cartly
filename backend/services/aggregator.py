from scraper.blinkit import get_blinkit_price

def compare_prices(product: str):
    prices = [get_blinkit_price(product)]

    # prices = [p for p in prices if p["available"]]
    prices.sort(key=lambda x: x["price"])

    return {
        "product": product,
        "prices": prices
    }
