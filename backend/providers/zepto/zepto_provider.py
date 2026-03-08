"""
Zepto Provider - Handles parsing and normalizing Zepto API responses
"""
import json
from typing import List, Dict, Any, Optional


class ZeptoProvider:
    """Provider class for Zepto API response parsing"""
    
    PROVIDER_NAME = "zepto"
    
    def __init__(self):
        """Initialize the Zepto provider"""
        pass
    
    @staticmethod
    def parse_price(price: Any) -> str:
        """Extract numeric price - Zepto API returns prices in paise, convert to rupees"""
        try:
            if isinstance(price, (int, float)):
                # Convert paise to rupees (divide by 100)
                price_in_rupees = int(price) / 100
                return str(int(price_in_rupees))
            return str(price) if price else ""
        except Exception:
            return ""
    
    @staticmethod
    def extract_product(product_response: Dict[str, Any]) -> Optional[Dict[str, str]]:
        """
        Extract product information from a product response object
        
        Args:
            product_response: A single product response from the items list
            
        Returns:
            Normalized product dict or None if extraction fails
        """
        try:
            # Product info is nested in productResponse
            product_info = product_response.get("product", {})
            name = product_info.get("name", "")
            brand = product_info.get("brand", "")
            
            # Product variant contains size and images
            product_variant = product_response.get("productVariant", {})
            size = product_variant.get("formattedPacksize", "")
            
            # Product ID is at the variant level
            product_id = product_variant.get("productId", product_info.get("id", ""))
            
            # Get price - try sellingPrice first, then discountedSellingPrice
            price = product_response.get("sellingPrice", product_response.get("discountedSellingPrice", ""))
            price_str = ZeptoProvider.parse_price(price)
            
            # Get image from productVariant
            images = product_variant.get("images", [])
            image_url = ""
            if images:
                first_image = images[0]
                image_path = first_image.get("path", "")
                if image_path:
                    image_url = f"https://cdn.grofers.com/cdn-cgi/image/f=auto,fit=scale-down,quality=70,w=270,h=336/{image_path}"
            
            return {
                "product_id": product_id,
                "name": name,
                "brand": brand,
                "size": size,
                "price": price_str,
                "price_raw": f"₹{price_str}" if price_str else "",
                "store_id": "",
                "image": image_url,
                "provider": ZeptoProvider.PROVIDER_NAME
            }
        except Exception as e:
            print(f"Error extracting product: {e}")
            return None
    
    @classmethod
    def search(cls, response_data: Dict[str, Any]) -> List[Dict[str, str]]:
        """
        Parse Zepto response and extract products
        
        Args:
            response_data: The full API response dict
            
        Returns:
            List of normalized products
        """
        products = []
        
        try:
            # Navigate through the layout structure
            layout = response_data.get("layout", [])
            
            for widget in layout:
                data = widget.get("data", {})
                resolver = data.get("resolver", {})
                
                if resolver:
                    # Products are in resolver.data.items
                    resolver_data = resolver.get("data", {})
                    items = resolver_data.get("items", [])
                    
                    for item in items:
                        # Each item has a productResponse object
                        product_response = item.get("productResponse", {})
                        if product_response:
                            product = cls.extract_product(product_response)
                            if product and product.get("product_id"):
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
