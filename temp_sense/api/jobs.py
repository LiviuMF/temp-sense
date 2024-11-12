from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger

from .mail import send_daily_notification


def start():
    scheduler = BackgroundScheduler()
    scheduler.add_job(send_daily_notification, CronTrigger.from_crontab('0 12 * * *'))
    scheduler.start()