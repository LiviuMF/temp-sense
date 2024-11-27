import requests
from django.conf import settings


def send_message(message):
    response = requests.post(
        url=settings.DISCORD_SEND_MESSAGE_URL,
        headers={
            "Authorization": f"Bot {settings.DISCORD_BOT_TOKEN}",
        },
        json={"content": message},
    )

    if response.status_code == 200:
        print("Message sent successfully.")
    else:
        print("Failed to send the message.")
        print(response.text)
