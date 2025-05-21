from database import get_db
from auth import get_current_user  # Assuming this returns a User
from models import User, Project, Experiment
from fastapi import APIRouter, Depends, HTTPException, Response
from sqlalchemy.orm import Session
from weasyprint import HTML
from jinja2 import Template
from datetime import datetime
import matplotlib.pyplot as plt
import matplotlib
import os
from pathlib import Path

matplotlib.use("Agg")
router = APIRouter(tags=["Projects"])

@router.get("/projects")
def get_projects(current_user: User = Depends(get_current_user)):
    return current_user.projects


def generate_chart(metric_name, values, names, output_dir="C:/tmp"):
    # Ensure directory exists
    os.makedirs("C:/tmp", exist_ok=True)


    plt.figure(figsize=(6, 4))
    bars = plt.bar(names, values, color="#4c72b0")
    plt.title(f"{metric_name} of Top 5 Experiments")
    plt.ylabel(metric_name)
    plt.xticks(rotation=45, ha='right')
    for bar in bars:
        yval = bar.get_height()
        plt.text(bar.get_x() + bar.get_width()/2.0, yval, f'{yval:.2f}', va='bottom', ha='center', fontsize=8)
    file_path = os.path.join(output_dir, f"{metric_name.lower()}_chart.png")
    plt.tight_layout()
    plt.savefig(file_path)
    plt.close()

    # ✅ This returns a properly formatted `file:///C:/...` URI
    return Path(file_path).as_uri()

def generate_metric_line_chart(metric_name, experiments, output_dir="C:/tmp"):
    os.makedirs(output_dir, exist_ok=True)
    plt.figure(figsize=(8, 5))

    for exp in experiments:
        sorted_metrics = sorted(exp.metrics, key=lambda m: m.epoch)
        epochs = [m.epoch for m in sorted_metrics]
        values = [getattr(m, metric_name.lower()) for m in sorted_metrics]
        plt.plot(epochs, values, label=exp.name, marker='o')

    plt.xlabel("Epoch")
    plt.ylabel(metric_name)
    plt.title(f"{metric_name} over Epochs")
    plt.legend()
    plt.grid(True)
    plt.tight_layout()

    file_path = os.path.join(output_dir, f"{metric_name.lower()}_line_chart.png")
    plt.savefig(file_path)
    plt.close()
    return Path(file_path).as_uri()


@router.get("/projects/{project_id}/report", response_class=Response)
def generate_project_report(project_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    # Verify project access
    project = db.query(Project).filter(Project.id == project_id, Project.user_id == current_user.id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    # Fetch experiments
    experiments = db.query(Experiment).filter(
        Experiment.project_id == project.id,
        Experiment.user_id == current_user.id
    ).all()

    if not experiments:
        raise HTTPException(status_code=404, detail="No experiments found for this project")

    # Compute stats
    data = []
    for exp in experiments:
        metrics = sorted(exp.metrics, key=lambda m: m.epoch)
        if not metrics:
            continue
        avg_accuracy = sum(m.accuracy for m in metrics) / len(metrics)
        avg_precision = sum(m.precision for m in metrics) / len(metrics)
        avg_recall = sum(m.recall for m in metrics) / len(metrics)
        final_loss = metrics[-1].loss
        data.append({
            "name": exp.name,
            "accuracy": round(avg_accuracy, 4),
            "precision": round(avg_precision, 4),
            "recall": round(avg_recall, 4),
            "loss": round(final_loss, 4)
        })

    top5_data = sorted(data, key=lambda x: x["accuracy"], reverse=True)[:5]
    top5_names = [d["name"] for d in top5_data]
    top5_experiments = [e for e in experiments if e.name in top5_names]

    # Summary
    total = len(data)
    avg_acc = round(sum(d["accuracy"] for d in data) / total, 4)
    avg_recall = round(sum(d["recall"] for d in data) / total, 4)
    best_acc = max(d["accuracy"] for d in data)
    best_recall = max(d["recall"] for d in data)

    # Bar Charts
    acc_path = generate_chart("Accuracy", [d["accuracy"] for d in top5_data], top5_names)
    rec_path = generate_chart("Recall", [d["recall"] for d in top5_data], top5_names)
    prec_path = generate_chart("Precision", [d["precision"] for d in top5_data], top5_names)

    # Line Charts (metric-specific)
    acc_line_path = generate_metric_line_chart("Accuracy", top5_experiments)
    prec_line_path = generate_metric_line_chart("Precision", top5_experiments)
    rec_line_path = generate_metric_line_chart("Recall", top5_experiments)
    loss_line_path = generate_metric_line_chart("Loss", top5_experiments)

    # Template
    template_str = """
    <html><head><style>
        body { font-family: Arial, sans-serif; padding: 30px; }
        h1, h2 { color: #2e6c80; }
        table { border-collapse: collapse; width: 100%; margin: 20px 0; }
        th, td { border: 1px solid #ccc; padding: 8px; text-align: center; }
        th { background-color: #f0f0f0; }
        img { max-width: 100%; height: auto; margin-bottom: 20px; }
    </style></head><body>
        <h1>Project Report</h1>
        <p><strong>Generated on:</strong> {{ date }}</p>
        <h2>User Info</h2>
        <p><strong>Username:</strong> {{ user.username }}</p>
        <p><strong>Email:</strong> {{ user.email }}</p>
        <h2>Summary</h2>
        <p><strong>Total Experiments:</strong> {{ summary.total }}</p>
        <p><strong>Best Accuracy:</strong> {{ summary.best_acc }}</p>
        <p><strong>Best Recall:</strong> {{ summary.best_recall }}</p>
        <p><strong>Avg Accuracy:</strong> {{ summary.avg_acc }}</p>
        <p><strong>Avg Recall:</strong> {{ summary.avg_recall }}</p>

        <h2>Top 5 Experiments</h2>
        <table>
            <tr><th>Name</th><th>Accuracy</th><th>Precision</th><th>Recall</th><th>Loss</th></tr>
            {% for e in experiments %}
            <tr><td>{{ e.name }}</td><td>{{ e.accuracy }}</td><td>{{ e.precision }}</td><td>{{ e.recall }}</td><td>{{ e.loss }}</td></tr>
            {% endfor %}
        </table>

        <h2>Bar Charts</h2>
        <h3>Accuracy</h3><img src="{{ acc_chart }}">
        <h3>Recall</h3><img src="{{ rec_chart }}">
        <h3>Precision</h3><img src="{{ prec_chart }}">

        <h2>Line Charts</h2>
        <h3>Accuracy over Epochs</h3><img src="{{ acc_line }}">
        <h3>Precision over Epochs</h3><img src="{{ prec_line }}">
        <h3>Recall over Epochs</h3><img src="{{ rec_line }}">
        <h3>Loss over Epochs</h3><img src="{{ loss_line }}">
    </body></html>
    """

    html = Template(template_str).render(
        date=datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S UTC"),
        user={"username": current_user.username, "email": current_user.email},
        experiments=top5_data,
        summary={
            "total": total,
            "best_acc": best_acc,
            "best_recall": best_recall,
            "avg_acc": avg_acc,
            "avg_recall": avg_recall,
        },
        acc_chart=acc_path,
        rec_chart=rec_path,
        prec_chart=prec_path,
        acc_line=acc_line_path,
        prec_line=prec_line_path,
        rec_line=rec_line_path,
        loss_line=loss_line_path
    )

    pdf_bytes = HTML(string=html, base_url="/").write_pdf()

    return Response(content=pdf_bytes, media_type="application/pdf", headers={
        "Content-Disposition": f"attachment; filename=project_{project_id}_report.pdf"
    })
