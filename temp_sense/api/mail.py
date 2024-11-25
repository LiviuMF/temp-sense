import logging
import smtplib
from datetime import timedelta
from email.mime.application import MIMEApplication
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from io import BytesIO

import matplotlib.pyplot as plt
import pymupdf
from django.conf import settings
from django.utils import timezone

from .models import DeviceData, DeviceReading

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
TZ_NOW = timezone.now().replace(microsecond=0, tzinfo=None)


def plot_graph(plot_data: list[dict]) -> BytesIO:
    x_values = [p["time"] for p in plot_data]
    y_values = [float(p["tempc_ds"]) for p in plot_data]

    plt.plot(x_values, y_values, color="#e5b75f", marker="o")
    plt.xticks([], [])  # remove x axis labels

    graph_buffer = BytesIO()  # return as buffer object
    plt.savefig(graph_buffer, format="png", transparent=True)
    plt.close()
    return graph_buffer


def plot_report(
    data: list[dict], client_name: str, client_address: str, device_name: str
):
    template_pdf = pymupdf.open("api/media/pdf_template.pdf")

    page = template_pdf[0]
    page.insert_text((50, 195), f'"{client_name}"', fontsize=12, color=(0, 0, 0))
    page.insert_text((50, 210), f"{client_address}", fontsize=11, color=(0, 0, 0))
    page.insert_text((216, 205), f"{device_name}", fontsize=12, color=(0, 0, 0))

    image_rect = pymupdf.Rect(260, -200, 560, 500)
    graph = plot_graph(data)
    page.insert_image(image_rect, stream=graph.getvalue())

    row_height = 20.18
    for index, device in enumerate(data):
        text_position = (80, 295 + (index * row_height))
        page.insert_text(
            text_position,
            f"{device['date']}  {device['time'].time().replace(microsecond=0)}",
            fontsize=12,
            color=(0, 0, 0),
        )
        page.insert_text(
            (text_position[0] + 300, text_position[1]),
            device["tempc_ds"],
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
    attachments: list,
    from_email: str = settings.OFFICE_EMAIL,
):
    msg = MIMEMultipart()
    msg["from"] = from_email
    msg["to"] = to_email
    msg["subject"] = subject
    msg.attach(MIMEText(message_body, "plain"))

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


def send_daily_notification() -> None:
    dev_owners = DeviceData.objects.all().values_list("dev_owner", flat=True).distinct()

    for owner in dev_owners:
        attachment_details: list[tuple] = []
        owner_devices: list[DeviceData] = DeviceData.objects.filter(dev_owner=owner)
        for device in owner_devices:
            sensor_data = (
                DeviceReading.objects.filter(
                    dev_eui=device, timestamp__gte=(TZ_NOW - timedelta(days=1))
                )
                .values("tempc_ds", "timestamp")
                .order_by("timestamp")
            )

            # it's used to solve unsupported sqlite feature .distinct('value)
            # switch db to postgres
            sensor_data_clean = group_data_by_hour(sensor_data)

            if sensor_data_clean:
                pdf_table = plot_report(
                    data=sensor_data_clean,
                    client_name=owner,
                    client_address=device.dev_owner_address,
                    device_name=device.dev_name,
                )
                attachment_details.append((pdf_table, device))
            else:
                print(f"Device {device.dev_eui} has not sent any data yet")
                continue
        owner_details = DeviceData.objects.filter(dev_owner=owner).first()
        message = build_message_body(
            to_email=owner_details.dev_owner_email,
            subject=f"Hourly temperature for {owner_details.dev_owner}",
            message_body="This is an email from Horepa.ro with hourly temperature",
            attachments=attachment_details,
        )
        send_email(to_email=settings.ADMIN_EMAIL, message_body=message)
        logger.info(f"Successfully sent email to {send_email}")


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
            }
        )
    return results[-24:]
