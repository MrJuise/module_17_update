from fastapi import APIRouter, Depends, status, HTTPException
# Сессия БД
from sqlalchemy.orm import Session
# Функция подключения к БД
from app.backend.db_depends import get_db
# Аннотации, Модели БД и Pydantic.
from typing import Annotated
from app.models import User, Task
from app.schemas import CreateUser, UpdateUser
# Функции работы с записями.
from sqlalchemy import insert, select, update, delete
# Функция создания slug-строки
from slugify import slugify


router = APIRouter(prefix="/user", tags=["user"])


@router.get("/")
async def all_users(db: Annotated[Session, Depends(get_db)]):
    users = db.scalars(select(User)).all()
    return users


@router.get("/{user_id}")
async def user_by_id(user_id: int, db: Annotated[Session, Depends(get_db)]):
    user = db.scalar(select(User).where(User.id == user_id))
    if user is None:
        raise HTTPException(status_code=404, detail="User was not found")
    return user


@router.get("/user_id/tasks")
async def tasks_by_user_id(db: Annotated[Session, Depends(get_db)], user_id: int):
    tasks = db.scalars(select(Task).where(Task.user_id == user_id)).all()
    if tasks is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='Tasks was not found'
        )
    return tasks


@router.post("/create")
async def create_user(user: CreateUser, db: Annotated[Session, Depends(get_db)]):
    slug = slugify(user.username) or "default-slug"
    new_user = User(
        username=user.username,
        firstname=user.firstname,
        lastname=user.lastname,
        age=user.age,
        slug=slug
    )
    db.execute(
        insert(User).values(
            username=new_user.username,
            firstname=new_user.firstname,
            lastname=new_user.lastname,
            age=new_user.age,
            slug=new_user.slug
        )
    )
    db.commit()
    return {"status_code": status.HTTP_201_CREATED, "transaction": "Successful"}


@router.put("/update/{id}")
async def update_user(user_id: int, user: UpdateUser, db: Annotated[Session, Depends(get_db)]):
    existing_user = db.scalars(select(User).where(User.id == user_id)).first()
    if existing_user:
        db.execute(
            update(User).where(User.id == user_id).values(
                firstname=user.firstname,
                lastname=user.lastname,
                age=user.age,
            )
        )
        db.commit()
        return {"status_code": status.HTTP_200_OK, "transaction": "User update is successful!"}
    else:
        raise HTTPException(status_code=404, detail="User was not found")


@router.delete("/delete/{id}")
async def delete_user(user_id: int, db: Annotated[Session, Depends(get_db)]):
    existing_user = db.scalar(select(User).where(User.id == user_id))
    if existing_user:
        db.execute(delete(User).where(User.id == user_id))
        db.execute(delete(Task).where(Task.user_id == user_id))
        db.commit()
        return {"status_code": status.HTTP_200_OK, "transaction": "User delete is successful!"}
    else:
        raise HTTPException(status_code=404, detail="User was not found")
