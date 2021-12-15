from fastapi.security import HTTPAuthorizationCredentials
from .auth import security_authorization
from fastapi import Security, Depends
from sqlalchemy.orm import Session
from .jwt import decode_token
from .. import crud
from ..database import SessionLocal


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def get_user(authorization: HTTPAuthorizationCredentials = Security(security_authorization),
             db: Session = Depends(get_db)):
    data = decode_token(authorization.credentials)
    user = crud.get_user_by_email(db, email=data['user_email'])
    return user.id
