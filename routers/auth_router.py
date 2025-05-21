from fastapi import APIRouter, Depends, HTTPException, Form, Request
from sqlalchemy.orm import Session
import uuid
from database import get_db
from models import User
from auth import get_password_hash, verify_password, create_access_token, SECRET_KEY, ALGORITHM
from fastapi.security import OAuth2PasswordRequestForm
from fastapi.security import HTTPBearer
from jose import JWTError, jwt
security = HTTPBearer()
router = APIRouter(tags=["Auth"])


@router.post("/register")
def register_user(username: str = Form(...), email: str = Form(...), password: str = Form(...),
                  db: Session = Depends(get_db)):
    hashed_pw = get_password_hash(password)
    api_key = str(uuid.uuid4())
    user = User(username=username, email=email, hashed_password=hashed_pw, api_key=api_key)
    db.add(user)
    db.commit()
    db.refresh(user)
    return {"api_key": user.api_key, "user_id": user.id}


@router.post("/token")
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = db.query(User).filter(User.username == form_data.username).first()
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(status_code=400, detail="Invalid credentials")
    access_token = create_access_token(data={"sub": str(user.id)})
    return {"access_token": access_token, "token_type": "bearer"}

@router.get("/validate-token")
def validate_token(token: str = Depends(security)):
    try:
        payload = jwt.decode(token.credentials, SECRET_KEY, algorithms=[ALGORITHM])
        return {"valid": True}
    except JWTError:
        raise HTTPException(status_code=401, detail="Token expired or invalid")
