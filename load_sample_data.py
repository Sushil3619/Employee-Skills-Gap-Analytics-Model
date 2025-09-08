#!/usr/bin/env python3
"""
Script to load sample data into the Employee Skills Gap Analyzer database.
This script populates the database with sample employees, skills, roles, and their relationships.
"""

import json
import sys
import os
from datetime import datetime

# Add the src directory to Python path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

from app import create_app, db
from models import Employee, Skill, Role, employee_skills, role_skills


def load_skills():
    """Load skills from sample_skills.json"""
    print("Loading skills...")
    
    with open('../data/raw/sample_skills.json', 'r', encoding='utf-8') as f:
        skills_data = json.load(f)
    
    skills_created = 0
    for skill_data in skills_data:
        # Check if skill already exists
        existing_skill = Skill.query.filter_by(name=skill_data['name']).first()
        if existing_skill:
            print(f"Skill '{skill_data['name']}' already exists, skipping...")
            continue
        
        skill = Skill(
            name=skill_data['name'],
            category=skill_data['category'],
            description=skill_data['description']
        )
        db.session.add(skill)
        skills_created += 1
    
    db.session.commit()
    print(f"Created {skills_created} skills")
    return skills_created


def load_roles():
    """Load roles from sample_roles.json"""
    print("Loading roles...")
    
    with open('../data/raw/sample_roles.json', 'r', encoding='utf-8') as f:
        roles_data = json.load(f)
    
    roles_created = 0
    for role_data in roles_data:
        # Check if role already exists
        existing_role = Role.query.filter_by(title=role_data['title']).first()
        if existing_role:
            print(f"Role '{role_data['title']}' already exists, skipping...")
            continue
        
        role = Role(
            title=role_data['title'],
            description=role_data['description'],
            department=role_data['department'],
            level=role_data['level']
        )
        db.session.add(role)
        db.session.flush()  # Flush to get the ID
        
        # Add required skills for this role
        for skill_req in role_data['required_skills']:
            skill = Skill.query.filter_by(name=skill_req['skill_name']).first()
            if skill:
                # Insert into role_skills association table
                db.session.execute(
                    role_skills.insert().values(
                        role_id=role.id,
                        skill_id=skill.id,
                        required_level=skill_req['required_level']
                    )
                )
        
        roles_created += 1
    
    db.session.commit()
    print(f"Created {roles_created} roles")
    return roles_created


def load_employees():
    """Load employees from sample_employees.json"""
    print("Loading employees...")
    
    with open('../data/raw/sample_employees.json', 'r', encoding='utf-8') as f:
        employees_data = json.load(f)
    
    employees_created = 0
    for emp_data in employees_data:
        # Check if employee already exists
        existing_emp = Employee.query.filter_by(employee_id=emp_data['employee_id']).first()
        if existing_emp:
            print(f"Employee '{emp_data['employee_id']}' already exists, skipping...")
            continue
        
        # Find the role
        role = Role.query.filter_by(title=emp_data['role']).first()
        
        employee = Employee(
            employee_id=emp_data['employee_id'],
            first_name=emp_data['first_name'],
            last_name=emp_data['last_name'],
            email=emp_data['email'],
            department=emp_data['department'],
            hire_date=datetime.fromisoformat(emp_data['hire_date']),
            role_id=role.id if role else None
        )
        db.session.add(employee)
        db.session.flush()  # Flush to get the ID
        
        # Add employee skills
        for skill_data in emp_data['skills']:
            skill = Skill.query.filter_by(name=skill_data['skill_name']).first()
            if skill:
                # Insert into employee_skills association table
                db.session.execute(
                    employee_skills.insert().values(
                        employee_id=employee.id,
                        skill_id=skill.id,
                        proficiency_level=skill_data['proficiency_level'],
                        assessed_date=datetime.utcnow()
                    )
                )
        
        employees_created += 1
    
    db.session.commit()
    print(f"Created {employees_created} employees")
    return employees_created


def main():
    """Main function to load all sample data"""
    print("Starting data loading process...")
    
    # Create Flask app and database tables
    app = create_app()
    
    with app.app_context():
        # Create all tables
        db.create_all()
        print("Database tables created/verified")
        
        # Load data in order of dependencies
        skills_count = load_skills()
        roles_count = load_roles()
        employees_count = load_employees()
        
        print("\n" + "="*50)
        print("DATA LOADING SUMMARY")
        print("="*50)
        print(f"Skills created: {skills_count}")
        print(f"Roles created: {roles_count}")
        print(f"Employees created: {employees_count}")
        print("="*50)
        
        if skills_count > 0 or roles_count > 0 or employees_count > 0:
            print("✅ Sample data loaded successfully!")
            print("\nYou can now:")
            print("1. Run the Flask application: python src/app.py")
            print("2. Open the frontend: frontend/index.html")
            print("3. Run skill gap analysis through the web interface")
        else:
            print("ℹ️  No new data was loaded (data already exists)")


if __name__ == '__main__':
    main()
