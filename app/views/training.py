# ABOUTME: Training session management views with CRUD, cancellation, and recurring generation
# ABOUTME: Blueprint for scheduling team practices, friendlies, tournaments, and events

from datetime import datetime, timedelta
from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from flask_babel import gettext as _
from sqlalchemy.orm import joinedload
from app import db
from app.models import TrainingSession, Team, Season, Staff
from app.forms.training_forms import (
    TrainingSessionForm, RecurringSessionForm, CancelSessionForm
)

training_bp = Blueprint('training', __name__, url_prefix='/training')


def _populate_form_choices(form):
    """Populate SelectField choices for team, season, and coach fields."""
    teams = Team.query.filter_by(is_active=True).order_by(Team.name).all()
    form.team_id.choices = [(t.id, t.name) for t in teams]

    seasons = Season.query.filter_by(is_active=True).order_by(Season.start_date.desc()).all()
    form.season_id.choices = [('', _('-- No Season --'))] + [(s.id, s.name) for s in seasons]

    all_coaches = Staff.query.filter_by(is_active=True).filter(
        Staff.role.in_(['coach', 'assistant_coach'])
    ).order_by(Staff.last_name, Staff.first_name).all()
    form.coach_id.choices = [('', _('-- No Coach --'))] + [
        (c.id, c.get_full_name()) for c in all_coaches
    ]


@training_bp.route('/')
@login_required
def index():
    """List training sessions with pagination and filters."""
    page = request.args.get('page', 1, type=int)
    per_page = 20

    query = TrainingSession.query.options(
        joinedload(TrainingSession.team),
        joinedload(TrainingSession.coach),
        joinedload(TrainingSession.season)
    ).filter_by(is_active=True)

    # Filter by team
    team_id = request.args.get('team_id', type=int)
    if team_id:
        query = query.filter(TrainingSession.team_id == team_id)

    # Filter by date range
    date_from = request.args.get('date_from')
    if date_from:
        try:
            query = query.filter(
                TrainingSession.date >= datetime.strptime(date_from, '%Y-%m-%d').date()
            )
        except ValueError:
            pass

    date_to = request.args.get('date_to')
    if date_to:
        try:
            query = query.filter(
                TrainingSession.date <= datetime.strptime(date_to, '%Y-%m-%d').date()
            )
        except ValueError:
            pass

    # Filter by season
    season_id = request.args.get('season_id', type=int)
    if season_id:
        query = query.filter(TrainingSession.season_id == season_id)

    # Hide cancelled unless requested
    show_cancelled = request.args.get('show_cancelled', '0')
    if show_cancelled != '1':
        query = query.filter(TrainingSession.cancelled == False)  # noqa: E712

    query = query.order_by(TrainingSession.date.desc(), TrainingSession.start_time.desc())
    pagination = query.paginate(page=page, per_page=per_page, error_out=False)
    sessions = pagination.items

    # Populate filter dropdowns
    teams = Team.query.filter_by(is_active=True).order_by(Team.name).all()
    seasons = Season.query.filter_by(is_active=True).order_by(Season.start_date.desc()).all()

    return render_template(
        'training/index.html',
        sessions=sessions,
        pagination=pagination,
        teams=teams,
        seasons=seasons,
        selected_team=team_id,
        selected_season=season_id,
        show_cancelled=show_cancelled
    )


@training_bp.route('/new', methods=['GET', 'POST'])
@login_required
def new():
    """Create a new training session."""
    if not (current_user.is_admin() or current_user.is_coach()):
        flash(_('Permission denied. Only admins and coaches can create training sessions.'), 'error')
        return redirect(url_for('training.index'))

    form = TrainingSessionForm()
    _populate_form_choices(form)

    if form.validate_on_submit():
        session = TrainingSession(
            title=form.title.data,
            date=form.date.data,
            start_time=form.start_time.data,
            end_time=form.end_time.data,
            location=form.location.data,
            session_type=form.session_type.data,
            team_id=form.team_id.data,
            season_id=form.season_id.data if form.season_id.data else None,
            coach_id=form.coach_id.data if form.coach_id.data else None,
            notes=form.notes.data,
            created_by=current_user.id
        )
        db.session.add(session)
        db.session.commit()
        flash(_('Training session created successfully.'), 'success')
        return redirect(url_for('training.view', id=session.id))

    return render_template('training/new.html', form=form)


@training_bp.route('/<int:id>')
@login_required
def view(id):
    """View training session details."""
    session = TrainingSession.query.get_or_404(id)
    cancel_form = CancelSessionForm()
    return render_template('training/view.html', session=session, cancel_form=cancel_form)


@training_bp.route('/<int:id>/edit', methods=['GET', 'POST'])
@login_required
def edit(id):
    """Edit a training session."""
    if not (current_user.is_admin() or current_user.is_coach()):
        flash(_('Permission denied.'), 'error')
        return redirect(url_for('training.index'))

    session = TrainingSession.query.get_or_404(id)
    form = TrainingSessionForm(obj=session)
    _populate_form_choices(form)

    if form.validate_on_submit():
        session.title = form.title.data
        session.date = form.date.data
        session.start_time = form.start_time.data
        session.end_time = form.end_time.data
        session.location = form.location.data
        session.session_type = form.session_type.data
        session.team_id = form.team_id.data
        session.season_id = form.season_id.data if form.season_id.data else None
        session.coach_id = form.coach_id.data if form.coach_id.data else None
        session.notes = form.notes.data
        session.updated_at = datetime.utcnow()

        db.session.commit()
        flash(_('Training session updated successfully.'), 'success')
        return redirect(url_for('training.view', id=session.id))

    return render_template('training/edit.html', form=form, session=session)


@training_bp.route('/<int:id>/delete', methods=['POST'])
@login_required
def delete(id):
    """Soft delete a training session."""
    if not current_user.is_admin():
        flash(_('Permission denied. Only admins can delete training sessions.'), 'error')
        return redirect(url_for('training.index'))

    session = TrainingSession.query.get_or_404(id)
    session.is_active = False
    db.session.commit()

    flash(_('Training session deleted.'), 'success')
    return redirect(url_for('training.index'))


@training_bp.route('/<int:id>/cancel', methods=['POST'])
@login_required
def cancel(id):
    """Cancel a training session with optional reason."""
    if not (current_user.is_admin() or current_user.is_coach()):
        flash(_('Permission denied.'), 'error')
        return redirect(url_for('training.index'))

    session = TrainingSession.query.get_or_404(id)
    form = CancelSessionForm()

    if form.validate_on_submit():
        session.cancelled = True
        session.cancellation_reason = form.cancellation_reason.data
        session.updated_at = datetime.utcnow()
        db.session.commit()
        flash(_('Training session cancelled.'), 'success')
    else:
        flash(_('Error cancelling session.'), 'error')

    return redirect(url_for('training.view', id=session.id))


@training_bp.route('/generate-recurring', methods=['GET', 'POST'])
@login_required
def generate_recurring():
    """Generate multiple sessions from a recurring pattern."""
    if not (current_user.is_admin() or current_user.is_coach()):
        flash(_('Permission denied. Only admins and coaches can generate sessions.'), 'error')
        return redirect(url_for('training.index'))

    form = RecurringSessionForm()
    _populate_form_choices(form)

    if form.validate_on_submit():
        start = form.start_date.data
        end = form.end_date.data
        if start is None or end is None:
            flash(_('Start date and end date are required.'), 'error')
            return render_template('training/generate_recurring.html', form=form)

        # Jump to first occurrence of the target weekday, then step by 7 days
        days_ahead = (form.recurrence_day.data - start.weekday()) % 7
        current_date = start + timedelta(days=days_ahead)
        count = 0

        while current_date <= end:
            session = TrainingSession(
                title=form.title.data,
                date=current_date,
                start_time=form.start_time.data,
                end_time=form.end_time.data,
                location=form.location.data,
                session_type=form.session_type.data,
                team_id=form.team_id.data,
                season_id=form.season_id.data if form.season_id.data else None,
                coach_id=form.coach_id.data if form.coach_id.data else None,
                notes=form.notes.data,
                is_recurring=True,
                recurrence_day=form.recurrence_day.data,
                recurrence_end_date=end,
                created_by=current_user.id
            )
            db.session.add(session)
            count += 1
            current_date += timedelta(days=7)

        db.session.commit()
        flash(
            _('%(count)d recurring sessions generated successfully.', count=count),
            'success'
        )
        return redirect(url_for('training.index'))

    return render_template('training/generate_recurring.html', form=form)


@training_bp.route('/<int:id>/check-in')
@login_required
def check_in(id):
    """Redirect to attendance check-in pre-filled for this session."""
    session = TrainingSession.query.get_or_404(id)
    return redirect(url_for(
        'attendance.check_in',
        team_id=session.team_id,
        training_session_id=session.id
    ))
