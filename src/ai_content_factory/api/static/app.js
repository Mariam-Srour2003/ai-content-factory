// AI Content Factory - Frontend JavaScript

// API base URL
const API_BASE = window.location.origin;

// State
let currentTaskId = null;
let pollInterval = null;
let performanceChart = null;
let rankingChart = null;

// Initialize on page load
document.addEventListener('DOMContentLoaded', () => {
    loadDashboard();
    loadSettings();
});

// ==================== Navigation ====================

function toggleMenu() {
    const sidebar = document.getElementById('sidebar');
    sidebar.classList.toggle('active');
}

function switchTab(tabName) {
    // Update nav items
    document.querySelectorAll('.nav-item').forEach(item => {
        item.classList.remove('active');
    });
    document.querySelector(`.nav-item[data-tab="${tabName}"]`).classList.add('active');

    // Update tab content
    document.querySelectorAll('.tab-content').forEach(tab => {
        tab.classList.remove('active');
    });
    document.getElementById(`${tabName}-tab`).classList.add('active');

    // Close mobile menu
    document.getElementById('sidebar').classList.remove('active');

    // Load content for specific tabs
    if (tabName === 'dashboard') {
        loadDashboard();
    } else if (tabName === 'library') {
        loadContentLibrary();
    } else if (tabName === 'analytics') {
        loadAnalytics();
    } else if (tabName === 'settings') {
        loadSettings();
    }
}

// ==================== Dashboard ====================

async function loadDashboard() {
    try {
        const response = await fetch(`${API_BASE}/api/analytics/dashboard`);
        const data = await response.json();

        // Update KPIs with actual metrics
        const kpiGrid = document.getElementById('kpiGrid');
        kpiGrid.innerHTML = `
            <div class="kpi-card">
                <div class="kpi-header">
                    <div>
                        <p class="kpi-label">Content Generated</p>
                        <p class="kpi-value">${data.kpis.content_generated}</p>
                    </div>
                    <div class="kpi-icon icon-blue">
                        <svg fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 6.253v13m0-13C10.832 5.477 9.246 5 7.5 5S4.168 5.477 3 6.253v13C4.168 18.477 5.754 18 7.5 18s3.332.477 4.5 1.253m0-13C13.168 5.477 14.754 5 16.5 5c1.747 0 3.332.477 4.5 1.253v13C19.832 18.477 18.247 18 16.5 18c-1.746 0-3.332.477-4.5 1.253"/>
                        </svg>
                    </div>
                </div>
            </div>
            <div class="kpi-card">
                <div class="kpi-header">
                    <div>
                        <p class="kpi-label">Avg Quality Score</p>
                        <p class="kpi-value">${data.kpis.avg_quality_score}</p>
                    </div>
                    <div class="kpi-icon icon-green">
                        <svg fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"/>
                        </svg>
                    </div>
                </div>
            </div>
            <div class="kpi-card">
                <div class="kpi-header">
                    <div>
                        <p class="kpi-label">Avg Brand Voice</p>
                        <p class="kpi-value">${data.kpis.avg_brand_voice}</p>
                    </div>
                    <div class="kpi-icon icon-purple">
                        <svg fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M7 8h10M7 12h4m1 8l-4-4H5a2 2 0 01-2-2V6a2 2 0 012-2h14a2 2 0 012 2v8a2 2 0 01-2 2h-3l-4 4z"/>
                        </svg>
                    </div>
                </div>
            </div>
            <div class="kpi-card">
                <div class="kpi-header">
                    <div>
                        <p class="kpi-label">Avg Gen Time</p>
                        <p class="kpi-value">${data.kpis.avg_generation_time}</p>
                    </div>
                    <div class="kpi-icon icon-orange">
                        <svg fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z"/>
                        </svg>
                    </div>
                </div>
            </div>
        `;

        // Update charts with real metrics data
        updatePerformanceChart(data.performance_data);
        updateMetricsChart(data.performance_data);
    } catch (error) {
        console.error('Error loading dashboard:', error);
    }
}

function updatePerformanceChart(data) {
    const ctx = document.getElementById('performanceChart');
    
    if (performanceChart) {
        performanceChart.destroy();
    }

    if (!data || data.length === 0) {
        return;
    }

    performanceChart = new Chart(ctx, {
        type: 'line',
        data: {
            labels: data.map(d => `#${d.index}`),
            datasets: [
                {
                    label: 'Quality Score',
                    data: data.map(d => d.quality_score),
                    borderColor: '#3b82f6',
                    backgroundColor: 'rgba(59, 130, 246, 0.1)',
                    tension: 0.4
                },
                {
                    label: 'Brand Voice %',
                    data: data.map(d => d.brand_voice),
                    borderColor: '#a855f7',
                    backgroundColor: 'rgba(168, 85, 247, 0.1)',
                    tension: 0.4
                }
            ]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    position: 'bottom'
                }
            },
            scales: {
                y: {
                    beginAtZero: true,
                    max: 100
                }
            }
        }
    });
}

function updateMetricsChart(data) {
    const ctx = document.getElementById('rankingChart');
    
    if (rankingChart) {
        rankingChart.destroy();
    }

    if (!data || data.length === 0) {
        return;
    }

    rankingChart = new Chart(ctx, {
        type: 'bar',
        data: {
            labels: data.map(d => `#${d.index}`),
            datasets: [
                {
                    label: 'Readability Score',
                    data: data.map(d => d.readability),
                    backgroundColor: '#22c55e'
                },
                {
                    label: 'Generation Time (s)',
                    data: data.map(d => d.generation_time),
                    backgroundColor: '#f59e0b'
                }
            ]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    position: 'bottom'
                }
            },
            scales: {
                y: {
                    beginAtZero: true
                }
            }
        }
    });
}

// ==================== Content Generation ====================

function showCreateModal() {
    switchTab('create');
}

async function generateContent(event) {
    event.preventDefault();
    
    const form = event.target;
    const formData = new FormData(form);

    // Clear any previous task/polling to avoid stale status updates
    if (pollInterval) {
        clearInterval(pollInterval);
        pollInterval = null;
    }
    currentTaskId = null;
    
    const requestData = {
        topic: formData.get('topic'),
        target_keyword: formData.get('target_keyword'),
        word_count: parseInt(formData.get('word_count')),
        content_type: formData.get('content_type'),
        target_audience: formData.get('target_audience')
    };

    try {
        const response = await fetch(`${API_BASE}/api/content/generate`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(requestData)
        });

        const result = await response.json();
        currentTaskId = result.task_id;

        // Show progress modal
        showProgressModal();

        // Fetch and render initial status immediately to avoid flash
        try {
            const initialResp = await fetch(`${API_BASE}/api/content/status/${currentTaskId}`);
            const initialStatus = await initialResp.json();
            updateProgressModal(initialStatus);
        } catch (e) {
            // If initial fetch fails, still proceed with polling
            console.warn('Initial status fetch failed, starting polling...', e);
        }

        // Start polling for status
        pollGenerationStatus();

        // Clear form
        form.reset();
    } catch (error) {
        console.error('Error generating content:', error);
        alert('Failed to start content generation. Please try again.');
    }
}

function showProgressModal() {
    const modal = document.getElementById('progressModal');
    modal.classList.add('active');
    // Reset progress UI state before any polling begins
    const progressFill = document.getElementById('progressFill');
    const progressMessage = document.getElementById('progressMessage');
    if (progressFill) {
        progressFill.style.width = '0%';
        progressFill.style.backgroundColor = '#4f46e5';
    }
    if (progressMessage) {
        progressMessage.textContent = 'Initializing...';
    }
    document.getElementById('closeProgressBtn').style.display = 'none';
}

function closeProgressModal() {
    const modal = document.getElementById('progressModal');
    modal.classList.remove('active');
    if (pollInterval) {
        clearInterval(pollInterval);
        pollInterval = null;
    }
}

async function pollGenerationStatus() {
    if (pollInterval) {
        clearInterval(pollInterval);
    }

    pollInterval = setInterval(async () => {
        try {
            // Guard against missing task id
            if (!currentTaskId) { return; }
            const response = await fetch(`${API_BASE}/api/content/status/${currentTaskId}`);
            const status = await response.json();

            updateProgressModal(status);

            if (status.status === 'completed' || status.status === 'error') {
                clearInterval(pollInterval);
                pollInterval = null;
                document.getElementById('closeProgressBtn').style.display = 'block';
                
                if (status.status === 'completed') {
                    // Refresh content library
                    setTimeout(() => {
                        closeProgressModal();
                        switchTab('library');
                    }, 2000);
                }
            }
        } catch (error) {
            console.error('Error polling status:', error);
        }
    }, 2000);
}

function updateProgressModal(status) {
    const progressFill = document.getElementById('progressFill');
    const progressMessage = document.getElementById('progressMessage');

    const pct = typeof status.progress === 'number' ? status.progress : 0;
    progressFill.style.width = `${pct}%`;
    progressMessage.textContent = status.message || 'Initializing...';

    if (status.status === 'error') {
        progressFill.style.backgroundColor = '#ef4444';
    } else if (status.status === 'completed') {
        progressFill.style.backgroundColor = '#22c55e';
    } else {
        // In-progress states
        progressFill.style.backgroundColor = '#4f46e5';
    }
}

// ==================== Content Library ====================

async function loadContentLibrary() {
    try {
        const response = await fetch(`${API_BASE}/api/content/library`);
        const content = await response.json();

        const tableBody = document.getElementById('contentTableBody');
        
        if (content.length === 0) {
            tableBody.innerHTML = '<tr><td colspan="6" style="text-align: center; padding: 2rem;">No content generated yet. Create your first content!</td></tr>';
            return;
        }

        tableBody.innerHTML = content.map(item => `
            <tr>
                <td><strong>${item.title}</strong></td>
                <td>
                    <span class="status-badge status-${item.status}">
                        ${item.status.charAt(0).toUpperCase() + item.status.slice(1)}
                    </span>
                </td>
                <td>${item.leads}</td>
                <td>${item.ranking ? '#' + item.ranking : 'N/A'}</td>
                <td>${item.date}</td>
                <td>
                    <div class="action-buttons">
                        <button class="action-btn" onclick="viewContent('${item.id}')" title="View">
                            <svg fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z"/>
                                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z"/>
                            </svg>
                        </button>
                        <button class="action-btn" onclick="downloadContent('${item.id}')" title="Download">
                            <svg fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-4l-4 4m0 0l-4-4m4 4V4"/>
                            </svg>
                        </button>
                        <button class="action-btn" onclick="deleteContent('${item.id}')" title="Delete">
                            <svg fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16"/>
                            </svg>
                        </button>
                    </div>
                </td>
            </tr>
        `).join('');
    } catch (error) {
        console.error('Error loading content library:', error);
    }
}

function filterContent() {
    const searchInput = document.getElementById('searchInput').value.toLowerCase();
    const rows = document.querySelectorAll('#contentTableBody tr');

    rows.forEach(row => {
        const text = row.textContent.toLowerCase();
        row.style.display = text.includes(searchInput) ? '' : 'none';
    });
}

async function viewContent(contentId) {
    try {
        const response = await fetch(`${API_BASE}/api/content/${contentId}`);
        const content = await response.json();

        const modal = document.getElementById('contentModal');
        const modalTitle = document.getElementById('contentModalTitle');
        const modalBody = document.getElementById('contentModalBody');

        modalTitle.textContent = content.title;
        
        // Convert markdown to HTML (simple version)
        const htmlContent = content.content.replace(/\n/g, '<br>');
        
        modalBody.innerHTML = `
            <div style="margin-bottom: 1rem;">
                <strong>Meta Description:</strong>
                <p>${content.meta_description}</p>
            </div>
            <div style="margin-bottom: 1rem;">
                <strong>Topic:</strong> ${content.topic} | 
                <strong>Keyword:</strong> ${content.keyword} | 
                <strong>Word Count:</strong> ${content.word_count}
            </div>
            <hr style="margin: 1rem 0; border: none; border-top: 1px solid #e2e8f0;">
            <div style="line-height: 1.8;">
                ${htmlContent}
            </div>
        `;

        modal.classList.add('active');
    } catch (error) {
        console.error('Error viewing content:', error);
        alert('Failed to load content.');
    }
}

function closeContentModal() {
    const modal = document.getElementById('contentModal');
    modal.classList.remove('active');
}

async function downloadContent(contentId) {
    try {
        const response = await fetch(`${API_BASE}/api/content/${contentId}`);
        const content = await response.json();

        const blob = new Blob([content.content], { type: 'text/markdown' });
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `${contentId}.md`;
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
        URL.revokeObjectURL(url);
    } catch (error) {
        console.error('Error downloading content:', error);
        alert('Failed to download content.');
    }
}

async function deleteContent(contentId) {
    if (!confirm('Are you sure you want to delete this content?')) {
        return;
    }

    try {
        const response = await fetch(`${API_BASE}/api/content/${contentId}`, {
            method: 'DELETE'
        });

        if (response.ok) {
            loadContentLibrary();
        } else {
            alert('Failed to delete content.');
        }
    } catch (error) {
        console.error('Error deleting content:', error);
        alert('Failed to delete content.');
    }
}

// ==================== Analytics ====================

async function loadAnalytics() {
    try {
        const response = await fetch(`${API_BASE}/api/analytics/dashboard`);
        const data = await response.json();

        // Top topics
        const topTopics = document.getElementById('topTopics');
        if (data.top_topics && data.top_topics.length > 0) {
            topTopics.innerHTML = data.top_topics.map(item => `
                <div class="metric-row">
                    <span>${item.topic}</span>
                    <span class="metric-value">${item.leads}</span>
                </div>
            `).join('');
        } else {
            topTopics.innerHTML = '<p>No data available</p>';
        }

        // Status breakdown
        const statusBreakdown = document.getElementById('statusBreakdown');
        statusBreakdown.innerHTML = `
            <div class="metric-row">
                <span class="status-badge status-published">Published</span>
                <span class="metric-value">${data.status_breakdown.published}</span>
            </div>
            <div class="metric-row">
                <span class="status-badge status-review">In Review</span>
                <span class="metric-value">${data.status_breakdown.review}</span>
            </div>
            <div class="metric-row">
                <span class="status-badge status-draft">Draft</span>
                <span class="metric-value">${data.status_breakdown.draft}</span>
            </div>
        `;

        // Efficiency & Advanced Metrics (remove placeholder values)
        const efficiency = document.getElementById('efficiencyMetrics');
        const adv = data.advanced_metrics || { keyword_density: 0, word_count_accuracy: 0, heading_structure: 0, seo_requirements: 0, pass_rate: 0 };
        efficiency.innerHTML = `
            <div class="metric-row">
                <span>Avg. Keyword Density</span>
                <span class="metric-value">${adv.keyword_density}%</span>
            </div>
            <div class="metric-row">
                <span>Word Count Accuracy</span>
                <span class="metric-value">${adv.word_count_accuracy}%</span>
            </div>
            <div class="metric-row">
                <span>Heading Structure Score</span>
                <span class="metric-value">${adv.heading_structure}</span>
            </div>
            <div class="metric-row">
                <span>SEO Requirements Score</span>
                <span class="metric-value">${adv.seo_requirements}</span>
            </div>
            <div class="metric-row">
                <span>Requirements Pass Rate</span>
                <span class="metric-value">${adv.pass_rate}%</span>
            </div>
        `;
    } catch (error) {
        console.error('Error loading analytics:', error);
    }
}

// ==================== Settings ====================

async function loadSettings() {
    try {
        const response = await fetch(`${API_BASE}/api/settings`);
        const settings = await response.json();

        document.getElementById('llmModel').value = settings.llm_model;
        document.getElementById('temperature').value = settings.temperature;
        document.getElementById('autoPublish').checked = settings.auto_publish;
        document.getElementById('generateSocial').checked = settings.generate_social;
        document.getElementById('requireFactCheck').checked = settings.require_fact_check;
    } catch (error) {
        console.error('Error loading settings:', error);
    }
}

async function saveSettings(event) {
    event.preventDefault();

    const form = event.target;
    const formData = new FormData(form);

    const settings = {
        llm_model: formData.get('llm_model'),
        temperature: parseFloat(formData.get('temperature')),
        auto_publish: formData.get('auto_publish') === 'on',
        generate_social: formData.get('generate_social') === 'on',
        require_fact_check: formData.get('require_fact_check') === 'on'
    };

    try {
        const response = await fetch(`${API_BASE}/api/settings`, {
            method: 'PUT',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(settings)
        });

        if (response.ok) {
            alert('Settings saved successfully!');
        } else {
            alert('Failed to save settings.');
        }
    } catch (error) {
        console.error('Error saving settings:', error);
        alert('Failed to save settings.');
    }
}

// Close modals when clicking outside
window.onclick = function(event) {
    const progressModal = document.getElementById('progressModal');
    const contentModal = document.getElementById('contentModal');
    
    if (event.target === progressModal) {
        closeProgressModal();
    }
    if (event.target === contentModal) {
        closeContentModal();
    }
}
