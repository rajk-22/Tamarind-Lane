"""All the restaurant's content lives here. Edit this file to rebrand the site."""

RESTAURANT = {
    "name": "Tamarind Lane",
    "tagline": "Modern South Indian kitchen",
    "address_lines": ["14, 12th Main, Indiranagar", "Bengaluru 560038"],
    "phone": "+91 80 5550 0142",
    "email": "hello@tamarindlane.example",
    "maps_url": "https://www.google.com/maps/search/?api=1&query=Indiranagar+Bengaluru",
    "instagram": "https://instagram.com/",
}

TIMEZONE = "Asia/Kolkata"

# Weekday numbers: Monday=0 ... Sunday=6
# Hours the restaurant is open (used for the "Open now" badge).
OPEN_HOURS = {
    1: [("12:00", "15:30"), ("19:00", "23:00")],
    2: [("12:00", "15:30"), ("19:00", "23:00")],
    3: [("12:00", "15:30"), ("19:00", "23:00")],
    4: [("12:00", "15:30"), ("19:00", "23:00")],
    5: [("12:00", "23:00")],
    6: [("12:00", "23:00")],
}

# Earliest and latest table times guests can book, in 30-minute steps.
BOOKING_WINDOWS = {
    1: [("12:00", "14:30"), ("19:00", "22:00")],
    2: [("12:00", "14:30"), ("19:00", "22:00")],
    3: [("12:00", "14:30"), ("19:00", "22:00")],
    4: [("12:00", "14:30"), ("19:00", "22:00")],
    5: [("12:00", "22:00")],
    6: [("12:00", "22:00")],
}

HOURS_DISPLAY = [
    ("Monday", "Closed"),
    ("Tuesday to Friday", "12 pm to 3:30 pm, 7 pm to 11 pm"),
    ("Saturday and Sunday", "12 pm to 11 pm"),
]

SLOT_MINUTES = 30
SEATS_PER_SLOT = 30      # total guests we can seat per time slot
MAX_PARTY = 10           # largest party bookable online
ADVANCE_DAYS = 60        # how far ahead guests can book
MIN_LEAD_MINUTES = 60    # stop taking bookings this long before the slot

DAY_NAMES = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]

MENU = [
    {
        "category": "To start",
        "items": [
            {"name": "Podi idli bites", "desc": "Fried mini idlis tossed in gunpowder, curry leaf and ghee.", "price": 280, "tags": ["V"]},
            {"name": "Pepper mushroom fry", "desc": "Button mushrooms, crushed pepper, shallots, coconut shavings.", "price": 340, "tags": ["VG", "GF"]},
            {"name": "Guntur chilli chicken", "desc": "Crisp thigh pieces in a hot Andhra chilli glaze.", "price": 380, "tags": []},
            {"name": "Gunpowder prawns", "desc": "Tiger prawns, roasted lentil spice, lime, curry leaf oil.", "price": 460, "tags": ["GF"], "signature": True},
        ],
    },
    {
        "category": "Mains",
        "items": [
            {"name": "Ghee roast dosa", "desc": "Paper-thin and crackling, with three chutneys and sambar.", "price": 320, "tags": ["V"], "signature": True},
            {"name": "Malabar vegetable stew", "desc": "Seasonal vegetables in coconut milk, served with lacy appam.", "price": 420, "tags": ["VG"]},
            {"name": "Meen moilee", "desc": "Seer fish in a gentle coconut and green chilli curry.", "price": 520, "tags": ["GF"]},
            {"name": "Chettinad lamb pepper roast", "desc": "Slow-cooked shoulder, black pepper, fennel, fresh curry leaf.", "price": 560, "tags": ["GF"], "signature": True},
            {"name": "Dindigul chicken biryani", "desc": "Seeraga samba rice, pepper-heavy masala, onion raita.", "price": 440, "tags": []},
        ],
    },
    {
        "category": "To finish",
        "items": [
            {"name": "Filter coffee tiramisu", "desc": "Decoction-soaked sponge, mascarpone, jaggery dust.", "price": 320, "tags": ["V"]},
            {"name": "Jaggery payasam brulee", "desc": "Rice and milk pudding with a burnt jaggery crust.", "price": 280, "tags": ["V", "GF"]},
            {"name": "Tender coconut panna cotta", "desc": "Set with agar, served with cardamom mango.", "price": 300, "tags": ["V", "GF"]},
        ],
    },
    {
        "category": "To drink",
        "items": [
            {"name": "Filter kaapi", "desc": "Chicory-blend decoction, hot milk, brass tumbler.", "price": 120, "tags": ["V"]},
            {"name": "Spiced buttermilk", "desc": "Curd, ginger, green chilli, curry leaf.", "price": 140, "tags": ["V", "GF"]},
            {"name": "Tamarind sour", "desc": "Tamarind, lime, black salt, soda. No alcohol.", "price": 220, "tags": ["VG", "GF"]},
            {"name": "Kokum cooler", "desc": "Kokum, rose, roasted cumin, crushed ice.", "price": 200, "tags": ["VG", "GF"]},
        ],
    },
]

# Set "image" to a filename inside static/img/ once you have real photos.
GALLERY = [
    {"caption": "Ghee roast dosa, straight off the tawa", "tone": "a", "image": None, "wide": True},
    {"caption": "The pass at Friday dinner", "tone": "b", "image": None},
    {"caption": "Filter kaapi in brass", "tone": "c", "image": None},
    {"caption": "Chettinad lamb pepper roast", "tone": "b", "image": None},
    {"caption": "Corner table by the window", "tone": "a", "image": None},
    {"caption": "Tamarind sour and kokum cooler", "tone": "c", "image": None, "wide": True},
]

TEAM = [
    {"name": "Meera Raghavan", "role": "Chef and co-owner", "bio": "Grew up between Madurai and Mysuru. Spent eight years cooking in Chennai and Copenhagen before coming home to open Tamarind Lane."},
    {"name": "Arjun Nair", "role": "Co-owner and front of house", "bio": "Runs the floor and the coffee. Believes a good meal starts with someone remembering your name."},
]
