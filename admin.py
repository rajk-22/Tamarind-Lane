"""Owner-only pages: view and manage bookings and messages."""
import csv
import hmac
import io
import time
from datetime import datetime
from functools import wraps

from flask import (Blueprint, Response, current_app, flash, redirect,
                   render_template, request, session, url_for)
from sqlalchemy import func

from extensions import db
from mailer import notify_status
from models import STATUSES, Booking, Message
from utils import check_csrf, today_local

admin_bp = Blueprint("admin", __name__, url_prefix="/admin")


def admin_required(view):
    @wraps(view)
    def wrapped(*args, **kwargs):
        if not session.get("is_admin"):
            return redirect(url_for("admin.login"))
        return view(*args, **kwargs)
    return wrapped


@admin_bp.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        check_csrf()
        password = request.form.get("password", "")
        if hmac.compare_digest(password, current_app.config["ADMIN_PASSWORD"]):
            session.clear()
            session["is_admin"] = True
            return redirect(url_for("admin.bookings"))
        time.sleep(0.6)  # slows down password guessing
        flash("That password is not right.", "error")
    return render_template("admin/login.html")


@admin_bp.route("/logout", methods=["POST"])
def logout():
    check_csrf()
    session.clear()
    return redirect(url_for("admin.login"))


def _filtered_bookings():
    status = request.args.get("status", "")
    day = request.args.get("date", "")
    show_past = request.args.get("past") == "1"
    query = Booking.query
    if status in STATUSES:
        query = query.filter_by(status=status)
    if day:
        try:
            query = query.filter_by(date=datetime.strptime(day, "%Y-%m-%d").date())
        except ValueError:
            pass
    elif not show_past:
        query = query.filter(Booking.date >= today_local())
    return query.order_by(Booking.date, Booking.time)


@admin_bp.route("/")
@admin_required
def bookings():
    today = today_local()
    rows = _filtered_bookings().limit(300).all()
    stats = {
        "pending": Booking.query.filter_by(status="pending").count(),
        "today": db.session.query(func.coalesce(func.sum(Booking.guests), 0))
                 .filter(Booking.date == today, Booking.status != "cancelled").scalar(),
        "upcoming": Booking.query.filter(Booking.date >= today, Booking.status != "cancelled").count(),
    }
    return render_template("admin/bookings.html", bookings=rows, stats=stats,
                           statuses=STATUSES, filters=request.args, today=today)


@admin_bp.post("/bookings/<int:booking_id>/status")
@admin_required
def set_status(booking_id):
    check_csrf()
    booking = db.get_or_404(Booking, booking_id)
    new_status = request.form.get("status")
    if new_status in STATUSES and new_status != booking.status:
        booking.status = new_status
        db.session.commit()
        notify_status(current_app._get_current_object(), booking)
        flash(f"{booking.name}'s booking is now {new_status}.", "ok")
    return redirect(url_for("admin.bookings"))


@admin_bp.post("/bookings/<int:booking_id>/delete")
@admin_required
def delete_booking(booking_id):
    check_csrf()
    booking = db.get_or_404(Booking, booking_id)
    db.session.delete(booking)
    db.session.commit()
    flash("Booking deleted.", "ok")
    return redirect(url_for("admin.bookings"))


@admin_bp.route("/export.csv")
@admin_required
def export_csv():
    buffer = io.StringIO()
    writer = csv.writer(buffer)
    writer.writerow(["Reference", "Date", "Time", "Guests", "Name", "Phone", "Email", "Status", "Notes"])
    for b in _filtered_bookings().all():
        writer.writerow([b.reference, b.date.isoformat(), b.time, b.guests, b.name,
                         b.phone, b.email, b.status, b.notes])
    return Response(buffer.getvalue(), mimetype="text/csv",
                    headers={"Content-Disposition": "attachment; filename=bookings.csv"})


@admin_bp.route("/messages")
@admin_required
def messages():
    rows = Message.query.order_by(Message.created_at.desc()).limit(200).all()
    return render_template("admin/messages.html", messages=rows)
