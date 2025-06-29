from app import db
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash

class User(db.Model):
    __tablename__ = 'users'
    
    user_id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(20), nullable=False, default='pending')

    # Job seeker fields
    skills = db.Column(db.Text, nullable=True)
    current_role = db.Column(db.String(100))
    preferred_location = db.Column(db.String(100))

    # Employer profile fields
    company_name = db.Column(db.String(255), nullable=True)
    experience = db.Column(db.String(50), nullable=True)
    industry = db.Column(db.String(100), nullable=True)
    company_website = db.Column(db.String(255), nullable=True)
    company_location = db.Column(db.String(100), nullable=True)

    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __init__(self, name, email, password, role='pending', skills=None,
                 current_role=None, preferred_location=None, company_name=None,
                 experience=None, industry=None, company_website=None, company_location=None):
        self.name = name
        self.email = email
        self.password = password
        self.role = role
        self.skills = skills
        self.current_role = current_role
        self.preferred_location = preferred_location
        self.company_name = company_name
        self.experience = experience
        self.industry = industry
        self.company_website = company_website
        self.company_location = company_location

    def set_password(self, password):
        self.password = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password, password)
