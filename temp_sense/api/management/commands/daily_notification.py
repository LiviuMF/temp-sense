from api.mail import send_daily_notification
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    def handle(self, *args, **options):
        owner = options.get('owner')
        send_daily_notification(to_owner=owner)

    def add_arguments(self, parser):
        parser.add_argument('--owner', type=str)
