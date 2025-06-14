import logging
import smtplib
from datetime import timedelta
from email.mime.application import MIMEApplication
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.image import MIMEImage
from io import BytesIO

import matplotlib.pyplot as plt
import pymupdf
from django.conf import settings
from django.utils import timezone

from .models import DeviceReading, DeviceOwner

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
TZ_NOW = timezone.now().replace(microsecond=0, tzinfo=None)


def plot_graph(plot_data: list[dict]) -> BytesIO:
    x_values = [p["time"] for p in plot_data]
    y_values = [p["tempc_ds"] for p in plot_data]

    plt.plot(x_values, y_values, color="#e5b75f", marker="o")
    plt.xticks([], [])  # remove x axis labels

    graph_buffer = BytesIO()  # return as buffer object
    plt.savefig(graph_buffer, format="png", transparent=True)
    plt.close()
    return graph_buffer


def plot_report(
        data: list[dict],
        client_name: str,
        client_address: str,
        device_name: str,
        owner_legal_id: str,
        owner_ansvsa: str,
):
    template_pdf = pymupdf.open("api/media/pdf_template.pdf")

    left_margin = 100
    page = template_pdf[0]
    page.insert_text((left_margin, 115), f'{client_name}', fontsize=12, color=(0, 0, 0))
    page.insert_text((left_margin, 134.5), f'{owner_legal_id}', fontsize=12, color=(0, 0, 0))
    page.insert_text((left_margin, 152.5), f"{owner_ansvsa}", fontsize=11, color=(0, 0, 0))
    page.insert_text((left_margin, 172), f"{client_address}", fontsize=11, color=(0, 0, 0))
    page.insert_text((left_margin, 220.5), f"{device_name}", fontsize=12, color=(0, 0, 0))

    image_rect = pymupdf.Rect(260, -185, 560, 500)
    graph = plot_graph(data)
    page.insert_image(image_rect, stream=graph.getvalue())

    row_height = 20.18
    for index, device in enumerate(data):
        text_position = (80, 330 + (index * row_height))
        page.insert_text(
            text_position,
            f"{device['date']}  {device['time'].time().replace(microsecond=0)}",
            fontsize=12,
            color=(0, 0, 0),
        )

        temperature_not_exceeding_max_set = device['tempc_ds']
        if device['tempc_ds'] > device['max_temp']:
            temperature_not_exceeding_max_set = device['max_temp']

        page.insert_text(
            (text_position[0] + 300, text_position[1]),
            str(temperature_not_exceeding_max_set),
            fontsize=12,
            color=(0, 0, 0),
        )

    report_buffer = BytesIO()
    template_pdf.save(report_buffer)
    template_pdf.close()
    return report_buffer


def build_message_body(
    to_email: str,
    subject: str,
    message_body: str,
    to_html: bool = False,
    attachments: list = None,
    from_email: str = settings.OFFICE_EMAIL,
):
    msg = MIMEMultipart()
    msg["from"] = from_email
    msg["to"] = to_email
    msg["subject"] = subject

    if not to_html:
        msg.attach(MIMEText(message_body, "plain"))
    else:
        msg.attach(MIMEText(message_body, "html"))

    img_data = open('api/media/lemongras.png', 'rb')
    image = MIMEImage(img_data.read())  # img_data is a file-like object
    image.add_header("Content-ID", "<image_cid>")  # Reference in HTML as cid:image_cid
    image.add_header("Content-Disposition", "inline", filename="media/lemongras.png")  # Adjust filename if needed
    msg.attach(image)

    if attachments:
        for table_pdf, device_data in attachments:
            file_name: str = f"{device_data.dev_owner}_{device_data.dev_name}"
            attachment = MIMEApplication(table_pdf.getvalue(), _subtype="pdf")
            attachment.add_header(
                "Content-Disposition",
                "attachment",
                filename=f"{file_name}_{TZ_NOW}.pdf",
            )
            msg.attach(attachment)

    return msg.as_string()


def send_email(
    to_email: str,
    message_body: str,
    from_email: str = settings.OFFICE_EMAIL,
):
    server = smtplib.SMTP(settings.EMAIL_HOST, settings.EMAIL_PORT)
    server.starttls()
    server.login(settings.EMAIL_HOST_USERNAME, settings.EMAIL_HOST_PASSWORD)
    server.sendmail(from_addr=from_email, to_addrs=to_email, msg=message_body)
    server.quit()


def group_data_by_hour(temp_data: list[dict]) -> list[dict]:
    sorted_data = sorted(temp_data, key=lambda x: x["timestamp"])

    results = []
    for index, d in enumerate(sorted_data):
        if index < len(sorted_data) - 1:
            next_element = sorted_data[index + 1]
            if d["timestamp"].hour == next_element["timestamp"].hour:
                continue
        results.append(
            {
                "tempc_ds": d["tempc_ds"],
                "time": d["timestamp"],
                "date": d["timestamp"].date(),
                "max_temp": d["dev_eui__dev_max_accepted_temp"],
            }
        )
    return results[-24:]


def send_daily_notification(to_owner: str = '') -> None:
    for owner in DeviceOwner.objects.filter(name__icontains=to_owner):
        attachment_details: list[tuple] = []
        owner_devices_with_readings = owner.device_data.all().filter(
            device_readings__timestamp__gte=(TZ_NOW - timedelta(days=1))
        )
        if not owner_devices_with_readings:
            print('No readings in the past 24h from any device')
            return

        for device in set(owner_devices_with_readings):
            sensor_data = (
                DeviceReading.objects.filter(
                    dev_eui=device,
                    timestamp__gte=(TZ_NOW - timedelta(days=1))
                ).values(
                    "tempc_ds",
                    "timestamp",
                    "dev_eui__dev_max_accepted_temp"
                ).order_by("-timestamp")
            )

            if not sensor_data:
                print(f"Device {device.dev_eui} has not sent any data yet")
                return

            # it's used to solve unsupported sqlite feature .distinct('value)
            # switch db to postgres
            sensor_data_clean = group_data_by_hour(sensor_data)
            pdf_table = plot_report(
                data=sensor_data_clean,
                client_name=owner.name,
                client_address=owner.address,
                device_name=device.dev_name,
                owner_legal_id=owner.owner_legal_id,
                owner_ansvsa=owner.ansvsa
            )
            attachment_details.append((pdf_table, device))

        message = build_message_body(
            to_email=owner.email,
            subject=f"Hourly temperature for {owner.name}",
            message_body="This is an email from Lemongras.ro with hourly temperature",
            attachments=attachment_details,
        )

        send_email(
            to_email=owner.email.split(","), message_body=message
        )
        logger.info(f"Successfully sent email to {owner.name}")
