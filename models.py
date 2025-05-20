from sqlalchemy import Column, Integer, String, Float, ForeignKey, DateTime, Text
from sqlalchemy.orm import relationship
from datetime import datetime
from database import Base
from sqlalchemy.sql import func

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    email = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    api_key = Column(String, unique=True, index=True)
    experiments = relationship("Experiment", back_populates="owner")
    projects = relationship("Project", back_populates="owner")

class Project(Base):
    __tablename__ = "projects"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    description = Column(Text)
    user_id = Column(Integer, ForeignKey("users.id"))
    created_at = Column(DateTime, default=func.now())

    owner = relationship("User", back_populates="projects")
    experiments = relationship("Experiment", back_populates="project", cascade="all, delete")


class Experiment(Base):
    __tablename__ = "experiments"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    description = Column(Text)
    user_id = Column(Integer, ForeignKey("users.id"))
    created_at = Column(DateTime, default=func.now())

    owner = relationship("User", back_populates="experiments")
    metrics = relationship("Metric", back_populates="experiment", cascade="all, delete")
    model = relationship("ModelFile", back_populates="experiment", uselist=False, cascade="all, delete")
    project_id = Column(Integer, ForeignKey("projects.id"))
    project = relationship("Project", back_populates="experiments")

class Metric(Base):
    __tablename__ = "metrics"
    id = Column(Integer, primary_key=True, index=True)
    experiment_id = Column(Integer, ForeignKey("experiments.id"))
    epoch = Column(Integer)
    accuracy = Column(Float)
    precision = Column(Float)
    recall = Column(Float)
    loss = Column(Float)
    timestamp = Column(DateTime, default=func.now())
    experiment = relationship("Experiment", back_populates="metrics")



class ModelFile(Base):
    __tablename__ = "model_files"
    id = Column(Integer, primary_key=True, index=True)
    experiment_id = Column(Integer, ForeignKey("experiments.id"))
    file_path = Column(String)
    uploaded_at = Column(DateTime, default=datetime.utcnow)
    experiment = relationship("Experiment", back_populates="model")
