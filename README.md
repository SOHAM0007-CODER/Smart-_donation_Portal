# 🌐 Smart Donation Transparency Portal

A full-stack Flask + MySQL web application for transparent NGO donation management with role-based access, payment proof verification, expense tracking, and a public transparency dashboard.

---

## 🗂️ Project Structure

```
smart_donation_portal/
├── run.py                        # App entry point
├── create_admin.py               # One-time admin setup script
├── schema.sql                    # Full MySQL database schema
├── requirements.txt
├── .env.example                  # Environment config template
└── app/
    ├── __init__.py               # App factory + extensions
    ├── models/
    │   ├── db.py                 # MySQL helper (query_db)
    │   ├── user.py               # User model (Flask-Login)
    │   ├── forms.py              # All WTForms (CSRF-protected)
    │   └── utils.py              # File upload + activity logging
    ├── routes/
    │   ├── auth.py               # Register, login, logout, profile
    │   ├── main.py               # Homepage + transparency dashboard
    │   ├── campaigns.py          # Campaign CRUD (NGO-only create/edit)
    │   ├── donations.py          # Donate form + my donations
    │   ├── expenses.py           # Expense logging (NGO-only)
    │   └── admin.py              # Admin dashboard + all approvals
    ├── templates/
    │   ├── base.html
    │   ├── 404.html
    │   ├── main/                 # index.html, transparency.html
    │   ├── auth/                 # login, register, profile
    │   ├── campaigns/            # list, detail, create (edit)
    │   ├── donations/            # donate, my_donations
    │   ├── expenses/             # log.html
    │   └── admin/                # dashboard, ngos, donations, expenses, suspicious
    └── static/
        ├── css/main.css
        ├── js/main.js
        └── uploads/
            ├── payment_proofs/
            ├── expense_proofs/
            └── campaign_images/
```

---

## 🚀 Step-by-Step Setup

### 1. Prerequisites

- Python 3.9+
- MySQL 8.0+ (or MariaDB 10.5+)
- `pip`, `virtualenv`

### 2. Clone / Extract the project

```bash
cd smart_donation_portal
```

### 3. Create virtual environment

```bash
python -m venv venv
# Linux/Mac:
source venv/bin/activate
# Windows:
venv\Scripts\activate
```

### 4. Install dependencies

```bash
pip install -r requirements.txt
```

> If you see `Exception: Install 'email_validator' for email validation support.`, install `email-validator` (it’s included in `requirements.txt`).

> **On Ubuntu/Debian**, you may need:
> ```bash
> sudo apt-get install python3-dev default-libmysqlclient-dev build-essential
> ```

### 5. Configure environment

```bash
cp .env.example .env
# Edit .env with your MySQL credentials and a strong SECRET_KEY
```

## Team Setup

For local development, each team member must create their own `.env` file (it is intentionally git-ignored).

1. Copy the template:

```bash
cp .env.example .env
```

2. Fill in your TiDB Cloud credentials (TiDB Serverless uses `MYSQL_PORT=4000`):

- `SECRET_KEY` (required)
- `MYSQL_HOST`
- `MYSQL_PORT=4000`
- `MYSQL_USER`
- `MYSQL_PASSWORD`
- `MYSQL_DB`

### 6. Create the database

```bash
mysql -u root -p
```
```sql
CREATE DATABASE smart_donation_portal CHARACTER SET utf8mb4;
EXIT;
```

### 7. Import the schema

```bash
mysql -u root -p smart_donation_portal < schema.sql
```

### 8. Create the admin user

```bash
python create_admin.py
```

This creates:
- **Email:** `admin@portal.com`
- **Password:** `Admin@123`

> ⚠️ Change the password in `create_admin.py` before running in production!

### 9. Run the application

```bash
python run.py
```

Open: **http://localhost:5000**

---

## 👥 User Roles

| Role  | Capabilities |
|-------|-------------|
| **donor** | Browse campaigns, donate with proof upload, view own donations |
| **ngo** | Create campaigns (after verification), log expenses |
| **admin** | Verify NGOs, approve/reject donations & expenses, monitor suspicious activity |

---

## 🔑 Default Credentials

| Role  | Email | Password |
|-------|-------|----------|
| Admin | admin@portal.com | Admin@123 |

Register new donors and NGOs through the `/auth/register` page.

---

## ✨ Key Features

### 🏗️ Architecture
- **MVC pattern** with Flask blueprints
- **Flask-Login** session management
- **Flask-WTF** CSRF protection on all forms
- **Secure file upload** with UUID filenames + extension whitelist

### 📊 Transparency Dashboard (`/transparency/<campaign_id>`)
- Total collected vs spent vs remaining balance
- Animated dual progress bars
- Public donor list (with anonymous option)
- Chronological expense timeline

### 🔐 Security
- Passwords hashed with PBKDF2-SHA256 (Werkzeug)
- CSRF tokens on every form
- Role-based route decorators (`admin_required`, `ngo_required`)
- File type validation (whitelist) + size limit (10 MB)
- Activity logging for audit trail
- Suspicious activity detection (high-frequency IPs, unusually large donations)

### 💡 Admin Dashboard
- Pending NGO verifications
- Donation payment proof review (view uploaded document before approving)
- Expense proof review
- Suspicious activity monitor (IP frequency + outlier amounts)
- Real-time activity log

---

## 🗄️ Database Tables

| Table | Purpose |
|-------|---------|
| `users` | Donors, NGOs, Admin with role column |
| `campaigns` | NGO campaigns with progress tracking |
| `donations` | Donor payments with proof and verification status |
| `expenses` | NGO expenses with proof and verification status |
| `activity_log` | Full audit trail of all user actions |

---

## 📦 Dependencies

```
Flask==3.0.0
Flask-Login==0.6.3
Flask-WTF==1.2.1
Flask-MySQLdb==1.0.1
Werkzeug==3.0.1
WTForms==3.1.1
PyMySQL==1.1.0
python-dotenv==1.0.0
Pillow==10.1.0
```

---

## 🚦 Common Issues

**`OperationalError: Can't connect to MySQL`**  
→ Check MySQL is running and `.env` credentials are correct.

**`ModuleNotFoundError: No module named 'MySQLdb'`**  
→ Install dependencies from `requirements.txt` (this project uses `PyMySQL`, which provides a `MySQLdb`-compatible shim).

**File uploads not showing**  
→ Ensure the `app/static/uploads/` subfolders exist (auto-created on startup).

---

## 🔒 Production Checklist

- [ ] Set a strong `SECRET_KEY` in `.env`
- [ ] Set `debug=False` in `run.py`
- [ ] Use Gunicorn/uWSGI behind Nginx
- [ ] Enable HTTPS (SSL certificate)
- [ ] Change default admin password
- [ ] Set `MYSQL_PASSWORD` to a strong password
- [ ] Configure proper file storage (e.g., AWS S3) for uploads
