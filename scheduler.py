import schedule
import time


# def job():
#     print("I'm working...")
#
#
# schedule.every(3).seconds.do(job)

from scrape import Scraper
from mongo import Mongo

def scheduled_job():
    scraper = Scraper()
    mongo = Mongo()

    scraper.scrape()
    scraper.quit()
    mongo.insert_latest_record()

schedule.every().monday.at("18:30").do(scheduled_job)
schedule.every().thursday.at("18:30").do(scheduled_job)

while True:
    schedule.run_pending()
    time.sleep(1)
