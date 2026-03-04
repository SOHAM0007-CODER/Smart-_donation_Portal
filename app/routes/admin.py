from flask import Blueprint, render_template, redirect, url_for, flash, request, abort
from flask_login import login_required, current_user
from functools import wraps
from app.models.db import query_db
from app.models.utils import log_activity

admin_bp = Blueprint('admin', __name__)


def admin_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if not current_user.is_authenticated or not current_user.is_admin():
            abort(403)
        return f(*args, **kwargs)
    return decorated


@admin_bp.route('/dashboard')
@login_required
@admin_required
def dashboard():
    stats = query_db(
        """SELECT
            (SELECT COUNT(*) FROM users WHERE role='ngo') as total_ngos,
            (SELECT COUNT(*) FROM users WHERE role='ngo' AND is_verified=0) as pending_ngos,
            (SELECT COUNT(*) FROM donations WHERE status='pending') as pending_donations,
            (SELECT COUNT(*) FROM expenses WHERE status='pending') as pending_expenses,
            (SELECT COUNT(*) FROM campaigns WHERE status='active') as active_campaigns,
            (SELECT COALESCE(SUM(amount),0) FROM donations WHERE status='approved') as total_approved
        """, one=True
    )
    recent_activity = query_db(
        """SELECT al.*, u.name as user_name, u.role
           FROM activity_log al LEFT JOIN users u ON al.user_id=u.id
           ORDER BY al.created_at DESC LIMIT 20"""
    )
    return render_template('admin/dashboard.html', stats=stats, recent_activity=recent_activity)


# ── NGO Management ────────────────────────────────────────────────────────────

@admin_bp.route('/ngos')
@login_required
@admin_required
def ngos():
    all_ngos = query_db(
        "SELECT * FROM users WHERE role='ngo' ORDER BY created_at DESC"
    )
    return render_template('admin/ngos.html', ngos=all_ngos)


@admin_bp.route('/ngos/<int:ngo_id>/verify', methods=['POST'])
@login_required
@admin_required
def verify_ngo(ngo_id):
    action = request.form.get('action')
    if action == 'approve':
        query_db("UPDATE users SET is_verified=1 WHERE id=%s AND role='ngo'",
                 (ngo_id,), commit=True)
        log_activity(current_user.id, 'NGO_VERIFIED', f"NGO {ngo_id} verified")
        flash('NGO verified successfully.', 'success')
    elif action == 'reject':
        query_db("UPDATE users SET is_active=0 WHERE id=%s AND role='ngo'",
                 (ngo_id,), commit=True)
        log_activity(current_user.id, 'NGO_REJECTED', f"NGO {ngo_id} deactivated")
        flash('NGO account deactivated.', 'warning')
    return redirect(url_for('admin.ngos'))


# ── Donations Management ──────────────────────────────────────────────────────

@admin_bp.route('/donations')
@login_required
@admin_required
def donations():
    status = request.args.get('status', 'pending')
    rows = query_db(
        """SELECT d.*, u.name as donor_name, c.title as campaign_title
           FROM donations d
           JOIN users u ON d.donor_id=u.id
           JOIN campaigns c ON d.campaign_id=c.id
           WHERE d.status=%s ORDER BY d.created_at DESC""",
        (status,)
    )
    return render_template('admin/donations.html', donations=rows, status=status)


@admin_bp.route('/donations/<int:donation_id>/action', methods=['POST'])
@login_required
@admin_required
def donation_action(donation_id):
    action    = request.form.get('action')
    note      = request.form.get('admin_note', '')
    donation  = query_db("SELECT * FROM donations WHERE id=%s", (donation_id,), one=True)
    if not donation or donation['status'] != 'pending':
        flash('Donation not found or already processed.', 'danger')
        return redirect(url_for('admin.donations'))

    if action == 'approve':
        query_db(
            "UPDATE donations SET status='approved', admin_note=%s, approved_by=%s, approved_at=NOW() WHERE id=%s",
            (note, current_user.id, donation_id), commit=True
        )
        # Update campaign current_amount
        query_db(
            "UPDATE campaigns SET current_amount=current_amount+%s WHERE id=%s",
            (donation['amount'], donation['campaign_id']), commit=True
        )
        log_activity(current_user.id, 'DONATION_APPROVED', f"Donation {donation_id} approved")
        flash('Donation approved and campaign balance updated.', 'success')
    elif action == 'reject':
        query_db(
            "UPDATE donations SET status='rejected', admin_note=%s, approved_by=%s, approved_at=NOW() WHERE id=%s",
            (note, current_user.id, donation_id), commit=True
        )
        log_activity(current_user.id, 'DONATION_REJECTED', f"Donation {donation_id} rejected")
        flash('Donation rejected.', 'warning')

    return redirect(url_for('admin.donations'))


# ── Expenses Management ───────────────────────────────────────────────────────

@admin_bp.route('/expenses')
@login_required
@admin_required
def expenses():
    status = request.args.get('status', 'pending')
    rows = query_db(
        """SELECT e.*, u.organization_name as ngo_name, c.title as campaign_title
           FROM expenses e
           JOIN users u ON e.ngo_id=u.id
           JOIN campaigns c ON e.campaign_id=c.id
           WHERE e.status=%s ORDER BY e.created_at DESC""",
        (status,)
    )
    return render_template('admin/expenses.html', expenses=rows, status=status)


@admin_bp.route('/expenses/<int:expense_id>/action', methods=['POST'])
@login_required
@admin_required
def expense_action(expense_id):
    action  = request.form.get('action')
    note    = request.form.get('admin_note', '')
    expense = query_db("SELECT * FROM expenses WHERE id=%s", (expense_id,), one=True)
    if not expense or expense['status'] != 'pending':
        flash('Expense not found or already processed.', 'danger')
        return redirect(url_for('admin.expenses'))

    if action == 'approve':
        query_db(
            "UPDATE expenses SET status='approved', admin_note=%s, approved_by=%s, approved_at=NOW() WHERE id=%s",
            (note, current_user.id, expense_id), commit=True
        )
        query_db(
            "UPDATE campaigns SET total_expenses=total_expenses+%s WHERE id=%s",
            (expense['amount'], expense['campaign_id']), commit=True
        )
        log_activity(current_user.id, 'EXPENSE_APPROVED', f"Expense {expense_id} approved")
        flash('Expense approved.', 'success')
    elif action == 'reject':
        query_db(
            "UPDATE expenses SET status='rejected', admin_note=%s, approved_by=%s, approved_at=NOW() WHERE id=%s",
            (note, current_user.id, expense_id), commit=True
        )
        log_activity(current_user.id, 'EXPENSE_REJECTED', f"Expense {expense_id} rejected")
        flash('Expense rejected.', 'warning')

    return redirect(url_for('admin.expenses'))


# ── Suspicious Activity ───────────────────────────────────────────────────────

@admin_bp.route('/suspicious')
@login_required
@admin_required
def suspicious():
    # Flag: >3 donations from same IP within 1 hour
    suspicious_ips = query_db(
        """SELECT al.ip_address, COUNT(*) as cnt, MAX(al.created_at) as last_seen
           FROM activity_log al
           WHERE al.action='DONATION_SUBMIT'
             AND al.created_at > NOW() - INTERVAL 24 HOUR
           GROUP BY al.ip_address
           HAVING cnt >= 3
           ORDER BY cnt DESC"""
    )
    # Large donations (above 3× average)
    large_donations = query_db(
        """SELECT d.*, u.name as donor_name, c.title as campaign_title
           FROM donations d JOIN users u ON d.donor_id=u.id
           JOIN campaigns c ON d.campaign_id=c.id
           WHERE d.amount > (SELECT AVG(amount)*3 FROM donations)
             AND d.status='pending'
           ORDER BY d.amount DESC LIMIT 20"""
    )
    return render_template('admin/suspicious.html',
                           suspicious_ips=suspicious_ips,
                           large_donations=large_donations)
