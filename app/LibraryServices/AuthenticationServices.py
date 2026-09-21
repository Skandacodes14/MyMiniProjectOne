from datetime import datetime, timezone, timedelta
import jwt
from app.DataBaseModels import UserRecordDB
from app.SystemConfiguration import settings, UserRoles, ResponseMessages
from typing import Optional
import bcrypt
from sqlalchemy.orm import Session
from fastapi import Depends, HTTPException, status
from app.DataBaseConnectionInfra import oauth2_scheme, get_db


def get_password_hashed(raw_password: str) -> str:
    password_bytes = raw_password.encode('utf-8')[:72]
    salt = bcrypt.gensalt()
    return bcrypt.hashpw(password_bytes, salt).decode('utf-8')

def verify_password(raw_password: str, hashed_password: str) -> bool:
    password_bytes = raw_password.encode('utf-8')[:72]
    return bcrypt.checkpw(password_bytes, hashed_password.encode('utf-8'))

def generate_access_token(data: dict) -> str:
    # here the method takes a copy of the input data and updates its expir time, then signs and encodes the copy data
    copy_of_data = data.copy()
    current_time = datetime.now(timezone.utc)
    expiration_time = current_time + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    copy_of_data.update({"exp": expiration_time})
    return jwt.encode(copy_of_data, settings.SECRET_KEY, algorithm=settings.ALGORITHM)

def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)) -> type[UserRecordDB]:
    unauthorized_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail=ResponseMessages.UNAUTHORIZED, # FIXED
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        user_identifier: Optional[str] = payload.get("sub")
        if user_identifier is None:
            raise unauthorized_exception
    except jwt.PyJWTError:
        raise unauthorized_exception

    user = db.query(UserRecordDB).filter(UserRecordDB.username == user_identifier).first()
    if user is None:
        raise unauthorized_exception
    return user

def get_current_admin_user(current_user: UserRecordDB = Depends(get_current_user)) -> UserRecordDB:
    if current_user.role != UserRoles.ADMIN.value: # FIXED
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=ResponseMessages.INVALID_OPERATION, # FIXED
        )
    return current_user