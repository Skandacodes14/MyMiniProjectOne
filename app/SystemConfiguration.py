from enum import Enum

class Settings:
    "Infrastructure settings"
    DATABASE_URL = "sqlite:///./library.db"
    ALGORITHM = "HS256"
    SECRET_KEY = "MY_SECRET_KEY"
    ACCESS_TOKEN_EXPIRE_MINUTES = 30

    "Business settings"
    MAX_BORROW_LIMIT: int = 4
    ALLOWED_BORROW_DAYS: int = 7
    FINE_PER_DAYS: float = 5.0

class UserRoles(str, Enum):
    ADMIN = "admin"
    MEMBER = "member"

class SortOrder(str, Enum):
    ASC = "asc"
    DESC = "desc"

class SortField(str, Enum):
    ID = "id"
    TITLE = "title"
    AUTHOR = "author"
    GENRE = "genre"
    PAGES = "pages"
    IS_DELETED = "is_deleted"
    IS_ISSUED = "is_issued"

class ResponseMessages:
    BOOK_NOT_FOUND: str = "The requested book was not found."
    INVALID_SORT_FIELD: str = "Sort field is invalid."
    INVALID_OPERATION: str = "Operation not permitted."
    USER_ALREADY_EXISTS: str = "User already exists."
    USER_DOES_NOT_EXISTS: str = "User does not exist."
    BOOK_OUT_OF_STOCK: str = "The requested book is out of stock. Queued for reservation."
    UNAUTHORIZED: str = "Unauthorized."
    BORROW_LIMIT_REACHED: str = "You have reached the borrow limit."
    BOOK_NOT_BORROWED: str = "The requested book was not borrowed."
    BOOK_ALREADY_BORROWED_BY_YOU: str = "The requested book was already borated."

settings = Settings()