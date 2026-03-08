"""
Blinkit Provider - Handles parsing and normalizing Blinkit API responses
"""
import json
from typing import List, Dict, Any, Optional


class BlinkitProvider:
    """Provider class for Blinkit API response parsing"""
    
    PROVIDER_NAME = "blinkit"
    PRODUCT_WIDGET_TYPE = "product_card_snippet_type_2"
    
    def __init__(self):
        """Initialize the Blinkit provider"""
        pass
    
    @staticmethod
    def parse_price(price_text: str) -> str:
        """Extract numeric price from text like '₹88'"""
        if not price_text:
            return ""
        # Remove currency symbol and return the number
        return price_text.replace("₹", "").strip()
    
    @staticmethod
    def extract_product(snippet: Dict[str, Any]) -> Optional[Dict[str, str]]:
        """
        Extract product information from a snippet
        
        Args:
            snippet: A single snippet from the response
            
        Returns:
            Normalized product dict or None if extraction fails
        """
        try:
            data = snippet.get("data", {})
            
            # Extract fields with safe navigation
            product_id = data.get("identity", {}).get("id", "")
            name = data.get("name", {}).get("text", "")
            variant = data.get("variant", {}).get("text", "")
            price_text = data.get("normal_price", {}).get("text", "")
            brand = data.get("atc_action", {}).get("add_to_cart", {}).get("cart_item", {}).get("brand", "")
            merchant_id = data.get("merchant_id", "")
            image_url = data.get("image", {}).get("url", "")
            
            # If brand is not found, try another location
            if not brand:
                brand = data.get("brand_name", "")
            
            # Parse price (remove currency symbol)
            price = BlinkitProvider.parse_price(price_text)
            
            return {
                "product_id": product_id,
                "name": name,
                "brand": brand,
                "size": variant,
                "price": price,
                "price_raw": price_text,
                "store_id": merchant_id,
                "image": image_url,
                "provider": BlinkitProvider.PROVIDER_NAME
            }
        except Exception as e:
            print(f"Error extracting product: {e}")
            return None
    
    @classmethod
    def search(cls, response_data: Dict[str, Any]) -> List[Dict[str, str]]:
        """
        Parse Blinkit response and extract products
        
        Args:
            response_data: The full API response dict
            
        Returns:
            List of normalized products
        """
        products = []
        
        try:
            snippets = response_data.get("response", {}).get("snippets", [])
            
            for snippet in snippets:
                # Filter by widget type
                if snippet.get("widget_type") != cls.PRODUCT_WIDGET_TYPE:
                    continue
                
                product = cls.extract_product(snippet)
                if product:
                    products.append(product)
        
        except Exception as e:
            print(f"Error parsing response: {e}")
        
        return products


def load_response_from_file(file_path: str) -> Dict[str, Any]:
    """
    Load JSON response from file
    
    Args:
        file_path: Path to the JSON file
        
    Returns:
        Parsed JSON dict
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        print(f"Error: File not found - {file_path}")
        return {}
    except json.JSONDecodeError:
        print(f"Error: Invalid JSON in file - {file_path}")
        return {}
