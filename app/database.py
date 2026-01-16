from sqlmodel import SQLModel, Session, create_engine
from app.config import settings

# check_same_thread=False is needed only for SQLite
engine = create_engine(settings.DATABASE_URL, connect_args={"check_same_thread": False})

def get_db():
    with Session(engine) as session:
        yield session

def init_db():
    SQLModel.metadata.create_all(engine)