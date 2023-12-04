from project import create_app

app = create_app()
celery = app.celery_app

# TIMEZONE = "US/Eastern"
# celery.conf.timezone = TIMEZONE
