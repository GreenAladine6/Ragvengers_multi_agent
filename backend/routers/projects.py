from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
import database, models, schemas, crud, auth

router = APIRouter(tags=["Projects"])

@router.post("/projects/", response_model=schemas.Project)
def create_project(project: schemas.ProjectCreate, db: Session = Depends(database.get_db), current_user = Depends(auth.get_current_active_user)):
    # Add authorization check if needed
    return crud.create_project(db=db, project=project)

@router.get("/projects/", response_model=List[schemas.Project])
def read_projects(skip: int = 0, limit: int = 100, db: Session = Depends(database.get_db), current_user = Depends(auth.get_current_active_user)):
    return crud.get_projects(db, skip=skip, limit=limit)

@router.post("/feedback/", response_model=schemas.Feedback)
def create_feedback(feedback: schemas.FeedbackCreate, db: Session = Depends(database.get_db), current_user = Depends(auth.get_current_active_user)):
    return crud.create_feedback(db=db, feedback=feedback)

@router.get("/feedback/", response_model=List[schemas.Feedback])
def read_feedbacks(skip: int = 0, limit: int = 100, db: Session = Depends(database.get_db), current_user = Depends(auth.get_current_active_user)):
    return crud.get_feedbacks(db, skip=skip, limit=limit)
