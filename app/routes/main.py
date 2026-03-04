from flask import Blueprint, render_template
from app.models.db import query_db
from app.models.utils import progress_percent

main_bp = Blueprint('main', __name__)


@main_bp.route('/')
def index():
    # Stats for hero section
    stats = query_db(
        """SELECT
            (SELECT COUNT(*) FROM campaigns WHERE status='active') as active_campaigns,
            (SELECT COALESCE(SUM(amount),0) FROM donations WHERE status='approved') as total_donated,
            (SELECT COUNT(DISTINCT donor_id) FROM donations WHERE status='approved') as total_donors,
            (SELECT COUNT(*) FROM users WHERE role='ngo' AND is_verified=1) as verified_ngos
        """, one=True
    )
    featured = query_db(
        """SELECT c.*, u.organization_name, u.is_verified,
                  ROUND((c.current_amount/c.target_amount)*100,1) as pct
           FROM campaigns c JOIN users u ON c.ngo_id = u.id
           WHERE c.status='active' AND u.is_verified=1
           ORDER BY c.current_amount DESC LIMIT 6"""
    )
    return render_template('main/index.html', stats=stats, featured=featured,
                           progress_percent=progress_percent)


@main_bp.route('/transparency/<int:campaign_id>')
def transparency(campaign_id):
    campaign = query_db(
        """SELECT c.*, u.organization_name, u.is_verified, u.name as ngo_name,
                  u.phone as ngo_phone
           FROM campaigns c JOIN users u ON c.ngo_id = u.id
           WHERE c.id = %s""",
        (campaign_id,), one=True
    )
    if not campaign:
        return render_template('404.html'), 404

    donations = query_db(
        """SELECT d.amount, d.created_at, d.is_anonymous,
                  CASE WHEN d.is_anonymous=1 THEN 'Anonymous' ELSE u.name END as donor_name,
                  d.message
           FROM donations d JOIN users u ON d.donor_id = u.id
           WHERE d.campaign_id = %s AND d.status='approved'
           ORDER BY d.created_at DESC""",
        (campaign_id,)
    )
    expenses = query_db(
        """SELECT * FROM expenses WHERE campaign_id = %s AND status='approved'
           ORDER BY expense_date DESC""",
        (campaign_id,)
    )
    pct = progress_percent(campaign['current_amount'], campaign['target_amount'])
    remaining = float(campaign['current_amount']) - float(campaign['total_expenses'])

    return render_template('main/transparency.html', campaign=campaign,
                           donations=donations, expenses=expenses,
                           pct=pct, remaining=remaining)
