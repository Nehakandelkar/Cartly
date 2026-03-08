"""
Instamart Provider - Handles parsing and normalizing Instamart API responses
"""
import json
from typing import List, Dict, Any, Optional


class InstamartProvider:
    """Provider class for Instamart API response parsing"""
    
    PROVIDER_NAME = "instamart"
    
    def __init__(self):
        """Initialize the Instamart provider"""
        pass
    
    @staticmethod
    def parse_price(price_obj: Any) -> str:
        """Extract price from price object"""
        try:
            if isinstance(price_obj, dict):
                # Try offerPrice first, then mrp
                if "offerPrice" in price_obj:
                    units = price_obj["offerPrice"].get("units", "0")
                elif "mrp" in price_obj:
                    units = price_obj["mrp"].get("units", "0")
                else:
                    units = "0"
                return str(units)
            return ""
        except Exception:
            return ""
    
    @staticmethod
    def extract_product(product_item: Dict[str, Any]) -> Optional[Dict[str, str]]:
        """
        Extract product information from a product item
        
        Args:
            product_item: A single product item from the response
            
        Returns:
            Normalized product dict or None if extraction fails
        """
        try:
            # Get basic info
            display_name = product_item.get("displayName", "")
            brand = product_item.get("brand", "")
            product_id = product_item.get("productId", "")
            
            # Get price and size from variations
            size = ""
            price = ""
            image_url = ""
            
            variations = product_item.get("variations", [])
            if variations:
                first_variant = variations[0]
                size = first_variant.get("quantityDescription", "")
                
                # Get price
                price_obj = first_variant.get("price", {})
                price = InstamartProvider.parse_price(price_obj)
                
                # Get image
                image_ids = first_variant.get("imageIds", [])
                if image_ids:
                    # Construct image URL from imageId
                    image_url = f"https://cdn.grofers.com/cdn-cgi/image/f=auto,fit=scale-down,quality=70,w=270,h=336/v2/assets/{image_ids[0]}.jpeg"
            
            return {
                "product_id": product_id,
                "name": display_name,
                "brand": brand,
                "size": size,
                "price": price,
                "price_raw": f"₹{price}" if price else "",
                "store_id": "",
                "image": image_url,
                "provider": InstamartProvider.PROVIDER_NAME
            }
        except Exception as e:
            print(f"Error extracting product: {e}")
            return None
    
    @classmethod
    def search(cls, response_data: Dict[str, Any]) -> List[Dict[str, str]]:
        """
        Parse Instamart response and extract products
        
        Args:
            response_data: The full API response dict
            
        Returns:
            List of normalized products
        """
        products = []
        
        try:
            # Navigate through the response structure
            cards = response_data.get("data", {}).get("cards", [])
            
            for card in cards:
                card_obj = card.get("card", {}).get("card", {})
                
                # Look for products in gridElements.infoWithStyle.items
                grid_elements = card_obj.get("gridElements", {})
                info_with_style = grid_elements.get("infoWithStyle", {})
                items = info_with_style.get("items", [])
                
                for item in items:
                    # Handle product items with displayName
                    if isinstance(item, dict) and "displayName" in item:
                        product = cls.extract_product(item)
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
