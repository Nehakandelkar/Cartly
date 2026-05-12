import asyncio
from app.providers.blinkit import BlinkitProvider
from app.providers.zepto import ZeptoProvider

async def main():
    print("=== Blinkit ===")
    blinkit = BlinkitProvider()
    blinkit_results = await blinkit.search("milk", "560001")
    print(f"Found {len(blinkit_results)} products")
    for r in blinkit_results:
        print(f"{r.product_name} | {r.unit} | ₹{r.price} | In stock: {r.in_stock}")

    print("\n=== Zepto ===")
    zepto = ZeptoProvider()
    zepto_results = await zepto.search("milk", "560001")
    print(f"Found {len(zepto_results)} products")
    for r in zepto_results:
        print(f"{r.product_name} | {r.unit} | ₹{r.price} | In stock: {r.in_stock}")

if __name__ == "__main__":
    asyncio.run(main())