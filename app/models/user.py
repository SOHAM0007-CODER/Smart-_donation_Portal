from flask_login import UserMixin
from app import login_manager
from app.models.db import query_db


class User(UserMixin):
    def __init__(self, user_dict):
        self.id                = user_dict['id']
        self.name              = user_dict['name']
        self.email             = user_dict['email']
        self.password_hash     = user_dict['password_hash']
        self.role              = user_dict['role']
        self.is_verified       = bool(user_dict['is_verified'])
        self.is_active_flag    = bool(user_dict['is_active'])
        self.organization_name = user_dict.get('organization_name')
        self.registration_number = user_dict.get('registration_number')
        self.phone             = user_dict.get('phone')
        self.address           = user_dict.get('address')

    @property
    def is_active(self):
        return self.is_active_flag

    def is_admin(self):
        return self.role == 'admin'

    def is_ngo(self):
        return self.role == 'ngo'

    def is_donor(self):
        return self.role == 'donor'

    @staticmethod
    def get_by_id(user_id):
        row = query_db("SELECT * FROM users WHERE id = %s", (user_id,), one=True)
        return User(row) if row else None

    @staticmethod
    def get_by_email(email):
        row = query_db("SELECT * FROM users WHERE email = %s", (email,), one=True)
        return User(row) if row else None


@login_manager.user_loader
def load_user(user_id):
    return User.get_by_id(int(user_id))
