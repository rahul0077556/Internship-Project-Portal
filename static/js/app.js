// Global state
let currentUser = null;
let currentToken = null;
let socket = null;

// Initialize
document.addEventListener('DOMContentLoaded', () => {
    checkAuth();
    initializeSocket();
    loadDomains();
});

// Socket.IO initialization
function initializeSocket() {
    socket = io();
    
    socket.on('connect', () => {
        console.log('Connected to server');
    });
    
    socket.on('new_message', (data) => {
        if (currentUser && data.receiver_id === currentUser.id) {
            showNotification('New message received', 'info');
            updateMessageBadge();
        }
    });
    
    socket.on('notification_read', (data) => {
        if (currentUser && data.user_id === currentUser.id) {
            updateNotificationBadge();
        }
    });
    
    socket.on('all_notifications_read', (data) => {
        if (currentUser && data.user_id === currentUser.id) {
            updateNotificationBadge();
        }
    });
}

// Authentication
function checkAuth() {
    const token = localStorage.getItem('token');
    if (token) {
        currentToken = token;
        fetchCurrentUser();
    } else {
        showView('home');
    }
}

async function fetchCurrentUser() {
    try {
        const response = await fetch('/api/auth/me', {
            headers: {
                'Authorization': `Bearer ${currentToken}`
            }
        });
        
        if (response.ok) {
            const data = await response.json();
            currentUser = data.user;
            updateUI();
            showView('dashboard');
        } else {
            localStorage.removeItem('token');
            currentToken = null;
            currentUser = null;
            showView('home');
        }
    } catch (error) {
        console.error('Error fetching user:', error);
    }
}

async function handleLogin(event) {
    event.preventDefault();
    showLoading(true);
    
    const email = document.getElementById('loginEmail').value;
    const password = document.getElementById('loginPassword').value;
    
    try {
        const response = await fetch('/api/auth/login', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ email, password })
        });
        
        const data = await response.json();
        
        if (response.ok) {
            currentToken = data.token;
            currentUser = data.user;
            localStorage.setItem('token', currentToken);
            showNotification('Login successful!', 'success');
            updateUI();
            showView('dashboard');
        } else {
            showNotification(data.error || 'Login failed', 'error');
        }
    } catch (error) {
        showNotification('An error occurred', 'error');
    } finally {
        showLoading(false);
    }
}

async function handleRegister(event) {
    event.preventDefault();
    showLoading(true);
    
    const role = document.getElementById('registerRole').value;
    const email = document.getElementById('registerEmail').value;
    const password = document.getElementById('registerPassword').value;
    
    const profile = {};
    if (role === 'student') {
        profile.first_name = document.getElementById('registerFirstName').value;
        profile.last_name = document.getElementById('registerLastName').value;
    } else {
        profile.name = document.getElementById('registerCompanyName').value;
    }
    
    try {
        const response = await fetch('/api/auth/register', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ email, password, role, profile })
        });
        
        const data = await response.json();
        
        if (response.ok) {
            showNotification('Registration successful! Please login.', 'success');
            showView('login');
        } else {
            showNotification(data.error || 'Registration failed', 'error');
        }
    } catch (error) {
        showNotification('An error occurred', 'error');
    } finally {
        showLoading(false);
    }
}

function logout() {
    localStorage.removeItem('token');
    currentToken = null;
    currentUser = null;
    updateUI();
    showView('home');
    showNotification('Logged out successfully', 'info');
}

function toggleRegisterFields() {
    const role = document.getElementById('registerRole').value;
    document.getElementById('studentFields').style.display = role === 'student' ? 'block' : 'none';
    document.getElementById('companyFields').style.display = (role === 'company' || role === 'faculty') ? 'block' : 'none';
}

// View Management
function showView(viewName) {
    // Hide all views
    document.querySelectorAll('.view').forEach(view => {
        view.classList.remove('active');
    });
    
    // Show selected view
    const view = document.getElementById(viewName + 'View');
    if (view) {
        view.classList.add('active');
        
        // Load view-specific content
        switch(viewName) {
            case 'dashboard':
                loadDashboard();
                break;
            case 'profile':
                loadProfile();
                break;
            case 'opportunities':
                loadOpportunities();
                break;
            case 'messages':
                loadMessages();
                break;
            case 'notifications':
                loadNotifications();
                break;
        }
    }
    
    // Update nav links
    document.querySelectorAll('.nav-link').forEach(link => {
        link.classList.remove('active');
    });
}

function updateUI() {
    if (currentUser) {
        document.getElementById('authLinks').style.display = 'none';
        document.getElementById('userLinks').style.display = 'flex';
        updateNotificationBadge();
        updateMessageBadge();
    } else {
        document.getElementById('authLinks').style.display = 'flex';
        document.getElementById('userLinks').style.display = 'none';
    }
}

// Dashboard
async function loadDashboard() {
    if (!currentUser) return;
    
    showLoading(true);
    
    try {
        let endpoint = '';
        if (currentUser.role === 'student') {
            endpoint = '/api/student/dashboard';
        } else if (currentUser.role === 'company' || currentUser.role === 'faculty') {
            endpoint = '/api/company/dashboard';
        } else {
            endpoint = '/api/admin/analytics';
        }
        
        const response = await fetch(endpoint, {
            headers: {
                'Authorization': `Bearer ${currentToken}`
            }
        });
        
        if (response.ok) {
            const data = await response.json();
            renderDashboard(data);
        }
    } catch (error) {
        console.error('Error loading dashboard:', error);
    } finally {
        showLoading(false);
    }
}

function renderDashboard(data) {
    const container = document.getElementById('dashboardContent');
    
    if (currentUser.role === 'student') {
        container.innerHTML = `
            <div class="stats-grid">
                <div class="stat-card">
                    <div class="stat-value">${data.stats.total_applications}</div>
                    <div class="stat-label">Total Applications</div>
                </div>
                <div class="stat-card">
                    <div class="stat-value">${data.stats.pending}</div>
                    <div class="stat-label">Pending</div>
                </div>
                <div class="stat-card">
                    <div class="stat-value">${data.stats.shortlisted}</div>
                    <div class="stat-label">Shortlisted</div>
                </div>
                <div class="stat-card">
                    <div class="stat-value">${data.stats.interview}</div>
                    <div class="stat-label">Interviews</div>
                </div>
            </div>
            <h3>Recommended Opportunities</h3>
            <div class="opportunities-grid" id="recommendedOpps"></div>
            <h3>My Applications</h3>
            <div id="myApplications"></div>
        `;
        
        renderOpportunities(data.recommended_opportunities, 'recommendedOpps');
        renderApplications(data.applications, 'myApplications');
    } else if (currentUser.role === 'company' || currentUser.role === 'faculty') {
        container.innerHTML = `
            <div class="stats-grid">
                <div class="stat-card">
                    <div class="stat-value">${data.stats.total_opportunities}</div>
                    <div class="stat-label">Total Opportunities</div>
                </div>
                <div class="stat-card">
                    <div class="stat-value">${data.stats.active_opportunities}</div>
                    <div class="stat-label">Active</div>
                </div>
                <div class="stat-card">
                    <div class="stat-value">${data.stats.total_applications}</div>
                    <div class="stat-label">Total Applications</div>
                </div>
                <div class="stat-card">
                    <div class="stat-value">${data.stats.pending_applications}</div>
                    <div class="stat-label">Pending</div>
                </div>
            </div>
            <h3>My Opportunities</h3>
            <div class="opportunities-grid" id="myOpportunities"></div>
        `;
        
        renderOpportunities(data.opportunities, 'myOpportunities');
    }
}

// Profile
async function loadProfile() {
    if (!currentUser) return;
    
    showLoading(true);
    
    try {
        let endpoint = '';
        if (currentUser.role === 'student') {
            endpoint = '/api/student/profile';
        } else {
            endpoint = '/api/company/profile';
        }
        
        const response = await fetch(endpoint, {
            headers: {
                'Authorization': `Bearer ${currentToken}`
            }
        });
        
        if (response.ok) {
            const data = await response.json();
            renderProfile(data);
        }
    } catch (error) {
        console.error('Error loading profile:', error);
    } finally {
        showLoading(false);
    }
}

function renderProfile(profile) {
    const container = document.getElementById('profileContent');
    
    if (currentUser.role === 'student') {
        container.innerHTML = `
            <div class="card">
                <h3>Personal Information</h3>
                <form id="profileForm" onsubmit="updateProfile(event)">
                    <div class="form-group">
                        <label>First Name</label>
                        <input type="text" id="profileFirstName" value="${profile.first_name || ''}" required>
                    </div>
                    <div class="form-group">
                        <label>Last Name</label>
                        <input type="text" id="profileLastName" value="${profile.last_name || ''}" required>
                    </div>
                    <div class="form-group">
                        <label>Phone</label>
                        <input type="tel" id="profilePhone" value="${profile.phone || ''}">
                    </div>
                    <div class="form-group">
                        <label>Bio</label>
                        <textarea id="profileBio">${profile.bio || ''}</textarea>
                    </div>
                    <div class="form-group">
                        <label>Skills (comma-separated)</label>
                        <input type="text" id="profileSkills" value="${(profile.skills || []).join(', ')}">
                    </div>
                    <div class="form-group">
                        <label>Interests (comma-separated)</label>
                        <input type="text" id="profileInterests" value="${(profile.interests || []).join(', ')}">
                    </div>
                    <button type="submit" class="btn btn-primary">Update Profile</button>
                </form>
                <h3 style="margin-top: 2rem;">Resume</h3>
                <input type="file" id="resumeFile" accept=".pdf,.doc,.docx" onchange="uploadResume()">
                ${profile.resume_path ? '<p>Resume uploaded</p>' : '<p>No resume uploaded</p>'}
            </div>
        `;
    } else {
        container.innerHTML = `
            <div class="card">
                <form id="profileForm" onsubmit="updateCompanyProfile(event)">
                    <div class="form-group">
                        <label>Name</label>
                        <input type="text" id="companyName" value="${profile.name || ''}" required>
                    </div>
                    <div class="form-group">
                        <label>Description</label>
                        <textarea id="companyDescription">${profile.description || ''}</textarea>
                    </div>
                    <div class="form-group">
                        <label>Website</label>
                        <input type="url" id="companyWebsite" value="${profile.website || ''}">
                    </div>
                    <div class="form-group">
                        <label>Phone</label>
                        <input type="tel" id="companyPhone" value="${profile.phone || ''}">
                    </div>
                    <button type="submit" class="btn btn-primary">Update Profile</button>
                </form>
            </div>
        `;
    }
}

async function updateProfile(event) {
    event.preventDefault();
    
    const skills = document.getElementById('profileSkills').value.split(',').map(s => s.trim()).filter(s => s);
    const interests = document.getElementById('profileInterests').value.split(',').map(i => i.trim()).filter(i => i);
    
    const data = {
        first_name: document.getElementById('profileFirstName').value,
        last_name: document.getElementById('profileLastName').value,
        phone: document.getElementById('profilePhone').value,
        bio: document.getElementById('profileBio').value,
        skills: skills,
        interests: interests
    };
    
    try {
        const response = await fetch('/api/student/profile', {
            method: 'PUT',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${currentToken}`
            },
            body: JSON.stringify(data)
        });
        
        if (response.ok) {
            showNotification('Profile updated successfully', 'success');
            loadProfile();
        } else {
            const error = await response.json();
            showNotification(error.error || 'Update failed', 'error');
        }
    } catch (error) {
        showNotification('An error occurred', 'error');
    }
}

async function uploadResume() {
    const file = document.getElementById('resumeFile').files[0];
    if (!file) return;
    
    const formData = new FormData();
    formData.append('resume', file);
    
    showLoading(true);
    
    try {
        const response = await fetch('/api/student/resume/upload', {
            method: 'POST',
            headers: {
                'Authorization': `Bearer ${currentToken}`
            },
            body: formData
        });
        
        if (response.ok) {
            showNotification('Resume uploaded successfully', 'success');
            loadProfile();
        } else {
            const error = await response.json();
            showNotification(error.error || 'Upload failed', 'error');
        }
    } catch (error) {
        showNotification('An error occurred', 'error');
    } finally {
        showLoading(false);
    }
}

// Opportunities
async function loadOpportunities() {
    showLoading(true);
    
    try {
        const response = await fetch('/api/opportunities', {
            headers: currentToken ? {
                'Authorization': `Bearer ${currentToken}`
            } : {}
        });
        
        if (response.ok) {
            const data = await response.json();
            renderOpportunities(data.opportunities, 'opportunitiesList');
        }
    } catch (error) {
        console.error('Error loading opportunities:', error);
    } finally {
        showLoading(false);
    }
}

async function loadDomains() {
    try {
        const response = await fetch('/api/opportunities/domains');
        if (response.ok) {
            const data = await response.json();
            const select = document.getElementById('domainFilter');
            data.forEach(domain => {
                const option = document.createElement('option');
                option.value = domain;
                option.textContent = domain;
                select.appendChild(option);
            });
        }
    } catch (error) {
        console.error('Error loading domains:', error);
    }
}

function renderOpportunities(opportunities, containerId) {
    const container = document.getElementById(containerId);
    if (!container) return;
    
    if (opportunities.length === 0) {
        container.innerHTML = '<p>No opportunities found</p>';
        return;
    }
    
    container.innerHTML = opportunities.map(opp => `
        <div class="opportunity-card" onclick="showOpportunityDetails(${opp.id})">
            <h3>${opp.title}</h3>
            <p>${opp.company_name || 'Company'}</p>
            <div class="opportunity-meta">
                <span><i class="fas fa-tag"></i> ${opp.domain}</span>
                <span><i class="fas fa-map-marker-alt"></i> ${opp.location || 'Remote'}</span>
                <span><i class="fas fa-clock"></i> ${opp.duration || 'N/A'}</span>
                ${opp.has_applied ? '<span class="status-badge status-pending">Applied</span>' : ''}
            </div>
        </div>
    `).join('');
}

async function showOpportunityDetails(oppId) {
    showLoading(true);
    
    try {
        const response = await fetch(`/api/opportunities/${oppId}`, {
            headers: currentToken ? {
                'Authorization': `Bearer ${currentToken}`
            } : {}
        });
        
        if (response.ok) {
            const data = await response.json();
            renderOpportunityModal(data);
        }
    } catch (error) {
        console.error('Error loading opportunity:', error);
    } finally {
        showLoading(false);
    }
}

function renderOpportunityModal(opp) {
    const container = document.getElementById('opportunityModalContent');
    container.innerHTML = `
        <h2>${opp.title}</h2>
        <p><strong>Company:</strong> ${opp.company_name}</p>
        <p><strong>Domain:</strong> ${opp.domain}</p>
        <p><strong>Location:</strong> ${opp.location || 'Remote'}</p>
        <p><strong>Work Type:</strong> ${opp.work_type}</p>
        <p><strong>Duration:</strong> ${opp.duration || 'N/A'}</p>
        <p><strong>Stipend:</strong> ${opp.stipend || 'Not specified'}</p>
        <p><strong>Description:</strong></p>
        <p>${opp.description}</p>
        ${opp.required_skills && opp.required_skills.length > 0 ? `
            <p><strong>Required Skills:</strong></p>
            <div class="skills-tags">
                ${opp.required_skills.map(skill => `<span class="skill-tag">${skill}</span>`).join('')}
            </div>
        ` : ''}
        ${currentUser && currentUser.role === 'student' && !opp.has_applied ? `
            <div style="margin-top: 2rem;">
                <button onclick="applyToOpportunity(${opp.id})" class="btn btn-primary">Apply Now</button>
            </div>
        ` : ''}
        ${opp.has_applied ? '<p class="alert alert-info">You have already applied for this opportunity</p>' : ''}
    `;
    
    document.getElementById('opportunityModal').style.display = 'block';
}

function closeModal() {
    document.getElementById('opportunityModal').style.display = 'none';
}

async function applyToOpportunity(oppId) {
    if (!currentUser || currentUser.role !== 'student') {
        showNotification('Please login as a student to apply', 'error');
        return;
    }
    
    const coverLetter = prompt('Enter cover letter (optional):');
    
    try {
        const response = await fetch('/api/applications', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${currentToken}`
            },
            body: JSON.stringify({
                opportunity_id: oppId,
                cover_letter: coverLetter || ''
            })
        });
        
        const data = await response.json();
        
        if (response.ok) {
            showNotification('Application submitted successfully!', 'success');
            closeModal();
            loadOpportunities();
            if (currentUser.role === 'student') {
                loadDashboard();
            }
        } else {
            showNotification(data.error || 'Application failed', 'error');
        }
    } catch (error) {
        showNotification('An error occurred', 'error');
    }
}

function filterOpportunities() {
    const search = document.getElementById('searchInput').value;
    const domain = document.getElementById('domainFilter').value;
    const workType = document.getElementById('workTypeFilter').value;
    
    const params = new URLSearchParams();
    if (search) params.append('search', search);
    if (domain) params.append('domain', domain);
    if (workType) params.append('work_type', workType);
    
    showLoading(true);
    
    fetch(`/api/opportunities?${params.toString()}`, {
        headers: currentToken ? {
            'Authorization': `Bearer ${currentToken}`
        } : {}
    })
    .then(res => res.json())
    .then(data => {
        renderOpportunities(data.opportunities, 'opportunitiesList');
    })
    .catch(err => console.error('Error filtering:', err))
    .finally(() => showLoading(false));
}

// Applications
function renderApplications(applications, containerId) {
    const container = document.getElementById(containerId);
    if (!container) return;
    
    if (applications.length === 0) {
        container.innerHTML = '<p>No applications yet</p>';
        return;
    }
    
    container.innerHTML = applications.map(app => `
        <div class="card">
            <div class="card-header">
                <h3>${app.opportunity_title}</h3>
                <span class="status-badge status-${app.status}">${app.status}</span>
            </div>
            <p>Applied on: ${new Date(app.applied_at).toLocaleDateString()}</p>
            ${app.skill_match_percentage ? `<p>Skill Match: ${app.skill_match_percentage.toFixed(1)}%</p>` : ''}
        </div>
    `).join('');
}

// Notifications
async function loadNotifications() {
    if (!currentUser) return;
    
    showLoading(true);
    
    try {
        const response = await fetch('/api/notifications', {
            headers: {
                'Authorization': `Bearer ${currentToken}`
            }
        });
        
        if (response.ok) {
            const data = await response.json();
            renderNotifications(data);
        }
    } catch (error) {
        console.error('Error loading notifications:', error);
    } finally {
        showLoading(false);
    }
}

function renderNotifications(notifications) {
    const container = document.getElementById('notificationsContent');
    
    if (notifications.length === 0) {
        container.innerHTML = '<p>No notifications</p>';
        return;
    }
    
    container.innerHTML = notifications.map(notif => `
        <div class="card ${notif.is_read ? '' : 'unread'}" onclick="markNotificationRead(${notif.id})">
            <h3>${notif.title}</h3>
            <p>${notif.message}</p>
            <small>${new Date(notif.created_at).toLocaleString()}</small>
        </div>
    `).join('');
}

async function markNotificationRead(notifId) {
    try {
        await fetch(`/api/notifications/${notifId}/read`, {
            method: 'PUT',
            headers: {
                'Authorization': `Bearer ${currentToken}`
            }
        });
        
        updateNotificationBadge();
        loadNotifications();
    } catch (error) {
        console.error('Error marking notification as read:', error);
    }
}

async function updateNotificationBadge() {
    if (!currentUser) return;
    
    try {
        const response = await fetch('/api/notifications/unread-count', {
            headers: {
                'Authorization': `Bearer ${currentToken}`
            }
        });
        
        if (response.ok) {
            const data = await response.json();
            const badge = document.getElementById('notificationBadge');
            if (data.unread_count > 0) {
                badge.textContent = data.unread_count;
                badge.style.display = 'inline';
            } else {
                badge.style.display = 'none';
            }
        }
    } catch (error) {
        console.error('Error updating notification badge:', error);
    }
}

async function updateMessageBadge() {
    // Similar implementation for messages
    // For now, just a placeholder
}

// Messages
async function loadMessages() {
    if (!currentUser) return;
    
    showLoading(true);
    
    try {
        const response = await fetch('/api/messages/conversations', {
            headers: {
                'Authorization': `Bearer ${currentToken}`
            }
        });
        
        if (response.ok) {
            const data = await response.json();
            renderMessages(data);
        }
    } catch (error) {
        console.error('Error loading messages:', error);
    } finally {
        showLoading(false);
    }
}

function renderMessages(conversations) {
    const container = document.getElementById('messagesContent');
    
    if (conversations.length === 0) {
        container.innerHTML = '<p>No messages</p>';
        return;
    }
    
    container.innerHTML = conversations.map(conv => `
        <div class="card" onclick="openConversation(${conv.user.id})">
            <h3>${conv.user.email}</h3>
            ${conv.last_message ? `<p>${conv.last_message.content.substring(0, 100)}...</p>` : ''}
            ${conv.unread_count > 0 ? `<span class="badge">${conv.unread_count}</span>` : ''}
        </div>
    `).join('');
}

function openConversation(userId) {
    // TODO: Implement conversation view
    showNotification('Conversation feature coming soon', 'info');
}

async function updateCompanyProfile(event) {
    event.preventDefault();
    
    const data = {
        name: document.getElementById('companyName').value,
        description: document.getElementById('companyDescription').value,
        website: document.getElementById('companyWebsite').value,
        phone: document.getElementById('companyPhone').value
    };
    
    try {
        const response = await fetch('/api/company/profile', {
            method: 'PUT',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${currentToken}`
            },
            body: JSON.stringify(data)
        });
        
        if (response.ok) {
            showNotification('Profile updated successfully', 'success');
            loadProfile();
        } else {
            const error = await response.json();
            showNotification(error.error || 'Update failed', 'error');
        }
    } catch (error) {
        showNotification('An error occurred', 'error');
    }
}

// Utility functions
function showLoading(show) {
    document.getElementById('loadingSpinner').style.display = show ? 'flex' : 'none';
}

function showNotification(message, type = 'info') {
    const alertClass = type === 'error' ? 'alert-error' : type === 'success' ? 'alert-success' : 'alert-info';
    const notification = document.createElement('div');
    notification.className = `alert ${alertClass}`;
    notification.textContent = message;
    notification.style.position = 'fixed';
    notification.style.top = '80px';
    notification.style.right = '20px';
    notification.style.zIndex = '4000';
    notification.style.minWidth = '300px';
    
    document.body.appendChild(notification);
    
    setTimeout(() => {
        notification.remove();
    }, 5000);
}

// Close modal when clicking outside
window.onclick = function(event) {
    const modal = document.getElementById('opportunityModal');
    if (event.target === modal) {
        closeModal();
    }
}

