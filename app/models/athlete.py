from datetime import datetime, date
from app import db

class Athlete(db.Model):
    __tablename__ = 'athletes'
    
    id = db.Column(db.Integer, primary_key=True)
    
    # Personal data
    first_name = db.Column(db.String(100), nullable=False)
    last_name = db.Column(db.String(100), nullable=False)
    birth_date = db.Column(db.Date, nullable=False)
    birth_place = db.Column(db.String(100), nullable=False)
    fiscal_code = db.Column(db.String(16), unique=True, nullable=False, index=True)
    
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
    
    # Medical certificate/sports booklet
    has_medical_certificate = db.Column(db.Boolean, default=False, nullable=False)
    certificate_type = db.Column(db.String(50), nullable=True)  # 'medical' or 'sports_booklet'
    certificate_expiry = db.Column(db.Date, nullable=True)
    
    # Metadata
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    created_by = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    is_active = db.Column(db.Boolean, default=True, nullable=False)
    
    # Relationships
    guardians = db.relationship('Guardian', backref='athlete', lazy=True, cascade='all, delete-orphan')
    created_by_user = db.relationship('User', backref='athletes_created')
    
    def get_full_name(self):
        """Returns the full name"""
        return f"{self.first_name} {self.last_name}"
    
    def get_age(self):
        """Calculates the athlete's age"""
        today = date.today()
        return today.year - self.birth_date.year - ((today.month, today.day) < (self.birth_date.month, self.birth_date.day))
    
    def get_full_address(self):
        """Returns the formatted full address"""
        return f"{self.street_address} {self.street_number}, {self.postal_code} {self.city} ({self.province})"
    
    def is_certificate_expired(self):
        """Checks if the medical certificate is expired"""
        if not self.has_medical_certificate or not self.certificate_expiry:
            return True
        return self.certificate_expiry < date.today()
    
    def is_document_expired(self):
        """Checks if the document is expired"""
        return self.document_expiry < date.today()
    
    def days_until_certificate_expiry(self):
        """Returns days remaining until certificate expiry"""
        if not self.certificate_expiry:
            return None
        return (self.certificate_expiry - date.today()).days
    
    def days_until_document_expiry(self):
        """Returns days remaining until document expiry"""
        return (self.document_expiry - date.today()).days
    
    def __repr__(self):
        return f'<Athlete {self.get_full_name()}>'