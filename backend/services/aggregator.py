from typing import Dict, Any

from providers.blinkit.blinkit_provider import get_blinkit_price
from providers.zepto.zepto_provider import get_zepto_price
from providers.instamart.instamart_provider import get_instamart_price


class AggregatorService:

    def search_all(self, query: str) -> Dict[str, Any]:

        results = {
            "blinkit": [],
            "zepto": [],
            "instamart": []
        }

        # ---------------- Blinkit ----------------

        print("🔎 Searching Blinkit...")

        try:
            results["blinkit"] = get_blinkit_price(query)
            print(f"Parsed {len(results['blinkit'])} Blinkit products")

        except Exception as e:
            print(f"⚠️ Blinkit failed: {e}")

        # ---------------- Zepto ----------------

        print("🔎 Searching Zepto...")

        try:
            results["zepto"] = get_zepto_price(query)
            print(f"Parsed {len(results['zepto'])} Zepto products")

        except Exception as e:
            print(f"⚠️ Zepto failed: {e}")

        # ---------------- Instamart ----------------

        print("🔎 Searching Instamart...")

        try:
            results["instamart"] = get_instamart_price(query)
            print(f"Parsed {len(results['instamart'])} Instamart products")

        except Exception as e:
            print(f"⚠️ Instamart failed: {e}")

        print("✅ Search complete")

        return {
            "query": query,
            "results": results
        }