from sqlmodel import SQLModel, create_engine, Session
from xavierlabs.config import settings

DATABASE_URL = f"sqlite:///{settings.DB_PATH}"

# Connect args needed for SQLite concurrent access
engine = create_engine(
    DATABASE_URL,
    echo=False,
    connect_args={"check_same_thread": False}
)


def init_db():
    """Initializes the database schema."""
    SQLModel.metadata.create_all(engine)


def get_session():
    """Yields a database session."""
    with Session(engine) as session:
        yield session
