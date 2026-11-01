"""Tamarind Lane: restaurant website with online table booking."""
import re
from datetime import datetime, timedelta

from flask import (Flask, abort, flash, jsonify, redirect, render_template,
                   request, url_for, current_app)

import data
from admin import admin_bp
from config import Config
from extensions import db
from mailer import notify_message, notify_new_booking
from models import Booking, Message
from utils import (availability, check_csrf, csrf_token, fmt_date, fmt_time,
                   inr, now_local, open_status, service_slots, today_local)

app = Flask(__name__)
app.config.from_object(Config)
db.init_app(app)
app.register_blueprint(admin_bp)

app.jinja_env.globals["csrf_token"] = csrf_token
app.jinja_env.filters.update(fmt_time=fmt_time, fmt_date=fmt_date, inr=inr)

EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")


@app.context_processor
def site_context():
    is_open, status_text = open_status()
    return {
        "restaurant": data.RESTAURANT,
        "hours": data.HOURS_DISPLAY,
        "is_open": is_open,
        "status_text": status_text,
        "year": now_local().year,
    }


# ---------- Public pages ----------
@app.route("/")
def home():
    signature = [item for group in data.MENU for item in group["items"] if item.get("signature")]
    return render_template("index.html", signature=signature, gallery=data.GALLERY[:2])


@app.route("/menu")
def menu():
    return render_template("menu.html", menu=data.MENU)


@app.route("/gallery")
def gallery():
    return render_template("gallery.html", gallery=data.GALLERY)


@app.route("/about")
def about():
    return render_template("about.html", team=data.TEAM)


@app.route("/contact", methods=["GET", "POST"])
def contact():
    values, errors = {}, {}
    if request.method == "POST":
        check_csrf()
        if request.form.get("website"):  # honeypot field, humans leave it empty
            return redirect(url_for("contact"))
        values = {k: request.form.get(k, "").strip() for k in ("name", "email", "body")}
        if len(values["name"]) < 2:
            errors["name"] = "Tell us your name."
        if not EMAIL_RE.match(values["email"]):
            errors["email"] = "Enter a valid email so we can reply."
        if len(values["body"]) < 5:
            errors["body"] = "Write a short message."
        if not errors:
            message = Message(name=values["name"][:80], email=values["email"][:120].lower(),
                              body=values["body"][:2000])
            db.session.add(message)
            db.session.commit()
            notify_message(current_app._get_current_object(), message)
            flash("Thanks, your message is on its way. We reply within a day.", "ok")
            return redirect(url_for("contact"))
    return render_template("contact.html", values=values, errors=errors)


# ---------- Booking ----------
def validate_booking(v):
    errors = {}

    if not 2 <= len(v["name"]) <= 80:
        errors["name"] = "Enter your name."
    if not EMAIL_RE.match(v["email"]) or len(v["email"]) > 120:
        errors["email"] = "Enter a valid email address so we can confirm your table."
    if not 8 <= len(re.sub(r"\D", "", v["phone"])) <= 15 or len(v["phone"]) > 30:
        errors["phone"] = "Enter a phone number we can reach you on."
    if len(v["notes"]) > 300:
        errors["notes"] = "Keep notes under 300 characters."

    try:
        guests = int(v["guests"])
    except ValueError:
        guests = 0
    if not 1 <= guests <= data.MAX_PARTY:
        errors["guests"] = f"We seat 1 to {data.MAX_PARTY} guests online. For larger groups, call us."

    day = None
    try:
        day = datetime.strptime(v["date"], "%Y-%m-%d").date()
    except ValueError:
        errors["date"] = "Choose a date."
    if day:
        today = today_local()
        if day < today or day > today + timedelta(days=data.ADVANCE_DAYS):
            errors["date"] = f"Choose a date within the next {data.ADVANCE_DAYS} days."
        elif not service_slots(day):
            errors["date"] = f"We're closed on {day:%A}s. Please choose another day."
        else:
            slots = availability(day)
            if v["time"] not in slots:
                errors["time"] = "Choose a time from the list."
            elif guests and slots[v["time"]] < guests:
                errors["time"] = "That time just filled up. Please pick another."
    elif not v["time"]:
        errors["time"] = "Choose a date first, then a time."

    cleaned = dict(name=v["name"], email=v["email"].lower(), phone=v["phone"],
                   date=day, time=v["time"], guests=guests, notes=v["notes"])
    return cleaned, errors


@app.route("/book", methods=["GET", "POST"])
def book():
    values, errors = {"guests": "2"}, {}
    if request.method == "POST":
        check_csrf()
        if request.form.get("website"):
            return redirect(url_for("home"))
        values = {k: request.form.get(k, "").strip()
                  for k in ("name", "email", "phone", "date", "time", "guests", "notes")}
        cleaned, errors = validate_booking(values)
        if not errors:
            booking = Booking(**cleaned)
            db.session.add(booking)
            db.session.commit()
            notify_new_booking(current_app._get_current_object(), booking)
            return redirect(url_for("booking_received", reference=booking.reference))
    today = today_local()
    return render_template("book.html", values=values, errors=errors,
                           min_date=today.isoformat(),
                           max_date=(today + timedelta(days=data.ADVANCE_DAYS)).isoformat(),
                           party_sizes=range(1, data.MAX_PARTY + 1))


@app.route("/book/received/<reference>")
def booking_received(reference):
    booking = Booking.query.filter_by(reference=reference).first_or_404()
    return render_template("booking_received.html", booking=booking)


@app.route("/api/availability")
def api_availability():
    try:
        day = datetime.strptime(request.args.get("date", ""), "%Y-%m-%d").date()
    except ValueError:
        return jsonify(error="Invalid date"), 400

    today = today_local()
    if day < today or day > today + timedelta(days=data.ADVANCE_DAYS):
        return jsonify(closed=True, message=f"Choose a date within the next {data.ADVANCE_DAYS} days.", slots=[])
    if not service_slots(day):
        return jsonify(closed=True, message=f"We're closed on {day:%A}s. Please choose another day.", slots=[])

    slots = availability(day)
    if not slots:
        return jsonify(closed=True, message="No times left on that day. Try another date.", slots=[])
    return jsonify(closed=False, message="",
                   slots=[{"time": t, "label": fmt_time(t), "left": left} for t, left in slots.items()])


# ---------- Errors ----------
@app.errorhandler(400)
@app.errorhandler(404)
@app.errorhandler(500)
def handle_error(error):
    code = getattr(error, "code", 500)
    messages = {
        400: "That request did not go through. Go back, refresh the page and try again.",
        404: "We couldn't find that page.",
        500: "Something went wrong on our side. Please try again in a moment.",
    }
    return render_template("error.html", code=code, message=messages.get(code, messages[500])), code


with app.app_context():
    db.create_all()

if __name__ == "__main__":
    app.run(debug=True)
