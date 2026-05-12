from fastapi import APIRouter
from app.services.aggregator import AggregatorService

router = APIRouter()
aggregator = AggregatorService()


@router.get("/search")
async def search(query: str, pincode: str = "560001"):
    results = await aggregator.search(query, pincode)

    return [r.__dict__ for r in results]