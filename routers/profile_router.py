from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from database import get_db
from models import User, Experiment, Metric, ModelFile
from auth import get_current_user

router = APIRouter(tags=["Profile"])

@router.get("/profile")
def get_profile(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    experiments = db.query(Experiment).filter(Experiment.user_id == current_user.id).all()

    experiment_ids = [exp.id for exp in experiments]
    metrics = db.query(Metric).filter(Metric.experiment_id.in_(experiment_ids)).all()
    models = db.query(ModelFile).filter(ModelFile.experiment_id.in_(experiment_ids)).all()

    # Aggregate metrics by experiment
    metric_summary = {}
    for m in metrics:
        metric_summary.setdefault(m.experiment_id, []).append(m)

    chart_data = []
    for exp in experiments:
        m_list = metric_summary.get(exp.id, [])
        if m_list:
            avg_accuracy = sum(m.accuracy for m in m_list) / len(m_list)
            chart_data.append({
                "experiment": exp.name,
                "accuracy": round(avg_accuracy, 3)
            })

    return {
        "username": current_user.username,
        "email": current_user.email,
        "stats": {
            "experimentCount": len(experiments),
            "modelCount": len(models),
            "metricCount": len(metrics),
        },
        "experiment_metrics": chart_data
    }
