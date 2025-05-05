from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from database import Base, engine
from routers import auth_router, experiments_router, upload_router, profile_router


# Initialize tables
Base.metadata.create_all(bind=engine)

# FastAPI app setup
app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["Content-Disposition"],
)

# Register routers
app.include_router(auth_router.router)
app.include_router(experiments_router.router)
app.include_router(upload_router.router)
app.include_router(profile_router.router)
