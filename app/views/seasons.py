# ABOUTME: Blueprint for season management CRUD operations
# ABOUTME: Handles listing, creating, viewing, editing, deleting, and setting current season

from flask import Blueprint, render_template, redirect, url_for, flash
from flask_login import login_required, current_user
from flask_babel import gettext as _
from app import db
from app.models import Season
from app.forms.season_forms import SeasonForm
from datetime import datetime

seasons_bp = Blueprint('seasons', __name__, url_prefix='/seasons')


@seasons_bp.route('/')
@login_required
def index():
    """List all active seasons, ordered by start_date descending"""
    seasons = Season.query.filter_by(is_active=True).order_by(Season.start_date.desc()).all()
    return render_template('seasons/index.html', seasons=seasons)


@seasons_bp.route('/new', methods=['GET', 'POST'])
@login_required
def new():
    """Create a new season"""
    if not (current_user.is_admin() or current_user.is_coach()):
        flash(_('Permission denied.'), 'error')
        return redirect(url_for('seasons.index'))

    form = SeasonForm()

    if form.validate_on_submit():
        season = Season(
            name=form.name.data,
            start_date=form.start_date.data,
            end_date=form.end_date.data,
            description=form.description.data,
            created_by=current_user.id
        )
        db.session.add(season)
        db.session.commit()
        flash(_('Season created successfully.'), 'success')
        return redirect(url_for('seasons.view', id=season.id))

    return render_template('seasons/new.html', form=form)


@seasons_bp.route('/<int:id>')
@login_required
def view(id):
    """View season details with team and training session counts"""
    season = Season.query.get_or_404(id)
    teams_count = season.teams.filter_by(is_active=True).count()
    sessions_count = season.training_sessions.filter_by(is_active=True).count()
    return render_template('seasons/view.html', season=season,
                           teams_count=teams_count, sessions_count=sessions_count)


@seasons_bp.route('/<int:id>/edit', methods=['GET', 'POST'])
@login_required
def edit(id):
    """Edit an existing season"""
    if not (current_user.is_admin() or current_user.is_coach()):
        flash(_('Permission denied.'), 'error')
        return redirect(url_for('seasons.index'))

    season = Season.query.get_or_404(id)
    form = SeasonForm(obj=season)

    if form.validate_on_submit():
        season.name = form.name.data
        season.start_date = form.start_date.data
        season.end_date = form.end_date.data
        season.description = form.description.data
        season.updated_at = datetime.utcnow()
        db.session.commit()
        flash(_('Season updated successfully.'), 'success')
        return redirect(url_for('seasons.view', id=season.id))

    return render_template('seasons/edit.html', form=form, season=season)


@seasons_bp.route('/<int:id>/delete', methods=['POST'])
@login_required
def delete(id):
    """Soft delete a season"""
    if not current_user.is_admin():
        flash(_('Permission denied.'), 'error')
        return redirect(url_for('seasons.index'))

    season = Season.query.get_or_404(id)
    season.is_active = False
    db.session.commit()
    flash(_('Season deleted.'), 'success')
    return redirect(url_for('seasons.index'))


@seasons_bp.route('/<int:id>/set-current', methods=['POST'])
@login_required
def set_current(id):
    """Set a season as the current season (unsets all others)"""
    if not current_user.is_admin():
        flash(_('Permission denied.'), 'error')
        return redirect(url_for('seasons.index'))

    season = Season.query.get_or_404(id)
    # Unset all other current seasons
    Season.query.filter(Season.id != id).update({'is_current': False})
    season.is_current = True
    db.session.commit()
    flash(_('Season "%(name)s" set as current.', name=season.name), 'success')
    return redirect(url_for('seasons.view', id=season.id))
