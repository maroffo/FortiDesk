# ABOUTME: Match management blueprint with CRUD, result entry, and lineup management
# ABOUTME: Supports scheduling, filtering by team/season/status, and player lineup tracking

from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from flask_babel import gettext as _
from sqlalchemy.orm import joinedload
from app import db
from app.models import Match, MatchLineup, Team, Season, Athlete
from app.forms.match_forms import MatchForm, MatchResultForm, MatchLineupForm
from datetime import datetime

matches_bp = Blueprint('matches', __name__, url_prefix='/matches')


def _populate_form_choices(form):
    """Populate team and season select field choices"""
    teams = Team.query.filter_by(is_active=True).order_by(Team.name).all()
    form.team_id.choices = [(t.id, t.name) for t in teams]
    seasons = Season.query.filter_by(is_active=True).order_by(Season.start_date.desc()).all()
    form.season_id.choices = [('', _('-- No Season --'))] + [(s.id, s.name) for s in seasons]


@matches_bp.route('/')
@login_required
def index():
    """List matches with filtering and pagination"""
    page = request.args.get('page', 1, type=int)
    per_page = 20

    query = Match.query.options(
        joinedload(Match.team),
        joinedload(Match.season)
    ).filter_by(is_active=True)

    # Filter by team
    team_id = request.args.get('team_id', type=int)
    if team_id:
        query = query.filter(Match.team_id == team_id)

    # Filter by season
    season_id = request.args.get('season_id', type=int)
    if season_id:
        query = query.filter(Match.season_id == season_id)

    # Filter by status
    status = request.args.get('status', '')
    if status:
        query = query.filter(Match.status == status)

    # Filter by match type
    match_type = request.args.get('match_type', '')
    if match_type:
        query = query.filter(Match.match_type == match_type)

    pagination = query.order_by(Match.date.desc()).paginate(
        page=page, per_page=per_page, error_out=False
    )
    matches = pagination.items

    # Get filter options
    teams = Team.query.filter_by(is_active=True).order_by(Team.name).all()
    seasons = Season.query.filter_by(is_active=True).order_by(Season.start_date.desc()).all()

    return render_template('matches/index.html',
                           matches=matches,
                           pagination=pagination,
                           teams=teams,
                           seasons=seasons,
                           selected_team=team_id,
                           selected_season=season_id,
                           selected_status=status,
                           selected_match_type=match_type)


@matches_bp.route('/new', methods=['GET', 'POST'])
@login_required
def new():
    """Create a new match"""
    if not (current_user.is_admin() or current_user.is_coach()):
        flash(_('Permission denied.'), 'error')
        return redirect(url_for('matches.index'))

    form = MatchForm()
    _populate_form_choices(form)

    if form.validate_on_submit():
        match = Match(
            date=form.date.data,
            kick_off_time=form.kick_off_time.data,
            opponent=form.opponent.data,
            location=form.location.data,
            is_home=form.is_home.data,
            match_type=form.match_type.data,
            team_id=form.team_id.data,
            season_id=form.season_id.data if form.season_id.data else None,
            notes=form.notes.data,
            created_by=current_user.id
        )
        db.session.add(match)
        db.session.commit()
        flash(_('Match created successfully.'), 'success')
        return redirect(url_for('matches.view', id=match.id))

    return render_template('matches/new.html', form=form)


@matches_bp.route('/<int:id>')
@login_required
def view(id):
    """View match details including lineup"""
    match = Match.query.options(
        joinedload(Match.team),
        joinedload(Match.season)
    ).get_or_404(id)

    # Get lineup entries with eager-loaded athletes
    lineup_entries = MatchLineup.query.options(
        joinedload(MatchLineup.athlete)
    ).filter_by(match_id=id).order_by(
        MatchLineup.is_starter.desc(),
        MatchLineup.jersey_number
    ).all()

    return render_template('matches/view.html', match=match, lineup_entries=lineup_entries)


@matches_bp.route('/<int:id>/edit', methods=['GET', 'POST'])
@login_required
def edit(id):
    """Edit an existing match"""
    if not (current_user.is_admin() or current_user.is_coach()):
        flash(_('Permission denied.'), 'error')
        return redirect(url_for('matches.index'))

    match = Match.query.get_or_404(id)
    form = MatchForm(obj=match)
    _populate_form_choices(form)

    if form.validate_on_submit():
        match.date = form.date.data
        match.kick_off_time = form.kick_off_time.data
        match.opponent = form.opponent.data
        match.location = form.location.data
        match.is_home = form.is_home.data
        match.match_type = form.match_type.data
        match.team_id = form.team_id.data
        match.season_id = form.season_id.data if form.season_id.data else None
        match.notes = form.notes.data
        match.updated_at = datetime.utcnow()
        db.session.commit()
        flash(_('Match updated successfully.'), 'success')
        return redirect(url_for('matches.view', id=match.id))

    return render_template('matches/edit.html', form=form, match=match)


@matches_bp.route('/<int:id>/delete', methods=['POST'])
@login_required
def delete(id):
    """Soft delete a match"""
    if not current_user.is_admin():
        flash(_('Permission denied.'), 'error')
        return redirect(url_for('matches.index'))

    match = Match.query.get_or_404(id)
    match.is_active = False
    db.session.commit()
    flash(_('Match deleted.'), 'success')
    return redirect(url_for('matches.index'))


@matches_bp.route('/<int:id>/result', methods=['GET', 'POST'])
@login_required
def result(id):
    """Enter or edit match result"""
    if not (current_user.is_admin() or current_user.is_coach()):
        flash(_('Permission denied.'), 'error')
        return redirect(url_for('matches.index'))

    match = Match.query.options(
        joinedload(Match.team)
    ).get_or_404(id)
    form = MatchResultForm(obj=match)

    if form.validate_on_submit():
        match.score_home = form.score_home.data
        match.score_away = form.score_away.data
        match.result = form.result.data
        match.notes = form.notes.data
        match.status = 'completed'
        match.updated_at = datetime.utcnow()
        db.session.commit()
        flash(_('Match result saved.'), 'success')
        return redirect(url_for('matches.view', id=match.id))

    return render_template('matches/result.html', form=form, match=match)


@matches_bp.route('/<int:id>/lineup', methods=['GET', 'POST'])
@login_required
def lineup(id):
    """Manage match lineup"""
    if not (current_user.is_admin() or current_user.is_coach()):
        flash(_('Permission denied.'), 'error')
        return redirect(url_for('matches.index'))

    match = Match.query.options(
        joinedload(Match.team)
    ).get_or_404(id)
    form = MatchLineupForm()  # for CSRF

    # Get team athletes
    athletes = Athlete.query.filter_by(
        team_id=match.team_id, is_active=True
    ).order_by(Athlete.last_name, Athlete.first_name).all()

    # Get existing lineup entries as dict {athlete_id: lineup}
    existing = {entry.athlete_id: entry for entry in match.lineups.all()}

    if form.validate_on_submit():
        # Clear existing lineup
        MatchLineup.query.filter_by(match_id=id).delete()

        selected_ids = request.form.getlist('athlete_ids')
        for athlete_id_str in selected_ids:
            athlete_id = int(athlete_id_str)
            jersey_raw = request.form.get(f'jersey_{athlete_id}', '')
            entry = MatchLineup(
                match_id=id,
                athlete_id=athlete_id,
                position=request.form.get(f'position_{athlete_id}', ''),
                jersey_number=int(jersey_raw) if jersey_raw.strip() else None,
                is_starter=f'starter_{athlete_id}' in request.form,
                is_captain=f'captain_{athlete_id}' in request.form,
                notes=request.form.get(f'notes_{athlete_id}', '')
            )
            db.session.add(entry)

        db.session.commit()
        flash(_('Lineup saved.'), 'success')
        return redirect(url_for('matches.view', id=id))

    return render_template('matches/lineup.html', match=match, form=form,
                           athletes=athletes, existing=existing)
