from fastapi import APIRouter, Depends, status, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from app.DataBaseConnectionInfra import get_db
from app.DataBaseSchemas import UserCreateSchema, UserResponseSchema, TokenSchema
from app.DataBaseModels import UserRecordDB
from app.LibraryServices import AuthenticationServices as auth

router = APIRouter(
    prefix="/auth",
    tags=["Authentication"],
)

@router.post(
    "/register",
    response_model=UserResponseSchema,
    status_code=status.HTTP_201_CREATED,
    summary="Register a new user",
)
def register_user(
    payload: UserCreateSchema,
    db: Session = Depends(get_db)
):
    existing_user = db.query(UserRecordDB).filter(
        UserRecordDB.username == payload.username
    ).first()
    if existing_user:
        raise HTTPException(
            status_code=400,
            detail="User already exists"
        )

    hashed_pw = auth.get_password_hashed(payload.password)

    new_user = UserRecordDB(
        username=payload.username,
        hashed_password=hashed_pw,
        role=payload.role.value if hasattr(payload.role, "value") else payload.role
    )

    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return new_user

@router.post(
    "/login",
    response_model=TokenSchema,
    status_code=status.HTTP_200_OK,
    summary="Login a user and obtain a JWT access token"
)
def login_user(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):
    # gets the first user with the same name as form_data
    user = db.query(UserRecordDB).filter(
        UserRecordDB.username == form_data.username
    ).first()

    # checks if username or password is wrong
    if not user or not auth.verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    # generates access_token
    access_token = auth.generate_access_token(
        data={"sub": user.username, "role": user.role}
    )

    return {"access_token": access_token, "token_type": "bearer"}

