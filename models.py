import secrets
from datetime import datetime, timezone

from extensions import db

STATUSES = ("pending", "confirmed", "cancelled")


def make_reference():
    return "TL-" + secrets.token_hex(3).upper()


def utc_now():
    return datetime.now(timezone.utc)


class Booking(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    reference = db.Column(db.String(12), unique=True, nullable=False, default=make_reference)
    name = db.Column(db.String(80), nullable=False)
    email = db.Column(db.String(120), nullable=False)
    phone = db.Column(db.String(30), nullable=False)
    date = db.Column(db.Date, nullable=False, index=True)
    time = db.Column(db.String(5), nullable=False)       # "19:30"
    guests = db.Column(db.Integer, nullable=False)
    notes = db.Column(db.String(300), default="")
    status = db.Column(db.String(12), nullable=False, default="pending")
    created_at = db.Column(db.DateTime, default=utc_now)


class Message(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), nullable=False)
    email = db.Column(db.String(120), nullable=False)
    body = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=utc_now)
