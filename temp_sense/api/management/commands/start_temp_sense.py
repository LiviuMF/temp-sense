import os
import logging
import sys

from django.core.management.base import BaseCommand

import requests


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


START_FILE_PATH = sys.argv[1]


def start_api(file_path: str):
    os.system(f'chmod +x {file_path}')
    os.system(file_path)


class Command(BaseCommand):
    def handle(self, *args, **options):
        response = requests.get('https://temp-sense.cohe.ro/')
        if response.status_code != 200:
            try:
                start_api(START_FILE_PATH)
                logger.info(f'Started process')
            except:
                pass
