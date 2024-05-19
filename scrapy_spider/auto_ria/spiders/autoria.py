import sys
import os
from concurrent.futures import ProcessPoolExecutor
import scrapy
import re
from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from app.database import SessionLocal, init_db
from app.models import Advertisement
from app.redis_client import redis_client
import json

init_db()

def run_spider():
    process = CrawlerProcess(settings=get_project_settings())
    process.crawl(AutoSpider)
    process.start()

def run_spider_for_url(url):
    process = CrawlerProcess(settings=get_project_settings())
    process.crawl(AutoSpider, start_url=url)
    process.start()

def start_scrapy_process(url):
    with ProcessPoolExecutor() as executor:
        future = executor.submit(run_spider_for_url, url)
        future.result()

class AutoSpider(scrapy.Spider):
    name = 'auto_spider'
    start_urls = ['https://auto.ria.com/last/today/']

    def __init__(self, start_url=None, *args, **kwargs):
        super(AutoSpider, self).__init__(*args, **kwargs)
        if start_url:
            self.start_urls = [start_url]

    def parse(self, response):
        if 'last/today' in response.url:
            # Собираем все ссылки на объявления
            ad_links = response.xpath('//a[@class="address"]/@href').getall()
            for link in ad_links:
                yield response.follow(link, self.parse_ad)
        else:
            yield self.parse_ad(response)

    def parse_ad(self, response):
        title = response.xpath('//h1[@class="head"]/@title').get()
        price = response.xpath('//div[@class="price_value"]/strong/text()').get()
        region = response.xpath('//div[contains(@class, "item_inner")]/text()').get().strip()
        color = response.xpath('//span[contains(@class, "argument")]/span[contains(@class, "car-color")]/following-sibling::text()').get()
        if color:
            color = color.strip()
        mileage = response.xpath('//div[@class="base-information bold"]/span[@class="size18"]/text()').get()
        if not mileage:
            mileage = response.xpath('//span[@class="argument"]/text()').get()
        if not mileage:
            mileage = response.xpath('//dd/span[@class="argument"]/text()').get()

        contact_info = response.xpath('//div[@class="seller_info_name bold"]/text()').get()

        marka, model = self.extract_marka_model(title)

        ad_data = {
            'title': title,
            'price': float(price.replace(' ', '').replace('$', '')) if price else None,
            'model': model,
            'marka': marka,
            'region': region,
            'mileage': f'{mileage} тыс. км' if mileage else 'Неизвестно',
            'color': color,
            'contact_info': contact_info if contact_info else 'Неизвестно',
            'link': response.url
        }
        self.save_to_db(ad_data)

    def extract_marka_model(self, title):
        match = re.match(r'(\w+)\s+(.*?)(?:\d{4})?$', title)
        if match:
            marka = match.group(1)
            model = match.group(2).strip()
            return marka, model
        return 'Неизвестно', 'Неизвестно'

    def save_to_db(self, ad_data):
        db = SessionLocal()
        existing_ad = db.query(Advertisement).filter(Advertisement.link == ad_data['link']).first()
        if existing_ad:
            # Проверяем, нужно ли обновлять данные
            if datetime.utcnow() - existing_ad.updated_at < timedelta(days=1):
                db.close()
                return  # Уже есть актуальные данные, пропускаем
            # Обновляем данные
            for key, value in ad_data.items():
                setattr(existing_ad, key, value)
            existing_ad.updated_at = datetime.utcnow()
            db.commit()
            db.refresh(existing_ad)
        else:
            # Создаем новое объявление
            ad = Advertisement(**ad_data)
            db.add(ad)
            db.commit()
            db.refresh(ad)
        
        # Сохранение данных в Redis на 24 часа
        redis_client.setex(f"advertisement:{ad.id}", timedelta(days=1), json.dumps(ad_data))

        db.close()