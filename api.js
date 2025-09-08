// API client for Skills Gap Analyzer

class ApiClient {
    constructor(baseUrl = 'http://localhost:5000/api') {
        this.baseUrl = baseUrl;
    }

    async request(endpoint, options = {}) {
        const url = `${this.baseUrl}${endpoint}`;
        const config = {
            headers: {
                'Content-Type': 'application/json',
                ...options.headers
            },
            ...options
        };

        try {
            const response = await fetch(url, config);
            const data = await response.json();

            if (!response.ok) {
                throw new Error(data.error || `HTTP error! status: ${response.status}`);
            }

            return data;
        } catch (error) {
            console.error('API request failed:', error);
            throw error;
        }
    }

    // Employee endpoints
    async getEmployees(filters = {}) {
        const queryParams = new URLSearchParams(filters).toString();
        const endpoint = queryParams ? `/employees?${queryParams}` : '/employees';
        return this.request(endpoint);
    }

    async getEmployee(id) {
        return this.request(`/employees/${id}`);
    }

    async createEmployee(employeeData) {
        return this.request('/employees', {
            method: 'POST',
            body: JSON.stringify(employeeData)
        });
    }

    async updateEmployee(id, employeeData) {
        return this.request(`/employees/${id}`, {
            method: 'PUT',
            body: JSON.stringify(employeeData)
        });
    }

    async deleteEmployee(id) {
        return this.request(`/employees/${id}`, {
            method: 'DELETE'
        });
    }

    async getEmployeeSkills(employeeId) {
        return this.request(`/employees/${employeeId}/skills`);
    }

    async addEmployeeSkill(employeeId, skillData) {
        return this.request(`/employees/${employeeId}/skills`, {
            method: 'POST',
            body: JSON.stringify(skillData)
        });
    }

    // Skills endpoints
    async getSkills(filters = {}) {
        const queryParams = new URLSearchParams(filters).toString();
        const endpoint = queryParams ? `/skills?${queryParams}` : '/skills';
        return this.request(endpoint);
    }

    async getSkill(id) {
        return this.request(`/skills/${id}`);
    }

    async createSkill(skillData) {
        return this.request('/skills', {
            method: 'POST',
            body: JSON.stringify(skillData)
        });
    }

    async updateSkill(id, skillData) {
        return this.request(`/skills/${id}`, {
            method: 'PUT',
            body: JSON.stringify(skillData)
        });
    }

    async deleteSkill(id) {
        return this.request(`/skills/${id}`, {
            method: 'DELETE'
        });
    }

    async getSkillCategories() {
        return this.request('/skills/categories');
    }

    // Analysis endpoints
    async analyzeSkillGaps(employeeId = null) {
        const body = employeeId ? { employee_id: employeeId } : {};
        return this.request('/analysis/gaps', {
            method: 'POST',
            body: JSON.stringify(body)
        });
    }

    async getEmployeeSkillGaps(employeeId) {
        return this.request(`/analysis/gaps/${employeeId}`);
    }

    async getSkillPredictions(employeeId) {
        return this.request(`/analysis/predictions/${employeeId}`);
    }

    async getTrainingRecommendations(employeeId = null, priority = 'all') {
        const body = {};
        if (employeeId) body.employee_id = employeeId;
        if (priority !== 'all') body.priority = priority;
        
        return this.request('/analysis/recommendations', {
            method: 'POST',
            body: JSON.stringify(body)
        });
    }

    // Health check
    async healthCheck() {
        return this.request('/', { 
            baseUrl: 'http://localhost:5000' 
        });
    }
}

// Create a global API client instance
window.apiClient = new ApiClient();

// Utility functions
function showLoading() {
    document.getElementById('loading').classList.remove('d-none');
}

function hideLoading() {
    document.getElementById('loading').classList.add('d-none');
}

function showAlert(message, type = 'info') {
    const alertDiv = document.createElement('div');
    alertDiv.className = `alert alert-${type} alert-dismissible fade show`;
    alertDiv.innerHTML = `
        ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
    `;
    
    // Insert at the top of the main container
    const container = document.querySelector('.container-fluid');
    container.insertBefore(alertDiv, container.firstChild);
    
    // Auto-dismiss after 5 seconds
    setTimeout(() => {
        if (alertDiv.parentNode) {
            alertDiv.remove();
        }
    }, 5000);
}

function formatDate(dateString) {
    if (!dateString) return '-';
    const date = new Date(dateString);
    return date.toLocaleDateString();
}

function formatProficiencyLevel(level) {
    if (!level) return 'Not assessed';
    const stars = '★'.repeat(level) + '☆'.repeat(5 - level);
    return `${stars} (${level}/5)`;
}

function getPriorityClass(priority) {
    switch (priority.toLowerCase()) {
        case 'high': return 'priority-high';
        case 'medium': return 'priority-medium';
        case 'low': return 'priority-low';
        default: return '';
    }
}

// Export for use in other files
if (typeof module !== 'undefined' && module.exports) {
    module.exports = ApiClient;
}
