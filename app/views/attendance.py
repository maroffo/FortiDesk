from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from flask_babel import gettext as _
from app import db
from app.models import Attendance, Athlete
from app.forms.attendance_forms import AttendanceForm, BulkAttendanceForm, AttendanceReportForm
from datetime import datetime

attendance_bp = Blueprint('attendance', __name__, url_prefix='/attendance')


@attendance_bp.route('/')
@login_required
def index():
    """List recent attendance records"""
    page = request.args.get('page', 1, type=int)
    per_page = 20

    query = Attendance.query.filter_by(is_active=True).order_by(Attendance.date.desc())

    # Filter by date if provided
    date_filter = request.args.get('date')
    if date_filter:
        try:
            filter_date = datetime.strptime(date_filter, '%Y-%m-%d').date()
            query = query.filter(Attendance.date == filter_date)
        except ValueError:
            pass

    # Filter by session type
    session_type = request.args.get('session_type')
    if session_type:
        query = query.filter(Attendance.session_type == session_type)

    pagination = query.paginate(page=page, per_page=per_page, error_out=False)
    attendance_records = pagination.items

    return render_template('attendance/index.html',
                           attendance_records=attendance_records,
                           pagination=pagination)


@attendance_bp.route('/check-in', methods=['GET', 'POST'])
@login_required
def check_in():
    """Bulk check-in for multiple athletes"""
    if not (current_user.is_admin() or current_user.is_coach()):
        flash(_('Permission denied. Only admins and coaches can record attendance.'), 'error')
        return redirect(url_for('attendance.index'))

    form = BulkAttendanceForm()
    athletes = Athlete.query.filter_by(is_active=True).order_by(Athlete.last_name, Athlete.first_name).all()

    if form.validate_on_submit():
        # Get selected athletes from request (checkboxes)
        present_ids = request.form.getlist('present')
        absent_ids = request.form.getlist('absent')
        excused_ids = request.form.getlist('excused')
        late_ids = request.form.getlist('late')

        count = 0
        for athlete_id in present_ids:
            attendance = Attendance(
                athlete_id=int(athlete_id),
                date=form.date.data,
                session_type=form.session_type.data,
                status='present',
                notes=form.notes.data,
                created_by=current_user.id
            )
            db.session.add(attendance)
            count += 1

        for athlete_id in absent_ids:
            attendance = Attendance(
                athlete_id=int(athlete_id),
                date=form.date.data,
                session_type=form.session_type.data,
                status='absent',
                notes=form.notes.data,
                created_by=current_user.id
            )
            db.session.add(attendance)
            count += 1

        for athlete_id in excused_ids:
            attendance = Attendance(
                athlete_id=int(athlete_id),
                date=form.date.data,
                session_type=form.session_type.data,
                status='excused',
                notes=form.notes.data,
                created_by=current_user.id
            )
            db.session.add(attendance)
            count += 1

        for athlete_id in late_ids:
            attendance = Attendance(
                athlete_id=int(athlete_id),
                date=form.date.data,
                session_type=form.session_type.data,
                status='late',
                notes=form.notes.data,
                created_by=current_user.id
            )
            db.session.add(attendance)
            count += 1

        db.session.commit()
        flash(_('Attendance recorded for %(count)d athletes.', count=count), 'success')
        return redirect(url_for('attendance.index'))

    return render_template('attendance/check_in.html', form=form, athletes=athletes)


@attendance_bp.route('/<int:id>')
@login_required
def view(id):
    """View attendance record details"""
    attendance = Attendance.query.get_or_404(id)
    return render_template('attendance/view.html', attendance=attendance)


@attendance_bp.route('/<int:id>/edit', methods=['GET', 'POST'])
@login_required
def edit(id):
    """Edit attendance record"""
    if not (current_user.is_admin() or current_user.is_coach()):
        flash(_('Permission denied.'), 'error')
        return redirect(url_for('attendance.index'))

    attendance = Attendance.query.get_or_404(id)
    form = AttendanceForm(obj=attendance)

    # Populate athlete choices
    athletes = Athlete.query.filter_by(is_active=True).order_by(Athlete.last_name, Athlete.first_name).all()
    form.athlete_id.choices = [(a.id, a.get_full_name()) for a in athletes]

    if form.validate_on_submit():
        attendance.athlete_id = form.athlete_id.data
        attendance.date = form.date.data
        attendance.session_type = form.session_type.data
        attendance.status = form.status.data
        attendance.notes = form.notes.data
        attendance.updated_at = datetime.utcnow()

        db.session.commit()
        flash(_('Attendance record updated successfully.'), 'success')
        return redirect(url_for('attendance.view', id=attendance.id))

    return render_template('attendance/edit.html', form=form, attendance=attendance)


@attendance_bp.route('/<int:id>/delete', methods=['POST'])
@login_required
def delete(id):
    """Delete (soft) attendance record"""
    if not current_user.is_admin():
        flash(_('Permission denied. Only admins can delete attendance records.'), 'error')
        return redirect(url_for('attendance.index'))

    attendance = Attendance.query.get_or_404(id)
    attendance.is_active = False
    db.session.commit()

    flash(_('Attendance record deleted.'), 'success')
    return redirect(url_for('attendance.index'))


@attendance_bp.route('/report', methods=['GET', 'POST'])
@login_required
def report():
    """Generate attendance report"""
    form = AttendanceReportForm()

    # Populate athlete choices
    athletes = Athlete.query.filter_by(is_active=True).order_by(Athlete.last_name, Athlete.first_name).all()
    form.athlete_id.choices = [('', _('All Athletes'))] + [(str(a.id), a.get_full_name()) for a in athletes]

    attendance_records = []
    stats = None

    if form.validate_on_submit() or request.method == 'GET':
        query = Attendance.query.filter_by(is_active=True)

        # Apply filters
        if form.athlete_id.data:
            query = query.filter(Attendance.athlete_id == int(form.athlete_id.data))

        if form.start_date.data:
            query = query.filter(Attendance.date >= form.start_date.data)

        if form.end_date.data:
            query = query.filter(Attendance.date <= form.end_date.data)

        if form.session_type.data:
            query = query.filter(Attendance.session_type == form.session_type.data)

        if form.status.data:
            query = query.filter(Attendance.status == form.status.data)

        attendance_records = query.order_by(Attendance.date.desc()).all()

        # Calculate stats
        if attendance_records:
            total = len(attendance_records)
            present_count = sum(1 for a in attendance_records if a.status == 'present')
            absent_count = sum(1 for a in attendance_records if a.status == 'absent')
            excused_count = sum(1 for a in attendance_records if a.status == 'excused')
            late_count = sum(1 for a in attendance_records if a.status == 'late')

            stats = {
                'total': total,
                'present': present_count,
                'absent': absent_count,
                'excused': excused_count,
                'late': late_count,
                'present_percentage': round((present_count / total * 100), 1) if total > 0 else 0
            }

    return render_template('attendance/report.html',
                           form=form,
                           attendance_records=attendance_records,
                           stats=stats)
