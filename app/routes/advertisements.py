from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from datetime import timedelta, datetime
import logging
import redis
import json
from .. import models, schemas, auth, database
from fastapi import FastAPI, status, Query
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm

from scrapy_spider.auto_ria.spiders.autoria import start_scrapy_process

router = APIRouter()


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


redis_client = redis.StrictRedis(host='localhost', port=6379, db=0)


@router.post("/token")
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(database.get_db)):
    user = auth.authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Incorrect username or password",
        )
    access_token = auth.create_access_token(data={"sub": user.username})
    return {"access_token": access_token, "token_type": "bearer"}

@router.post("/users/", response_model=schemas.UserResponse)
def create_user(user: schemas.UserCreate, db: Session = Depends(database.get_db)):
    db_user = db.query(models.User).filter(models.User.username == user.username).first()
    if db_user:
        raise HTTPException(status_code=400, detail="Username already registered")
    hashed_password = auth.get_password_hash(user.password)
    db_user = models.User(username=user.username, hashed_password=hashed_password)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

@router.get("/advertisements/{ad_id}", response_model=schemas.AdvertisementResponse)
def read_advertisement(ad_id: int, db: Session = Depends(database.get_db), token: str = Depends(oauth2_scheme)):
    current_user = auth.get_current_user(token, db)

    ad_data = redis_client.get(f"advertisement:{ad_id}")
    if ad_data:
        logger.info(f"Cache hit for advertisement ID {ad_id}")

        # Декодируем JSON строку из Redis
        ad_data = json.loads(ad_data)
        # Добавляем поле 'from'
        ad_data['from'] = 'cache'
        return ad_data

    ad = db.query(models.Advertisement).filter(models.Advertisement.id == ad_id).first()
    if ad is None:
        raise HTTPException(status_code=404, detail="Advertisement not found")
    
    ad_response = schemas.AdvertisementResponse.from_orm(ad)

    redis_client.setex(f"advertisement:{ad_id}", timedelta(days=1), ad_response.json())

    return ad_response



@router.get("/advertisements", response_model=list[schemas.AdvertisementResponse])
def read_advertisements(start_date: datetime, end_date: datetime, db: Session = Depends(database.get_db)):
    cache_key = f"advertisements:{start_date}:{end_date}"

    ads_data = redis_client.get(cache_key)
    if ads_data:
        
        return json.loads(ads_data)
    
    ads = db.query(models.Advertisement).filter(models.Advertisement.created_at.between(start_date, end_date)).all()
    ads_json = [ad.json() for ad in ads]
    redis_client.setex(cache_key, timedelta(days=1), json.dumps(ads_json))

    return ads

@router.get("/statistics", response_model=dict)
def get_statistics(marka: str, model: str, db: Session = Depends(database.get_db)):

    cache_key = f"statistics:{marka}:{model}"
    # Проверка наличия данных в кэше
    cached_stats = redis_client.get(cache_key)
    if cached_stats:
        return json.loads(cached_stats)
    
    # Если данных нет в кэше, ищем в базе данных
    ads = db.query(models.Advertisement).filter(models.Advertisement.marka == marka, models.Advertisement.model == model).all()
    if not ads:
        return {"message": "No data available for the specified marka and model"}

    min_price = min(ad.price for ad in ads)
    max_price = max(ad.price for ad in ads)
    now = datetime.utcnow()
    count_day = sum(1 for ad in ads if ad.created_at >= now - timedelta(days=1))
    count_week = sum(1 for ad in ads if ad.created_at >= now - timedelta(weeks=1))
    count_month = sum(1 for ad in ads if ad.created_at >= now - timedelta(days=30))

    redis_client.setex(cache_key, timedelta(days=1), json.dumps(statistics))

    statistics = {
        "min_price": min_price,
        "max_price": max_price,
        "count_day": count_day,
        "count_week": count_week,
        "count_month": count_month,
    }
    # 6379
    # Сохранение данных в Redis на 24 часа
    redis_client.setex(cache_key, timedelta(days=1), json.dumps(statistics))
    
    return statistics

@router.get("/advertisement_by_link", response_model=schemas.AdvertisementResponse)
def get_advertisement_by_link(
    link: str = Query(..., description="The link to the advertisement"),
    db: Session = Depends(database.get_db)
    ):
    ad = db.query(models.Advertisement).filter(models.Advertisement.link == link).first()
    if ad:
        return ad

    start_scrapy_process(link)

    ad = db.query(models.Advertisement).filter(models.Advertisement.link == link).first()
    if not ad:
        raise HTTPException(status_code=404, detail="Advertisement not found")
    return ad
