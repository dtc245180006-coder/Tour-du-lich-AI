from datetime import datetime, timedelta, timezone

VIETNAM = timezone(timedelta(hours=7))

def today():
    return datetime.now(VIETNAM).date()
