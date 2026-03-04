from flask import Blueprint, render_template, redirect, url_for, flash, request, abort
from flask_login import login_required, current_user
from app.models.db import query_db
from app.models.forms import DonationForm
from app.models.utils import save_upload, log_activity

donations_bp = Blueprint('donations', __name__)


@donations_bp.route('/donate/<int:campaign_id>', methods=['GET', 'POST'])
@login_required
def donate(campaign_id):
    if not current_user.is_donor():
        flash('Only donors can make donations.', 'warning')
        return redirect(url_for('campaigns.detail', campaign_id=campaign_id))

    campaign = query_db(
        "SELECT c.*, u.organization_name FROM campaigns c JOIN users u ON c.ngo_id=u.id "
        "WHERE c.id=%s AND c.status='active'",
        (campaign_id,), one=True
    )
    if not campaign:
        abort(404)

    form = DonationForm()
    form.campaign_id.data = campaign_id

    if form.validate_on_submit():
        proof_file = save_upload(request.files.get('payment_proof'), 'PAYMENT_PROOF_FOLDER')
        if not proof_file:
            flash('Payment proof upload failed or file type not allowed.', 'danger')
            return render_template('donations/donate.html', form=form, campaign=campaign)

        did = query_db(
            """INSERT INTO donations (campaign_id, donor_id, amount, payment_method,
               transaction_id, payment_proof, message, is_anonymous)
               VALUES (%s,%s,%s,%s,%s,%s,%s,%s)""",
            (campaign_id, current_user.id, form.amount.data,
             form.payment_method.data, form.transaction_id.data,
             proof_file, form.message.data, int(form.is_anonymous.data)),
            commit=True
        )
        log_activity(current_user.id, 'DONATION_SUBMIT',
                     f"Donation {did} submitted for campaign {campaign_id}")
        flash('Donation submitted! It will appear after admin verification.', 'success')
        return redirect(url_for('campaigns.detail', campaign_id=campaign_id))

    return render_template('donations/donate.html', form=form, campaign=campaign)


@donations_bp.route('/my-donations')
@login_required
def my_donations():
    donations = query_db(
        """SELECT d.*, c.title as campaign_title
           FROM donations d JOIN campaigns c ON d.campaign_id=c.id
           WHERE d.donor_id=%s ORDER BY d.created_at DESC""",
        (current_user.id,)
    )
    return render_template('donations/my_donations.html', donations=donations)
