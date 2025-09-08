from flask import Blueprint, request, jsonify
from src.app import db
from src.models import Skill

skills_bp = Blueprint('skills', __name__)

@skills_bp.route('', methods=['GET'])
def get_skills():
    """Get all skills with optional filtering"""
    try:
        category = request.args.get('category')
        
        query = Skill.query
        
        if category:
            query = query.filter(Skill.category == category)
        
        skills = query.all()
        return jsonify({
            'skills': [skill.to_dict() for skill in skills],
            'count': len(skills)
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@skills_bp.route('/<int:skill_id>', methods=['GET'])
def get_skill(skill_id):
    """Get a specific skill by ID"""
    try:
        skill = Skill.query.get_or_404(skill_id)
        return jsonify(skill.to_dict())
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@skills_bp.route('', methods=['POST'])
def create_skill():
    """Create a new skill"""
    try:
        data = request.get_json()
        
        # Validate required fields
        if 'name' not in data:
            return jsonify({'error': 'Missing required field: name'}), 400
        
        # Check if skill name already exists
        existing_skill = Skill.query.filter(Skill.name == data['name']).first()
        if existing_skill:
            return jsonify({'error': 'Skill name already exists'}), 409
        
        # Create new skill
        skill = Skill(
            name=data['name'],
            description=data.get('description'),
            category=data.get('category')
        )
        
        db.session.add(skill)
        db.session.commit()
        
        return jsonify(skill.to_dict()), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@skills_bp.route('/<int:skill_id>', methods=['PUT'])
def update_skill(skill_id):
    """Update a skill"""
    try:
        skill = Skill.query.get_or_404(skill_id)
        data = request.get_json()
        
        # Update fields if provided
        for field in ['name', 'description', 'category']:
            if field in data:
                setattr(skill, field, data[field])
        
        db.session.commit()
        return jsonify(skill.to_dict())
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@skills_bp.route('/<int:skill_id>', methods=['DELETE'])
def delete_skill(skill_id):
    """Delete a skill"""
    try:
        skill = Skill.query.get_or_404(skill_id)
        db.session.delete(skill)
        db.session.commit()
        return jsonify({'message': 'Skill deleted successfully'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@skills_bp.route('/categories', methods=['GET'])
def get_skill_categories():
    """Get all unique skill categories"""
    try:
        categories = db.session.query(Skill.category).distinct().filter(
            Skill.category.isnot(None)
        ).all()
        
        category_list = [category[0] for category in categories]
        return jsonify({
            'categories': category_list,
            'count': len(category_list)
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500
