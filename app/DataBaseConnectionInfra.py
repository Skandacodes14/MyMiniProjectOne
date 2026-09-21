from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from app.SystemConfiguration import settings
from fastapi.security import OAuth2PasswordBearer

engine = create_engine(settings.DATABASE_URL, connect_args={"check_same_thread": False})

LocalSession = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)

Base = declarative_base()

def get_db():
    db = LocalSession() # creates a session
    try:
        yield db # fetches the value
    finally:
        db.close() # closes the db and the session

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/token")
