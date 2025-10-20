from datetime import datetime
from app import db

class Guardian(db.Model):
    __tablename__ = 'guardians'
    
    id = db.Column(db.Integer, primary_key=True)
    
    # Personal data
    first_name = db.Column(db.String(100), nullable=False)
    last_name = db.Column(db.String(100), nullable=False)
    
    # Contact information
    phone = db.Column(db.String(20), nullable=False)
    email = db.Column(db.String(120), nullable=False, index=True)
    
    # Guardian type
    guardian_type = db.Column(db.String(10), nullable=False)  # 'father' or 'mother' or 'guardian'
    
    # Relationship with athlete
    athlete_id = db.Column(db.Integer, db.ForeignKey('athletes.id'), nullable=False)
    
    # Metadata
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    is_active = db.Column(db.Boolean, default=True, nullable=False)
    
    def get_full_name(self):
        """Returns the full name"""
        return f"{self.first_name} {self.last_name}"
    
    def get_guardian_type_display(self):
        """Returns the formatted guardian type"""
        mapping = {
            'father': 'Father',
            'mother': 'Mother', 
            'guardian': 'Guardian'
        }
        return mapping.get(self.guardian_type, self.guardian_type.title())
    
    def __repr__(self):
        return f'<Guardian {self.get_full_name()} ({self.get_guardian_type_display()})>'