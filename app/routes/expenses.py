from flask import Blueprint, render_template, redirect, url_for, flash, request, abort
from flask_login import login_required, current_user
from app.models.db import query_db
from app.models.forms import ExpenseForm
from app.models.utils import save_upload, log_activity

expenses_bp = Blueprint('expenses', __name__)


@expenses_bp.route('/log', methods=['GET', 'POST'])
@login_required
def log_expense():
    if not current_user.is_ngo():
        abort(403)
    if not current_user.is_verified:
        flash('Your NGO must be verified before logging expenses.', 'warning')
        return redirect(url_for('main.index'))

    # Only campaigns belonging to this NGO
    ngo_campaigns = query_db(
        "SELECT id, title FROM campaigns WHERE ngo_id=%s AND status='active'",
        (current_user.id,)
    )
    if not ngo_campaigns:
        flash('You have no active campaigns to log expenses for.', 'warning')
        return redirect(url_for('main.index'))

    form = ExpenseForm()
    form.campaign_id.choices = [(c['id'], c['title']) for c in ngo_campaigns]

    if form.validate_on_submit():
        # Validate campaign ownership
        campaign = query_db(
            "SELECT id FROM campaigns WHERE id=%s AND ngo_id=%s",
            (form.campaign_id.data, current_user.id), one=True
        )
        if not campaign:
            abort(403)

        proof = save_upload(request.files.get('proof_document'), 'EXPENSE_PROOF_FOLDER')
        if not proof:
            flash('Proof document upload failed.', 'danger')
            return render_template('expenses/log.html', form=form)

        eid = query_db(
            """INSERT INTO expenses (campaign_id, ngo_id, title, description, amount,
               category, expense_date, vendor_name, proof_document)
               VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s)""",
            (form.campaign_id.data, current_user.id, form.title.data,
             form.description.data, form.amount.data, form.category.data,
             form.expense_date.data, form.vendor_name.data, proof),
            commit=True
        )
        log_activity(current_user.id, 'EXPENSE_SUBMIT', f"Expense {eid} submitted")
        flash('Expense logged! Awaiting admin approval.', 'success')
        return redirect(url_for('auth.profile'))

    return render_template('expenses/log.html', form=form)


@expenses_bp.route('/campaign/<int:campaign_id>')
def campaign_expenses(campaign_id):
    expenses = query_db(
        "SELECT * FROM expenses WHERE campaign_id=%s AND status='approved' ORDER BY expense_date DESC",
        (campaign_id,)
    )
    return render_template('expenses/list.html', expenses=expenses, campaign_id=campaign_id)
