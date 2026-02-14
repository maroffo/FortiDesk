# ABOUTME: Main blueprint with dashboard, index redirect, and language switcher
# ABOUTME: Dashboard queries counts, expiry alerts, maintenance, and recent activity
from flask import Blueprint, render_template, redirect, url_for, session, request
from flask_login import login_required, current_user
from datetime import date, timedelta
from app.models import Athlete, Staff, Team, Equipment, Attendance

main_bp = Blueprint('main', __name__)


@main_bp.route('/')
def index():
    if current_user.is_authenticated:
        return redirect(url_for('main.dashboard'))
    return redirect(url_for('auth.login'))


@main_bp.route('/dashboard')
@login_required
def dashboard():
    today = date.today()
    alert_threshold = today + timedelta(days=30)

    # Counts
    athlete_count = Athlete.query.filter_by(is_active=True).count()
    staff_count = Staff.query.filter_by(is_active=True).count()
    team_count = Team.query.filter_by(is_active=True).count()
    equipment_count = Equipment.query.filter_by(is_active=True).count()

    # Expiry alerts: athletes
    athlete_doc_alerts = Athlete.query.filter(
        Athlete.is_active == True,
        Athlete.document_expiry <= alert_threshold
    ).order_by(Athlete.document_expiry).all()

    athlete_cert_alerts = Athlete.query.filter(
        Athlete.is_active == True,
        Athlete.has_medical_certificate == True,
        Athlete.certificate_expiry <= alert_threshold
    ).order_by(Athlete.certificate_expiry).all()

    # Expiry alerts: staff
    staff_doc_alerts = Staff.query.filter(
        Staff.is_active == True,
        Staff.document_expiry <= alert_threshold
    ).order_by(Staff.document_expiry).all()

    staff_cert_alerts = Staff.query.filter(
        Staff.is_active == True,
        Staff.has_medical_certificate == True,
        Staff.certificate_expiry <= alert_threshold
    ).order_by(Staff.certificate_expiry).all()

    staff_bg_alerts = Staff.query.filter(
        Staff.is_active == True,
        Staff.has_background_check == True,
        Staff.background_check_expiry <= alert_threshold
    ).order_by(Staff.background_check_expiry).all()

    # Equipment needing maintenance
    equipment_maintenance = Equipment.query.filter(
        Equipment.is_active == True,
        Equipment.next_maintenance_date <= today
    ).all()

    # Recent activity
    recent_athletes = Athlete.query.filter_by(is_active=True).order_by(
        Athlete.created_at.desc()
    ).limit(5).all()

    recent_attendance = Attendance.query.filter_by(is_active=True).order_by(
        Attendance.created_at.desc()
    ).limit(5).all()

    return render_template('dashboard.html',
        user=current_user,
        athlete_count=athlete_count,
        staff_count=staff_count,
        team_count=team_count,
        equipment_count=equipment_count,
        athlete_doc_alerts=athlete_doc_alerts,
        athlete_cert_alerts=athlete_cert_alerts,
        staff_doc_alerts=staff_doc_alerts,
        staff_cert_alerts=staff_cert_alerts,
        staff_bg_alerts=staff_bg_alerts,
        equipment_maintenance=equipment_maintenance,
        recent_athletes=recent_athletes,
        recent_attendance=recent_attendance,
        today=today,
    )


@main_bp.route('/set_language/<language>')
def set_language(language):
    """Set the user's language preference"""
    if language in ['en', 'it']:
        session['language'] = language
    # Redirect back to the page the user came from
    return redirect(request.referrer or url_for('main.index'))
