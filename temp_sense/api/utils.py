from datetime import datetime, timedelta


def get_current_time():
    return datetime.now()


def get_yesterday():
    return get_current_time().date() - timedelta(days=1)


def one_hour_ago():
    return get_current_time() - timedelta(hours=1)
