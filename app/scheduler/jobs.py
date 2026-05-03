from apscheduler.schedulers.background import BackgroundScheduler

scheduler = BackgroundScheduler(timezone="UTC")

def start_jobs(fetch_news_job, fetch_price_job, fetch_kap_job):
    scheduler.add_job(fetch_news_job, "interval", minutes=15, id="fetch_news")
    scheduler.add_job(fetch_price_job, "cron", hour=18, minute=0, id="fetch_prices")
    scheduler.add_job(fetch_kap_job, "interval", minutes=30, id="fetch_kap")
    scheduler.start()
