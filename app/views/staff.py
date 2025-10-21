from datetime import datetime
from flask import Blueprint, render_template, request, redirect, url_for, flash, abort
from flask_login import login_required, current_user
from flask_babel import gettext as _
from app import db
from app.models import Staff
from app.forms.staff_forms import StaffForm

staff_bp = Blueprint('staff', __name__, url_prefix='/staff')

@staff_bp.route('/')
@login_required
def index():
    """List of all staff members"""
    page = request.args.get('page', 1, type=int)
    search = request.args.get('search', '')
    role_filter = request.args.get('role', '')

    query = Staff.query.filter_by(is_active=True)

    if search:
        search_filter = f"%{search}%"
        query = query.filter(
            (Staff.first_name.ilike(search_filter)) |
            (Staff.last_name.ilike(search_filter)) |
            (Staff.fiscal_code.ilike(search_filter)) |
            (Staff.email.ilike(search_filter))
        )

    if role_filter:
        query = query.filter_by(role=role_filter)

    staff_members = query.order_by(Staff.last_name, Staff.first_name).paginate(
        page=page, per_page=20, error_out=False
    )

    return render_template('staff/index.html',
                         staff_members=staff_members,
                         search=search,
                         role_filter=role_filter)

@staff_bp.route('/new', methods=['GET', 'POST'])
@login_required
def new():
    """Create new staff member"""
    if not (current_user.is_admin() or current_user.is_coach()):
        flash(_('You do not have permission to create new staff members'), 'danger')
        return redirect(url_for('staff.index'))

    form = StaffForm()

    if form.validate_on_submit():
        try:
            # Check if fiscal code already exists
            existing_staff = Staff.query.filter_by(
                fiscal_code=form.fiscal_code.data.upper()
            ).first()

            if existing_staff:
                flash(_('A staff member with this fiscal code already exists'), 'danger')
                return render_template('staff/form.html', form=form, title=_('New Staff Member'))

            # Create new staff member
            staff = Staff(
                first_name=form.first_name.data.strip().title(),
                last_name=form.last_name.data.strip().title(),
                birth_date=form.birth_date.data,
                birth_place=form.birth_place.data.strip().title(),
                fiscal_code=form.fiscal_code.data.upper(),
                phone=form.phone.data.strip(),
                email=form.email.data.strip().lower(),
                street_address=form.street_address.data.strip(),
                street_number=form.street_number.data.strip(),
                postal_code=form.postal_code.data.strip(),
                city=form.city.data.strip().title(),
                province=form.province.data.upper(),
                document_number=form.document_number.data.strip(),
                issuing_authority=form.issuing_authority.data.strip(),
                document_expiry=form.document_expiry.data,
                role=form.role.data,
                role_notes=form.role_notes.data.strip() if form.role_notes.data else None,
                has_medical_certificate=form.has_medical_certificate.data,
                certificate_type=form.certificate_type.data if form.has_medical_certificate.data else None,
                certificate_expiry=form.certificate_expiry.data if form.has_medical_certificate.data else None,
                has_background_check=form.has_background_check.data,
                background_check_date=form.background_check_date.data if form.has_background_check.data else None,
                background_check_expiry=form.background_check_expiry.data if form.has_background_check.data else None,
                created_by=current_user.id
            )

            db.session.add(staff)
            db.session.commit()

            flash(_('Staff member %(name)s created successfully!', name=staff.get_full_name()), 'success')
            return redirect(url_for('staff.detail', id=staff.id))

        except Exception as e:
            db.session.rollback()
            flash(_('Error saving data. Please try again.'), 'danger')
            print(f"Error: {e}")

    return render_template('staff/form.html', form=form, title=_('New Staff Member'))

@staff_bp.route('/<int:id>')
@login_required
def detail(id):
    """View staff member details"""
    staff = Staff.query.get_or_404(id)
    if not staff.is_active:
        abort(404)

    return render_template('staff/detail.html', staff=staff)

@staff_bp.route('/<int:id>/edit', methods=['GET', 'POST'])
@login_required
def edit(id):
    """Edit staff member"""
    if not (current_user.is_admin() or current_user.is_coach()):
        flash(_('You do not have permission to edit staff records'), 'danger')
        return redirect(url_for('staff.detail', id=id))

    staff = Staff.query.get_or_404(id)
    if not staff.is_active:
        abort(404)

    form = StaffForm(obj=staff)

    if form.validate_on_submit():
        try:
            # Check fiscal code is not duplicated (excluding current staff member)
            existing_staff = Staff.query.filter(
                Staff.fiscal_code == form.fiscal_code.data.upper(),
                Staff.id != staff.id
            ).first()

            if existing_staff:
                flash(_('Another staff member with this fiscal code already exists'), 'danger')
                return render_template('staff/form.html', form=form, title=_('Edit Staff Member'), staff=staff)

            # Update staff data
            staff.first_name = form.first_name.data.strip().title()
            staff.last_name = form.last_name.data.strip().title()
            staff.birth_date = form.birth_date.data
            staff.birth_place = form.birth_place.data.strip().title()
            staff.fiscal_code = form.fiscal_code.data.upper()
            staff.phone = form.phone.data.strip()
            staff.email = form.email.data.strip().lower()
            staff.street_address = form.street_address.data.strip()
            staff.street_number = form.street_number.data.strip()
            staff.postal_code = form.postal_code.data.strip()
            staff.city = form.city.data.strip().title()
            staff.province = form.province.data.upper()
            staff.document_number = form.document_number.data.strip()
            staff.issuing_authority = form.issuing_authority.data.strip()
            staff.document_expiry = form.document_expiry.data
            staff.role = form.role.data
            staff.role_notes = form.role_notes.data.strip() if form.role_notes.data else None
            staff.has_medical_certificate = form.has_medical_certificate.data
            staff.certificate_type = form.certificate_type.data if form.has_medical_certificate.data else None
            staff.certificate_expiry = form.certificate_expiry.data if form.has_medical_certificate.data else None
            staff.has_background_check = form.has_background_check.data
            staff.background_check_date = form.background_check_date.data if form.has_background_check.data else None
            staff.background_check_expiry = form.background_check_expiry.data if form.has_background_check.data else None
            staff.updated_at = datetime.utcnow()

            db.session.commit()

            flash(_('Staff member %(name)s updated successfully!', name=staff.get_full_name()), 'success')
            return redirect(url_for('staff.detail', id=staff.id))

        except Exception as e:
            db.session.rollback()
            flash(_('Error saving data. Please try again.'), 'danger')
            print(f"Error: {e}")

    return render_template('staff/form.html', form=form, title=_('Edit Staff Member'), staff=staff)

@staff_bp.route('/<int:id>/delete', methods=['POST'])
@login_required
def delete(id):
    """Delete (deactivate) a staff member"""
    if not current_user.is_admin():
        flash(_('You do not have permission to delete staff records'), 'danger')
        return redirect(url_for('staff.detail', id=id))

    staff = Staff.query.get_or_404(id)

    try:
        staff.is_active = False
        staff.updated_at = datetime.utcnow()

        db.session.commit()

        flash(_('Staff member %(name)s deleted successfully', name=staff.get_full_name()), 'success')
        return redirect(url_for('staff.index'))

    except Exception as e:
        db.session.rollback()
        flash(_('Error during deletion. Please try again.'), 'danger')
        print(f"Error: {e}")
        return redirect(url_for('staff.detail', id=id))
