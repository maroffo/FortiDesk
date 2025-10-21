from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from flask_babel import gettext as _
from app import db
from app.models import Equipment, EquipmentAssignment, Athlete
from app.forms.equipment_forms import (EquipmentForm, EquipmentAssignmentForm,
                                       EquipmentReturnForm, EquipmentSearchForm)
from datetime import datetime

equipment_bp = Blueprint('equipment', __name__, url_prefix='/equipment')


@equipment_bp.route('/')
@login_required
def index():
    """List equipment inventory"""
    page = request.args.get('page', 1, type=int)
    per_page = 20

    form = EquipmentSearchForm(formdata=request.args)
    query = Equipment.query.filter_by(is_active=True)

    # Apply filters
    if form.category.data:
        query = query.filter(Equipment.category == form.category.data)

    if form.status.data:
        query = query.filter(Equipment.status == form.status.data)

    if form.condition.data:
        query = query.filter(Equipment.condition == form.condition.data)

    search = request.args.get('search', '')
    if search:
        query = query.filter(
            db.or_(
                Equipment.name.ilike(f'%{search}%'),
                Equipment.code.ilike(f'%{search}%'),
                Equipment.description.ilike(f'%{search}%')
            )
        )

    pagination = query.order_by(Equipment.name).paginate(page=page, per_page=per_page, error_out=False)
    equipment_items = pagination.items

    return render_template('equipment/index.html',
                           equipment_items=equipment_items,
                           pagination=pagination,
                           form=form,
                           search=search)


@equipment_bp.route('/new', methods=['GET', 'POST'])
@login_required
def new():
    """Create new equipment"""
    if not (current_user.is_admin() or current_user.is_coach()):
        flash(_('Permission denied.'), 'error')
        return redirect(url_for('equipment.index'))

    form = EquipmentForm()

    if form.validate_on_submit():
        # Check if code already exists
        existing = Equipment.query.filter_by(code=form.code.data, is_active=True).first()
        if existing:
            flash(_('Equipment code already exists.'), 'error')
            return render_template('equipment/new.html', form=form)

        equipment = Equipment(
            name=form.name.data,
            category=form.category.data,
            size=form.size.data,
            code=form.code.data,
            condition=form.condition.data,
            status=form.status.data,
            purchase_date=form.purchase_date.data,
            purchase_price=form.purchase_price.data,
            supplier=form.supplier.data,
            location=form.location.data,
            quantity=form.quantity.data or 1,
            description=form.description.data,
            maintenance_notes=form.maintenance_notes.data,
            last_maintenance_date=form.last_maintenance_date.data,
            next_maintenance_date=form.next_maintenance_date.data,
            created_by=current_user.id
        )

        db.session.add(equipment)
        db.session.commit()

        flash(_('Equipment added successfully.'), 'success')
        return redirect(url_for('equipment.view', id=equipment.id))

    return render_template('equipment/new.html', form=form)


@equipment_bp.route('/<int:id>')
@login_required
def view(id):
    """View equipment details"""
    equipment = Equipment.query.get_or_404(id)

    # Get assignment history
    assignments = EquipmentAssignment.query.filter_by(
        equipment_id=id,
        is_active=True
    ).order_by(EquipmentAssignment.assigned_date.desc()).all()

    return render_template('equipment/view.html', equipment=equipment, assignments=assignments)


@equipment_bp.route('/<int:id>/edit', methods=['GET', 'POST'])
@login_required
def edit(id):
    """Edit equipment"""
    if not (current_user.is_admin() or current_user.is_coach()):
        flash(_('Permission denied.'), 'error')
        return redirect(url_for('equipment.index'))

    equipment = Equipment.query.get_or_404(id)
    form = EquipmentForm(obj=equipment)

    if form.validate_on_submit():
        # Check code uniqueness
        existing = Equipment.query.filter(
            Equipment.code == form.code.data,
            Equipment.id != id,
            Equipment.is_active
        ).first()
        if existing:
            flash(_('Equipment code already exists.'), 'error')
            return render_template('equipment/edit.html', form=form, equipment=equipment)

        equipment.name = form.name.data
        equipment.category = form.category.data
        equipment.size = form.size.data
        equipment.code = form.code.data
        equipment.condition = form.condition.data
        equipment.status = form.status.data
        equipment.purchase_date = form.purchase_date.data
        equipment.purchase_price = form.purchase_price.data
        equipment.supplier = form.supplier.data
        equipment.location = form.location.data
        equipment.quantity = form.quantity.data or 1
        equipment.description = form.description.data
        equipment.maintenance_notes = form.maintenance_notes.data
        equipment.last_maintenance_date = form.last_maintenance_date.data
        equipment.next_maintenance_date = form.next_maintenance_date.data
        equipment.updated_at = datetime.utcnow()

        db.session.commit()
        flash(_('Equipment updated successfully.'), 'success')
        return redirect(url_for('equipment.view', id=equipment.id))

    return render_template('equipment/edit.html', form=form, equipment=equipment)


@equipment_bp.route('/<int:id>/delete', methods=['POST'])
@login_required
def delete(id):
    """Delete (soft) equipment"""
    if not current_user.is_admin():
        flash(_('Permission denied.'), 'error')
        return redirect(url_for('equipment.index'))

    equipment = Equipment.query.get_or_404(id)
    equipment.is_active = False
    db.session.commit()

    flash(_('Equipment deleted.'), 'success')
    return redirect(url_for('equipment.index'))


@equipment_bp.route('/assign', methods=['GET', 'POST'])
@login_required
def assign():
    """Assign equipment to athlete"""
    if not (current_user.is_admin() or current_user.is_coach()):
        flash(_('Permission denied.'), 'error')
        return redirect(url_for('equipment.index'))

    form = EquipmentAssignmentForm()

    # Populate choices
    available_equipment = Equipment.query.filter_by(status='available', is_active=True).order_by(Equipment.name).all()
    form.equipment_id.choices = [(e.id, f'{e.name} ({e.code})') for e in available_equipment]

    athletes = Athlete.query.filter_by(is_active=True).order_by(Athlete.last_name, Athlete.first_name).all()
    form.athlete_id.choices = [(a.id, a.get_full_name()) for a in athletes]

    if form.validate_on_submit():
        equipment = Equipment.query.get(form.equipment_id.data)

        assignment = EquipmentAssignment(
            equipment_id=form.equipment_id.data,
            athlete_id=form.athlete_id.data,
            assigned_date=form.assigned_date.data,
            expected_return_date=form.expected_return_date.data,
            condition_at_assignment=form.condition_at_assignment.data,
            assignment_notes=form.assignment_notes.data,
            assigned_by=current_user.id
        )

        # Update equipment status
        equipment.status = 'assigned'

        db.session.add(assignment)
        db.session.commit()

        flash(_('Equipment assigned successfully.'), 'success')
        return redirect(url_for('equipment.assignments'))

    return render_template('equipment/assign.html', form=form)


@equipment_bp.route('/assignments')
@login_required
def assignments():
    """List all equipment assignments"""
    page = request.args.get('page', 1, type=int)
    per_page = 20

    # Show only active (not returned) assignments by default
    show_all = request.args.get('show_all', 0, type=int)

    query = EquipmentAssignment.query.filter_by(is_active=True)
    if not show_all:
        query = query.filter_by(is_returned=False)

    pagination = query.order_by(EquipmentAssignment.assigned_date.desc()).paginate(
        page=page, per_page=per_page, error_out=False
    )
    assignments = pagination.items

    return render_template('equipment/assignments.html',
                           assignments=assignments,
                           pagination=pagination,
                           show_all=show_all)


@equipment_bp.route('/assignments/<int:id>/return', methods=['GET', 'POST'])
@login_required
def return_equipment(id):
    """Process equipment return"""
    if not (current_user.is_admin() or current_user.is_coach()):
        flash(_('Permission denied.'), 'error')
        return redirect(url_for('equipment.assignments'))

    assignment = EquipmentAssignment.query.get_or_404(id)

    if assignment.is_returned:
        flash(_('This equipment has already been returned.'), 'warning')
        return redirect(url_for('equipment.assignments'))

    form = EquipmentReturnForm()

    if form.validate_on_submit():
        assignment.actual_return_date = form.actual_return_date.data
        assignment.condition_at_return = form.condition_at_return.data
        assignment.return_notes = form.return_notes.data
        assignment.is_returned = True
        assignment.returned_by = current_user.id
        assignment.updated_at = datetime.utcnow()

        # Update equipment status and condition
        equipment = assignment.equipment
        equipment.status = 'available'
        equipment.condition = form.condition_at_return.data

        db.session.commit()

        flash(_('Equipment return processed successfully.'), 'success')
        return redirect(url_for('equipment.assignments'))

    return render_template('equipment/return.html', form=form, assignment=assignment)
