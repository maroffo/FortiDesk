# ABOUTME: Report views for generating team roster, attendance, equipment, document, and insurance reports
# ABOUTME: Each report supports HTML view plus CSV and PDF export via query parameter

from datetime import date, timedelta

from flask import Blueprint, render_template, request, flash, redirect, url_for
from flask_login import login_required, current_user
from flask_babel import gettext as _
from sqlalchemy.orm import joinedload

from app.models import (
    Athlete, Team, Season, Equipment, Attendance, Document, Insurance, Staff
)
from app.forms.report_forms import ReportFilterForm
from app.utils.export import export_csv, export_pdf

reports_bp = Blueprint('reports', __name__, url_prefix='/reports')


@reports_bp.route('/')
@login_required
def index():
    """Reports landing page."""
    if not (current_user.is_admin() or current_user.is_coach()):
        flash(_('Permission denied.'), 'error')
        return redirect(url_for('main.dashboard'))

    return render_template('reports/index.html')


@reports_bp.route('/team-roster')
@login_required
def team_roster():
    """Team roster with document status."""
    if not (current_user.is_admin() or current_user.is_coach()):
        flash(_('Permission denied.'), 'error')
        return redirect(url_for('main.dashboard'))

    form = ReportFilterForm(formdata=request.args)
    teams = Team.query.filter_by(is_active=True).order_by(Team.name).all()
    form.team_id.choices = [('', _('All Teams'))] + [
        (str(t.id), t.name) for t in teams
    ]
    # Not using season filter for this report
    form.season_id.choices = [('', _('All'))]

    query = Athlete.query.filter_by(is_active=True).options(
        joinedload(Athlete.team)
    )

    if form.team_id.data:
        query = query.filter(Athlete.team_id == form.team_id.data)

    athletes = query.order_by(Athlete.last_name, Athlete.first_name).all()

    today = date.today()
    alert_date = today + timedelta(days=30)
    headers = [
        _('Name'), _('Age'), _('FIR ID'), _('Team'),
        _('ID Document'), _('Medical Certificate'), _('Fiscal Code')
    ]

    rows = []
    for a in athletes:
        doc_status = _('Expired') if a.document_expiry and a.document_expiry < today else (
            _('Expiring') if a.document_expiry and a.document_expiry <= alert_date else _('Valid')
        )
        cert_status = _('N/A')
        if a.has_medical_certificate and a.certificate_expiry:
            cert_status = _('Expired') if a.certificate_expiry < today else (
                _('Expiring') if a.certificate_expiry <= alert_date else _('Valid')
            )

        doc_expiry_str = a.document_expiry.strftime('%d/%m/%Y') if a.document_expiry else '-'
        cert_expiry_str = a.certificate_expiry.strftime('%d/%m/%Y') if a.certificate_expiry else '-'

        rows.append([
            a.get_full_name(),
            str(a.get_age()),
            a.fir_id or '-',
            a.team.name if a.team else '-',
            f'{doc_status} ({doc_expiry_str})',
            f'{cert_status} ({cert_expiry_str})',
            a.fiscal_code
        ])

    fmt = request.args.get('format')
    if fmt == 'csv':
        return export_csv('team_roster', headers, rows)
    if fmt == 'pdf':
        return export_pdf('team_roster', _('Team Roster Report'), headers, rows)

    return render_template('reports/team_roster.html',
                           form=form, athletes=athletes,
                           today=today, alert_date=alert_date)


@reports_bp.route('/attendance-summary')
@login_required
def attendance_summary():
    """Attendance summary by team/season."""
    if not (current_user.is_admin() or current_user.is_coach()):
        flash(_('Permission denied.'), 'error')
        return redirect(url_for('main.dashboard'))

    form = ReportFilterForm(formdata=request.args)
    teams = Team.query.filter_by(is_active=True).order_by(Team.name).all()
    form.team_id.choices = [('', _('All Teams'))] + [
        (str(t.id), t.name) for t in teams
    ]
    seasons = Season.query.filter_by(is_active=True).order_by(
        Season.start_date.desc()
    ).all()
    form.season_id.choices = [('', _('All Seasons'))] + [
        (str(s.id), s.name) for s in seasons
    ]

    query = Attendance.query.filter_by(is_active=True).options(
        joinedload(Attendance.athlete)
    )

    if form.team_id.data:
        query = query.join(Athlete).filter(Athlete.team_id == form.team_id.data)

    if form.start_date.data:
        query = query.filter(Attendance.date >= form.start_date.data)
    if form.end_date.data:
        query = query.filter(Attendance.date <= form.end_date.data)

    records = query.order_by(Attendance.date.desc()).all()

    # Build per-athlete statistics
    athlete_stats = {}
    for r in records:
        aid = r.athlete_id
        if aid not in athlete_stats:
            athlete_stats[aid] = {
                'name': r.athlete.get_full_name() if r.athlete else _('Unknown'),
                'total': 0, 'present': 0, 'absent': 0, 'excused': 0, 'late': 0
            }
        athlete_stats[aid]['total'] += 1
        if r.status in athlete_stats[aid]:
            athlete_stats[aid][r.status] += 1

    stats_list = sorted(athlete_stats.values(), key=lambda x: x['name'])
    for s in stats_list:
        s['presence_pct'] = (
            round(s['present'] / s['total'] * 100, 1) if s['total'] > 0 else 0
        )

    headers = [
        _('Athlete'), _('Total'), _('Present'), _('Absent'),
        _('Excused'), _('Late'), _('Presence %')
    ]
    rows = [
        [s['name'], str(s['total']), str(s['present']), str(s['absent']),
         str(s['excused']), str(s['late']), f"{s['presence_pct']}%"]
        for s in stats_list
    ]

    fmt = request.args.get('format')
    if fmt == 'csv':
        return export_csv('attendance_summary', headers, rows)
    if fmt == 'pdf':
        return export_pdf(
            'attendance_summary', _('Attendance Summary Report'), headers, rows
        )

    return render_template('reports/attendance_summary.html',
                           form=form, stats=stats_list,
                           total_records=len(records))


@reports_bp.route('/equipment-inventory')
@login_required
def equipment_inventory():
    """Equipment inventory report."""
    if not (current_user.is_admin() or current_user.is_coach()):
        flash(_('Permission denied.'), 'error')
        return redirect(url_for('main.dashboard'))

    equipment = Equipment.query.filter_by(is_active=True).order_by(
        Equipment.category, Equipment.name
    ).all()

    headers = [
        _('Name'), _('Code'), _('Category'), _('Condition'),
        _('Status'), _('Location'), _('Quantity')
    ]
    rows = []
    for e in equipment:
        rows.append([
            e.name, e.code,
            e.get_category_display(), e.get_condition_display(),
            e.get_status_display(),
            e.location or '-', str(e.quantity or 1)
        ])

    fmt = request.args.get('format')
    if fmt == 'csv':
        return export_csv('equipment_inventory', headers, rows)
    if fmt == 'pdf':
        return export_pdf(
            'equipment_inventory', _('Equipment Inventory Report'), headers, rows
        )

    return render_template('reports/equipment_inventory.html',
                           equipment=equipment)


@reports_bp.route('/document-status')
@login_required
def document_status():
    """Document expiry status report."""
    if not (current_user.is_admin() or current_user.is_coach()):
        flash(_('Permission denied.'), 'error')
        return redirect(url_for('main.dashboard'))

    documents = Document.query.filter(
        Document.is_active.is_(True),
        Document.expiry_date.isnot(None)
    ).order_by(Document.expiry_date.asc()).all()

    # Batch resolve entity names
    athlete_ids = {d.entity_id for d in documents if d.entity_type == 'athlete'}
    staff_ids = {d.entity_id for d in documents if d.entity_type == 'staff'}

    athlete_map = {}
    if athlete_ids:
        for a in Athlete.query.filter(Athlete.id.in_(athlete_ids)).all():
            athlete_map[a.id] = a.get_full_name()

    staff_map = {}
    if staff_ids:
        for s in Staff.query.filter(Staff.id.in_(staff_ids)).all():
            staff_map[s.id] = s.get_full_name()

    today = date.today()
    alert_date = today + timedelta(days=30)
    headers = [
        _('Title'), _('Type'), _('Entity'), _('Entity Type'),
        _('Expiry Date'), _('Status')
    ]
    rows = []
    entity_names = {}
    for d in documents:
        if d.entity_type == 'athlete':
            ename = athlete_map.get(d.entity_id, _('Unknown'))
        else:
            ename = staff_map.get(d.entity_id, _('Unknown'))
        entity_names[d.id] = ename

        status = _('Expired') if d.expiry_date < today else (
            _('Expiring') if d.expiry_date <= alert_date else _('Valid')
        )
        rows.append([
            d.title, d.get_document_type_display(), ename,
            d.entity_type.title(),
            d.expiry_date.strftime('%d/%m/%Y'), status
        ])

    fmt = request.args.get('format')
    if fmt == 'csv':
        return export_csv('document_status', headers, rows)
    if fmt == 'pdf':
        return export_pdf(
            'document_status', _('Document Status Report'), headers, rows
        )

    return render_template('reports/document_status.html',
                           documents=documents, entity_names=entity_names,
                           today=today, alert_date=alert_date)


@reports_bp.route('/insurance-status')
@login_required
def insurance_status():
    """Insurance policy status report."""
    if not (current_user.is_admin() or current_user.is_coach()):
        flash(_('Permission denied.'), 'error')
        return redirect(url_for('main.dashboard'))

    insurances = Insurance.query.filter_by(is_active=True).options(
        joinedload(Insurance.athlete)
    ).order_by(Insurance.end_date.asc()).all()

    today = date.today()
    alert_date = today + timedelta(days=30)
    headers = [
        _('Athlete'), _('Type'), _('Provider'), _('Policy #'),
        _('Period'), _('Coverage'), _('Status')
    ]
    rows = []
    for ins in insurances:
        athlete_name = ins.athlete.get_full_name() if ins.athlete else _('Unknown')
        status = _('Expired') if ins.end_date < today else (
            _('Expiring') if ins.end_date <= alert_date else _('Active')
        )
        period = (
            f'{ins.start_date.strftime("%d/%m/%Y")} - '
            f'{ins.end_date.strftime("%d/%m/%Y")}'
        )
        coverage = f'{ins.coverage_amount:.2f}' if ins.coverage_amount else '-'

        rows.append([
            athlete_name, ins.get_insurance_type_display(), ins.provider,
            ins.policy_number, period, coverage, status
        ])

    fmt = request.args.get('format')
    if fmt == 'csv':
        return export_csv('insurance_status', headers, rows)
    if fmt == 'pdf':
        return export_pdf(
            'insurance_status', _('Insurance Status Report'), headers, rows
        )

    return render_template('reports/insurance_status.html',
                           insurances=insurances,
                           today=today, alert_date=alert_date)
