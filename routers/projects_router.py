from fastapi import Depends, HTTPException
from sqlalchemy.orm import Session
from models import Project
from database import get_db
from auth import get_current_user  # Assuming this returns a User
from models import User
from fastapi import APIRouter

router = APIRouter(tags=["Projects"])


@router.get("/projects")
def get_projects(current_user: User = Depends(get_current_user)):
    return current_user.projects
