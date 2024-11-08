from django.conf import settings

import requests


def create_device(
        dev_eui: str,
        dev_name: str,
        dev_join_eui: str,
) -> None:
    payload = {
        "device": {
            "applicationId": settings.CHIRPSTACK_APPLICATION_ID,
            "description": "",
            "devEui": dev_eui,
            "deviceProfileId": settings.CHIRPSTACK_DEVICE_PROFILE_ID,
            "isDisabled": False,
            "joinEui": dev_join_eui,
            "name": dev_name,
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
