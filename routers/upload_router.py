from fastapi import Query, APIRouter, Depends, HTTPException, UploadFile, File, Header
from sqlalchemy.orm import Session
from database import get_db
from models import User, Experiment, Metric, ModelFile, Project, ResourceUsage
import shutil, os
import random


router = APIRouter(tags=["Uploads"])

adjectives = [
    "brave", "calm", "eager", "fancy", "glad", "jolly", "kind", "lucky", "mighty", "noble",
    "quick", "silly", "tiny", "witty", "zesty", "shy", "snappy", "quirky", "breezy", "cheery",
    "dizzy", "feisty", "goofy", "grumpy", "jazzy", "lofty", "peppy", "sassy", "spunky", "zany",
    "swift", "gentle", "bold", "chirpy", "dandy", "fuzzy", "happy", "jumpy", "nifty", "plucky"
]

nouns = [
    "panda", "cobra", "sunflower", "rocket", "otter", "cactus", "falcon", "lemon", "moon", "nimbus",
    "python", "swan", "wave", "cloud", "eagle", "comet", "giraffe", "hedgehog", "iguana", "jaguar",
    "kitten", "llama", "mango", "nebula", "orca", "pebble", "quokka", "raccoon", "sakura", "toucan",
    "urchin", "violet", "walrus", "xenon", "yak", "zebra", "badger", "cherry", "dragon", "ember"
]

def generate_human_readable_name():
    return f"{random.choice(adjectives)}-{random.choice(nouns)}"

def get_user_by_api_key(db: Session, api_key: str):
    return db.query(User).filter(User.api_key == api_key).first()

@router.post("/projects")
def create_project(name: str, description: str, x_api_key: str = Header(...), db: Session = Depends(get_db)):
    user = get_user_by_api_key(db, x_api_key)
    if not user:
        raise HTTPException(status_code=403, detail="Invalid API Key")
    project = Project(name=name, description=description, owner=user)
    db.add(project)
    db.commit()
    db.refresh(project)
    return {"project_id": project.id}

@router.post("/experiments")
def create_experiment(project_id: int, description: str, x_api_key: str = Header(...), db: Session = Depends(get_db)):
    user = get_user_by_api_key(db, x_api_key)
    if not user:
        raise HTTPException(status_code=403, detail="Invalid API Key")
    experiment = Experiment(name=generate_human_readable_name(), description=description, owner=user, project_id=project_id)
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


@router.post("/resource-usage")
def add_resource_usage(
        experiment_id: int,
        epoch: int,
        cpu_percent: float = Query(None, alias="cpu_usage_percent"),
        memory_used_mb: float = Query(None, alias="memory_usage_mb"),
        gpu_percent: float = Query(None, alias="gpu_usage_percent"),
        gpu_memory_used_mb: float = Query(None, alias="gpu_memory_usage_mb"),
        training_time_sec: float = Query(None),
        x_api_key: str = Header(...),
        db: Session = Depends(get_db)
):
    user = get_user_by_api_key(db, x_api_key)

    experiment = db.query(Experiment).filter_by(id=experiment_id, user_id=user.id).first()
    if not experiment:
        raise HTTPException(status_code=404, detail="Experiment not found")

    resource = ResourceUsage(
        experiment_id=experiment_id,
        epoch=epoch,
        cpu_usage_percent=cpu_percent,
        memory_usage_mb=memory_used_mb,
        gpu_usage_percent=gpu_percent,
        gpu_memory_usage_mb=gpu_memory_used_mb,
        training_time_sec=training_time_sec
    )
    db.add(resource)
    db.commit()
    return {"status": "resource usage added"}
@router.post("/upload_model")
def upload_model(experiment_id: int, file: UploadFile = File(...), x_api_key: str = Header(...),
                 db: Session = Depends(get_db)):
    user = get_user_by_api_key(db, x_api_key)
    experiment = db.query(Experiment).filter_by(id=experiment_id, user_id=user.id).first()
    if not experiment:
        raise HTTPException(status_code=404, detail="Experiment not found")

    file_location = f"models/{experiment_id}_{file.filename}"
    # Extract the directory part of the file path
    directory = os.path.dirname(file_location)

    # Create the directory (and all intermediate directories) if they don't exist
    os.makedirs(directory, exist_ok=True)

    with open(file_location, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    model_file = ModelFile(experiment_id=experiment_id, file_path=file_location)
    db.add(model_file)
    db.commit()
    return {"status": "model uploaded"}

