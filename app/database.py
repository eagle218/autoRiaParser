# # database.py
# from sqlalchemy import create_engine
# from sqlalchemy.ext.declarative import declarative_base
# from sqlalchemy.orm import sessionmaker
# from datetime import datetime

# DATABASE_URL = "sqlite:///./advertisements.db"

# engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
# SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
# Base = declarative_base()

# # class Advertisement(Base):
# #     __tablename__ = "advertisements"

# #     id = Column(Integer, primary_key=True, index=True)
# #     title = Column(String, index=True)
# #     price = Column(Float)
# #     model = Column(String, index=True)
# #     marka = Column(String, index=True)
# #     region = Column(String)
# #     mileage = Column(String)
# #     color = Column(String)
# #     contact_info = Column(String)
# #     link = Column(String, unique=True, index=True)
# #     created_at = Column(DateTime, default=datetime.utcnow)

# # class User(Base):
# #     __tablename__ = "users"

# #     id = Column(Integer, primary_key=True, index=True)
# #     username = Column(String, unique=True, index=True)
# #     hashed_password = Column(String)
    
# def init_db():
#     Base.metadata.create_all(bind=engine)

from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

SQLALCHEMY_DATABASE_URL = "sqlite:///./advertisements.db"

engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db():
    from . import models  # Импортируйте модели здесь
    Base.metadata.create_all(bind=engine)