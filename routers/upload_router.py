from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Header
from sqlalchemy.orm import Session
from database import get_db
from models import User, Experiment, Metric, ModelFile
import uuid, shutil


router = APIRouter(tags=["Uploads"])


def get_user_by_api_key(db: Session, api_key: str):
    return db.query(User).filter(User.api_key == api_key).first()


@router.post("/experiments")
def create_experiment(name: str, description: str, x_api_key: str = Header(...), db: Session = Depends(get_db)):
    user = get_user_by_api_key(db, x_api_key)
    if not user:
        raise HTTPException(status_code=403, detail="Invalid API Key")
    experiment = Experiment(name=name, description=description, owner=user)
    db.add(experiment)
    db.commit()
    db.refresh(experiment)
    return {"experiment_id": experiment.id}


@router.post("/metrics")
def add_metric(experiment_id: int, epoch: int, accuracy: float, precision: float, recall: float, loss: float,
               x_api_key: str = Header(...), db: Session = Depends(get_db)):
    user = get_user_by_api_key(db, x_api_key)
    experiment = db.query(Experiment).filter_by(id=experiment_id, user_id=user.id).first()
    if not experiment:
        raise HTTPException(status_code=404, detail="Experiment not found")
    metric = Metric(experiment_id=experiment_id, epoch=epoch, accuracy=accuracy, precision=precision, recall=recall,
                    loss=loss)
    db.add(metric)
    db.commit()
    return {"status": "metric added"}


@router.post("/upload_model")
def upload_model(experiment_id: int, file: UploadFile = File(...), x_api_key: str = Header(...),
                 db: Session = Depends(get_db)):
    user = get_user_by_api_key(db, x_api_key)
    experiment = db.query(Experiment).filter_by(id=experiment_id, user_id=user.id).first()
    if not experiment:
        raise HTTPException(status_code=404, detail="Experiment not found")
    file_location = f"models/{experiment_id}_{file.filename}"
    with open(file_location, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    model_file = ModelFile(experiment_id=experiment_id, file_path=file_location)
    db.add(model_file)
    db.commit()
    return {"status": "model uploaded"}

