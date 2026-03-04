from flask import Blueprint, render_template, redirect, url_for, flash, request, abort
from flask_login import login_required, current_user
from app.models.db import query_db
from app.models.forms import CampaignForm
from app.models.utils import save_upload, log_activity, progress_percent

campaigns_bp = Blueprint('campaigns', __name__)


def ngo_required(f):
    from functools import wraps
    @wraps(f)
    def decorated(*args, **kwargs):
        if not current_user.is_authenticated or not current_user.is_ngo():
            abort(403)
        if not current_user.is_verified:
            flash('Your NGO account must be verified by admin before creating campaigns.', 'warning')
            return redirect(url_for('campaigns.list_campaigns'))
        return f(*args, **kwargs)
    return decorated


@campaigns_bp.route('/')
def list_campaigns():
    category = request.args.get('category', '')
    search   = request.args.get('q', '')
    base_q = """SELECT c.*, u.organization_name, u.is_verified,
                ROUND((c.current_amount/c.target_amount)*100,1) as pct
                FROM campaigns c JOIN users u ON c.ngo_id = u.id
                WHERE c.status='active' AND u.is_verified=1"""
    params = []
    if category:
        base_q += " AND c.category = %s"
        params.append(category)
    if search:
        base_q += " AND (c.title LIKE %s OR c.description LIKE %s)"
        params.extend([f'%{search}%', f'%{search}%'])
    base_q += " ORDER BY c.created_at DESC"
    campaigns = query_db(base_q, params)
    return render_template('campaigns/list.html', campaigns=campaigns,
                           category=category, search=search,
                           progress_percent=progress_percent)


@campaigns_bp.route('/create', methods=['GET', 'POST'])
@login_required
@ngo_required
def create():
    form = CampaignForm()
    if form.validate_on_submit():
        img_filename = save_upload(request.files.get('image'), 'CAMPAIGN_IMG_FOLDER')
        cid = query_db(
            """INSERT INTO campaigns (ngo_id, title, description, category,
               target_amount, start_date, end_date, image)
               VALUES (%s,%s,%s,%s,%s,%s,%s,%s)""",
            (current_user.id, form.title.data, form.description.data,
             form.category.data, form.target_amount.data,
             form.start_date.data, form.end_date.data, img_filename),
            commit=True
        )
        log_activity(current_user.id, 'CAMPAIGN_CREATE', f"Campaign {cid} created")
        flash('Campaign created successfully!', 'success')
        return redirect(url_for('campaigns.detail', campaign_id=cid))
    return render_template('campaigns/create.html', form=form)


@campaigns_bp.route('/<int:campaign_id>')
def detail(campaign_id):
    campaign = query_db(
        """SELECT c.*, u.organization_name, u.is_verified, u.name as ngo_name
           FROM campaigns c JOIN users u ON c.ngo_id = u.id
           WHERE c.id = %s""",
        (campaign_id,), one=True
    )
    if not campaign:
        abort(404)
    recent_donations = query_db(
        """SELECT d.amount, d.created_at,
                  CASE WHEN d.is_anonymous=1 THEN 'Anonymous' ELSE u.name END as donor_name
           FROM donations d JOIN users u ON d.donor_id = u.id
           WHERE d.campaign_id=%s AND d.status='approved'
           ORDER BY d.created_at DESC LIMIT 10""",
        (campaign_id,)
    )
    pct = progress_percent(campaign['current_amount'], campaign['target_amount'])
    return render_template('campaigns/detail.html', campaign=campaign,
                           recent_donations=recent_donations, pct=pct)


@campaigns_bp.route('/<int:campaign_id>/edit', methods=['GET', 'POST'])
@login_required
def edit(campaign_id):
    campaign = query_db("SELECT * FROM campaigns WHERE id=%s AND ngo_id=%s",
                        (campaign_id, current_user.id), one=True)
    if not campaign:
        abort(403)
    form = CampaignForm(data=campaign)
    if form.validate_on_submit():
        img_filename = save_upload(request.files.get('image'), 'CAMPAIGN_IMG_FOLDER') or campaign['image']
        query_db(
            """UPDATE campaigns SET title=%s, description=%s, category=%s,
               target_amount=%s, start_date=%s, end_date=%s, image=%s
               WHERE id=%s""",
            (form.title.data, form.description.data, form.category.data,
             form.target_amount.data, form.start_date.data, form.end_date.data,
             img_filename, campaign_id),
            commit=True
        )
        flash('Campaign updated.', 'success')
        return redirect(url_for('campaigns.detail', campaign_id=campaign_id))
    return render_template('campaigns/create.html', form=form, edit=True, campaign=campaign)
