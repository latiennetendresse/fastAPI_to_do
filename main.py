from fastapi import Depends, FastAPI, HTTPException
from sqlalchemy.orm import Session
from sql_app import models, schemas, crud
from sql_app.auth.depends import get_user, get_db
from sql_app.auth.jwt import create_access_token
from sql_app.database import engine

models.Base.metadata.create_all(bind=engine)

app = FastAPI()


@app.get("/")
async def home():
    return {"message": "To do shnik"}


@app.post("/create_task/", response_model=schemas.Task)
def create_task_for_user(task: schemas.TaskCreate, db: Session = Depends(get_db), user_id: int = Depends(get_user)):
    return crud.create_user_task(db=db, task=task, user_id=user_id)


@app.get("/user_profile/", response_model=schemas.User)
def read_user(user_id: int = Depends(get_user), db: Session = Depends(get_db)):
    db_user = crud.get_user(db, user_id=user_id)
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return db_user


@app.get("/tasks/", response_model=list[schemas.Task])
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
    return create_access_token(user.email)
