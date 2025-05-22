# 🚀 ML Insights Hub — Backend Server

This repository contains the backend server for the **ML Insights Hub** project — a platform designed for **real-time ML experiment tracking**, **model storage**, and **team collaboration**.

> 🔗 The frontend is developed in a separate repository: [banin-sensha/experiment-tracking](https://github.com/banin-sensha/experiment-tracking)

---

## ✨ Features

- **🔐 User Authentication & Authorization**
  - JWT-based login
  - API key management for programmatic access

- **📁 Project Management**
  - Create, view, and manage ML projects

- **🧪 Experiment Tracking**
  - Create/manage experiments within projects
  - Auto-generate human-readable experiment names
  - Track real-time metrics (accuracy, precision, recall, loss)
  - Monitor resource usage (CPU, memory, GPU, training time) per epoch
  - Download model files
  - Delete experiments

- **💾 Model Storage**
  - Upload and store trained model files per experiment

- **👤 User Profile & Statistics**
  - View personal experiment stats and model insights

- **📄 PDF Report Generation**
  - Generate reports with charts & top 5 experiment comparisons

- **🌐 CORS Enabled**
  - Seamless integration with frontend

---

## 🛠️ Tech Stack

- **Backend Framework**: [FastAPI](https://fastapi.tiangolo.com/)
- **Database**: PostgreSQL + SQLAlchemy ORM
- **Authentication**: `python-jose`, `passlib` (JWT & password hashing)
- **PDF & Charts**: `matplotlib`, `weasyprint`
- **Server**: `uvicorn`
- **Resource Monitoring**: `psutil` (for usage endpoints)

---

## 🗂️ Project Structure

```

.
├── alembic/                            # Alembic migration scripts
├── models/                             # Directory for ML model uploads (will be changed to s3 bucket in production)
├── routers/                            # Directory for API route modules
│   ├── auth_router.py                  # API routes for user registration, login, token validation
│   ├── experiments_router.py           # API routes for experiment operations (metrics, models, resource usage, deletion)
│   ├── profile_router.py               # API routes for user profile and statistics
│   ├── projects_router.py              # API routes for project management and PDF report generation
│   └── upload_router.py                # API routes for metrics, resource usage, and model uploads
├── .gitignore                          # Specifies intentionally untracked files to ignore by Git
├── alembic.ini                         # Alembic configuration file
├── auth.py                             # JWT authentication logic, password hashing
├── database.py                         # Database connection and session management
├── main.py                             # Main FastAPI application, CORS settings, router inclusion
├── models.py                           # SQLAlchemy models for database tables (User, Project, Experiment, Metric, ModelFile, ResourceUsage)
├── requirements.txt                    # Python dependencies
└── README.md                           # This file

```

---

## ⚙️ Setup and Installation

### 1. Clone the Repository

```bash
git clone https://github.com/affanmehmood/experiment-tracking-backend
cd experiment-tracking-backend
```

### 2. Create a Virtual Environment (Recommended)

```bash
python -m venv venv
# On macOS/Linux
source venv/bin/activate
# On Windows
venv\Scriptsctivate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Database Setup

- **Install PostgreSQL** if it's not already installed.
- **Create a database** (e.g., `ml_tracker`):

```sql
CREATE DATABASE ml_tracker;
```

- **Update `DATABASE_URL`** in `database.py`:

```python
DATABASE_URL = "postgresql://postgres:admin@localhost/ml_tracker"
```

> Replace `postgres`, `admin`, or `localhost` with your actual PostgreSQL credentials.

### 5. Run Database Migrations

> Optional – If you're not using Alembic, tables will auto-create via:

```python
Base.metadata.create_all(bind=engine)
```

> For production environments, use Alembic for managing schema migrations.

### 6. Start the FastAPI Server

```bash
uvicorn main:app --reload
```

- The server will run at: [http://127.0.0.1:8000](http://127.0.0.1:8000)
- API Docs (Swagger UI): [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)

---

## 📡 API Endpoints Summary

### 🔐 Authentication (`/auth`)

- `POST /register`: Register a new user
- `POST /token`: Obtain a JWT token
- `GET /validate-token`: Validate a token

### 📁 Projects (`/projects`)

- `POST /projects`: Create a new project *(API key required)*
- `GET /projects`: Retrieve user’s projects
- `GET /projects/{project_id}/report`: Generate PDF report for a project

### 🧪 Experiments (`/experiments`)

- `POST /experiments`: Create a new experiment *(API key required)*
- `GET /projects/{project_id}/experiments`: List experiments in a project
- `DELETE /experiments/{experiment_id}`: Delete an experiment
- `GET /experiments/{experiment_id}/metrics`: Get all metrics for an experiment
- `GET /experiments/{experiment_id}/metrics/last`: Get latest epoch metrics
- `GET /experiments/{experiment_id}/resource-usage`: Get experiment resource usage
- `GET /experiments/{experiment_id}/model`: Download the experiment’s model file

### ⬆️ Uploads (`/uploads`)

- `POST /metrics`: Add new metric data *(API key required)*
- `POST /resource-usage`: Add resource usage data *(API key required)*
- `POST /upload_model`: Upload a model file *(API key required)*

### 👤 Profile (`/profile`)

- `GET /profile`: Get user profile and statistics

---

## 🔑 Authentication Notes

### API Key
- Used for programmatic operations (e.g., script uploads)
- Sent in headers as:  
  `X-API-Key: your_api_key_here`

### JWT Token
- Used for session-based user access the dashboard
- Sent in headers as:  
  `Authorization: Bearer your_jwt_token_here`

---

