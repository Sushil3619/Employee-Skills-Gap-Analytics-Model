# WARP.md

This file provides guidance to WARP (warp.dev) when working with code in this repository.

## Development Commands

### Setup and Installation
```bash
# Create and activate virtual environment (Windows PowerShell)
python -m venv venv
venv\Scripts\Activate.ps1

# Install dependencies
pip install -r requirements.txt

# Set up environment variables
copy .env.example .env
# Edit .env with your configuration

# Fix matplotlib backend for Windows (if you encounter "backend not supported" error)
pip install --upgrade matplotlib
# Add this to your .env file: MPLBACKEND=Agg
```

### Database Operations
```bash
# Create database tables
python src/app.py  # Tables created automatically on first run

# Load sample data (from scripts directory)
cd scripts
python load_sample_data.py
cd ..
```

### Running the Application
```bash
# Development server (default: http://localhost:5000)
python src/app.py

# With specific configuration
set FLASK_CONFIG=development
set FLASK_DEBUG=True
python src/app.py

# Production mode
set FLASK_CONFIG=production
python src/app.py
```

### Testing and Quality
```bash
# Run tests (pytest framework configured in requirements.txt)
pytest

# Run specific test files
pytest tests/test_employees.py

# Code formatting with black
black src/ api/ config/ scripts/

# Linting with flake8
flake8 src/ api/ config/ scripts/
```

### API Testing
```bash
# Test health check
curl http://localhost:5000/

# Test employee endpoints
curl http://localhost:5000/api/employees
curl -X POST http://localhost:5000/api/employees -H "Content-Type: application/json" -d "{\"employee_id\":\"EMP001\",\"first_name\":\"John\",\"last_name\":\"Doe\",\"email\":\"john.doe@company.com\"}"

# Run skill gap analysis
curl -X POST http://localhost:5000/api/analysis/gaps -H "Content-Type: application/json" -d "{}"
```

## Architecture Overview

### Application Structure
The application follows a Flask blueprint pattern with clear separation of concerns:

- **`src/app.py`**: Application factory with Flask app configuration and blueprint registration
- **`api/`**: REST API blueprints (employees, skills, analysis) - each blueprint handles specific domain endpoints
- **`config/config.py`**: Configuration management with environment-specific settings (development, production, testing)
- **`src/models.py`**: SQLAlchemy ORM models with complex many-to-many relationships

### Data Model Architecture
The core data model centers around four main entities with association tables:

1. **Employee** ↔ **Skills** (many-to-many via `employee_skills` with proficiency levels)
2. **Role** ↔ **Skills** (many-to-many via `role_skills` with required levels)  
3. **Employee** → **Role** (many-to-one)
4. **TrainingRecord** → Employee + Skill (tracking training history)
5. **SkillGapAnalysis** → Employee + Skill (analysis results)

### Key Architectural Patterns

**Blueprint-based API Organization**: Each major domain (employees, skills, analysis) has its own blueprint in the `api/` directory, making the codebase modular and maintainable.

**Association Table Pattern**: Complex many-to-many relationships use association tables (`employee_skills`, `role_skills`) that store additional metadata like proficiency levels and assessment dates.

**Analysis Engine**: The `api/analysis.py` contains the core skill gap analysis logic that compares employee current skills against role requirements, calculates gap scores, and generates training predictions.

**Configuration Management**: Environment-specific configurations are managed through the `config/config.py` file with support for development, production, and testing environments.

### Frontend Integration
- Single-page application in `frontend/index.html` with Bootstrap UI
- JavaScript API client in `frontend/js/api.js` 
- Chart.js integration for data visualization
- Modal-based forms for data entry

### Database Design Notes
- Uses SQLite for development, PostgreSQL for production
- Association tables store metadata (proficiency levels, required levels, assessment dates)
- Timestamps tracked on all major entities (`created_at`, `updated_at`)
- Skill gap analysis results are persisted for historical tracking

### Data Loading and Seeding
The `scripts/load_sample_data.py` script demonstrates the proper sequence for loading related data:
1. Skills (independent)
2. Roles (with skill requirements) 
3. Employees (with skills and role assignments)

### Analysis Workflow
The skill gap analysis follows this pattern:
1. Retrieve employee's current role and required skills
2. Compare employee's skill levels with role requirements  
3. Calculate gap scores (negative = skill deficit)
4. Determine priority levels (High/Medium/Low)
5. Generate training time predictions
6. Store results in `SkillGapAnalysis` table

### Environment Configuration
Key environment variables:
- `FLASK_CONFIG`: development/production/testing
- `DATABASE_URL`: Database connection string
- `SECRET_KEY`: Flask secret key
- `API_HOST`/`API_PORT`: Server configuration
- `MODEL_PATH`: ML model storage location
- `MPLBACKEND=Agg`: Fix for matplotlib backend issues on Windows

## Troubleshooting

### "Backend not supported" Error
This matplotlib error commonly occurs on Windows systems:

```bash
# Solution 1: Set matplotlib backend environment variable
set MPLBACKEND=Agg
python src/app.py

# Solution 2: Add to your .env file
echo MPLBACKEND=Agg >> .env

# Solution 3: Programmatically set in Python code (already handled in analysis.py)
# The application should automatically use the 'Agg' backend for headless operations
```

### Virtual Environment Issues
```bash
# If activation fails, try:
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
venv\Scripts\Activate.ps1

# Alternative activation methods:
venv\Scripts\activate.bat  # CMD
venv\Scripts\activate     # Git Bash
```

### Database Connection Issues
```bash
# Ensure SQLite database directory exists
mkdir -p data

# Reset database if corrupted
rm skills_gap_analyzer.db
python src/app.py  # Will recreate tables
```
