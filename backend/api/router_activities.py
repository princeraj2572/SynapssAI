from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional
from db.session import get_db
from models.activity import Activity

router = APIRouter(prefix="/api/activities", tags=["activities"])


class ActivityCreateRequest(BaseModel):
    name: str
    category: Optional[str] = "general"
    unit: Optional[str] = "count"
    target_value: Optional[float] = None
    description: Optional[str] = None


@router.get("")
def list_activities(db: Session = Depends(get_db)):
    activities = db.query(Activity).order_by(Activity.category, Activity.name).all()
    return [
        {"id": a.id, "name": a.name, "category": a.category,
         "unit": a.unit, "target_value": a.target_value, "description": a.description}
        for a in activities
    ]


@router.post("")
def create_activity(req: ActivityCreateRequest, db: Session = Depends(get_db)):
    existing = db.query(Activity).filter(Activity.name == req.name).first()
    if existing:
        raise HTTPException(status_code=400, detail=f"Activity '{req.name}' already exists")
    activity = Activity(**req.dict())
    db.add(activity)
    db.commit()
    db.refresh(activity)
    return {"status": "created", "id": activity.id, "name": activity.name}


@router.delete("/{activity_id}")
def delete_activity(activity_id: int, db: Session = Depends(get_db)):
    activity = db.query(Activity).filter(Activity.id == activity_id).first()
    if not activity:
        raise HTTPException(status_code=404, detail="Activity not found")
    db.delete(activity)
    db.commit()
    return {"status": "deleted"}
