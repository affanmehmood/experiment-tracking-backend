from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database import get_db
from auth import get_current_user
from models import Experiment, User, ModelFile
from fastapi.responses import FileResponse
import os

router = APIRouter(tags=["Dashboard"])


@router.get("/projects/{project_id}/experiments")
def get_user_experiments(project_id: int, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    experiments = db.query(Experiment).filter(
        Experiment.user_id == current_user.id,
        Experiment.project_id == project_id
    ).all()
    return experiments

@router.delete("/experiments/{experiment_id}")
def delete_experiment(experiment_id: int, current_user: User = Depends(get_current_user),
                      db: Session = Depends(get_db)):
    experiment = db.query(Experiment).filter_by(id=experiment_id, user_id=current_user.id).first()
    if not experiment:
        raise HTTPException(status_code=404, detail="Experiment not found")
    db.delete(experiment)
    db.commit()
    return {"status": "experiment deleted"}


@router.get("/experiments/{experiment_id}/metrics")
def get_experiment_metrics(experiment_id: int, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    experiment = db.query(Experiment).filter(Experiment.id == experiment_id, Experiment.user_id == current_user.id,).first()
    if not experiment:
        raise HTTPException(status_code=404, detail="Experiment not found in this project")
    return experiment.metrics


@router.get("/experiments/{experiment_id}/metrics/last")
def get_last_epoch_metrics(
    experiment_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    experiment = db.query(Experiment).filter(
        Experiment.id == experiment_id,
        Experiment.user_id == current_user.id
    ).first()

    if not experiment:
        raise HTTPException(status_code=404, detail="Experiment not found in this project")

    if not experiment.metrics or len(experiment.metrics) == 0:
        raise HTTPException(status_code=404, detail="No metrics found for this experiment")

    # Ensure we get the metric for the last epoch
    last_metric = max(experiment.metrics, key=lambda m: m.epoch)
    return {
        "epoch": last_metric.epoch,
        "accuracy": last_metric.accuracy,
        "f1": 2 * (last_metric.precision * last_metric.recall) / (last_metric.precision + last_metric.recall + 1e-8),  # avoid division by zero
        "precision": last_metric.precision,
        "recall": last_metric.recall,
        "loss": last_metric.loss,
        "timestamp": last_metric.timestamp
    }


@router.get("/experiments/{experiment_id}/model")
def download_model_file(
    experiment_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    experiment = db.query(Experiment).filter_by(id=experiment_id, user_id=current_user.id).first()
    if not experiment:
        raise HTTPException(status_code=404, detail="Experiment not found")

    model_file = db.query(ModelFile).filter_by(experiment_id=experiment_id).first()
    if not model_file or not os.path.exists(model_file.file_path):
        raise HTTPException(status_code=404, detail="Model file not found")

    return FileResponse(
        path=model_file.file_path,
        filename=os.path.basename(model_file.file_path),
        media_type='application/octet-stream'
    )

@router.get("/experiments/{experiment_id}/resource-usage")
def get_resource_usage(
    experiment_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    experiment = db.query(Experiment).filter(
        Experiment.id == experiment_id,
        Experiment.user_id == current_user.id
    ).first()

    if not experiment:
        raise HTTPException(status_code=404, detail="Experiment not found")

    return experiment.resource_usages  # Assuming a relationship is defined

# username: affan
# password: pass
# api_key: b9a89c8f-b364-4ae6-9987-3c083b48e9cc
# access_token: eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxIiwiZXhwIjoxNzQzNDM4MzUyfQ.nplyKKRmrogYY0b1BANDXBkxAvSORglycXWgwsey-O8
