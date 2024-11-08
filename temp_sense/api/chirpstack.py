from django.conf import settings

import requests


def create_device(
        dev_eui: str,
        join_eui: str,
) -> None:
    payload = {
        "device": {
            "applicationId": settings.CHIRPSTACK_APPLICATION_ID,
            "description": "",
            "devEui": dev_eui,
            "deviceProfileId": settings.CHIRPSTACK_DEVICE_PROFILE_ID,
            "isDisabled": False,
            "joinEui": join_eui,
            "name": "LHT65",
            "skipFcntCheck": True,
            "tags": {
                "additionalProp1": "",
                "additionalProp2": "",
                "additionalProp3": ""
            },
            "variables": {
                "additionalProp1": "",
                "additionalProp2": "",
                "additionalProp3": ""
            }
        }
    }

    try:
        requests.post(
            settings.CHIRPSTACK_URL,
            headers={
                'Authorization': f'Bearer {settings.CHIRPSTACK_API_TOKEN}',
                'Content-Type': 'application/json',
            },
            json=payload
        )
    except requests.exceptions.RequestException as e:
        print(f'Request failed with exception: {e}')
