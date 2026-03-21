from fastapi import APIRouter
router = APIRouter()

@router.get("/digest/weekly")
async def get_weekly_digest():
    # TODO Phase 9
    return {"digest": "Weekly digest not yet available."}
