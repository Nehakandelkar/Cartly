"""
CLI entry point for the price aggregator
"""

import argparse

from services.aggregator import AggregatorService


def print_products(products, platform):
    """Pretty print products from a platform"""

    if not products:
        print(f"\n❌ No products found on {platform}")
        return

    print(f"\n🛒 {platform.upper()} RESULTS")
    print("-" * 60)

    for i, product in enumerate(products, 1):

        print(f"\n{i}. {product.get('name')}")
        print(f"   Brand: {product.get('brand')}")
        print(f"   Size: {product.get('size')}")
        print(f"   Price: ₹{product.get('price')}")
        print(f"   Product ID: {product.get('id')}")
        print(f"   Store ID: {product.get('store_id')}")
        print(f"   Image: {str(product.get('image'))[:60]}...")


def main():

    parser = argparse.ArgumentParser()
    parser.add_argument("-q", "--query", required=True)

    args = parser.parse_args()

    print("\n🔎 Searching across Blinkit, Zepto, and Instamart...")
    print("=" * 70)

    aggregator = AggregatorService()

    result = aggregator.search_all(args.query)

    print("\n" + "=" * 70)
    print("✅ Search complete")

    for platform, products in result["results"].items():
        print_products(products, platform)


if __name__ == "__main__":
    main()