from app import db

class Job(db.Model):
       __tablename__ = 'jobs'

       job_id = db.Column(db.Integer, primary_key=True)
       title = db.Column(db.String(255), nullable=False)
       description = db.Column(db.Text, nullable=False)
       company = db.Column(db.String(255), nullable=False)
       location = db.Column(db.String(255), nullable=False)
       salary = db.Column(db.Float, nullable=False)  # Ensure this line exists
       requirements = db.Column(db.Text, nullable=False)
       posted_by = db.Column(db.String(255), nullable=False)
       employer_id = db.Column(db.Integer, db.ForeignKey('users.user_id'), nullable=False)

       def __init__(self, title, description, company, location, salary, requirements, posted_by,employer_id):
           self.title = title
           self.description = description
           self.company = company
           self.location = location
           self.salary = salary
           self.requirements = requirements
           self.posted_by = posted_by
           self.employer_id = employer_id 
       
       def __repr__(self):
            return f'<Job {self.title} at {self.company}>'