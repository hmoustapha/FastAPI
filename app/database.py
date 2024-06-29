from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

SQLALCHEMY_DATABASE_URL = "postgresql://ormAdmin:orm2010zero@localhost/fastapi"

engine = create_engine(SQLALCHEMY_DATABASE_URL)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

# version 3 - Dependency for openning a session for each api call
# db: Session = Depends(get_db) >> add for each call
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()