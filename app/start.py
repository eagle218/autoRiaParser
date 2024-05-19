import sys
import os
import subprocess
import threading
import time

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from scrapy_spider.auto_ria.spiders.autoria import run_spider

def start_scraper():
    print("Starting scraper...")
    run_spider()
    print("Scraper finished.")

def start_fastapi():
    print("Starting FastAPI server...")
    subprocess.run(["uvicorn", "app.main:app", "--reload"])

if __name__ == "__main__":
    scraper_thread = threading.Thread(target=start_scraper)
    fastapi_thread = threading.Thread(target=start_fastapi)

    scraper_thread.start()
    time.sleep(5)  # Ждем немного времени перед запуском FastAPI сервера

    fastapi_thread.start()

    scraper_thread.join()
    fastapi_thread.join()