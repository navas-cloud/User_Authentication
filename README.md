# PrivyDesk — Role-Based Access & File Management System

![Python](https://img.shields.io/badge/Python-3.10-3776AB?logo=python&logoColor=white)
![Django](https://img.shields.io/badge/Framework-Django-092E20?logo=django&logoColor=white)
![SQLite](https://img.shields.io/badge/DB-SQLite-003B57?logo=sqlite&logoColor=white)
![Bootstrap](https://img.shields.io/badge/UI-Bootstrap_5-7952B3?logo=bootstrap&logoColor=white)
![Status](https://img.shields.io/badge/Status-Active-brightgreen)

> A web-based role-based access control (RBAC) system where Admins, Managers, and Employees operate within strictly defined permission boundaries — with file management, category assignments, OTP-verified registration, and full activity audit logging.

---

## Problem Statement

In multi-user organizations, not everyone should access, upload, or manage all files. PrivyDesk enforces this by giving each role a scoped view and permission set — Admins control the full system, Managers oversee employee files and categories, and Employees access only their own uploads. Every action across all roles is timestamped and auditable.

---

## Screenshots

### Login Page
![Login](Output_Screenshots/login.png)

### Register
![Register](Output_Screenshots/Register.png)

### Profile Page
![Profile](Output_Screenshots/Profile.png)

### Categories
![Categories](Output_Screenshots/Categories.png)

### Log Activity
![Log_Activity](Output_Screenshots/Log_Activity.png)

---

## Features

| Feature | Roles | Description |
|---|---|---|
| OTP Email Verification | All | Email OTP sent on registration before account is created |
| Daily Passcode for Roles | Admin / Manager | SHA-256 date-based passcode required to register as Admin or Manager |
| Login / Logout | All | Django session-based auth with activity logging |
| Forgot Password | All | Username-based password reset |
| Role-based Dashboard | All | Scoped stats — file count, category count, user count, upload charts |
| File Upload | All | Upload any file type with title and description |
| File Edit / Delete | Admin, Manager | Edit or delete any uploaded file; employees edit own only |
| Category Management | Admin, Manager | Create categories, assign files to categories, reassign to employees |
| File Access Control | Admin, Manager | Grant view/edit permissions per file per employee |
| User List | Admin, Manager | Paginated view of all registered users |
| Delete User | Admin only | Remove any user except self |
| Profile Management | All | Edit profile with photo, DOB, phone, city, country, postal code |
| Activity Log | Admin only | Paginated, timestamped log of every action across all users |
| Upload Analytics Chart | All | 7-day upload trend + category-wise file distribution (JSON API) |

---

## Tech Stack

| Layer | Technology |
|---|---|
| Language | Python 3.x |
| Backend Framework | Django |
| Frontend | Bootstrap 5, JavaScript, HTML, CSS |
| Database | SQLite |
| ORM | Django ORM |
| Authentication | `django.contrib.auth` — `AbstractUser` extended with role field |
| Email | Django `send_mail` (SMTP) — for OTP delivery |
| File Storage | Django `MEDIA_ROOT` — local filesystem |
| Templating | Django Templates |

---

## Project Structure

```
Auth_Project/
│
├── Auth_Project/               # Django project config
│   ├── settings.py
│   ├── urls.py
│   ├── wsgi.py
│   └── static/
│
├── UserApp/                    # Main application
│   ├── models.py               # CustomUser, Profile, File, Category,
│   │                           # FileCategoryMapping, FileAccess, ActivityLog
│   ├── views.py                # All view logic (auth, dashboard, files, users, logs)
│   ├── urls.py                 # All URL routes
│   ├── forms.py                # Registration, login, profile, file, category forms
│   ├── decorator.py            # Custom @role_required decorator
│   ├── utils.py                # OTP generator, daily passcode (SHA-256), log helper
│   ├── admin.py
│   ├── apps.py
│   │
│   ├── templates/              # All HTML pages
│   │   ├── base.html           # Bootstrap base layout
│   │   ├── login.html
│   │   ├── register.html
│   │   ├── forgot_password.html
│   │   ├── dashboard.html      # Stats + upload chart
│   │   ├── file_upload.html    # Upload + paginated file list
│   │   ├── file_edit.html
│   │   ├── file_list.html
│   │   ├── category_list.html  # Assign files to categories + employees
│   │   ├── user_list.html
│   │   ├── profile.html
│   │   ├── edit_profile.html
│   │   ├── activity_log.html
│   │   └── logout.html
│   │
│   ├── static/
│   │   └── style.css
│   │
│   ├── templatetags/
│   │   └── custom_tags.py
│   │
│   └── migrations/             # 11 migration files
│
├── media/                      # User-uploaded files (runtime)
│   ├── uploads/
│   └── profile_pics/
│
├── db.sqlite3
└── manage.py
```

---

## Database Schema

```
CustomUser  (extends AbstractUser)      Profile
──────────────────────────────          ───────────────────────
id (PK)                                 id (PK)
username                                user_id (FK → CustomUser)
password (hashed)                       firstname, lastname
email                                   dob, phone, email
role → admin | manager | employee       country, city, postalcode
                                        profile_image


File                                    Category
──────────────────────────              ──────────────
id (PK)                                 id (PK)
title, description                      name
file (FileField)                        description
uploader_id (FK → CustomUser)
uploaded_at, updated_at
updated_by_id (FK → CustomUser)


FileCategoryMapping                     FileAccess
────────────────────────────            ──────────────────────
id (PK)                                 id (PK)
file_id (FK → File)                     file_id (FK → File)
category_id (FK → Category)             user_id (FK → CustomUser)
assigned_by_id (FK → CustomUser)        can_view (bool)
assigned_to_id (FK → CustomUser)        can_edit (bool)
assigned_at
reassigned_by_id (FK → CustomUser)      ActivityLog
reassigned_at                           ──────────────────────
                                        id (PK)
                                        user_id (FK → CustomUser)
                                        role (CharField)
                                        action (TextField)
                                        created_at
```

---

## Role & Permission Matrix

| Action | Employee | Manager | Admin |
|---|:---:|:---:|:---:|
| Register with OTP verification | ✅ | ✅ (passcode) | ✅ (passcode) |
| Login / Logout | ✅ | ✅ | ✅ |
| View own dashboard | ✅ | ✅ | ✅ |
| Upload files | ✅ | ✅ | ✅ |
| Edit / Delete own files | ✅ | ✅ | ✅ |
| Edit / Delete any file | ❌ | ✅ | ✅ |
| Manage categories and assignments | ❌ | ✅ | ✅ |
| View user list | ❌ | ✅ | ✅ |
| Delete users | ❌ | ❌ | ✅ |
| View activity log | ❌ | ❌ | ✅ |

---

## Security Design

- **OTP email verification** — registration is blocked until the email OTP is confirmed via AJAX; OTP state is stored server-side in Django session
- **Daily passcode for privileged roles** — Admin/Manager registration requires a SHA-256 date-hashed passcode that rotates every day, preventing unauthorized role escalation
- **Custom `@role_required` decorator** — applied at view level; unauthorized role access silently redirects to dashboard
- **`AbstractUser` role field** — role stored directly on the user object, making permission checks a single attribute lookup (`user.role`) with no extra DB query
- **Activity logging on every state change** — login, logout, upload, edit, delete, password reset, and profile updates all write to `ActivityLog`

---

## Getting Started

### Prerequisites

```bash
Python 3.8+
pip
A configured SMTP email account (for OTP delivery)
```

### Installation

```bash
# Clone the repo
git clone https://github.com/navas-cloud/User_Authentication.git
cd User_Authentication/Auth_Project

# Install dependencies
pip install -r requirements.txt

# Configure email settings in settings.py
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = 'your@email.com'
EMAIL_HOST_PASSWORD = 'your_app_password'

# Run migrations
python manage.py makemigrations
python manage.py migrate

# Start the server
python manage.py runserver
```

Open **http://127.0.0.1:8000** in your browser.

---

## Generating the Admin/Manager Passcode

Admin and Manager roles require a daily passcode during registration. Run this to get today's passcode:

```bash
python manage.py shell
>>> from UserApp.utils import get_daily_passcode
>>> print(get_daily_passcode())
# Example output: A3F9C2
```

The passcode is SHA-256 hashed from today's date and rotates automatically every day.

---

## API Endpoints

| Method | Endpoint | Access | Description |
|---|---|---|---|
| GET/POST | `/` | Public | Login |
| GET | `/register/` | Public | Register page |
| POST | `/send-otp/` | Public | Send OTP to email |
| POST | `/verify-otp/` | Public | Verify OTP (AJAX) |
| POST | `/register-submit/` | Public | Create account |
| GET | `/dashboard/` | All | Role-based dashboard |
| GET | `/dashboard/chart-data/` | All | Upload chart JSON API |
| GET/POST | `/filesupload/` | All | Upload and view files |
| POST | `/files/edit/<id>/` | Manager, Admin | Edit file |
| POST | `/files/delete/<id>/` | Manager, Admin | Delete file |
| GET/POST | `/categories/` | Manager, Admin | Manage categories and assignments |
| GET | `/user_list/` | Manager, Admin | View all users |
| POST | `/users/delete/<id>/` | Admin | Delete user |
| GET | `/activity-log/` | Admin | View audit log |
| GET/POST | `/profile/edit/` | All | Edit profile |

---

## Key Engineering Decisions

- **`AbstractUser` over a profile-only model for roles** — role is a first-class field on the user object; permission checks in views and decorators are a single attribute lookup with no extra join
- **SHA-256 date-based daily passcode** — lightweight, stateless privileged registration gate without needing an invite system or separate admin approval flow
- **Custom `@role_required` decorator** — centralizes access control; adding a new protected view is one decorator line, not repeated if-else blocks across views
- **AJAX OTP flow with server-side session state** — OTP stored in Django session, verified before `register_submit` proceeds; prevents form bypass and client-side OTP exposure
- **`FileCategoryMapping` as a dedicated model** — decouples file-to-category assignment from the `File` model itself; supports full reassignment history (`reassigned_by`, `reassigned_at`) without mutating original records
- **`ActivityLog` written inline in every view** — explicit `log_activity()` call before each response; no signals or middleware, making the audit trail easy to trace and test

---

## What I'd Improve Next

- [ ] Migrate SQLite to PostgreSQL for production readiness
- [ ] Add Django REST Framework to expose a proper API layer
- [ ] Write `pytest` / Django `TestCase` unit tests for auth, OTP flow, and role decorator
- [ ] Dockerize with `docker-compose` (app + DB)
- [ ] Deploy to AWS EC2 with RDS (PostgreSQL)
- [ ] Replace username-based password reset with a secure email token link
- [ ] Add password strength validation on registration form

---

## Author

**MohammedNavas A**
[LinkedIn](https://linkedin.com/in/mohammed-navas-a-) · [GitHub](https://github.com/navas-cloud) · navash.a.v012@gmail.com
