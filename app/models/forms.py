from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from wtforms import (StringField, PasswordField, SelectField, TextAreaField,
                     DecimalField, DateField, BooleanField, HiddenField, IntegerField)
from wtforms.validators import (DataRequired, Email, EqualTo, Length,
                                NumberRange, Optional, ValidationError)


# ─── Auth ────────────────────────────────────────────────────────────────────

class RegistrationForm(FlaskForm):
    name  = StringField('Full Name',  validators=[DataRequired(), Length(2, 150)])
    email = StringField('Email',      validators=[DataRequired(), Email()])
    role  = SelectField('Register As', choices=[('donor', 'Donor'), ('ngo', 'NGO / Organisation')],
                        validators=[DataRequired()])
    organization_name    = StringField('Organisation Name',       validators=[Optional(), Length(max=200)])
    registration_number  = StringField('NGO Registration Number', validators=[Optional(), Length(max=100)])
    phone   = StringField('Phone',   validators=[Optional(), Length(max=20)])
    address = TextAreaField('Address', validators=[Optional(), Length(max=500)])
    password         = PasswordField('Password',         validators=[DataRequired(), Length(8, 128)])
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password')])

    def validate_role(self, field):
        if field.data == 'ngo':
            if not self.organization_name.data:
                raise ValidationError('Organisation name is required for NGO registration.')


class LoginForm(FlaskForm):
    email    = StringField('Email',    validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember = BooleanField('Remember Me')


# ─── Campaigns ───────────────────────────────────────────────────────────────

class CampaignForm(FlaskForm):
    title       = StringField('Campaign Title', validators=[DataRequired(), Length(5, 255)])
    description = TextAreaField('Description',  validators=[DataRequired(), Length(20)])
    category    = SelectField('Category', choices=[
        ('education',        'Education'),
        ('health',           'Health'),
        ('environment',      'Environment'),
        ('disaster_relief',  'Disaster Relief'),
        ('poverty',          'Poverty Alleviation'),
        ('animal_welfare',   'Animal Welfare'),
        ('other',            'Other'),
    ], validators=[DataRequired()])
    target_amount = DecimalField('Target Amount (₹)', places=2,
                                 validators=[DataRequired(), NumberRange(min=100)])
    start_date    = DateField('Start Date', validators=[DataRequired()])
    end_date      = DateField('End Date',   validators=[Optional()])
    image         = FileField('Campaign Image',
                              validators=[Optional(),
                                          FileAllowed(['jpg', 'jpeg', 'png', 'gif'], 'Images only')])


# ─── Donations ───────────────────────────────────────────────────────────────

class DonationForm(FlaskForm):
    campaign_id    = HiddenField('Campaign', validators=[DataRequired()])
    amount         = DecimalField('Amount (₹)', places=2,
                                  validators=[DataRequired(), NumberRange(min=1)])
    payment_method = SelectField('Payment Method', choices=[
        ('upi',           'UPI'),
        ('bank_transfer', 'Bank Transfer'),
        ('cheque',        'Cheque'),
        ('online',        'Online (Card/Netbanking)'),
        ('cash',          'Cash'),
    ], validators=[DataRequired()])
    transaction_id = StringField('Transaction / Reference ID', validators=[Optional(), Length(max=100)])
    payment_proof  = FileField('Upload Payment Proof',
                               validators=[DataRequired(),
                                           FileAllowed(['jpg', 'jpeg', 'png', 'pdf'], 'Images or PDF only')])
    message        = TextAreaField('Message (optional)', validators=[Optional(), Length(max=500)])
    is_anonymous   = BooleanField('Donate anonymously')


# ─── Expenses ────────────────────────────────────────────────────────────────

class ExpenseForm(FlaskForm):
    campaign_id  = SelectField('Campaign', coerce=int, validators=[DataRequired()])
    title        = StringField('Expense Title', validators=[DataRequired(), Length(3, 255)])
    description  = TextAreaField('Description', validators=[Optional()])
    amount       = DecimalField('Amount (₹)', places=2,
                                validators=[DataRequired(), NumberRange(min=1)])
    category     = SelectField('Category', choices=[
        ('salaries',        'Salaries / Wages'),
        ('supplies',        'Supplies / Materials'),
        ('infrastructure',  'Infrastructure'),
        ('transport',       'Transport / Logistics'),
        ('communication',   'Communication / Marketing'),
        ('events',          'Events / Programs'),
        ('miscellaneous',   'Miscellaneous'),
    ], validators=[DataRequired()])
    expense_date   = DateField('Expense Date', validators=[DataRequired()])
    vendor_name    = StringField('Vendor / Payee Name', validators=[Optional(), Length(max=200)])
    proof_document = FileField('Upload Proof Document',
                               validators=[DataRequired(),
                                           FileAllowed(['jpg', 'jpeg', 'png', 'pdf'], 'Images or PDF only')])


# ─── Admin note ───────────────────────────────────────────────────────────────

class AdminNoteForm(FlaskForm):
    admin_note = TextAreaField('Note (optional)', validators=[Optional(), Length(max=500)])
