import hashlib
from datetime import date
import random
from .models import ActivityLog

def get_daily_passcode():
    today_str = date.today().strftime("%Y-%m-%d")
    hash_str = hashlib.sha256(today_str.encode()).hexdigest()[:6].upper()
    return hash_str

def generate_email_otp():
    return str(random.randint(100000, 999999))

def log_activity(user, action):
    """
    Logs an activity with the username, role, and timestamp.
    """
    role = getattr(user, 'role', 'Anonymous') if user else 'Anonymous'
    ActivityLog.objects.create(user=user, role=role, action=action)

