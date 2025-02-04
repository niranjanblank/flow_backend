from fastapi import APIRouter, Depends, Query, HTTPException, status
from sqlmodel import Session
from ..schemas.schemas import UserRead, UserCreate, UserReadWithBoard, Token, UserUpdate
from ..crud.user_crud import create_user, get_user_by_id, read_users, get_user_by_username, update_user
from ..database import get_session
from fastapi.security import OAuth2PasswordRequestForm
from ..auth import authenticate_user, create_access_token, get_current_active_user
from ..models.user import User

router = APIRouter()


@router.post("/users/", response_model=UserRead)
def create_user_endpoint(user: UserCreate, db: Session = Depends(get_session)):
    print(user)
    db_user = create_user(db=db, user=user)
    return db_user


@router.get("/users/{user_id}", response_model=UserReadWithBoard)
def get_user_by_userid_endpoint(user_id: int, db: Session = Depends(get_session)):
    db_user = get_user_by_id(db, user_id)
    return db_user

@router.get("/users/details/{username}", response_model=UserReadWithBoard)
def read_user_by_id(username: str, db: Session = Depends(get_session),current_user: User = Depends(get_current_active_user)):
    db_user = get_user_by_username(db, username)
    return db_user


@router.get("/users/", response_model=list[UserRead])
def read_users_endpoint(skip: int = Query(0, ge=0), limit: int = Query(10, gt=0), db: Session = Depends(get_session)):
    db_users = read_users(db, skip=skip, limit=limit)
    return db_users

@router.put("/users/update/{user_id}", response_model=UserRead)
def update_user_endpoint(user_id: int, user: UserUpdate, db: Session = Depends(get_session)):
    db_user = update_user(db, user_id, user)
    return db_user