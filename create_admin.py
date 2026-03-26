"""
Run once after importing schema.sql to set the admin password properly.
Usage: python create_admin.py
"""
from werkzeug.security import generate_password_hash
import os
from dotenv import load_dotenv

load_dotenv()

try:
    import pymysql

    pymysql.install_as_MySQLdb()
except ModuleNotFoundError:
    pymysql = None

ADMIN_EMAIL    = 'admin@portal.com'
ADMIN_PASSWORD = 'Admin@123'   # Change this!
ADMIN_NAME     = 'Super Admin'

def main():
    if pymysql is None:
        raise RuntimeError("PyMySQL is not installed. Run: pip install -r requirements.txt")

    conn = pymysql.connect(
        host=os.getenv('MYSQL_HOST', 'localhost'),
        user=os.getenv('MYSQL_USER', 'root'),
        password=os.getenv('MYSQL_PASSWORD', ''),
        database=os.getenv('MYSQL_DB', 'smart_donation_portal'),
        port=int(os.getenv('MYSQL_PORT', '4000')),
    )
    cur = conn.cursor()

    # Remove placeholder admin
    cur.execute("DELETE FROM users WHERE role='admin'")

    # Insert real admin
    pwd = generate_password_hash(ADMIN_PASSWORD)
    cur.execute(
        "INSERT INTO users (name, email, password_hash, role, is_verified) VALUES (%s,%s,%s,'admin',1)",
        (ADMIN_NAME, ADMIN_EMAIL, pwd)
    )
    conn.commit()
    cur.close()
    conn.close()

    print(f"✅ Admin created: {ADMIN_EMAIL} / {ADMIN_PASSWORD}")
    print("⚠️  Change the password after first login!")


if __name__ == '__main__':
    main()
