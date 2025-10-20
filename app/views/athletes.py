from datetime import datetime
from flask import Blueprint, render_template, request, redirect, url_for, flash, abort
from flask_login import login_required, current_user
from flask_babel import gettext as _
from app import db
from app.models import Athlete, Guardian
from app.forms.athletes_forms import AthleteForm

athletes_bp = Blueprint('athletes', __name__, url_prefix='/athletes')

@athletes_bp.route('/')
@login_required
def index():
    """List of all athletes in the registry"""
    page = request.args.get('page', 1, type=int)
    search = request.args.get('search', '')

    query = Athlete.query.filter_by(is_active=True)
    
    if search:
        search_filter = f"%{search}%"
        query = query.filter(
            (Athlete.first_name.ilike(search_filter)) |
            (Athlete.last_name.ilike(search_filter)) |
            (Athlete.fiscal_code.ilike(search_filter))
        )

    athletes = query.order_by(Athlete.last_name, Athlete.first_name).paginate(
        page=page, per_page=20, error_out=False
    )

    return render_template('athletes/index.html', athletes=athletes, search=search)

@athletes_bp.route('/new', methods=['GET', 'POST'])
@login_required
def new():
    """Create new athlete"""
    if not (current_user.is_admin() or current_user.is_coach()):
        flash(_('You do not have permission to create new athletes'), 'danger')
        return redirect(url_for('athletes.index'))

    form = AthleteForm()
    
    if form.validate_on_submit():
        try:
            # Check if fiscal code already exists
            existing_athlete = Athlete.query.filter_by(
                fiscal_code=form.fiscal_code.data.upper()
            ).first()

            if existing_athlete:
                flash(_('An athlete with this fiscal code already exists'), 'danger')
                return render_template('athletes/form.html', form=form, title=_('New Athlete'))

            # Create new athlete
            athlete = Athlete(
                first_name=form.first_name.data.strip().title(),
                last_name=form.last_name.data.strip().title(),
                birth_date=form.birth_date.data,
                birth_place=form.birth_place.data.strip().title(),
                fiscal_code=form.fiscal_code.data.upper(),
                street_address=form.street_address.data.strip(),
                street_number=form.street_number.data.strip(),
                postal_code=form.postal_code.data.strip(),
                city=form.city.data.strip().title(),
                province=form.province.data.upper(),
                document_number=form.document_number.data.strip(),
                issuing_authority=form.issuing_authority.data.strip(),
                document_expiry=form.document_expiry.data,
                has_medical_certificate=form.has_medical_certificate.data,
                certificate_type=form.certificate_type.data if form.has_medical_certificate.data else None,
                certificate_expiry=form.certificate_expiry.data if form.has_medical_certificate.data else None,
                created_by=current_user.id
            )

            db.session.add(athlete)
            db.session.flush()  # Get athlete ID

            # Create two guardians
            guardian1 = Guardian(
                first_name=form.guardian1_first_name.data.strip().title(),
                last_name=form.guardian1_last_name.data.strip().title(),
                phone=form.guardian1_phone.data.strip(),
                email=form.guardian1_email.data.strip().lower(),
                guardian_type=form.guardian1_type.data,
                athlete_id=athlete.id
            )

            guardian2 = Guardian(
                first_name=form.guardian2_first_name.data.strip().title(),
                last_name=form.guardian2_last_name.data.strip().title(),
                phone=form.guardian2_phone.data.strip(),
                email=form.guardian2_email.data.strip().lower(),
                guardian_type=form.guardian2_type.data,
                athlete_id=athlete.id
            )

            db.session.add(guardian1)
            db.session.add(guardian2)

            db.session.commit()

            flash(_('Athlete %(name)s created successfully!', name=athlete.get_full_name()), 'success')
            return redirect(url_for('athletes.detail', id=athlete.id))

        except Exception as e:
            db.session.rollback()
            flash(_('Error saving data. Please try again.'), 'danger')
            print(f"Error: {e}")

    return render_template('athletes/form.html', form=form, title=_('New Athlete'))

@athletes_bp.route('/<int:id>')
@login_required
def detail(id):
    """View athlete details"""
    athlete = Athlete.query.get_or_404(id)
    if not athlete.is_active:
        abort(404)

    return render_template('athletes/detail.html', athlete=athlete)

@athletes_bp.route('/<int:id>/edit', methods=['GET', 'POST'])
@login_required
def edit(id):
    """Edit athlete registry"""
    if not (current_user.is_admin() or current_user.is_coach()):
        flash(_('You do not have permission to edit athlete records'), 'danger')
        return redirect(url_for('athletes.detail', id=id))

    athlete = Athlete.query.get_or_404(id)
    if not athlete.is_active:
        abort(404)

    form = AthleteForm(obj=athlete)

    # Populate guardian data in form
    guardians = athlete.guardians
    if len(guardians) >= 1:
        form.guardian1_first_name.data = guardians[0].first_name
        form.guardian1_last_name.data = guardians[0].last_name
        form.guardian1_phone.data = guardians[0].phone
        form.guardian1_email.data = guardians[0].email
        form.guardian1_type.data = guardians[0].guardian_type

    if len(guardians) >= 2:
        form.guardian2_first_name.data = guardians[1].first_name
        form.guardian2_last_name.data = guardians[1].last_name
        form.guardian2_phone.data = guardians[1].phone
        form.guardian2_email.data = guardians[1].email
        form.guardian2_type.data = guardians[1].guardian_type
    
    if form.validate_on_submit():
        try:
            # Check fiscal code is not duplicated (excluding current athlete)
            existing_athlete = Athlete.query.filter(
                Athlete.fiscal_code == form.fiscal_code.data.upper(),
                Athlete.id != athlete.id
            ).first()

            if existing_athlete:
                flash(_('Another athlete with this fiscal code already exists'), 'danger')
                return render_template('athletes/form.html', form=form, title=_('Edit Athlete'), athlete=athlete)

            # Update athlete data
            athlete.first_name = form.first_name.data.strip().title()
            athlete.last_name = form.last_name.data.strip().title()
            athlete.birth_date = form.birth_date.data
            athlete.birth_place = form.birth_place.data.strip().title()
            athlete.fiscal_code = form.fiscal_code.data.upper()
            athlete.street_address = form.street_address.data.strip()
            athlete.street_number = form.street_number.data.strip()
            athlete.postal_code = form.postal_code.data.strip()
            athlete.city = form.city.data.strip().title()
            athlete.province = form.province.data.upper()
            athlete.document_number = form.document_number.data.strip()
            athlete.issuing_authority = form.issuing_authority.data.strip()
            athlete.document_expiry = form.document_expiry.data
            athlete.has_medical_certificate = form.has_medical_certificate.data
            athlete.certificate_type = form.certificate_type.data if form.has_medical_certificate.data else None
            athlete.certificate_expiry = form.certificate_expiry.data if form.has_medical_certificate.data else None
            athlete.updated_at = datetime.utcnow()

            # Update existing guardians or create new ones
            guardians = athlete.guardians

            # Update first guardian
            if len(guardians) >= 1:
                guardians[0].first_name = form.guardian1_first_name.data.strip().title()
                guardians[0].last_name = form.guardian1_last_name.data.strip().title()
                guardians[0].phone = form.guardian1_phone.data.strip()
                guardians[0].email = form.guardian1_email.data.strip().lower()
                guardians[0].guardian_type = form.guardian1_type.data
                guardians[0].updated_at = datetime.utcnow()
            else:
                new_guardian1 = Guardian(
                    first_name=form.guardian1_first_name.data.strip().title(),
                    last_name=form.guardian1_last_name.data.strip().title(),
                    phone=form.guardian1_phone.data.strip(),
                    email=form.guardian1_email.data.strip().lower(),
                    guardian_type=form.guardian1_type.data,
                    athlete_id=athlete.id
                )
                db.session.add(new_guardian1)

            # Update second guardian
            if len(guardians) >= 2:
                guardians[1].first_name = form.guardian2_first_name.data.strip().title()
                guardians[1].last_name = form.guardian2_last_name.data.strip().title()
                guardians[1].phone = form.guardian2_phone.data.strip()
                guardians[1].email = form.guardian2_email.data.strip().lower()
                guardians[1].guardian_type = form.guardian2_type.data
                guardians[1].updated_at = datetime.utcnow()
            else:
                new_guardian2 = Guardian(
                    first_name=form.guardian2_first_name.data.strip().title(),
                    last_name=form.guardian2_last_name.data.strip().title(),
                    phone=form.guardian2_phone.data.strip(),
                    email=form.guardian2_email.data.strip().lower(),
                    guardian_type=form.guardian2_type.data,
                    athlete_id=athlete.id
                )
                db.session.add(new_guardian2)

            db.session.commit()

            flash(_('Athlete %(name)s updated successfully!', name=athlete.get_full_name()), 'success')
            return redirect(url_for('athletes.detail', id=athlete.id))

        except Exception as e:
            db.session.rollback()
            flash(_('Error saving data. Please try again.'), 'danger')
            print(f"Error: {e}")

    return render_template('athletes/form.html', form=form, title=_('Edit Athlete'), athlete=athlete)

@athletes_bp.route('/<int:id>/delete', methods=['POST'])
@login_required
def delete(id):
    """Delete (deactivate) an athlete"""
    if not current_user.is_admin():
        flash(_('You do not have permission to delete athlete records'), 'danger')
        return redirect(url_for('athletes.detail', id=id))

    athlete = Athlete.query.get_or_404(id)

    try:
        athlete.is_active = False
        athlete.updated_at = datetime.utcnow()

        # Also deactivate guardians
        for guardian in athlete.guardians:
            guardian.is_active = False
            guardian.updated_at = datetime.utcnow()

        db.session.commit()

        flash(_('Athlete %(name)s deleted successfully', name=athlete.get_full_name()), 'success')
        return redirect(url_for('athletes.index'))

    except Exception as e:
        db.session.rollback()
        flash(_('Error during deletion. Please try again.'), 'danger')
        print(f"Error: {e}")
        return redirect(url_for('athletes.detail', id=id))