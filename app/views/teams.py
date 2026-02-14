from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from flask_babel import gettext as _
from sqlalchemy.orm import joinedload
from app import db
from app.models import Team, TeamStaffAssignment, Staff, Athlete, Season, TrainingSession
from app.forms.team_forms import TeamForm, TeamStaffAssignmentForm
from datetime import datetime, date, timedelta

teams_bp = Blueprint('teams', __name__, url_prefix='/teams')


@teams_bp.route('/')
@login_required
def index():
    """List all teams"""
    teams = Team.query.filter_by(is_active=True).order_by(Team.name).all()
    return render_template('teams/index.html', teams=teams)


@teams_bp.route('/new', methods=['GET', 'POST'])
@login_required
def new():
    """Create new team"""
    if not (current_user.is_admin() or current_user.is_coach()):
        flash(_('Permission denied.'), 'error')
        return redirect(url_for('teams.index'))

    form = TeamForm()
    staff_members = Staff.query.filter_by(is_active=True).order_by(Staff.last_name).all()
    form.head_coach_id.choices = [('', _('-- Select Head Coach --'))] + [(s.id, s.get_full_name()) for s in staff_members]
    seasons = Season.query.filter_by(is_active=True).order_by(Season.start_date.desc()).all()
    form.season_id.choices = [('', _('-- No Season --'))] + [(s.id, s.name) for s in seasons]

    if form.validate_on_submit():
        team = Team(
            name=form.name.data,
            description=form.description.data,
            age_group=form.age_group.data,
            season=form.season.data,
            season_id=form.season_id.data if form.season_id.data else None,
            head_coach_id=form.head_coach_id.data if form.head_coach_id.data else None,
            created_by=current_user.id
        )
        db.session.add(team)
        db.session.commit()
        flash(_('Team created successfully.'), 'success')
        return redirect(url_for('teams.view', id=team.id))

    return render_template('teams/new.html', form=form)


@teams_bp.route('/<int:id>')
@login_required
def view(id):
    """View team details"""
    team = Team.query.get_or_404(id)
    athletes = team.athletes.filter_by(is_active=True).order_by(Athlete.last_name, Athlete.first_name).all()

    # Get staff assignments with eager-loaded staff to avoid N+1
    assistant_assignments = TeamStaffAssignment.query.options(
        joinedload(TeamStaffAssignment.staff)
    ).filter_by(team_id=id, role='assistant_coach', is_active=True).all()
    escort_assignments = TeamStaffAssignment.query.options(
        joinedload(TeamStaffAssignment.staff)
    ).filter_by(team_id=id, role='escort', is_active=True).all()

    # Get upcoming training sessions (next 30 days)
    upcoming_sessions = TrainingSession.query.filter(
        TrainingSession.team_id == id,
        TrainingSession.is_active == True,  # noqa: E712
        TrainingSession.cancelled == False,  # noqa: E712
        TrainingSession.date >= date.today(),
        TrainingSession.date <= date.today() + timedelta(days=30)
    ).order_by(TrainingSession.date, TrainingSession.start_time).limit(5).all()

    return render_template('teams/view.html', team=team, athletes=athletes,
                           assistant_assignments=assistant_assignments,
                           escort_assignments=escort_assignments,
                           upcoming_sessions=upcoming_sessions)


@teams_bp.route('/<int:id>/edit', methods=['GET', 'POST'])
@login_required
def edit(id):
    """Edit team"""
    if not (current_user.is_admin() or current_user.is_coach()):
        flash(_('Permission denied.'), 'error')
        return redirect(url_for('teams.index'))

    team = Team.query.get_or_404(id)
    form = TeamForm(obj=team)
    staff_members = Staff.query.filter_by(is_active=True).order_by(Staff.last_name).all()
    form.head_coach_id.choices = [('', _('-- No Head Coach --'))] + [(s.id, s.get_full_name()) for s in staff_members]
    seasons = Season.query.filter_by(is_active=True).order_by(Season.start_date.desc()).all()
    form.season_id.choices = [('', _('-- No Season --'))] + [(s.id, s.name) for s in seasons]

    if form.validate_on_submit():
        team.name = form.name.data
        team.description = form.description.data
        team.age_group = form.age_group.data
        team.season = form.season.data
        team.season_id = form.season_id.data if form.season_id.data else None
        team.head_coach_id = form.head_coach_id.data if form.head_coach_id.data else None
        team.updated_at = datetime.utcnow()
        db.session.commit()
        flash(_('Team updated successfully.'), 'success')
        return redirect(url_for('teams.view', id=team.id))

    return render_template('teams/edit.html', form=form, team=team)


@teams_bp.route('/<int:id>/delete', methods=['POST'])
@login_required
def delete(id):
    """Delete (soft) team"""
    if not current_user.is_admin():
        flash(_('Permission denied.'), 'error')
        return redirect(url_for('teams.index'))

    team = Team.query.get_or_404(id)
    team.is_active = False
    db.session.commit()
    flash(_('Team deleted.'), 'success')
    return redirect(url_for('teams.index'))


@teams_bp.route('/<int:id>/assign-staff', methods=['GET', 'POST'])
@login_required
def assign_staff(id):
    """Assign staff to team"""
    if not (current_user.is_admin() or current_user.is_coach()):
        flash(_('Permission denied.'), 'error')
        return redirect(url_for('teams.index'))

    team = Team.query.get_or_404(id)
    form = TeamStaffAssignmentForm()

    staff_members = Staff.query.filter_by(is_active=True).order_by(Staff.last_name).all()
    form.staff_id.choices = [(s.id, f'{s.get_full_name()} - {s.get_role_display()}') for s in staff_members]

    if form.validate_on_submit():
        # Check if this assignment already exists (active or inactive)
        existing = TeamStaffAssignment.query.filter_by(
            team_id=id,
            staff_id=form.staff_id.data,
            role=form.role.data
        ).first()

        if existing and existing.is_active:
            flash(_('This staff member already has this role in this team.'), 'warning')
            return redirect(url_for('teams.view', id=id))

        if existing and not existing.is_active:
            # Reactivate the soft-deleted assignment
            existing.is_active = True
            existing.assigned_date = form.assigned_date.data
            existing.notes = form.notes.data
            existing.assigned_by = current_user.id
            existing.updated_at = datetime.utcnow()
        else:
            assignment = TeamStaffAssignment(
                team_id=id,
                staff_id=form.staff_id.data,
                role=form.role.data,
                assigned_date=form.assigned_date.data,
                notes=form.notes.data,
                assigned_by=current_user.id
            )
            db.session.add(assignment)

        db.session.commit()
        flash(_('Staff assigned successfully.'), 'success')
        return redirect(url_for('teams.view', id=id))

    # Set default date only on GET (preserve user input on validation failure)
    if request.method == 'GET':
        form.assigned_date.data = date.today()
    return render_template('teams/assign_staff.html', form=form, team=team)


@teams_bp.route('/staff-assignment/<int:id>/remove', methods=['POST'])
@login_required
def remove_staff(id):
    """Remove staff assignment"""
    if not (current_user.is_admin() or current_user.is_coach()):
        flash(_('Permission denied.'), 'error')
        return redirect(url_for('teams.index'))

    assignment = TeamStaffAssignment.query.get_or_404(id)
    team_id = assignment.team_id
    assignment.is_active = False
    db.session.commit()
    flash(_('Staff member removed from team.'), 'success')
    return redirect(url_for('teams.view', id=team_id))
