from typing import List

from fastapi import Depends, FastAPI, HTTPException
from sqlalchemy.orm import Session
from typing import Optional
from sql_app import crud, models, schemas
from sql_app.database import SessionLocal, engine

models.Base.metadata.create_all(bind=engine)

app = FastAPI()


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


@app.post("/users/", response_model=schemas.User)
def create_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
    db_user = crud.get_user_by_email(db, email=user.email)
    if db_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    return crud.create_user(db=db, user=user)


@app.get("/users/{user_id}", response_model=schemas.User)
def read_user(user_id: int, db: Session = Depends(get_db)):
    db_user = crud.get_user(db, user_id=user_id)
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return db_user


@app.post("/users/{user_id}/tasks/", response_model=schemas.Task)
def create_task_for_user(
    user_id: int, task: schemas.TaskCreate, db: Session = Depends(get_db)
):
    return crud.create_user_task(db=db, task=task, user_id=user_id)


@app.get("/tasks/", response_model=List[schemas.Task])
async def read_tasks(owner_id: int, db: Session = Depends(get_db)):
    tasks = crud.get_tasks_by_user(db, owner_id=owner_id)
    return tasks



