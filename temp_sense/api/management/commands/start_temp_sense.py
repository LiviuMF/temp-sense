import os
import logging

from django.core.management.base import BaseCommand

import requests


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def start_api(file_path: str):
    os.system(f'chmod +x {file_path}')
    os.system(file_path)


class Command(BaseCommand):
    def add_arguments(self, parser):
        parser.add_argument('path')
        
    def handle(self, *args, **options):
        response = requests.get('https://temp-sense.lemongras.ro/')
        if response.status_code != 200:
            try:
                start_api(options['path'])
                logger.info(f'Started process')
            except:
                pass
