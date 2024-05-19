# # main.py
# import jwt
# import json
# import logging
# import threading

# from typing import Optional
# from pydantic import BaseModel

# from sqlalchemy.orm import Session
# from datetime import datetime, timedelta

# from fastapi.security import OAuth2PasswordRequestForm
# from fastapi import FastAPI, Depends, HTTPException, status, Query
# from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm

# # from scrapy_spider.auto_ria.spiders.autoria import start_scrapy_process
# # from scrapy_spider.auto_ria.spiders.autoria import start_scrapy_process
# #from app.database import User

# from app.redis_client import redis_client
# from app.database import SessionLocal, init_db #Advertisement
# from app.schemas import AdvertisementResponse, UserResponse, UserCreate
# from app.models import Advertisement, User
# from app.auth import get_current_user, create_access_token, authenticate_user, get_password_hash



# # logging.basicConfig(level=logging.INFO)
# # logger = logging.getLogger(__name__)
# # init_db()

# # app = FastAPI()

# # oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

# # Конфигурации
# # SECRET_KEY = "your_secret_key"
# # ALGORITHM = "HS256"
# # ACCESS_TOKEN_EXPIRE_MINUTES = 30

# # Модели Pydantic
# # class Token(BaseModel):
# #     access_token: str
# #     token_type: str

# # class TokenData(BaseModel):
# #     username: Optional[str] = None


# # Зависимость для получения сессии базы данныхxxx
# # def get_db():
# #     db = SessionLocal()
# #     try:
# #         yield db
# #     finally:
# #         db.close()

# # class AdvertisementResponse(BaseModel):
# #     title: str
# #     price: float
# #     model: str
# #     marka: str
# #     region: str
# #     mileage: str
# #     color: str
# #     contact_info: Optional[str]  # Обновлено
# #     link: str
# #     created_at: datetime

# #     class Config:
# #         orm_mode = True
# #         from_attributes = True


# # class UserCreate(BaseModel):
# #     username: str
# #     password: str

# # class UserResponse(BaseModel):
# #     username: str

# #     class Config:
# #         orm_mode = True



# # @app.post("/token")
# # def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
# #     user = authenticate_user(db, form_data.username, form_data.password)
# #     if not user:
# #         raise HTTPException(
# #             status_code=status.HTTP_400_BAD_REQUEST,
# #             detail="Incorrect username or password",
# #         )
# #     access_token = create_access_token(data={"sub": user.username})
# #     return {"access_token": access_token, "token_type": "bearer"}

# # @app.post("/users/", response_model=UserResponse)
# # def create_user(user: UserCreate, db: Session = Depends(get_db)):
# #     db_user = db.query(User).filter(User.username == user.username).first()
# #     if db_user:
# #         raise HTTPException(status_code=400, detail="Username already registered")
# #     hashed_password = get_password_hash(user.password)
# #     db_user = User(username=user.username, hashed_password=hashed_password)
# #     db.add(db_user)
# #     db.commit()
# #     db.refresh(db_user)
# #     return db_user


# # @app.get("/advertisements/{ad_id}", response_model=AdvertisementResponse)
# # def read_advertisement(ad_id: int, db: Session = Depends(get_db), token: str = Depends(oauth2_scheme)):
# #     ad = db.query(Advertisement).filter(Advertisement.id == ad_id).first()
# #     if ad is None:
# #         raise HTTPException(status_code=404, detail="Advertisement not found")
# #     return ad

# # @app.get("/advertisements/{ad_id}", response_model=AdvertisementResponse)
# # def read_advertisement(ad_id: int, db: Session = Depends(get_db), token: str = Depends(oauth2_scheme)):
# #     current_user = get_current_user(token, db)

# #     ad_data = redis_client.get(f"advertisement:{ad_id}")
# #     if ad_data:
# #         logger.info(f"Cache hit for advertisement ID {ad_id}")

# #         # Декодируем JSON строку из Redis
# #         ad_data = json.loads(ad_data)
# #         # Добавляем поле 'from'
# #         ad_data['from'] = 'cache'
# #         return ad_data

# #     ad = db.query(Advertisement).filter(Advertisement.id == ad_id).first()
# #     if ad is None:
# #         raise HTTPException(status_code=404, detail="Advertisement not found")
    
# #     ad_response = AdvertisementResponse.from_orm(ad)

# #     redis_client.setex(f"advertisement:{ad_id}", timedelta(days=1), ad_response.json())

# #     return ad_response

# # @app.get("/advertisements", response_model=list[AdvertisementResponse])
# # def read_advertisements(start_date: datetime, end_date: datetime, db: Session = Depends(get_db)):
# #     cache_key = f"advertisements:{start_date}:{end_date}"

# #     ads_data = redis_client.get(cache_key)
# #     if ads_data:
        
# #         return json.loads(ads_data)
    
# #     ads = db.query(Advertisement).filter(Advertisement.created_at.between(start_date, end_date)).all()
# #     ads_json = [ad.json() for ad in ads]
# #     redis_client.setex(cache_key, timedelta(days=1), json.dumps(ads_json))

# #     return ads

# # @app.get("/statistics", response_model=dict)
# # def get_statistics(marka: str, model: str, db: Session = Depends(get_db)):

# #     cache_key = f"statistics:{marka}:{model}"
# #     # Проверка наличия данных в кэше
# #     cached_stats = redis_client.get(cache_key)
# #     if cached_stats:
# #         return json.loads(cached_stats)
    
# #     # Если данных нет в кэше, ищем в базе данных
# #     ads = db.query(Advertisement).filter(Advertisement.marka == marka, Advertisement.model == model).all()
# #     if not ads:
# #         return {"message": "No data available for the specified marka and model"}

# #     min_price = min(ad.price for ad in ads)
# #     max_price = max(ad.price for ad in ads)
# #     now = datetime.utcnow()
# #     count_day = sum(1 for ad in ads if ad.created_at >= now - timedelta(days=1))
# #     count_week = sum(1 for ad in ads if ad.created_at >= now - timedelta(weeks=1))
# #     count_month = sum(1 for ad in ads if ad.created_at >= now - timedelta(days=30))

# #     redis_client.setex(cache_key, timedelta(days=1), json.dumps(statistics))

# #     statistics = {
# #         "min_price": min_price,
# #         "max_price": max_price,
# #         "count_day": count_day,
# #         "count_week": count_week,
# #         "count_month": count_month,
# #     }
# #     # 6379
# #     # Сохранение данных в Redis на 24 часа
# #     redis_client.setex(cache_key, timedelta(days=1), json.dumps(statistics))
    
# #     return statistics

# # @app.get("/advertisement_by_link", response_model=AdvertisementResponse)
# # def get_advertisement_by_link(
# #     link: str = Query(..., description="The link to the advertisement"),
# #     db: Session = Depends(get_db)
# #     ):
# #     ad = db.query(Advertisement).filter(Advertisement.link == link).first()
# #     if ad:
# #         return ad

# #     start_scrapy_process(link)

# #     ad = db.query(Advertisement).filter(Advertisement.link == link).first()
# #     if not ad:
# #         raise HTTPException(status_code=404, detail="Advertisement not found")
# #     return ad


from fastapi import FastAPI
from app.database import engine, Base, init_db
from app.routes import advertisements

import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

logger.info("Creating FastAPI app")
app = FastAPI()

#Base.metadata.create_all(bind=engine)
# init_db()


app.include_router(advertisements.router)

if __name__ == "__main__":
    init_db()