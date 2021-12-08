from typing import List
import time
import jwt
from fastapi import Depends, FastAPI, HTTPException, Request, Security
from sqlalchemy.orm import Session
from typing import Optional

from starlette.status import HTTP_403_FORBIDDEN

from sql_app import crud, models, schemas
from sql_app.database import SessionLocal, engine
from fastapi.security import APIKeyHeader, HTTPAuthorizationCredentials
from fastapi.security.utils import get_authorization_scheme_param


models.Base.metadata.create_all(bind=engine)

app = FastAPI()
jwt_secret = '336215407d0ca400fecdf873c090345accd53ce976e705f8ed6a71492c8394c2'
jwt_algorithm = 'HS256'

user25 = 'eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJ1c2VyX2lkIjoidXNlcjI1QGV4YW1wbGUuY29tIiwiZXhwaXJlcyI6MTYzODg5NjIxMS4xMTk4NTczfQ.eG3AXiw1Fy7K6buTSkSz_H5VQyJL96kDD0t3mCEz7FY'


@app.get("/")
async def home():
    return {"message": "To do shnik"}


# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def create_access_token(user_email: str):
    payload = {
        "user_email": user_email,
        "expires": time.time() + 6000
    }
    encoded_token = jwt.encode(payload, jwt_secret, algorithm=jwt_algorithm)
    return {
        "access_token": encoded_token
    }


def decode_token(encoded_token: str):
    try:
        decoded_token = jwt.decode(encoded_token, jwt_secret, algorithms=[jwt_algorithm])
        return decoded_token if decoded_token["expires"] >= time.time() else None
    except:
        return {}


class TokenAPIKeyHeader(APIKeyHeader):
    async def __call__(self, request: Request) -> Optional[HTTPAuthorizationCredentials]:
        authorization: str = request.headers.get("Authorization")
        scheme, credentials = get_authorization_scheme_param(authorization)
        if not (authorization and scheme and credentials):
            if self.auto_error:
                raise HTTPException(status_code=HTTP_403_FORBIDDEN, detail="Not authenticated")
            else:
                return None
        if scheme.lower() != "jwt":
            if self.auto_error:
                raise HTTPException(
                    status_code=HTTP_403_FORBIDDEN,
                    detail="Invalid authentication credentials",
                )
            else:
                return None
        return HTTPAuthorizationCredentials(scheme=scheme, credentials=credentials)


security_authorization = TokenAPIKeyHeader(name="Authorization")


def get_user(authorization: HTTPAuthorizationCredentials = Security(security_authorization),
             db: Session = Depends(get_db)):
    data = decode_token(authorization.credentials)
    user = crud.get_user_by_email(db, email=data['user_email'])
    return user.id


@app.post("/create_task/", response_model=schemas.Task)
def create_task_for_user(task: schemas.TaskCreate, db: Session = Depends(get_db), user_id: int = Depends(get_user)):
    return crud.create_user_task(db=db, task=task, user_id=user_id)


@app.get("/user_profile/", response_model=schemas.User)
def read_user(user_id: int = Depends(get_user), db: Session = Depends(get_db)):
    db_user = crud.get_user(db, user_id=user_id)
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return db_user


@app.get("/tasks/", response_model=List[schemas.Task])
async def read_tasks(owner_id: int = Depends(get_user), db: Session = Depends(get_db)):
    tasks = crud.get_tasks_by_user(db, owner_id=owner_id)
    return tasks


@app.post("/user/signup", tags=["user"])
async def create_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
    db_user = crud.get_user_by_email(db, email=user.email)
    if db_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    return crud.create_user(db=db, user=user), create_access_token(user.email)


@app.post("/user/login", tags=["user"])
def user_login(user: schemas.UserLogin, db: Session = Depends(get_db)):
    fake_hashed_password = user.password + "notreallyhashed"
    check_user = crud.get_user_by_email_and_pass(db, email=user.email, password=fake_hashed_password)
    if check_user is None:
        raise HTTPException(status_code=400, detail="User not found")
    if check_user:
        if check_user.email == user.email and check_user.hashed_password == fake_hashed_password:
            return create_access_token(user.email)
    return {"Error": "Wrong login details"}



