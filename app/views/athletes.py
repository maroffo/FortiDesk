from datetime import datetime
from flask import Blueprint, render_template, request, redirect, url_for, flash, abort
from flask_login import login_required, current_user
from flask_babel import gettext as _
from app import db
from sqlalchemy.orm import joinedload
from app.models import Athlete, Guardian, Team, Match, MatchLineup, EmergencyContact, Insurance
from app.forms.athletes_forms import AthleteForm
from app.forms.emergency_contact_forms import EmergencyContactForm
from app.forms.insurance_forms import InsuranceForm

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
    form._athlete_id = None

    # Populate team choices
    teams = Team.query.filter_by(is_active=True).order_by(Team.name).all()
    form.team_id.choices = [('', _('-- No Team --'))] + [(t.id, t.name) for t in teams]

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
                fir_id=form.fir_id.data.strip() if form.fir_id.data else None,
                team_id=form.team_id.data if form.team_id.data else None,
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
                allergies=form.allergies.data,
                medical_conditions=form.medical_conditions.data,
                blood_type=form.blood_type.data if form.blood_type.data else None,
                special_notes=form.special_notes.data,
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

    # Get match history from lineups, ordered by match date descending
    match_lineups = MatchLineup.query.join(
        MatchLineup.match
    ).options(
        joinedload(MatchLineup.match)
    ).filter(
        MatchLineup.athlete_id == id
    ).order_by(Match.date.desc()).all()

    emergency_contacts = EmergencyContact.query.filter_by(
        athlete_id=id, is_active=True
    ).all()

    return render_template('athletes/detail.html', athlete=athlete,
                           match_lineups=match_lineups,
                           emergency_contacts=emergency_contacts)

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
    form._athlete_id = athlete.id

    # Populate team choices
    teams = Team.query.filter_by(is_active=True).order_by(Team.name).all()
    form.team_id.choices = [('', _('-- No Team --'))] + [(t.id, t.name) for t in teams]

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
            athlete.fir_id = form.fir_id.data.strip() if form.fir_id.data else None
            athlete.team_id = form.team_id.data if form.team_id.data else None
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
            athlete.allergies = form.allergies.data
            athlete.medical_conditions = form.medical_conditions.data
            athlete.blood_type = form.blood_type.data if form.blood_type.data else None
            athlete.special_notes = form.special_notes.data
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


@athletes_bp.route('/<int:id>/emergency-contacts/add', methods=['GET', 'POST'])
@login_required
def add_emergency_contact(id):
    """Add emergency contact to athlete"""
    if not (current_user.is_admin() or current_user.is_coach()):
        flash(_('Permission denied.'), 'error')
        return redirect(url_for('athletes.detail', id=id))

    athlete = Athlete.query.get_or_404(id)
    if not athlete.is_active:
        abort(404)

    form = EmergencyContactForm()
    if form.validate_on_submit():
        contact = EmergencyContact(
            athlete_id=id,
            contact_name=form.contact_name.data.strip(),
            relationship=form.relationship.data,
            phone=form.phone.data.strip(),
            email=form.email.data.strip() if form.email.data else None,
            is_primary_doctor=form.is_primary_doctor.data,
            medical_notes=form.medical_notes.data
        )
        db.session.add(contact)
        db.session.commit()
        flash(_('Emergency contact added.'), 'success')
        return redirect(url_for('athletes.detail', id=id))

    return render_template('athletes/emergency_contact_form.html',
                           form=form, athlete=athlete)


@athletes_bp.route('/<int:athlete_id>/emergency-contacts/<int:id>/edit', methods=['GET', 'POST'])
@login_required
def edit_emergency_contact(athlete_id, id):
    """Edit emergency contact"""
    if not (current_user.is_admin() or current_user.is_coach()):
        flash(_('Permission denied.'), 'error')
        return redirect(url_for('athletes.detail', id=athlete_id))

    athlete = Athlete.query.get_or_404(athlete_id)
    if not athlete.is_active:
        abort(404)

    contact = EmergencyContact.query.get_or_404(id)
    form = EmergencyContactForm(obj=contact)

    if form.validate_on_submit():
        contact.contact_name = form.contact_name.data.strip()
        contact.relationship = form.relationship.data
        contact.phone = form.phone.data.strip()
        contact.email = form.email.data.strip() if form.email.data else None
        contact.is_primary_doctor = form.is_primary_doctor.data
        contact.medical_notes = form.medical_notes.data
        contact.updated_at = datetime.utcnow()
        db.session.commit()
        flash(_('Emergency contact updated.'), 'success')
        return redirect(url_for('athletes.detail', id=athlete_id))

    return render_template('athletes/emergency_contact_form.html',
                           form=form, athlete=athlete, contact=contact)


@athletes_bp.route('/<int:athlete_id>/emergency-contacts/<int:id>/delete', methods=['POST'])
@login_required
def delete_emergency_contact(athlete_id, id):
    """Remove emergency contact (soft delete)"""
    if not (current_user.is_admin() or current_user.is_coach()):
        flash(_('Permission denied.'), 'error')
        return redirect(url_for('athletes.detail', id=athlete_id))

    contact = EmergencyContact.query.get_or_404(id)
    contact.is_active = False
    contact.updated_at = datetime.utcnow()
    db.session.commit()
    flash(_('Emergency contact removed.'), 'success')
    return redirect(url_for('athletes.detail', id=athlete_id))


@athletes_bp.route('/<int:id>/insurance/new', methods=['GET', 'POST'])
@login_required
def insurance_new(id):
    """Add insurance policy for an athlete."""
    if not (current_user.is_admin() or current_user.is_coach()):
        flash(_('Permission denied.'), 'error')
        return redirect(url_for('main.dashboard'))

    athlete = Athlete.query.get_or_404(id)
    if not athlete.is_active:
        abort(404)

    form = InsuranceForm()

    if form.validate_on_submit():
        insurance = Insurance(
            policy_number=form.policy_number.data,
            provider=form.provider.data,
            insurance_type=form.insurance_type.data,
            start_date=form.start_date.data,
            end_date=form.end_date.data,
            coverage_amount=form.coverage_amount.data,
            premium_amount=form.premium_amount.data,
            notes=form.notes.data,
            athlete_id=athlete.id,
            created_by=current_user.id
        )
        db.session.add(insurance)
        db.session.commit()
        flash(_('Insurance policy added successfully.'), 'success')
        return redirect(url_for('athletes.detail', id=athlete.id))

    return render_template('athletes/insurance_form.html', form=form, athlete=athlete)


@athletes_bp.route('/<int:id>/insurance/<int:ins_id>/edit', methods=['GET', 'POST'])
@login_required
def insurance_edit(id, ins_id):
    """Edit an insurance policy."""
    if not (current_user.is_admin() or current_user.is_coach()):
        flash(_('Permission denied.'), 'error')
        return redirect(url_for('main.dashboard'))

    athlete = Athlete.query.get_or_404(id)
    if not athlete.is_active:
        abort(404)

    insurance = Insurance.query.get_or_404(ins_id)

    if insurance.athlete_id != athlete.id:
        flash(_('Insurance policy not found.'), 'error')
        return redirect(url_for('athletes.detail', id=athlete.id))

    form = InsuranceForm(obj=insurance)

    if form.validate_on_submit():
        form.populate_obj(insurance)
        insurance.updated_at = datetime.utcnow()
        db.session.commit()
        flash(_('Insurance policy updated successfully.'), 'success')
        return redirect(url_for('athletes.detail', id=athlete.id))

    return render_template('athletes/insurance_form.html', form=form, athlete=athlete, insurance=insurance)


@athletes_bp.route('/<int:id>/insurance/<int:ins_id>/delete', methods=['POST'])
@login_required
def insurance_delete(id, ins_id):
    """Soft delete an insurance policy."""
    if not current_user.is_admin():
        flash(_('Permission denied.'), 'error')
        return redirect(url_for('athletes.detail', id=id))

    insurance = Insurance.query.get_or_404(ins_id)
    if insurance.athlete_id != id:
        flash(_('Insurance policy not found.'), 'error')
        return redirect(url_for('athletes.detail', id=id))

    insurance.is_active = False
    insurance.updated_at = datetime.utcnow()
    db.session.commit()
    flash(_('Insurance policy deleted.'), 'success')
    return redirect(url_for('athletes.detail', id=id))