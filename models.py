from datetime import datetime
from src.app import db

# Association tables for many-to-many relationships
employee_skills = db.Table('employee_skills',
    db.Column('employee_id', db.Integer, db.ForeignKey('employee.id'), primary_key=True),
    db.Column('skill_id', db.Integer, db.ForeignKey('skill.id'), primary_key=True),
    db.Column('proficiency_level', db.Integer, default=1),  # 1-5 scale
    db.Column('assessed_date', db.DateTime, default=datetime.utcnow)
)

role_skills = db.Table('role_skills',
    db.Column('role_id', db.Integer, db.ForeignKey('role.id'), primary_key=True),
    db.Column('skill_id', db.Integer, db.ForeignKey('skill.id'), primary_key=True),
    db.Column('required_level', db.Integer, default=3)  # Required proficiency level
)

class Employee(db.Model):
    """Employee model"""
    id = db.Column(db.Integer, primary_key=True)
    employee_id = db.Column(db.String(20), unique=True, nullable=False)
    first_name = db.Column(db.String(50), nullable=False)
    last_name = db.Column(db.String(50), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    department = db.Column(db.String(100))
    hire_date = db.Column(db.Date)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Foreign keys
    role_id = db.Column(db.Integer, db.ForeignKey('role.id'))
    
    # Relationships
    role = db.relationship('Role', backref='employees')
    skills = db.relationship('Skill', secondary=employee_skills, backref='employees')
    training_records = db.relationship('TrainingRecord', backref='employee', lazy='dynamic')
    
    def __repr__(self):
        return f'<Employee {self.employee_id}: {self.first_name} {self.last_name}>'
    
    def to_dict(self):
        return {
            'id': self.id,
            'employee_id': self.employee_id,
            'first_name': self.first_name,
            'last_name': self.last_name,
            'email': self.email,
            'department': self.department,
            'hire_date': self.hire_date.isoformat() if self.hire_date else None,
            'role': self.role.to_dict() if self.role else None,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }

class Skill(db.Model):
    """Skill model"""
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False)
    description = db.Column(db.Text)
    category = db.Column(db.String(50))  # Technical, Soft Skills, Domain Knowledge, etc.
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<Skill {self.name}>'
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'category': self.category,
            'created_at': self.created_at.isoformat()
        }

class Role(db.Model):
    """Job role model"""
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    department = db.Column(db.String(100))
    level = db.Column(db.String(50))  # Junior, Mid, Senior, Lead, etc.
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    required_skills = db.relationship('Skill', secondary=role_skills, backref='required_for_roles')
    
    def __repr__(self):
        return f'<Role {self.title}>'
    
    def to_dict(self):
        return {
            'id': self.id,
            'title': self.title,
            'description': self.description,
            'department': self.department,
            'level': self.level,
            'created_at': self.created_at.isoformat()
        }

class TrainingRecord(db.Model):
    """Training record model"""
    id = db.Column(db.Integer, primary_key=True)
    employee_id = db.Column(db.Integer, db.ForeignKey('employee.id'), nullable=False)
    skill_id = db.Column(db.Integer, db.ForeignKey('skill.id'), nullable=False)
    training_name = db.Column(db.String(200), nullable=False)
    training_provider = db.Column(db.String(100))
    start_date = db.Column(db.Date)
    end_date = db.Column(db.Date)
    completion_status = db.Column(db.String(20), default='In Progress')  # Completed, In Progress, Cancelled
    effectiveness_score = db.Column(db.Float)  # 0-10 scale
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    skill = db.relationship('Skill', backref='training_records')
    
    def __repr__(self):
        return f'<TrainingRecord {self.training_name}>'
    
    def to_dict(self):
        return {
            'id': self.id,
            'employee_id': self.employee_id,
            'skill_id': self.skill_id,
            'training_name': self.training_name,
            'training_provider': self.training_provider,
            'start_date': self.start_date.isoformat() if self.start_date else None,
            'end_date': self.end_date.isoformat() if self.end_date else None,
            'completion_status': self.completion_status,
            'effectiveness_score': self.effectiveness_score,
            'created_at': self.created_at.isoformat()
        }

class SkillGapAnalysis(db.Model):
    """Skill gap analysis results model"""
    id = db.Column(db.Integer, primary_key=True)
    employee_id = db.Column(db.Integer, db.ForeignKey('employee.id'), nullable=False)
    skill_id = db.Column(db.Integer, db.ForeignKey('skill.id'), nullable=False)
    current_level = db.Column(db.Integer)  # Current proficiency level
    required_level = db.Column(db.Integer)  # Required proficiency level
    gap_score = db.Column(db.Float)  # Gap score (negative = below requirement)
    priority = db.Column(db.String(20), default='Medium')  # High, Medium, Low
    predicted_training_time = db.Column(db.Integer)  # In hours
    analysis_date = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    employee = db.relationship('Employee', backref='skill_gaps')
    skill = db.relationship('Skill', backref='gap_analyses')
    
    def __repr__(self):
        return f'<SkillGapAnalysis Employee:{self.employee_id} Skill:{self.skill_id}>'
    
    def to_dict(self):
        return {
            'id': self.id,
            'employee_id': self.employee_id,
            'skill_id': self.skill_id,
            'current_level': self.current_level,
            'required_level': self.required_level,
            'gap_score': self.gap_score,
            'priority': self.priority,
            'predicted_training_time': self.predicted_training_time,
            'analysis_date': self.analysis_date.isoformat()
        }
