from api.mail import send_daily_notification
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    def handle(self, *args, **options):
        send_daily_notification()
