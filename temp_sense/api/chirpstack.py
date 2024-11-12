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
    make_request("", payload)


def register_device(
        dev_eui: str,
        dev_app_key: str,
        dev_nwk_key: str,
):
    payload = {
        "deviceKeys": {
            "appKey": dev_app_key,
            "nwkKey": dev_app_key  # chirpstack platform bug
        }
    }
    make_request(f"/{dev_eui}/keys", payload)


def make_request(url_path: str, payload: dict) -> None:
    try:
        requests.post(
            f'{settings.CHIRPSTACK_URL}{url_path}',
            headers={
                'Authorization': f'Bearer {settings.CHIRPSTACK_API_TOKEN}',
                'Content-Type': 'application/json',
            },
            json=payload
        )
    except requests.exceptions.RequestException as e:
        print(f'Request failed with exception: {e}')
