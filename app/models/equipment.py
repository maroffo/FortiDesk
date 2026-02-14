from datetime import datetime, date
from flask_babel import gettext as _
from app import db


class Equipment(db.Model):
    """Equipment inventory management"""

    __tablename__ = 'equipment'

    # Primary key
    id = db.Column(db.Integer, primary_key=True)

    # Equipment details
    name = db.Column(db.String(100), nullable=False, index=True)
    category = db.Column(db.String(50), nullable=False, index=True)  # ball, jersey, protective, training_aid
    size = db.Column(db.String(20))  # XS, S, M, L, XL, or numeric sizes
    code = db.Column(db.String(50), unique=True, index=True)  # Inventory code/barcode
    condition = db.Column(db.String(20), nullable=False)  # new, good, fair, poor, damaged
    status = db.Column(db.String(20), nullable=False, default='available')  # available, assigned, maintenance, retired

    # Purchase/value info
    purchase_date = db.Column(db.Date)
    purchase_price = db.Column(db.Numeric(10, 2))
    supplier = db.Column(db.String(100))

    # Maintenance
    last_maintenance_date = db.Column(db.Date)
    next_maintenance_date = db.Column(db.Date)
    maintenance_notes = db.Column(db.Text)

    # Additional info
    description = db.Column(db.Text)
    location = db.Column(db.String(100))  # Storage location
    quantity = db.Column(db.Integer, default=1)  # For bulk items

    # Metadata
    created_by = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    is_active = db.Column(db.Boolean, default=True, nullable=False)

    # Relationships
    creator = db.relationship('User', backref=db.backref('equipment_created', lazy='dynamic'))
    assignments = db.relationship('EquipmentAssignment', backref='equipment', lazy='dynamic',
                                   cascade='all, delete-orphan')

    def __repr__(self):
        return f'<Equipment {self.name} ({self.code})>'

    def get_category_display(self):
        """Return localized category display"""
        category_map = {
            'ball': _('Ball'),
            'jersey': _('Jersey'),
            'protective': _('Protective Gear'),
            'training_aid': _('Training Aid'),
            'other': _('Other')
        }
        return category_map.get(self.category, self.category)

    def get_condition_display(self):
        """Return localized condition display"""
        condition_map = {
            'new': _('New'),
            'good': _('Good'),
            'fair': _('Fair'),
            'poor': _('Poor'),
            'damaged': _('Damaged')
        }
        return condition_map.get(self.condition, self.condition)

    def get_status_display(self):
        """Return localized status display"""
        status_map = {
            'available': _('Available'),
            'assigned': _('Assigned'),
            'maintenance': _('In Maintenance'),
            'retired': _('Retired')
        }
        return status_map.get(self.status, self.status)

    def needs_maintenance(self):
        """Check if equipment needs maintenance"""
        if self.next_maintenance_date:
            return self.next_maintenance_date <= date.today()
        return False

    def is_available(self):
        """Check if equipment is available for assignment"""
        return self.status == 'available' and self.is_active


class EquipmentAssignment(db.Model):
    """Track equipment assignments to athletes"""

    __tablename__ = 'equipment_assignments'

    # Primary key
    id = db.Column(db.Integer, primary_key=True)

    # Foreign keys
    equipment_id = db.Column(db.Integer, db.ForeignKey('equipment.id'), nullable=False)
    athlete_id = db.Column(db.Integer, db.ForeignKey('athletes.id'), nullable=False)
    assigned_by = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    returned_by = db.Column(db.Integer, db.ForeignKey('users.id'))

    # Assignment details
    assigned_date = db.Column(db.Date, nullable=False, default=date.today, index=True)
    expected_return_date = db.Column(db.Date)
    actual_return_date = db.Column(db.Date, index=True)

    # Condition tracking
    condition_at_assignment = db.Column(db.String(20), nullable=False)
    condition_at_return = db.Column(db.String(20))

    # Notes
    assignment_notes = db.Column(db.Text)
    return_notes = db.Column(db.Text)

    # Status
    is_returned = db.Column(db.Boolean, default=False, nullable=False)
    is_active = db.Column(db.Boolean, default=True, nullable=False)

    # Metadata
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    athlete = db.relationship('Athlete', backref=db.backref('equipment_assignments', lazy='dynamic'))
    assigner = db.relationship('User', foreign_keys=[assigned_by],
                                backref=db.backref('assignments_made', lazy='dynamic'))
    returner = db.relationship('User', foreign_keys=[returned_by],
                               backref=db.backref('returns_processed', lazy='dynamic'))

    # Indexes
    __table_args__ = (
        db.Index('idx_assignment_athlete', 'athlete_id', 'is_returned'),
        db.Index('idx_assignment_equipment', 'equipment_id', 'is_returned'),
    )

    def __repr__(self):
        return f'<EquipmentAssignment {self.equipment.name} to {self.athlete.get_full_name()}>'

    def is_overdue(self):
        """Check if assignment is overdue"""
        if not self.is_returned and self.expected_return_date:
            return self.expected_return_date < date.today()
        return False

    def days_overdue(self):
        """Calculate days overdue"""
        if self.is_overdue():
            return (date.today() - self.expected_return_date).days
        return 0
