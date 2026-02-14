# ABOUTME: Calendar view showing training sessions and matches in a monthly grid
# ABOUTME: Supports HTMX navigation for month switching and team filtering

from calendar import monthrange, monthcalendar
from datetime import date

from flask import Blueprint, render_template, request, url_for
from flask_login import login_required
from flask_babel import gettext as _

from app.models import TrainingSession, Match, Team

calendar_bp = Blueprint('calendar', __name__, url_prefix='/calendar')


@calendar_bp.route('/')
@login_required
def index():
    """Show calendar view with monthly grid."""
    year = request.args.get('year', date.today().year, type=int)
    month = request.args.get('month', date.today().month, type=int)
    team_id = request.args.get('team_id', type=int)

    # Clamp month and handle year rollover
    if month < 1:
        month = 12
        year -= 1
    elif month > 12:
        month = 1
        year += 1

    # Build calendar weeks (list of lists, each inner list = week of day numbers, 0 = empty)
    cal_weeks = monthcalendar(year, month)

    # Get last day of month (first element from monthrange is weekday of day 1, unused)
    last_day = monthrange(year, month)[1]
    first_date = date(year, month, 1)
    last_date = date(year, month, last_day)

    # Query training sessions in this month
    ts_query = TrainingSession.query.filter(
        TrainingSession.date >= first_date,
        TrainingSession.date <= last_date,
        TrainingSession.is_active == True  # noqa: E712
    )
    if team_id:
        ts_query = ts_query.filter(TrainingSession.team_id == team_id)
    training_sessions = ts_query.all()

    # Query matches in this month
    m_query = Match.query.filter(
        Match.date >= first_date,
        Match.date <= last_date,
        Match.is_active == True  # noqa: E712
    )
    if team_id:
        m_query = m_query.filter(Match.team_id == team_id)
    matches = m_query.all()

    # Build events dict: {day_number: [event, event, ...]}
    events = {}
    for ts in training_sessions:
        day = ts.date.day
        events.setdefault(day, []).append({
            'type': 'training',
            'title': ts.title,
            'time': ts.start_time.strftime('%H:%M') if ts.start_time else '',
            'url': url_for('training.view', id=ts.id),
            'cancelled': ts.cancelled,
            'team': ts.team.name if ts.team else ''
        })
    for m in matches:
        day = m.date.day
        events.setdefault(day, []).append({
            'type': 'match',
            'title': _('vs %(opponent)s', opponent=m.opponent),
            'time': m.kick_off_time.strftime('%H:%M') if m.kick_off_time else '',
            'url': url_for('matches.view', id=m.id),
            'cancelled': m.status == 'cancelled',
            'team': m.team.name if m.team else '',
            'is_home': m.is_home
        })

    teams = Team.query.filter_by(is_active=True).order_by(Team.name).all()

    # Month names for display
    month_names = [
        '', _('January'), _('February'), _('March'), _('April'),
        _('May'), _('June'), _('July'), _('August'),
        _('September'), _('October'), _('November'), _('December')
    ]

    day_names = [
        _('Mon'), _('Tue'), _('Wed'), _('Thu'),
        _('Fri'), _('Sat'), _('Sun')
    ]

    # Compute prev/next month values with correct year rollover
    if month == 1:
        prev_month = 12
        prev_year = year - 1
    else:
        prev_month = month - 1
        prev_year = year

    if month == 12:
        next_month = 1
        next_year = year + 1
    else:
        next_month = month + 1
        next_year = year

    context = {
        'year': year,
        'month': month,
        'month_name': month_names[month],
        'cal_weeks': cal_weeks,
        'events': events,
        'teams': teams,
        'selected_team': team_id,
        'day_names': day_names,
        'today': date.today(),
        'prev_month': prev_month,
        'prev_year': prev_year,
        'next_month': next_month,
        'next_year': next_year,
    }

    # If HTMX request, return only the calendar grid partial
    if request.headers.get('HX-Request'):
        return render_template('calendar/_grid.html', **context)

    return render_template('calendar/index.html', **context)
