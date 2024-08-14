from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session

from src.model import Base


class DatabaseConfig:
    def __init__(self, database_url=None):
        if database_url:
            engine = create_engine(database_url)
            self.session_local = sessionmaker(autocommit=False, autoflush=False, bind=engine)
            Base.metadata.create_all(bind=engine)

    def get_db(self):
        db: Session = self.session_local()
        try:
            yield db
        finally:
            if hasattr(db, "close"):
                db.close()
