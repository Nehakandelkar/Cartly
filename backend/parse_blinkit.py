#!/usr/bin/env python3
"""
Blinkit Response Parser CLI
Parses Blinkit API responses and displays normalized products
"""
import sys
import os
from pathlib import Path

# Add backend directory to path for imports
backend_dir = Path(__file__).parent
sys.path.insert(0, str(backend_dir))

from providers.blinkit import BlinkitProvider, load_response_from_file


def print_product_table(products: list) -> None:
    """
    Print products in a nice CLI format
    
    Args:
        products: List of normalized products
    """
    if not products:
        print("❌ No products found")
        return
    
    print(f"\n✅ Found {len(products)} products\n")
    print("-" * 80)
    
    for idx, product in enumerate(products, 1):
        print(f"\n{idx}. {product['name']}")
        
        if product['brand']:
            print(f"   Brand: {product['brand']}")
        
        if product['size']:
            print(f"   Size: {product['size']}")
        
        print(f"   Price: {product['price_raw']}")
        print(f"   Store ID: {product['store_id']}")
        print(f"   Product ID: {product['product_id']}")
        
        if product['image']:
            print(f"   Image: {product['image'][:60]}...")
    
    print("\n" + "-" * 80)


def main():
    """Main CLI entry point"""
    
    # Get the response file path
    if len(sys.argv) > 1:
        response_file = sys.argv[1]
    else:
        # Default to sample_responses/blinkitResponse.json
        response_file = os.path.join(
            backend_dir, 
            "sample_responses", 
            "blinkitResponse.json"
        )
    
    print(f"📖 Loading response from: {response_file}")
    
    # Load and parse
    response_data = load_response_from_file(response_file)
    
    if not response_data:
        print("❌ Failed to load response")
        sys.exit(1)
    
    # Parse products
    products = BlinkitProvider.search(response_data)
    
    # Display results
    print_product_table(products)
    
    # Also print raw JSON for each product
    print("\n🔍 Raw JSON Output (for debugging):\n")
    for product in products:
        print(product)


if __name__ == "__main__":
    main()
