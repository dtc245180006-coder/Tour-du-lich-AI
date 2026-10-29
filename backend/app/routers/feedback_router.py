from typing import List, Optional
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from backend.app.database import get_db
from backend.app import models, schemas, crud

router = APIRouter(prefix="/feedbacks", tags=["Thu thập Phản hồi & Đánh giá"])

@router.get("", response_model=List[schemas.FeedbackOut])
def list_feedbacks(
    tour_id: Optional[int] = Query(None, description="Lọc theo Tour ID"),
    sentiment: Optional[str] = Query(None, description="POSITIVE, NEUTRAL, NEGATIVE"),
    rating: Optional[int] = Query(None, description="1-5"),
    keyword: Optional[str] = Query(None, description="Tìm theo tên khách, nội dung nhận xét, tên tour"),
    db: Session = Depends(get_db)
):
    feedbacks = crud.get_feedbacks(db, tour_id=tour_id, sentiment=sentiment, rating=rating, keyword=keyword)
    results = []
    for f in feedbacks:
        f_out = schemas.FeedbackOut.model_validate(f)
        if f.tour:
            f_out.tour_title = f.tour.title
        results.append(f_out)
    return results

@router.post("", response_model=schemas.FeedbackOut)
def submit_feedback(
    fb_in: schemas.FeedbackCreate,
    db: Session = Depends(get_db)
):
    fb = crud.create_feedback(db, fb_in)
    f_out = schemas.FeedbackOut.model_validate(fb)
    if fb.tour:
        f_out.tour_title = fb.tour.title
    return f_out
