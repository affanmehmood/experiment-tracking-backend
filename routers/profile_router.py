from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from database import get_db
from models import User, Experiment, Metric, ModelFile, Project
from auth import get_current_user

router = APIRouter(tags=["Profile"])

@router.get("/profile")
def get_profile(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    experiments = db.query(Experiment).filter(Experiment.user_id == current_user.id).all()
    experiment_ids = [exp.id for exp in experiments]

    metrics = db.query(Metric).filter(Metric.experiment_id.in_(experiment_ids)).all()
    models = db.query(ModelFile).filter(ModelFile.experiment_id.in_(experiment_ids)).all()
    projects = db.query(Project).filter(Project.user_id == current_user.id).all()

    # Aggregate metrics by experiment
    metric_summary_by_experiment = {}
    for m in metrics:
        metric_summary_by_experiment.setdefault(m.experiment_id, []).append(m)

    experiment_metrics = []
    for exp in experiments:
        m_list = metric_summary_by_experiment.get(exp.id, [])
        if m_list:
            avg_accuracy = sum(m.accuracy for m in m_list) / len(m_list)
            experiment_metrics.append({
                "experiment": exp.name,
                "accuracy": round(avg_accuracy, 3)
            })

    # Aggregate metrics by project
    project_summary = {}
    for exp in experiments:
        if exp.project_id:
            project_summary.setdefault(exp.project_id, []).append(exp.id)

    project_metrics = []
    for project in projects:
        exp_ids = project_summary.get(project.id, [])
        all_project_metrics = [m for m in metrics if m.experiment_id in exp_ids]
        if all_project_metrics:
            avg_accuracy = sum(m.accuracy for m in all_project_metrics) / len(all_project_metrics)
            project_metrics.append({
                "project": project.name,
                "accuracy": round(avg_accuracy, 3)
            })

    return {
        "username": current_user.username,
        "email": current_user.email,
        "api_key": current_user.api_key,
        "stats": {
            "experimentCount": len(experiments),
            "modelCount": len(models),
            "metricCount": len(metrics),
            "projectCount": len(projects),
        },
        "experiment_metrics": experiment_metrics,
        "project_metrics": project_metrics,
    }
