"""Time helpers, slot availability and CSRF protection."""
import hmac
import secrets
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

from flask import abort, request, session
from sqlalchemy import func

import data
from extensions import db
from models import Booking


# ---------- Time ----------
def now_local():
    return datetime.now(ZoneInfo(data.TIMEZONE))


def today_local():
    return now_local().date()


def fmt_time(value):
    hour, minute = (int(part) for part in value.split(":"))
    suffix = "am" if hour < 12 else "pm"
    hour12 = hour % 12 or 12
    return f"{hour12}:{minute:02d} {suffix}" if minute else f"{hour12} {suffix}"


def fmt_date(value):
    return f"{value:%a}, {value.day} {value:%b %Y}"


def inr(value):
    return f"₹{int(value):,}"


def open_status():
    """Returns (is_open, text) for the 'Open now' badge."""
    now = now_local()
    weekday, clock = now.weekday(), now.strftime("%H:%M")
    for start, end in data.OPEN_HOURS.get(weekday, []):
        if start <= clock < end:
            return True, f"Open now, serving until {fmt_time(end)}"
        if clock < start:
            return False, f"Opens today at {fmt_time(start)}"
    for offset in range(1, 8):
        day = (weekday + offset) % 7
        if data.OPEN_HOURS.get(day):
            name = "tomorrow" if offset == 1 else data.DAY_NAMES[day]
            return False, f"Closed now, opens {name} at {fmt_time(data.OPEN_HOURS[day][0][0])}"
    return False, "Closed"


# ---------- Slots ----------
def service_slots(day):
    """Every bookable time on a given date, ignoring what has passed or sold out."""
    slots = []
    for start, end in data.BOOKING_WINDOWS.get(day.weekday(), []):
        current = datetime.combine(day, datetime.strptime(start, "%H:%M").time())
        last = datetime.combine(day, datetime.strptime(end, "%H:%M").time())
        while current <= last:
            slots.append(current.strftime("%H:%M"))
            current += timedelta(minutes=data.SLOT_MINUTES)
    return slots


def availability(day):
    """{time: seats_left} for slots that are still in the future."""
    now = now_local()
    cutoff = now.replace(tzinfo=None) + timedelta(minutes=data.MIN_LEAD_MINUTES)
    booked = dict(
        db.session.query(Booking.time, func.sum(Booking.guests))
        .filter(Booking.date == day, Booking.status != "cancelled")
        .group_by(Booking.time)
        .all()
    )
    result = {}
    for slot in service_slots(day):
        slot_dt = datetime.combine(day, datetime.strptime(slot, "%H:%M").time())
        if slot_dt < cutoff:
            continue
        result[slot] = data.SEATS_PER_SLOT - int(booked.get(slot, 0))
    return result


# ---------- CSRF ----------
def csrf_token():
    if "_csrf" not in session:
        session["_csrf"] = secrets.token_hex(16)
    return session["_csrf"]


def check_csrf():
    sent = request.form.get("_csrf", "")
    expected = session.get("_csrf", "")
    if not sent or not expected or not hmac.compare_digest(sent, expected):
        abort(400)
