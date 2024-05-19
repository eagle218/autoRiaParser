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
