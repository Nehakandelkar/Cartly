import asyncio
import sys
from app.services.aggregator import AggregatorService

async def main():
    query = sys.argv[1] if len(sys.argv) > 1 else "milk"
    pincode = sys.argv[2] if len(sys.argv) > 2 else "560001"

    print(f"Searching for '{query}' in {pincode}...\n")

    service = AggregatorService()
    results = await service.search(query, pincode)

    print(f"Found {len(results)} results\n")
    for r in results:
        print(f"[{r.platform.upper()}] {r.product_name} | {r.unit} | ₹{r.price} | {'✓' if r.in_stock else '✗'}")

asyncio.run(main())