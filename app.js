// Main application logic for Skills Gap Analyzer

class SkillsGapAnalyzer {
    constructor() {
        this.currentSection = 'dashboard';
        this.charts = {};
        this.init();
    }

    async init() {
        this.setupEventListeners();
        this.setupNavigation();
        await this.loadDashboard();
        console.log('Skills Gap Analyzer initialized successfully');
    }

    setupEventListeners() {
        // Navigation
        document.querySelectorAll('[data-section]').forEach(link => {
            link.addEventListener('click', (e) => {
                e.preventDefault();
                const section = e.target.getAttribute('data-section') || 
                               e.target.closest('[data-section]').getAttribute('data-section');
                this.showSection(section);
            });
        });

        // Employee form
        const employeeForm = document.getElementById('employee-form');
        if (employeeForm) {
            employeeForm.addEventListener('submit', this.handleEmployeeSubmit.bind(this));
        }

        // Skill form
        const skillForm = document.getElementById('skill-form');
        if (skillForm) {
            skillForm.addEventListener('submit', this.handleSkillSubmit.bind(this));
        }

        // Analysis buttons
        const runAnalysisBtn = document.getElementById('run-analysis');
        if (runAnalysisBtn) {
            runAnalysisBtn.addEventListener('click', this.runSkillGapAnalysis.bind(this));
        }

        const getRecommendationsBtn = document.getElementById('get-recommendations');
        if (getRecommendationsBtn) {
            getRecommendationsBtn.addEventListener('click', this.getRecommendations.bind(this));
        }
    }

    setupNavigation() {
        document.querySelectorAll('.nav-link').forEach(link => {
            link.classList.remove('active');
        });
        document.querySelector(`[data-section="${this.currentSection}"]`).classList.add('active');
    }

    showSection(sectionName) {
        // Hide all sections
        document.querySelectorAll('.content-section').forEach(section => {
            section.classList.add('d-none');
        });

        // Show selected section
        const targetSection = document.getElementById(`${sectionName}-section`);
        if (targetSection) {
            targetSection.classList.remove('d-none');
        }

        // Update navigation
        document.querySelectorAll('.nav-link').forEach(link => {
            link.classList.remove('active');
        });
        document.querySelector(`[data-section="${sectionName}"]`).classList.add('active');

        this.currentSection = sectionName;

        // Load section-specific data
        switch (sectionName) {
            case 'dashboard':
                this.loadDashboard();
                break;
            case 'employees':
                this.loadEmployees();
                break;
            case 'skills':
                this.loadSkills();
                break;
            case 'analysis':
                // Analysis section doesn't need initial data load
                break;
        }
    }

    async loadDashboard() {
        try {
            showLoading();
            
            // Load dashboard metrics
            const [employeesData, skillsData] = await Promise.all([
                apiClient.getEmployees(),
                apiClient.getSkills()
            ]);

            // Update metrics cards
            document.getElementById('total-employees').textContent = employeesData.count || 0;
            document.getElementById('total-skills').textContent = skillsData.count || 0;

            // Create charts
            this.createSkillsCategoryChart(skillsData.skills || []);
            
            // Load gap analysis data for charts
            try {
                const gapsData = await apiClient.getTrainingRecommendations();
                this.updateGapMetrics(gapsData);
                this.createGapsPriorityChart(gapsData.recommendations || []);
            } catch (error) {
                console.log('No gap analysis data available yet');
                document.getElementById('skill-gaps').textContent = '0';
                document.getElementById('high-priority-gaps').textContent = '0';
            }

        } catch (error) {
            console.error('Failed to load dashboard:', error);
            showAlert('Failed to load dashboard data', 'danger');
        } finally {
            hideLoading();
        }
    }

    async loadEmployees() {
        try {
            showLoading();
            const data = await apiClient.getEmployees();
            this.renderEmployeesTable(data.employees || []);
        } catch (error) {
            console.error('Failed to load employees:', error);
            showAlert('Failed to load employees', 'danger');
        } finally {
            hideLoading();
        }
    }

    async loadSkills() {
        try {
            showLoading();
            const data = await apiClient.getSkills();
            this.renderSkillsTable(data.skills || []);
        } catch (error) {
            console.error('Failed to load skills:', error);
            showAlert('Failed to load skills', 'danger');
        } finally {
            hideLoading();
        }
    }

    renderEmployeesTable(employees) {
        const tbody = document.querySelector('#employees-table tbody');
        if (!tbody) return;

        tbody.innerHTML = employees.map(employee => `
            <tr>
                <td>${employee.employee_id}</td>
                <td>${employee.first_name} ${employee.last_name}</td>
                <td>${employee.email}</td>
                <td>${employee.department || '-'}</td>
                <td>${employee.role ? employee.role.title : '-'}</td>
                <td>
                    <button class=\"btn btn-sm btn-primary me-1\" onclick=\"app.viewEmployee(${employee.id})\">
                        <i class=\"fas fa-eye\"></i>
                    </button>
                    <button class=\"btn btn-sm btn-warning me-1\" onclick=\"app.editEmployee(${employee.id})\">
                        <i class=\"fas fa-edit\"></i>
                    </button>
                    <button class=\"btn btn-sm btn-danger\" onclick=\"app.deleteEmployee(${employee.id})\">
                        <i class=\"fas fa-trash\"></i>
                    </button>
                </td>
            </tr>
        `).join('');
    }

    renderSkillsTable(skills) {
        const tbody = document.querySelector('#skills-table tbody');
        if (!tbody) return;

        tbody.innerHTML = skills.map(skill => `
            <tr>
                <td>${skill.name}</td>
                <td><span class=\"badge bg-secondary\">${skill.category || 'Uncategorized'}</span></td>
                <td>${skill.description || '-'}</td>
                <td>
                    <button class=\"btn btn-sm btn-warning me-1\" onclick=\"app.editSkill(${skill.id})\">
                        <i class=\"fas fa-edit\"></i>
                    </button>
                    <button class=\"btn btn-sm btn-danger\" onclick=\"app.deleteSkill(${skill.id})\">
                        <i class=\"fas fa-trash\"></i>
                    </button>
                </td>
            </tr>
        `).join('');
    }

    async handleEmployeeSubmit(e) {
        e.preventDefault();
        
        try {
            showLoading();
            const formData = new FormData(e.target);
            const employeeData = Object.fromEntries(formData.entries());
            
            await apiClient.createEmployee(employeeData);
            showAlert('Employee created successfully!', 'success');
            
            // Close modal and refresh data
            bootstrap.Modal.getInstance(document.getElementById('employeeModal')).hide();
            e.target.reset();
            
            if (this.currentSection === 'employees') {
                this.loadEmployees();
            }
            
        } catch (error) {
            console.error('Failed to create employee:', error);
            showAlert(error.message || 'Failed to create employee', 'danger');
        } finally {
            hideLoading();
        }
    }

    async handleSkillSubmit(e) {
        e.preventDefault();
        
        try {
            showLoading();
            const formData = new FormData(e.target);
            const skillData = Object.fromEntries(formData.entries());
            
            await apiClient.createSkill(skillData);
            showAlert('Skill created successfully!', 'success');
            
            // Close modal and refresh data
            bootstrap.Modal.getInstance(document.getElementById('skillModal')).hide();
            e.target.reset();
            
            if (this.currentSection === 'skills') {
                this.loadSkills();
            }
            
        } catch (error) {
            console.error('Failed to create skill:', error);
            showAlert(error.message || 'Failed to create skill', 'danger');
        } finally {
            hideLoading();
        }
    }

    async runSkillGapAnalysis() {
        try {
            showLoading();
            const results = await apiClient.analyzeSkillGaps();
            
            showAlert(`Analysis completed! Found ${results.total_gaps_found} skill gaps across ${results.analyzed_employees} employees.`, 'success');
            
            this.displayAnalysisResults(results);
            
            // Refresh dashboard if we're on it
            if (this.currentSection === 'dashboard') {
                setTimeout(() => this.loadDashboard(), 1000);
            }
            
        } catch (error) {
            console.error('Failed to run analysis:', error);
            showAlert(error.message || 'Failed to run skill gap analysis', 'danger');
        } finally {
            hideLoading();
        }
    }

    async getRecommendations() {
        try {
            showLoading();
            const recommendations = await apiClient.getTrainingRecommendations();
            
            this.displayRecommendations(recommendations);
            
        } catch (error) {
            console.error('Failed to get recommendations:', error);
            showAlert(error.message || 'Failed to get training recommendations', 'danger');
        } finally {
            hideLoading();
        }
    }

    displayAnalysisResults(results) {
        const resultsDiv = document.getElementById('analysis-results');
        if (!resultsDiv) return;

        const gapsWithDeficit = results.results.filter(r => r.gap_score < 0);
        
        resultsDiv.innerHTML = `
            <div class=\"row mb-3\">\n                <div class=\"col-md-6\">\n                    <div class=\"card bg-info text-white\">\n                        <div class=\"card-body\">\n                            <h5>Analysis Summary</h5>\n                            <p>Analyzed: ${results.analyzed_employees} employees</p>\n                            <p>Gaps found: ${results.total_gaps_found}</p>\n                        </div>\n                    </div>\n                </div>\n            </div>\n            \n            ${gapsWithDeficit.length > 0 ? `\n                <h6>Skill Gaps Requiring Attention:</h6>\n                ${gapsWithDeficit.map(gap => `\n                    <div class=\"analysis-result-item ${gap.priority.toLowerCase()}-priority\">\n                        <strong>${gap.employee_name}</strong> - ${gap.skill_name}<br>\n                        <small class=\"text-muted\">\n                            Current: ${gap.current_level}/5 | Required: ${gap.required_level}/5 | \n                            Priority: <span class=\"${getPriorityClass(gap.priority)}\">${gap.priority}</span>\n                        </small>\n                    </div>\n                `).join('')}\n            ` : '<p class=\"text-success\">No skill gaps found! All employees meet their role requirements.</p>'}\n        `;\n    }\n\n    displayRecommendations(recommendations) {\n        const resultsDiv = document.getElementById('analysis-results');\n        if (!resultsDiv) return;\n\n        resultsDiv.innerHTML = `\n            <div class=\"row mb-3\">\n                <div class=\"col-md-12\">\n                    <div class=\"card bg-success text-white\">\n                        <div class=\"card-body\">\n                            <h5>Training Recommendations</h5>\n                            <div class=\"row\">\n                                <div class=\"col-md-4\">\n                                    <p>Employees needing training: ${recommendations.total_employees_needing_training}</p>\n                                </div>\n                                <div class=\"col-md-4\">\n                                    <p>Total training hours: ${recommendations.total_training_hours}</p>\n                                </div>\n                                <div class=\"col-md-4\">\n                                    <p>Estimated cost: $${recommendations.total_estimated_cost.toLocaleString()}</p>\n                                </div>\n                            </div>\n                        </div>\n                    </div>\n                </div>\n            </div>\n            \n            ${recommendations.recommendations.length > 0 ? `\n                <h6>Detailed Recommendations:</h6>\n                ${recommendations.recommendations.map(rec => `\n                    <div class=\"card mb-2\">\n                        <div class=\"card-body\">\n                            <h6 class=\"card-title\">${rec.employee_name} - ${rec.skill_name}</h6>\n                            <div class=\"row\">\n                                <div class=\"col-md-6\">\n                                    <p><strong>Gap:</strong> ${rec.current_level}/${rec.target_level} (${rec.gap_size} levels behind)</p>\n                                    <p><strong>Priority:</strong> <span class=\"${getPriorityClass(rec.priority)}\">${rec.priority}</span></p>\n                                    <p><strong>Duration:</strong> ${rec.estimated_duration} hours</p>\n                                    <p><strong>Cost:</strong> $${rec.cost_estimate}</p>\n                                </div>\n                                <div class=\"col-md-6\">\n                                    <p><strong>Recommended Training:</strong></p>\n                                    <ul>\n                                        ${rec.training_recommendations.map(tr => `<li>${tr}</li>`).join('')}\n                                    </ul>\n                                </div>\n                            </div>\n                        </div>\n                    </div>\n                `).join('')}\n            ` : '<p class=\"text-info\">No training recommendations needed at this time.</p>'}\n        `;\n    }\n\n    createSkillsCategoryChart(skills) {\n        const ctx = document.getElementById('skills-chart');\n        if (!ctx) return;\n\n        // Group skills by category\n        const categories = {};\n        skills.forEach(skill => {\n            const category = skill.category || 'Uncategorized';\n            categories[category] = (categories[category] || 0) + 1;\n        });\n\n        // Destroy existing chart if it exists\n        if (this.charts.skillsChart) {\n            this.charts.skillsChart.destroy();\n        }\n\n        this.charts.skillsChart = new Chart(ctx, {\n            type: 'doughnut',\n            data: {\n                labels: Object.keys(categories),\n                datasets: [{\n                    data: Object.values(categories),\n                    backgroundColor: [\n                        '#007bff', '#28a745', '#ffc107', '#dc3545', '#6f42c1', '#fd7e14'\n                    ]\n                }]\n            },\n            options: {\n                responsive: true,\n                maintainAspectRatio: false,\n                plugins: {\n                    legend: {\n                        position: 'bottom'\n                    }\n                }\n            }\n        });\n    }\n\n    createGapsPriorityChart(recommendations) {\n        const ctx = document.getElementById('gaps-chart');\n        if (!ctx) return;\n\n        // Group by priority\n        const priorities = { High: 0, Medium: 0, Low: 0 };\n        recommendations.forEach(rec => {\n            priorities[rec.priority] = (priorities[rec.priority] || 0) + 1;\n        });\n\n        // Destroy existing chart if it exists\n        if (this.charts.gapsChart) {\n            this.charts.gapsChart.destroy();\n        }\n\n        this.charts.gapsChart = new Chart(ctx, {\n            type: 'bar',\n            data: {\n                labels: Object.keys(priorities),\n                datasets: [{\n                    label: 'Number of Gaps',\n                    data: Object.values(priorities),\n                    backgroundColor: ['#dc3545', '#ffc107', '#28a745']\n                }]\n            },\n            options: {\n                responsive: true,\n                maintainAspectRatio: false,\n                plugins: {\n                    legend: {\n                        display: false\n                    }\n                },\n                scales: {\n                    y: {\n                        beginAtZero: true,\n                        ticks: {\n                            stepSize: 1\n                        }\n                    }\n                }\n            }\n        });\n    }\n\n    updateGapMetrics(gapsData) {\n        const totalGaps = gapsData.recommendations?.length || 0;\n        const highPriorityGaps = gapsData.recommendations?.filter(r => r.priority === 'High').length || 0;\n        \n        document.getElementById('skill-gaps').textContent = totalGaps;\n        document.getElementById('high-priority-gaps').textContent = highPriorityGaps;\n    }\n\n    // Employee management methods\n    async viewEmployee(id) {\n        // Implementation for viewing employee details\n        console.log('View employee:', id);\n    }\n\n    async editEmployee(id) {\n        // Implementation for editing employee\n        console.log('Edit employee:', id);\n    }\n\n    async deleteEmployee(id) {\n        if (confirm('Are you sure you want to delete this employee?')) {\n            try {\n                showLoading();\n                await apiClient.deleteEmployee(id);\n                showAlert('Employee deleted successfully!', 'success');\n                this.loadEmployees();\n            } catch (error) {\n                console.error('Failed to delete employee:', error);\n                showAlert(error.message || 'Failed to delete employee', 'danger');\n            } finally {\n                hideLoading();\n            }\n        }\n    }\n\n    // Skill management methods\n    async editSkill(id) {\n        // Implementation for editing skill\n        console.log('Edit skill:', id);\n    }\n\n    async deleteSkill(id) {\n        if (confirm('Are you sure you want to delete this skill?')) {\n            try {\n                showLoading();\n                await apiClient.deleteSkill(id);\n                showAlert('Skill deleted successfully!', 'success');\n                this.loadSkills();\n            } catch (error) {\n                console.error('Failed to delete skill:', error);\n                showAlert(error.message || 'Failed to delete skill', 'danger');\n            } finally {\n                hideLoading();\n            }\n        }\n    }\n}\n\n// Initialize the application when DOM is loaded\ndocument.addEventListener('DOMContentLoaded', () => {\n    window.app = new SkillsGapAnalyzer();\n});"
        ],
        "line_range_start": 1,
        "line_range_end": 436
    }
}
