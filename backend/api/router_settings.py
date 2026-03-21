from fastapi import APIRouter
router = APIRouter()

@router.get("/settings")
async def get_settings():
    return {"timezone": "Asia/Kolkata", "version": "0.1.0"}
