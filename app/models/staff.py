from datetime import datetime
from flask_babel import gettext as _
from app import db


class Staff(db.Model):
    __tablename__ = 'staff'

    id = db.Column(db.Integer, primary_key=True)

    # Personal data
    first_name = db.Column(db.String(100), nullable=False)
    last_name = db.Column(db.String(100), nullable=False)
    birth_date = db.Column(db.Date, nullable=False)
    birth_place = db.Column(db.String(100), nullable=False)
    fiscal_code = db.Column(db.String(16), unique=True, nullable=False, index=True)

    # Contact information
    phone = db.Column(db.String(20), nullable=False)
    email = db.Column(db.String(120), nullable=False, index=True)

    # Residential address
    street_address = db.Column(db.String(200), nullable=False)
    street_number = db.Column(db.String(10), nullable=False)
    postal_code = db.Column(db.String(5), nullable=False)
    city = db.Column(db.String(100), nullable=False)
    province = db.Column(db.String(2), nullable=False)

    # Identity document
    document_number = db.Column(db.String(50), nullable=False)
    issuing_authority = db.Column(db.String(100), nullable=False)
    document_expiry = db.Column(db.Date, nullable=False)

    # Role in organization
    # Possible values: 'coach', 'assistant_coach', 'escort', 'manager', 'president', 'vice_president', 'secretary'
    role = db.Column(db.String(50), nullable=False, index=True)

    # Additional role information
    role_notes = db.Column(db.Text, nullable=True)  # e.g., "Head coach U12", "Team manager"

    # Medical certificate (required for coaches and escorts who accompany teams)
    has_medical_certificate = db.Column(db.Boolean, default=False, nullable=False)
    certificate_type = db.Column(db.String(50), nullable=True)  # 'medical' or 'sports_booklet'
    certificate_expiry = db.Column(db.Date, nullable=True)

    # Background check (for those working with minors)
    has_background_check = db.Column(db.Boolean, default=False, nullable=False)
    background_check_date = db.Column(db.Date, nullable=True)
    background_check_expiry = db.Column(db.Date, nullable=True)

    # Metadata
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    created_by = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    is_active = db.Column(db.Boolean, default=True, nullable=False)

    # Relationships
    created_by_user = db.relationship('User', backref='staff_created')

    def get_full_name(self):
        """Returns the full name"""
        return f"{self.first_name} {self.last_name}"

    def get_age(self):
        """Calculates the staff member's age"""
        from datetime import date
        today = date.today()
        return today.year - self.birth_date.year - ((today.month, today.day) < (self.birth_date.month, self.birth_date.day))

    def get_full_address(self):
        """Returns the formatted full address"""
        return f"{self.street_address} {self.street_number}, {self.postal_code} {self.city} ({self.province})"

    def get_role_display(self):
        """Returns the formatted role name"""
        role_mapping = {
            'coach': _('Coach'),
            'assistant_coach': _('Assistant Coach'),
            'escort': _('Escort'),
            'manager': _('Manager'),
            'president': _('President'),
            'vice_president': _('Vice President'),
            'secretary': _('Secretary')
        }
        return role_mapping.get(self.role, self.role.replace('_', ' ').title())

    def is_certificate_expired(self):
        """Checks if the medical certificate is expired"""
        from datetime import date
        if not self.has_medical_certificate or not self.certificate_expiry:
            return True
        return self.certificate_expiry < date.today()

    def is_document_expired(self):
        """Checks if the document is expired"""
        from datetime import date
        return self.document_expiry < date.today()

    def is_background_check_expired(self):
        """Checks if the background check is expired"""
        from datetime import date
        if not self.has_background_check or not self.background_check_expiry:
            return True
        return self.background_check_expiry < date.today()

    def days_until_certificate_expiry(self):
        """Returns days remaining until certificate expiry"""
        from datetime import date
        if not self.certificate_expiry:
            return None
        return (self.certificate_expiry - date.today()).days

    def days_until_document_expiry(self):
        """Returns days remaining until document expiry"""
        from datetime import date
        return (self.document_expiry - date.today()).days

    def days_until_background_check_expiry(self):
        """Returns days remaining until background check expiry"""
        from datetime import date
        if not self.background_check_expiry:
            return None
        return (self.background_check_expiry - date.today()).days

    def requires_medical_certificate(self):
        """Checks if this role requires a medical certificate"""
        return self.role in ['coach', 'assistant_coach', 'escort']

    def requires_background_check(self):
        """Checks if this role requires a background check"""
        return self.role in ['coach', 'assistant_coach', 'escort']

    def __repr__(self):
        return f'<Staff {self.get_full_name()} ({self.get_role_display()})>'
