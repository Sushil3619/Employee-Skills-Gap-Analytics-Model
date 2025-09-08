import os
# Set matplotlib backend before importing matplotlib (fixes Windows backend issues)
if os.getenv('MPLBACKEND'):
    import matplotlib
    matplotlib.use(os.getenv('MPLBACKEND', 'Agg'))
else:
    import matplotlib
    matplotlib.use('Agg')  # Use non-interactive backend for server environments

from flask import Blueprint, request, jsonify
from src.app import db
from src.models import Employee, Skill, SkillGapAnalysis, employee_skills, role_skills
from datetime import datetime
import numpy as np

analysis_bp = Blueprint('analysis', __name__)

@analysis_bp.route('/gaps', methods=['POST'])
def analyze_skill_gaps():
    """Perform skill gap analysis for employees"""
    try:
        data = request.get_json()
        employee_id = data.get('employee_id')
        
        if employee_id:
            # Analyze specific employee
            employees = [Employee.query.get_or_404(employee_id)]
        else:
            # Analyze all employees
            employees = Employee.query.all()
        
        results = []
        for employee in employees:
            if not employee.role:
                continue  # Skip employees without assigned roles
            
            # Get required skills for the employee's role
            required_skills_query = db.session.query(
                role_skills.c.skill_id,
                role_skills.c.required_level
            ).filter(role_skills.c.role_id == employee.role.id)
            
            required_skills = {skill_id: req_level for skill_id, req_level in required_skills_query}
            
            for skill_id, required_level in required_skills.items():
                # Get current skill level for employee
                current_skill = db.session.execute(
                    employee_skills.select().where(
                        (employee_skills.c.employee_id == employee.id) &
                        (employee_skills.c.skill_id == skill_id)
                    )
                ).first()
                
                current_level = current_skill.proficiency_level if current_skill else 0
                gap_score = current_level - required_level
                
                # Determine priority based on gap size
                if gap_score <= -2:
                    priority = 'High'
                elif gap_score == -1:
                    priority = 'Medium'
                else:
                    priority = 'Low'
                
                # Predict training time (simplified algorithm)
                predicted_training_time = max(0, abs(gap_score) * 20) if gap_score < 0 else 0
                
                # Save or update skill gap analysis
                existing_analysis = SkillGapAnalysis.query.filter_by(
                    employee_id=employee.id,
                    skill_id=skill_id
                ).first()
                
                if existing_analysis:
                    existing_analysis.current_level = current_level
                    existing_analysis.required_level = required_level
                    existing_analysis.gap_score = gap_score
                    existing_analysis.priority = priority
                    existing_analysis.predicted_training_time = predicted_training_time
                    existing_analysis.analysis_date = datetime.utcnow()
                    gap_analysis = existing_analysis
                else:
                    gap_analysis = SkillGapAnalysis(
                        employee_id=employee.id,
                        skill_id=skill_id,
                        current_level=current_level,
                        required_level=required_level,
                        gap_score=gap_score,
                        priority=priority,
                        predicted_training_time=predicted_training_time
                    )
                    db.session.add(gap_analysis)
                
                results.append({
                    'employee_id': employee.id,
                    'employee_name': f"{employee.first_name} {employee.last_name}",
                    'skill_id': skill_id,
                    'skill_name': Skill.query.get(skill_id).name,
                    'current_level': current_level,
                    'required_level': required_level,
                    'gap_score': gap_score,
                    'priority': priority,
                    'predicted_training_time': predicted_training_time
                })
        
        db.session.commit()
        
        return jsonify({
            'message': 'Skill gap analysis completed',
            'analyzed_employees': len(employees),
            'total_gaps_found': len([r for r in results if r['gap_score'] < 0]),
            'results': results
        })
    
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@analysis_bp.route('/gaps/<int:employee_id>', methods=['GET'])
def get_employee_skill_gaps(employee_id):
    """Get skill gap analysis for a specific employee"""
    try:
        employee = Employee.query.get_or_404(employee_id)
        
        skill_gaps = SkillGapAnalysis.query.filter_by(employee_id=employee_id).all()
        
        gaps_data = []
        for gap in skill_gaps:
            gap_data = gap.to_dict()
            gap_data['skill_name'] = gap.skill.name
            gap_data['skill_category'] = gap.skill.category
            gaps_data.append(gap_data)
        
        return jsonify({
            'employee_id': employee_id,
            'employee_name': f"{employee.first_name} {employee.last_name}",
            'skill_gaps': gaps_data,
            'total_gaps': len([g for g in gaps_data if g['gap_score'] < 0]),
            'high_priority_gaps': len([g for g in gaps_data if g['priority'] == 'High'])
        })
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@analysis_bp.route('/predictions/<int:employee_id>', methods=['GET'])
def get_skill_predictions(employee_id):
    """Get skill development predictions for an employee"""
    try:
        employee = Employee.query.get_or_404(employee_id)
        
        # Get skill gaps for the employee
        skill_gaps = SkillGapAnalysis.query.filter_by(employee_id=employee_id).all()
        
        predictions = []
        for gap in skill_gaps:
            if gap.gap_score < 0:  # Only predict for skills below required level
                # Simple prediction model (in real implementation, use trained ML model)
                base_time = gap.predicted_training_time
                
                # Factors that affect training time
                experience_factor = 1.0  # Could be calculated based on hire date
                role_level_factor = 1.0  # Could be based on role level
                
                adjusted_time = base_time * experience_factor * role_level_factor
                
                # Success probability (simplified)
                success_probability = max(0.6, 1.0 - (abs(gap.gap_score) * 0.1))
                
                predictions.append({
                    'skill_id': gap.skill_id,
                    'skill_name': gap.skill.name,
                    'current_level': gap.current_level,
                    'target_level': gap.required_level,
                    'predicted_training_hours': int(adjusted_time),
                    'success_probability': round(success_probability, 2),
                    'estimated_completion_weeks': int(adjusted_time / 8),  # Assuming 8 hours per week
                    'priority': gap.priority
                })
        
        return jsonify({
            'employee_id': employee_id,
            'employee_name': f"{employee.first_name} {employee.last_name}",
            'predictions': predictions,
            'total_training_hours': sum(p['predicted_training_hours'] for p in predictions),
            'average_success_probability': round(
                np.mean([p['success_probability'] for p in predictions]) if predictions else 0, 2
            )
        })
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@analysis_bp.route('/recommendations', methods=['POST'])
def generate_training_recommendations():
    """Generate training recommendations based on skill gap analysis"""
    try:
        data = request.get_json()
        employee_id = data.get('employee_id')
        priority_filter = data.get('priority', 'all')  # 'high', 'medium', 'low', 'all'
        
        query = SkillGapAnalysis.query
        
        if employee_id:
            query = query.filter_by(employee_id=employee_id)
        
        if priority_filter != 'all':
            query = query.filter_by(priority=priority_filter.capitalize())
        
        # Only get gaps where improvement is needed
        skill_gaps = query.filter(SkillGapAnalysis.gap_score < 0).all()
        
        recommendations = []
        for gap in skill_gaps:
            # Generate recommendation based on skill and gap size
            recommendation = {
                'employee_id': gap.employee_id,
                'employee_name': f"{gap.employee.first_name} {gap.employee.last_name}",
                'skill_id': gap.skill_id,
                'skill_name': gap.skill.name,
                'skill_category': gap.skill.category,
                'current_level': gap.current_level,
                'target_level': gap.required_level,
                'gap_size': abs(gap.gap_score),
                'priority': gap.priority,
                'training_recommendations': generate_training_suggestions(gap.skill.name, abs(gap.gap_score)),
                'estimated_duration': gap.predicted_training_time,
                'cost_estimate': calculate_training_cost(gap.predicted_training_time)
            }
            recommendations.append(recommendation)
        
        # Sort by priority and gap size
        priority_order = {'High': 3, 'Medium': 2, 'Low': 1}
        recommendations.sort(
            key=lambda x: (priority_order[x['priority']], x['gap_size']), 
            reverse=True
        )
        
        return jsonify({
            'recommendations': recommendations,
            'total_employees_needing_training': len(set(r['employee_id'] for r in recommendations)),
            'total_estimated_cost': sum(r['cost_estimate'] for r in recommendations),
            'total_training_hours': sum(r['estimated_duration'] for r in recommendations)
        })
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

def generate_training_suggestions(skill_name, gap_size):
    """Generate training suggestions based on skill and gap size"""
    suggestions = []
    
    if gap_size >= 3:
        suggestions.append(f"Comprehensive {skill_name} bootcamp or certification program")
        suggestions.append(f"1-on-1 mentoring with {skill_name} expert")
    elif gap_size == 2:
        suggestions.append(f"Intermediate {skill_name} workshop series")
        suggestions.append(f"Online {skill_name} course with practical projects")
    else:
        suggestions.append(f"Targeted {skill_name} refresher training")
        suggestions.append(f"Peer learning session on {skill_name}")
    
    return suggestions

def calculate_training_cost(hours):
    """Calculate estimated training cost based on hours"""
    # Simple cost calculation (can be made more sophisticated)
    cost_per_hour = 50  # Average cost per training hour
    return hours * cost_per_hour
