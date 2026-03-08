"""
Blinkit CLI - Command line interface for testing Blinkit provider
"""
import json
import sys
from pathlib import Path
from blinkit_provider import BlinkitProvider


def load_response(response_file: str) -> dict:
    """Load Blinkit API response from JSON file"""
    try:
        with open(response_file, 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        print(f"Error: Response file not found: {response_file}")
        sys.exit(1)
    except json.JSONDecodeError:
        print(f"Error: Invalid JSON in {response_file}")
        sys.exit(1)


def format_price(price_text: str) -> str:
    """Format price for display"""
    return price_text if price_text else "N/A"


def main():
    """Main CLI entry point"""
    # Check if response file is provided
    if len(sys.argv) < 2:
        # Default to sample_responses folder
        response_file = Path(__file__).parent.parent.parent / "sample_responses" / "blinkitResponse.json"
    else:
        response_file = sys.argv[1]
    
    print(f"Loading Blinkit response from: {response_file}")
    response = load_response(str(response_file))
    
    # Parse products
    products = BlinkitProvider.search(response)
    
    # Display results
    print(f"\n✓ Found {len(products)} products\n")
    
    for idx, product in enumerate(products, 1):
        print(f"{idx}. {product['name']}")
        if product.get('size'):
            print(f"   Size: {product['size']}")
        print(f"   Price: {format_price(product['price'])}")
        print(f"   Brand: {product.get('brand', 'N/A')}")
        print(f"   Store ID: {product['store_id']}")
        if product.get('image'):
            print(f"   Image: {product['image'][:60]}...")
        print()


if __name__ == "__main__":
    main()
