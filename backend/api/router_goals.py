from fastapi import APIRouter
router = APIRouter()

@router.get("/goals")
async def get_goals():
    return {"goals": []}
