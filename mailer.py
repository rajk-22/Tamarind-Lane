"""Email helpers. Sends in a background thread so pages stay fast."""
import smtplib
import threading
from email.message import EmailMessage

import data
from utils import fmt_date, fmt_time

NAME = data.RESTAURANT["name"]


def send_email(app, to, subject, body):
    cfg = app.config
    if not cfg["MAIL_SERVER"]:
        app.logger.warning("EMAIL (not sent, MAIL_SERVER empty)\nTo: %s\nSubject: %s\n\n%s", to, subject, body)
        return

    message = EmailMessage()
    message["Subject"] = subject
    message["From"] = cfg["MAIL_FROM"]
    message["To"] = to
    message.set_content(body)

    def deliver():
        try:
            with smtplib.SMTP(cfg["MAIL_SERVER"], cfg["MAIL_PORT"], timeout=15) as server:
                if cfg["MAIL_USE_TLS"]:
                    server.starttls()
                if cfg["MAIL_USERNAME"]:
                    server.login(cfg["MAIL_USERNAME"], cfg["MAIL_PASSWORD"])
                server.send_message(message)
        except Exception:
            app.logger.exception("Could not send email to %s", to)

    threading.Thread(target=deliver, daemon=True).start()


def _summary(b):
    return (
        f"Reference: {b.reference}\n"
        f"Date: {fmt_date(b.date)}\n"
        f"Time: {fmt_time(b.time)}\n"
        f"Guests: {b.guests}\n"
    )


def notify_new_booking(app, b):
    owner = app.config["OWNER_EMAIL"]
    send_email(app, owner, f"New booking: {b.name}, {b.guests} guests, {fmt_date(b.date)} {fmt_time(b.time)}",
               f"{_summary(b)}Name: {b.name}\nPhone: {b.phone}\nEmail: {b.email}\n"
               f"Notes: {b.notes or 'None'}\n\nConfirm or cancel it in the admin panel.")
    send_email(app, b.email, f"We got your booking request, {b.name.split()[0]}",
               f"Hi {b.name.split()[0]},\n\nThanks for choosing {NAME}. We've received your request "
               f"and will confirm it shortly.\n\n{_summary(b)}\n"
               f"Need to change something? Call {data.RESTAURANT['phone']} and quote your reference.\n\n{NAME}")


def notify_status(app, b):
    first = b.name.split()[0]
    if b.status == "confirmed":
        subject = f"Confirmed: your table at {NAME}"
        body = f"Hi {first},\n\nYour table is confirmed. We look forward to seeing you.\n\n{_summary(b)}\n{NAME}\n{', '.join(data.RESTAURANT['address_lines'])}"
    elif b.status == "cancelled":
        subject = f"Your booking at {NAME} was cancelled"
        body = f"Hi {first},\n\nYour booking has been cancelled.\n\n{_summary(b)}\nIf this is a surprise, call us on {data.RESTAURANT['phone']}.\n\n{NAME}"
    else:
        return
    send_email(app, b.email, subject, body)


def notify_message(app, m):
    send_email(app, app.config["OWNER_EMAIL"], f"Website message from {m.name}",
               f"From: {m.name} <{m.email}>\n\n{m.body}")
