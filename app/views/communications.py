# ABOUTME: Communications views for creating and managing team announcements
# ABOUTME: Supports announcement CRUD with optional email delivery

from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from flask_babel import gettext as _
from sqlalchemy.orm import joinedload
from app import db
from app.models import Announcement, Team
from app.forms.communication_forms import AnnouncementForm
from app.utils.email import send_announcement_background

communications_bp = Blueprint('communications', __name__, url_prefix='/communications')


@communications_bp.route('/')
@login_required
def index():
    """List announcements with optional filters"""
    if not (current_user.is_admin() or current_user.is_coach()):
        flash(_('Permission denied.'), 'error')
        return redirect(url_for('main.dashboard'))

    page = request.args.get('page', 1, type=int)
    per_page = 20

    query = Announcement.query.filter_by(is_active=True).options(
        joinedload(Announcement.team),
        joinedload(Announcement.creator)
    )

    # Filter by announcement type
    announcement_type = request.args.get('announcement_type')
    if announcement_type:
        query = query.filter(Announcement.announcement_type == announcement_type)

    # Filter by team
    team_id = request.args.get('team_id', type=int)
    if team_id:
        query = query.filter(Announcement.team_id == team_id)

    pagination = query.order_by(Announcement.created_at.desc()).paginate(
        page=page, per_page=per_page, error_out=False
    )
    announcements = pagination.items

    # Get teams for filter dropdown
    teams = Team.query.filter_by(is_active=True).order_by(Team.name).all()

    return render_template('communications/index.html',
                           announcements=announcements,
                           pagination=pagination,
                           teams=teams,
                           selected_type=announcement_type,
                           selected_team=team_id)


@communications_bp.route('/new', methods=['GET', 'POST'])
@login_required
def new():
    """Create a new announcement"""
    if not (current_user.is_admin() or current_user.is_coach()):
        flash(_('Permission denied.'), 'error')
        return redirect(url_for('communications.index'))

    form = AnnouncementForm()

    # Populate team choices
    teams = Team.query.filter_by(is_active=True).order_by(Team.name).all()
    form.team_id.choices = [('', _('All Teams'))] + [(str(t.id), t.name) for t in teams]

    if form.validate_on_submit():
        announcement = Announcement(
            subject=form.subject.data,
            body=form.body.data,
            announcement_type=form.announcement_type.data,
            team_id=form.team_id.data,
            send_email=form.send_email.data,
            created_by=current_user.id
        )

        db.session.add(announcement)
        db.session.commit()

        if form.send_email.data:
            send_announcement_background(announcement.id)
            flash(_('Announcement created. Emails are being sent in the background.'), 'success')
        else:
            flash(_('Announcement created successfully.'), 'success')

        return redirect(url_for('communications.view', id=announcement.id))

    return render_template('communications/new.html', form=form)


@communications_bp.route('/<int:id>')
@login_required
def view(id):
    """View announcement details"""
    if not (current_user.is_admin() or current_user.is_coach()):
        flash(_('Permission denied.'), 'error')
        return redirect(url_for('main.dashboard'))

    announcement = Announcement.query.get_or_404(id)
    return render_template('communications/view.html', announcement=announcement)


@communications_bp.route('/<int:id>/delete', methods=['POST'])
@login_required
def delete(id):
    """Soft delete an announcement"""
    if not current_user.is_admin():
        flash(_('Permission denied.'), 'error')
        return redirect(url_for('communications.index'))

    announcement = Announcement.query.get_or_404(id)
    announcement.is_active = False
    db.session.commit()

    flash(_('Announcement deleted.'), 'success')
    return redirect(url_for('communications.index'))


@communications_bp.route('/<int:id>/send', methods=['POST'])
@login_required
def send(id):
    """Send or resend announcement email"""
    if not (current_user.is_admin() or current_user.is_coach()):
        flash(_('Permission denied.'), 'error')
        return redirect(url_for('communications.index'))

    announcement = Announcement.query.get_or_404(id)
    announcement.send_email = True
    db.session.commit()

    send_announcement_background(announcement.id)
    flash(_('Emails are being sent in the background.'), 'success')
    return redirect(url_for('communications.view', id=announcement.id))
