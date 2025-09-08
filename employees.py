from flask import Blueprint, request, jsonify
from src.app import db
from src.models import Employee, Role, Skill, employee_skills
from datetime import datetime

employees_bp = Blueprint('employees', __name__)

@app.route('/sikll gap analyze')
def start():
    return render_template('skills_gap_employee.html')
    

@employees_bp.route('', methods=['GET'])
def get_employees():
    """Get all employees with optional filtering"""
    try:
        department = request.args.get('department')
        role_id = request.args.get('role_id')
        
        query = Employee.query
        
        if department:
            query = query.filter(Employee.department == department)
        if role_id:
            query = query.filter(Employee.role_id == role_id)
        
        employees = query.all()
        return jsonify({
            'employees': [employee.to_dict() for employee in employees],
            'count': len(employees)
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@employees_bp.route('/<int:employee_id>', methods=['GET'])
def get_employee(employee_id):
    """Get a specific employee by ID"""
    try:
        employee = Employee.query.get_or_404(employee_id)
        
        # Get employee's skills with proficiency levels
        skills_data = []
        for skill in employee.skills:
            # Get proficiency level from association table
            result = db.session.execute(
                employee_skills.select().where(
                    (employee_skills.c.employee_id == employee_id) &
                    (employee_skills.c.skill_id == skill.id)
                )
            ).first()
            
            skill_data = skill.to_dict()
            skill_data['proficiency_level'] = result.proficiency_level if result else None
            skill_data['assessed_date'] = result.assessed_date.isoformat() if result and result.assessed_date else None
            skills_data.append(skill_data)
        
        employee_data = employee.to_dict()
        employee_data['skills'] = skills_data
        
        return jsonify(employee_data)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@employees_bp.route('', methods=['POST'])
def create_employee():
    """Create a new employee"""
    try:
        data = request.get_json()
        
        # Validate required fields
        required_fields = ['employee_id', 'first_name', 'last_name', 'email']
        for field in required_fields:
            if field not in data:
                return jsonify({'error': f'Missing required field: {field}'}), 400
        
        # Check if employee_id or email already exists
        existing_employee = Employee.query.filter(
            (Employee.employee_id == data['employee_id']) |
            (Employee.email == data['email'])
        ).first()
        
        if existing_employee:
            return jsonify({'error': 'Employee ID or email already exists'}), 409
        
        # Create new employee
        employee = Employee(
            employee_id=data['employee_id'],
            first_name=data['first_name'],
            last_name=data['last_name'],
            email=data['email'],
            department=data.get('department'),
            role_id=data.get('role_id'),
            hire_date=datetime.fromisoformat(data['hire_date']) if data.get('hire_date') else None
        )
        
        db.session.add(employee)
        db.session.commit()
        
        return jsonify(employee.to_dict()), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@employees_bp.route('/<int:employee_id>', methods=['PUT'])
def update_employee(employee_id):
    """Update an employee"""
    try:
        employee = Employee.query.get_or_404(employee_id)
        data = request.get_json()
        
        # Update fields if provided
        for field in ['first_name', 'last_name', 'email', 'department', 'role_id']:
            if field in data:
                setattr(employee, field, data[field])
        
        if 'hire_date' in data and data['hire_date']:
            employee.hire_date = datetime.fromisoformat(data['hire_date'])
        
        employee.updated_at = datetime.utcnow()
        
        db.session.commit()
        return jsonify(employee.to_dict())
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@employees_bp.route('/<int:employee_id>', methods=['DELETE'])
def delete_employee(employee_id):
    """Delete an employee"""
    try:
        employee = Employee.query.get_or_404(employee_id)
        db.session.delete(employee)
        db.session.commit()
        return jsonify({'message': 'Employee deleted successfully'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@employees_bp.route('/<int:employee_id>/skills', methods=['GET'])
def get_employee_skills(employee_id):
    """Get all skills for a specific employee"""
    try:
        employee = Employee.query.get_or_404(employee_id)
        
        skills_data = []
        for skill in employee.skills:
            result = db.session.execute(
                employee_skills.select().where(
                    (employee_skills.c.employee_id == employee_id) &
                    (employee_skills.c.skill_id == skill.id)
                )
            ).first()
            
            skill_data = skill.to_dict()
            skill_data['proficiency_level'] = result.proficiency_level if result else None
            skill_data['assessed_date'] = result.assessed_date.isoformat() if result and result.assessed_date else None
            skills_data.append(skill_data)
        
        return jsonify({
            'employee_id': employee_id,
            'skills': skills_data,
            'count': len(skills_data)
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@employees_bp.route('/<int:employee_id>/skills', methods=['POST'])
def add_employee_skill(employee_id):
    """Add a skill to an employee with proficiency level"""
    try:
        employee = Employee.query.get_or_404(employee_id)
        data = request.get_json()
        
        skill_id = data.get('skill_id')
        proficiency_level = data.get('proficiency_level', 1)
        
        if not skill_id:
            return jsonify({'error': 'skill_id is required'}), 400
        
        skill = Skill.query.get_or_404(skill_id)
        
        # Check if skill is already assigned
        existing = db.session.execute(
            employee_skills.select().where(
                (employee_skills.c.employee_id == employee_id) &
                (employee_skills.c.skill_id == skill_id)
            )
        ).first()
        
        if existing:
            return jsonify({'error': 'Skill already assigned to employee'}), 409
        
        # Add skill to employee
        db.session.execute(
            employee_skills.insert().values(
                employee_id=employee_id,
                skill_id=skill_id,
                proficiency_level=proficiency_level,
                assessed_date=datetime.utcnow()
            )
        )
        
        db.session.commit()
        return jsonify({'message': 'Skill added successfully'}), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500
