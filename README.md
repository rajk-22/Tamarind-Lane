# Tamarind Lane: restaurant website with online booking

A complete, responsive restaurant website built with Flask, SQLite and plain HTML/CSS/JS.

## Features
- Pages: home, menu, gallery, about, contact, booking
- Live availability: pick a date and the form shows which times are free (full times are crossed out)
- Booking rules: closed days, 30-minute slots, seat capacity per slot, 60-day window, lead time
- Emails: owner is notified of each booking, guest gets a receipt, and a confirmation or cancellation when the owner acts
- Admin panel (`/admin`): filter bookings, confirm or cancel, delete, export CSV, read contact messages
- Security basics: CSRF tokens, honeypot spam field, constant-time password check, server-side validation
- "Open now" badge on the home page, based on opening hours

## Folder structure
```
tamarind-lane/
├── app.py            routes, booking validation, availability API
├── admin.py          owner login, booking management, CSV export
├── models.py         Booking and Message tables
├── utils.py          time helpers, slot availability, CSRF
├── mailer.py         email sending (background thread)
├── data.py           ALL restaurant content: menu, hours, capacity, team
├── config.py         settings read from environment variables
├── extensions.py     database object
├── requirements.txt
├── Procfile          for Render / Railway
├── .env.example
├── static/
│   ├── css/style.css
│   ├── js/main.js
│   └── img/          put your photos here
└── templates/
    ├── base.html  index.html  menu.html  gallery.html
    ├── about.html  contact.html  book.html  booking_received.html  error.html
    ├── partials/tile.html
    └── admin/  layout.html  login.html  bookings.html  messages.html
```

## Run locally
```bash
python -m venv venv
source venv/bin/activate          # Windows: venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env              # Windows: copy .env.example .env
python app.py
```
- Site: http://127.0.0.1:5000
- Admin: http://127.0.0.1:5000/admin (default password `admin123`, change it in `.env`)

With `MAIL_SERVER` empty, emails are printed in the terminal instead of sent, so you can test without an email account.

## Customise for a real client
1. Edit `data.py`: name, address, hours, menu, capacity, team.
2. Add photos to `static/img/` and set the `image` field of each gallery item.
3. Change colours in the `:root` block at the top of `static/css/style.css`.
4. Fill in `.env` with a real `SECRET_KEY`, `ADMIN_PASSWORD` and SMTP details (Gmail needs an App Password).

## Deploy (Render, free tier)
1. Push to GitHub.
2. New Web Service on Render, build command `pip install -r requirements.txt`, start command `gunicorn app:app`.
3. Add the environment variables from `.env.example`.
4. SQLite resets on free hosting restarts. For a real client, add a Render PostgreSQL database and set `DATABASE_URL` (also add `psycopg2-binary` to requirements.txt).

## Ideas to extend
Email reminders the day before, an edit/reschedule link for guests, a table map, online menu photos, Google Analytics, tests with pytest.
