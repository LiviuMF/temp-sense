import logging
import signal
from subprocess import Popen, PIPE

from django.core.management.base import BaseCommand

import requests


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def kill_process_for_port(port: str) -> None:
    process_bytes = Popen(['ps', 'x'], stdout=PIPE).communicate()
    lines = process_bytes[0].decode('utf-8').split('\n')
    process_to_be_killed = [line for line in lines if port in line][0].split()[0]
    
    os.kill(
	int(process_to_be_killed),
        signal.SIGTERM
    )


class Command(BaseCommand):
    def add_arguments(self, parser):
        parser.add_argument("port", type=int)
        
    def handle(self, *args, **options):
        response = requests.get('https://temp-sense.cohe.ro/')
        if response.status_code != 200:
            try:
                kill_process_for_port(options['port'])
                logger.info(f'Port {PORT} killed')
            except:
                pass
