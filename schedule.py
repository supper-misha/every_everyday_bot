from apscheduler.schedulers.background import BackgroundScheduler
from routin import send_routin
from stats import send_daily_prog

scheduler = BackgroundScheduler()

# scheduler.add_job(send_routin, 'cron', hour=12, minute=40, args=["morning"])

scheduler.add_job(
    send_routin,
    'cron',
    hour=6,
    minute=5,
    args=["morning"],
    timezone="Europe/Moscow"
)
scheduler.add_job(
    send_routin,
    'cron',
    hour=20,
    minute=5,
    args=["evening"],
    timezone="Europe/Moscow"
)
scheduler.add_job(
    send_daily_prog,
    'cron',
    hour=21,
    minute=0,
    timezone="Europe/Moscow"
)

scheduler.start()
