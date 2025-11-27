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
    } else if (tabName === 'research') {
        // Initialize research tab
        showResearchSection('competitor');
        loadResearchInsights(); // Load any existing insights
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























// ==================== Research Tab Functions ====================

function showResearchSection(section) {
    // Hide all sections
    document.querySelectorAll('.research-section').forEach(sec => {
        sec.classList.remove('active');
    });
    
    // Remove active class from all buttons
    document.querySelectorAll('.research-tab-btn').forEach(btn => {
        btn.classList.remove('active');
    });
    
    // Show selected section
    document.getElementById(`${section}-section`).classList.add('active');
    
    // Activate corresponding button
    const activeBtn = document.querySelector(`.research-tab-btn[onclick="showResearchSection('${section}')"]`);
    if (activeBtn) {
        activeBtn.classList.add('active');
    }
    
    // Clear results when switching sections
    document.getElementById('researchResults').innerHTML = '';
    document.getElementById('topicAnalysisResults').innerHTML = '';
}

async function runQuickResearch() {
    // Run both competitor and topic analysis with default settings
    showResearchSection('competitor');
    
    const domains = ['https://techcrunch.com', 'https://www.theverge.com'];
    const keywords = ['ai', 'technology', 'digital', 'innovation'];
    
    showLoading('researchResults', 'Running comprehensive research analysis...');
    
    try {
        const response = await fetch('/api/research/analyze-competitors', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                competitor_domains: domains,
                keywords: keywords
            })
        });
        
        const result = await response.json();
        
        if (result.status === 'success') {
            displayResearchResults(result.data);
        } else {
            showError('researchResults', result.message);
        }
    } catch (error) {
        showError('researchResults', 'Quick research failed: ' + error.message);
    }
}

async function loadResearchInsights() {
    showLoading('insights-content', 'Loading research insights...');
    
    try {
        const response = await fetch('/api/research/insights');
        const result = await response.json();
        
        if (result.status === 'success') {
            displayResearchInsights(result.data);
        } else {
            showError('insights-content', result.message);
        }
    } catch (error) {
        showError('insights-content', 'Failed to load insights: ' + error.message);
    }
}

async function loadTopicRecommendations() {
    showLoading('insights-content', 'Loading topic recommendations...');
    
    try {
        const response = await fetch('/api/research/topic-recommendations');
        const result = await response.json();
        
        if (result.status === 'success') {
            displayTopicRecommendations(result.data);
        } else {
            showError('insights-content', result.message);
        }
    } catch (error) {
        showError('insights-content', 'Failed to load recommendations: ' + error.message);
    }
}

function displayResearchInsights(data) {
    const container = document.getElementById('insights-content');
    
    if (!data || Object.keys(data).length === 0) {
        container.innerHTML = '<p class="insights-placeholder">No research data available. Run research analysis first.</p>';
        return;
    }
    
    const webData = data.web_scraping_results || {};
    const topicData = data.topic_analysis_results || {};
    
    container.innerHTML = `
        <div style="width: 100%;">
            <div class="research-section-card">
                <h4>📈 Research Summary</h4>
                <div class="stats-grid">
                    <div class="stat-card">
                        <h4>${webData.metadata?.total_posts_scraped || 0}</h4>
                        <p>Posts Analyzed</p>
                    </div>
                    <div class="stat-card">
                        <h4>${webData.metadata?.total_content_gaps || 0}</h4>
                        <p>Content Gaps</p>
                    </div>
                    <div class="stat-card">
                        <h4>${topicData.analysis_metadata?.high_priority_topics || 0}</h4>
                        <p>High Priority</p>
                    </div>
                </div>
            </div>
            
            ${webData.research_insights ? `
            <div class="research-section-card">
                <h4>🎯 Content Opportunities</h4>
                <div class="opportunities-list">
                    ${(webData.research_insights.content_opportunities || []).slice(0, 8).map(opp => `
                        <div class="opportunity-item">
                            <strong>${opp}</strong>
                            <span>Opportunity</span>
                        </div>
                    `).join('')}
                </div>
            </div>
            ` : ''}
            
            ${topicData.content_recommendations ? `
            <div class="research-section-card">
                <h4>💡 Recommended Content</h4>
                <div class="recommendations">
                    ${topicData.content_recommendations.slice(0, 3).map(rec => `
                        <div class="recommendation">
                            <h5>${rec.topic_title}</h5>
                            <div class="rec-details">
                                <span>Angle: ${rec.content_angle}</span>
                                <span>Effort: ${rec.estimated_effort}</span>
                            </div>
                            <div class="keywords">
                                ${rec.target_keywords.map(kw => `<span class="keyword-tag">${kw}</span>`).join('')}
                            </div>
                        </div>
                    `).join('')}
                </div>
            </div>
            ` : ''}
        </div>
    `;
}

function displayTopicRecommendations(data) {
    const container = document.getElementById('insights-content');
    
    container.innerHTML = `
        <div style="width: 100%;">
            <div class="research-section-card">
                <h4>🚀 Top Priority Topics</h4>
                <div class="priority-topics">
                    ${(data.top_priority_topics || []).slice(0, 5).map(topic => `
                        <div class="priority-topic">
                            <div class="topic-header">
                                <strong>${topic.title}</strong>
                                <span class="priority-badge ${topic.priority_tier}">${topic.priority_tier?.toUpperCase() || 'MEDIUM'}</span>
                            </div>
                            <div class="topic-metrics">
                                <span>Score: ${topic.priority_score || 0}</span>
                                <span>Relevance: ${((topic.relevance_score || 0) * 100).toFixed(0)}%</span>
                            </div>
                            <p class="topic-summary">${topic.summary || 'No summary available'}</p>
                        </div>
                    `).join('')}
                </div>
            </div>
            
            ${data.content_recommendations ? `
            <div class="research-section-card">
                <h4>📝 Content Recommendations</h4>
                <div class="recommendations">
                    ${data.content_recommendations.map(rec => `
                        <div class="recommendation">
                            <h5>${rec.topic_title}</h5>
                            <div class="rec-details">
                                <span>Angle: ${rec.content_angle}</span>
                                <span>Effort: ${rec.estimated_effort}</span>
                                <span>Score: ${rec.priority_score}</span>
                            </div>
                            <div class="keywords">
                                ${rec.target_keywords.map(kw => `<span class="keyword-tag">${kw}</span>`).join('')}
                            </div>
                        </div>
                    `).join('')}
                </div>
            </div>
            ` : ''}
        </div>
    `;
}

// Helper functions for loading states
function showLoading(containerId, message = 'Loading...') {
    const container = document.getElementById(containerId);
    container.innerHTML = `
        <div class="research-loading">
            <div class="spinner"></div>
            <p>${message}</p>
        </div>
    `;
}

function showError(containerId, message) {
    const container = document.getElementById(containerId);
    container.innerHTML = `
        <div class="research-error">
            <p>${message}</p>
        </div>
    `;
}



async function analyzeCompetitors() {
    const domains = document.getElementById('competitorDomains').value.split(',').map(d => d.trim());
    const keywords = document.getElementById('researchKeywords').value.split(',').map(k => k.trim());
    
    showLoading('researchResults', 'Analyzing competitors...');
    
    try {
        const response = await fetch('/api/research/analyze-competitors', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                competitor_domains: domains,
                keywords: keywords
            })
        });
        
        const result = await response.json();
        
        if (result.status === 'success') {
            displayResearchResults(result.data);
        } else {
            showError('researchResults', result.message);
        }
    } catch (error) {
        showError('researchResults', 'Research analysis failed: ' + error.message);
    }
}

async function analyzeTopics() {
    const keywords = document.getElementById('topicKeywords').value.split(',').map(k => k.trim());
    const maxTopics = parseInt(document.getElementById('maxTopics').value) || 25;
    
    showLoading('topicAnalysisResults', 'Analyzing topics...');
    
    try {
        // Use JSON request body instead of query parameters
        const requestData = {
            domain_keywords: keywords,
            max_topics: maxTopics
        };
        
        const response = await fetch('/api/research/analyze-topics', {
            method: 'POST',
            headers: { 
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(requestData)
        });
        
        const result = await response.json();
        
        if (result.status === 'success') {
            displayTopicAnalysisResults(result.data);
        } else {
            showError('topicAnalysisResults', result.message);
        }
    } catch (error) {
        showError('topicAnalysisResults', 'Topic analysis failed: ' + error.message);
    }
}
function displayResearchResults(data) {
    const container = document.getElementById('researchResults');
    
    // Add safety checks
    if (!data) {
        showError('researchResults', 'No data received from analysis');
        return;
    }
    
    const webData = data.web_scraping_results || {};
    const topicData = data.topic_analysis_results || {};
    const executionSummary = data.execution_summary || {};
    
    container.innerHTML = `
        <div class="research-summary">
            <h3>📊 Comprehensive Research Summary</h3>
            <div class="stats-grid">
                <div class="stat-card">
                    <h4>${executionSummary.total_competitor_posts || 0}</h4>
                    <p>Competitor Posts</p>
                </div>
                <div class="stat-card">
                    <h4>${executionSummary.total_trending_topics || 0}</h4>
                    <p>Trending Topics</p>
                </div>
                <div class="stat-card">
                    <h4>${executionSummary.content_gaps_identified || 0}</h4>
                    <p>Content Gaps</p>
                </div>
                <div class="stat-card">
                    <h4>${executionSummary.high_priority_topics || 0}</h4>
                    <p>High Priority</p>
                </div>
            </div>
        </div>
        
        ${webData.content_gaps ? `
        <div class="research-section-card">
            <h4>🎯 Top Content Opportunities</h4>
            <div class="opportunities-list">
                ${Object.keys(webData.content_gaps).slice(0, 10).map(gap => `
                    <div class="opportunity-item">
                        <strong>${gap}</strong>
                        <span>Opportunity: ${(webData.content_gaps[gap]?.opportunity_score || 0).toFixed(2)}</span>
                    </div>
                `).join('')}
            </div>
        </div>
        ` : ''}
        
        ${topicData.top_priority_topics ? `
        <div class="research-section-card">
            <h4>📈 Top Priority Topics</h4>
            <div class="priority-topics">
                ${topicData.top_priority_topics.slice(0, 5).map(topic => `
                    <div class="priority-topic">
                        <div class="topic-header">
                            <strong>${topic.title || 'No title'}</strong>
                            <span class="priority-badge ${topic.priority_tier || 'medium'}">${(topic.priority_tier || 'MEDIUM').toUpperCase()}</span>
                        </div>
                        <div class="topic-metrics">
                            <span>Score: ${topic.priority_score || 0}</span>
                            <span>Relevance: ${((topic.relevance_score || 0) * 100).toFixed(0)}%</span>
                            <span>Sentiment: ${topic.sentiment || 'NEUTRAL'}</span>
                        </div>
                        <p class="topic-summary">${topic.summary || 'No summary available'}</p>
                    </div>
                `).join('')}
            </div>
        </div>
        ` : ''}
    `;
}

function displayTopicAnalysisResults(data) {
    const container = document.getElementById('topicAnalysisResults');
    
    // Add safety checks
    if (!data) {
        showError('topicAnalysisResults', 'No data received from analysis');
        return;
    }
    
    // Check if we have the expected structure
    const analyzedTopics = data.analyzed_topics || [];
    const contentRecommendations = data.content_recommendations || [];
    const topPriorityTopics = data.top_priority_topics || [];
    const analysisMetadata = data.analysis_metadata || {};
    
    container.innerHTML = `
        <div class="analysis-summary">
            <h3>📊 Topic Analysis Summary</h3>
            <div class="stats-grid">
                <div class="stat-card">
                    <h4>${analysisMetadata.total_topics_analyzed || analyzedTopics.length}</h4>
                    <p>Topics Analyzed</p>
                </div>
                <div class="stat-card">
                    <h4>${analysisMetadata.clusters_identified || 0}</h4>
                    <p>Topic Clusters</p>
                </div>
                <div class="stat-card">
                    <h4>${analysisMetadata.high_priority_topics || topPriorityTopics.length}</h4>
                    <p>High Priority</p>
                </div>
            </div>
        </div>
        
        ${topPriorityTopics.length > 0 ? `
        <div class="research-section-card">
            <h4>🎯 Top Priority Topics</h4>
            <div class="priority-topics">
                ${topPriorityTopics.slice(0, 5).map(topic => `
                    <div class="priority-topic">
                        <div class="topic-header">
                            <strong>${topic.title || 'No title'}</strong>
                            <span class="priority-badge ${topic.priority_tier || 'medium'}">${(topic.priority_tier || 'MEDIUM').toUpperCase()}</span>
                        </div>
                        <div class="topic-metrics">
                            <span>Score: ${topic.priority_score || 0}</span>
                            <span>Relevance: ${((topic.relevance_score || 0) * 100).toFixed(0)}%</span>
                            <span>Sentiment: ${topic.sentiment || 'NEUTRAL'}</span>
                        </div>
                        ${topic.summary ? `<p class="topic-summary">${topic.summary}</p>` : ''}
                    </div>
                `).join('')}
            </div>
        </div>
        ` : '<div class="research-section-card"><p>No priority topics available</p></div>'}
        
        ${contentRecommendations.length > 0 ? `
        <div class="research-section-card">
            <h4>💡 Content Recommendations</h4>
            <div class="recommendations">
                ${contentRecommendations.map(rec => `
                    <div class="recommendation">
                        <h5>${rec.topic_title || 'Untitled'}</h5>
                        <div class="rec-details">
                            <span>Angle: ${rec.content_angle || 'General'}</span>
                            <span>Effort: ${rec.estimated_effort || 'Medium'}</span>
                            <span>Score: ${rec.priority_score || 0}</span>
                        </div>
                        ${rec.target_keywords && rec.target_keywords.length > 0 ? `
                        <div class="keywords">
                            ${rec.target_keywords.map(kw => `<span class="keyword-tag">${kw}</span>`).join('')}
                        </div>
                        ` : ''}
                    </div>
                `).join('')}
            </div>
        </div>
        ` : '<div class="research-section-card"><p>No content recommendations available</p></div>'}
        
        ${analyzedTopics.length > 0 ? `
        <div class="research-section-card">
            <h4>📋 All Analyzed Topics</h4>
            <div class="topics-list">
                ${analyzedTopics.slice(0, 10).map(topic => `
                    <div class="topic-item">
                        <span class="topic-title">${topic.title || 'No title'}</span>
                        <span class="topic-score">${topic.priority_score || 0}</span>
                    </div>
                `).join('')}
            </div>
        </div>
        ` : ''}
    `;
}


























// ==================== SEO Strategy Functions ====================

function showSEOSection(section) {
    // Hide all sections
    document.querySelectorAll('.seo-section').forEach(sec => {
        sec.classList.remove('active');
    });
    
    // Remove active class from all buttons
    document.querySelectorAll('.seo-tab-btn').forEach(btn => {
        btn.classList.remove('active');
    });
    
    // Show selected section
    document.getElementById(`${section}-section`).classList.add('active');
    
    // Activate corresponding button
    const activeBtn = document.querySelector(`.seo-tab-btn[onclick="showSEOSection('${section}')"]`);
    if (activeBtn) {
        activeBtn.classList.add('active');
    }
    
    // Clear results when switching sections
    document.getElementById('keywordResults').innerHTML = '';
    document.getElementById('briefResults').innerHTML = '';
}

async function runQuickSEOAnalysis() {
    showSEOSection('keywords');
    
    const seedTopics = ['skincare routine', 'anti-aging', 'acne treatment'];
    
    showLoading('keywordResults', 'Running comprehensive SEO analysis...');
    
    try {
        // CORRECTED: Direct object, not nested
        const requestData = {
            seed_topics: seedTopics,
            max_keywords_per_topic: 20
        };
        
        console.log('Quick SEO analysis request:', requestData);
        
        const response = await fetch('/api/seo/research-keywords', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(requestData)
        });
        
        if (!response.ok) {
            const errorText = await response.text();
            throw new Error(`HTTP ${response.status}: ${errorText}`);
        }
        
        const result = await response.json();
        
        if (result.status === 'success') {
            displayKeywordResults(result.data);
        } else {
            showError('keywordResults', result.message);
        }
    } catch (error) {
        console.error('Quick SEO analysis error:', error);
        showError('keywordResults', 'SEO analysis failed: ' + error.message);
    }
}

async function researchKeywords() {
    const seedTopicsInput = document.getElementById('seedTopics').value;
    const seedTopics = seedTopicsInput.split(',').map(t => t.trim()).filter(t => t.length > 0);
    const maxKeywords = parseInt(document.getElementById('maxKeywords').value) || 20;
    
    // Validate input
    if (seedTopics.length === 0) {
        alert('Please enter at least one seed topic');
        return;
    }
    
    showLoading('keywordResults', 'Researching keywords...');
    
    try {
        // CORRECTED: The request body should be the data object itself, not nested
        const requestData = {
            seed_topics: seedTopics,
            max_keywords_per_topic: maxKeywords
        };
        
        console.log('Sending request data:', requestData);
        
        const response = await fetch('/api/seo/research-keywords', {
            method: 'POST',
            headers: { 
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(requestData)
        });
        
        // Check if response is OK
        if (!response.ok) {
            const errorText = await response.text();
            throw new Error(`HTTP ${response.status}: ${errorText}`);
        }
        
        const result = await response.json();
        
        if (result.status === 'success') {
            displayKeywordResults(result.data);
        } else {
            showError('keywordResults', result.message);
        }
    } catch (error) {
        console.error('Keyword research error:', error);
        showError('keywordResults', 'Keyword research failed: ' + error.message);
    }
}

async function generateContentBriefs() {
    const maxBriefs = parseInt(document.getElementById('maxBriefs').value) || 5;
    
    showLoading('briefResults', 'Generating content briefs...');
    
    try {
        // CORRECTED: Direct object
        const requestData = {
            max_briefs: maxBriefs
        };
        
        console.log('Brief generation request:', requestData);
        
        const response = await fetch('/api/seo/generate-briefs', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(requestData)
        });
        
        if (!response.ok) {
            const errorText = await response.text();
            throw new Error(`HTTP ${response.status}: ${errorText}`);
        }
        
        const result = await response.json();
        
        if (result.status === 'success') {
            displayBriefResults(result.data);
        } else {
            showError('briefResults', result.message);
        }
    } catch (error) {
        console.error('Brief generation error:', error);
        showError('briefResults', 'Brief generation failed: ' + error.message);
    }
}

async function loadKeywordResearch() {
    showLoading('seo-insights-content', 'Loading keyword research...');
    
    try {
        const response = await fetch('/api/seo/keyword-research');
        const result = await response.json();
        
        if (result.status === 'success') {
            displaySEOInsights(result.data);
        } else {
            showError('seo-insights-content', result.message);
        }
    } catch (error) {
        showError('seo-insights-content', 'Failed to load keyword research: ' + error.message);
    }
}

async function loadContentBriefs() {
    showLoading('seo-insights-content', 'Loading content briefs...');
    
    try {
        const response = await fetch('/api/seo/content-briefs');
        const result = await response.json();
        
        if (result.status === 'success') {
            displayContentBriefs(result.data);
        } else {
            showError('seo-insights-content', result.message);
        }
    } catch (error) {
        showError('seo-insights-content', 'Failed to load content briefs: ' + error.message);
    }
}

function displayKeywordResults(data) {
    const container = document.getElementById('keywordResults');
    
    if (!data) {
        showError('keywordResults', 'No data received from keyword research');
        return;
    }
    
    // Check if we have keywords
    const keywords = data.keywords || [];
    const clusters = data.cluster_analysis || {};
    
    container.innerHTML = `
        <div class="seo-summary">
            <h3>📊 Keyword Research Summary</h3>
            <div class="stats-grid">
                <div class="stat-card">
                    <h4>${data.total_keywords_generated || 0}</h4>
                    <p>Keywords Generated</p>
                </div>
                <div class="stat-card">
                    <h4>${keywords.length}</h4>
                    <p>Top Keywords</p>
                </div>
                <div class="stat-card">
                    <h4>${Object.keys(clusters).length}</h4>
                    <p>Topic Clusters</p>
                </div>
            </div>
        </div>
        
        ${keywords.length > 0 ? `
        <div class="research-section-card">
            <h4>🎯 Top Priority Keywords</h4>
            <div class="keywords-table">
                <table class="content-table">
                    <thead>
                        <tr>
                            <th>Keyword</th>
                            <th>Volume</th>
                            <th>Difficulty</th>
                            <th>Intent</th>
                            <th>Priority Score</th>
                        </tr>
                    </thead>
                    <tbody>
                        ${keywords.slice(0, 10).map(keyword => `
                            <tr>
                                <td><strong>${keyword.keyword || 'N/A'}</strong></td>
                                <td>${(keyword.search_volume || 0).toLocaleString()}</td>
                                <td>
                                    <div class="difficulty-bar">
                                        <div class="difficulty-fill" style="width: ${keyword.difficulty || 0}%"></div>
                                        <span>${keyword.difficulty || 0}/100</span>
                                    </div>
                                </td>
                                <td>
                                    <span class="intent-badge intent-${keyword.intent || 'informational'}">
                                        ${keyword.intent || 'informational'}
                                    </span>
                                </td>
                                <td>
                                    <div class="priority-score">
                                        ${(keyword.priority_score || 0).toFixed(2)}
                                    </div>
                                </td>
                            </tr>
                        `).join('')}
                    </tbody>
                </table>
            </div>
        </div>
        ` : '<div class="research-section-card"><p>No keywords generated</p></div>'}
        
        ${Object.keys(clusters).length > 0 ? `
        <div class="research-section-card">
            <h4>📈 Keyword Clusters</h4>
            <div class="clusters-grid">
                ${Object.values(clusters).slice(0, 6).map(cluster => `
                    <div class="cluster-card">
                        <h5>${cluster.label || 'Unnamed Cluster'}</h5>
                        <p>${cluster.size || 0} keywords</p>
                        <div class="cluster-keywords">
                            ${(cluster.keywords || []).slice(0, 3).map(kw => `
                                <span class="keyword-tag">${kw.keyword || 'N/A'}</span>
                            `).join('')}
                        </div>
                    </div>
                `).join('')}
            </div>
        </div>
        ` : ''}
    `;
}

function displayBriefResults(data) {
    const container = document.getElementById('briefResults');
    
    if (!data || !data.content_briefs) {
        showError('briefResults', 'No brief data received');
        return;
    }
    
    container.innerHTML = `
        <div class="seo-summary">
            <h3>📋 Content Briefs Generated</h3>
            <div class="stats-grid">
                <div class="stat-card">
                    <h4>${data.total_briefs_generated || 0}</h4>
                    <p>Briefs Created</p>
                </div>
                <div class="stat-card">
                    <h4>${data.content_briefs.length}</h4>
                    <p>Ready to Use</p>
                </div>
            </div>
        </div>
        
        <div class="briefs-grid">
            ${data.content_briefs.map(brief => `
                <div class="brief-card">
                    <div class="brief-header">
                        <h4>${brief.target_keyword}</h4>
                        <span class="priority-badge ${brief.priority_score > 0.7 ? 'high' : 'medium'}">
                            Priority: ${(brief.priority_score * 100).toFixed(0)}%
                        </span>
                    </div>
                    
                    <div class="brief-metrics">
                        <div class="metric">
                            <span class="metric-label">Volume</span>
                            <span class="metric-value">${brief.search_volume.toLocaleString()}</span>
                        </div>
                        <div class="metric">
                            <span class="metric-label">Difficulty</span>
                            <span class="metric-value">${brief.difficulty}/100</span>
                        </div>
                        <div class="metric">
                            <span class="metric-label">Word Count</span>
                            <span class="metric-value">${brief.target_word_count}</span>
                        </div>
                    </div>
                    
                    <div class="brief-actions">
                        <button onclick="viewBrief('${brief.brief_id}')" class="btn-secondary btn-small">
                            View Brief
                        </button>
                        <button onclick="downloadBrief('${brief.brief_id}')" class="btn-primary btn-small">
                            Download
                        </button>
                    </div>
                </div>
            `).join('')}
        </div>
    `;
}

function displaySEOInsights(data) {
    const container = document.getElementById('seo-insights-content');
    
    if (!data) {
        container.innerHTML = '<p class="seo-placeholder">No SEO data available. Run keyword research first.</p>';
        return;
    }
    
    container.innerHTML = `
        <div style="width: 100%;">
            <div class="research-section-card">
                <h4>📈 Keyword Research Summary</h4>
                <div class="stats-grid">
                    <div class="stat-card">
                        <h4>${data.total_keywords_generated || 0}</h4>
                        <p>Total Keywords</p>
                    </div>
                    <div class="stat-card">
                        <h4>${data.keywords?.length || 0}</h4>
                        <p>Prioritized</p>
                    </div>
                    <div class="stat-card">
                        <h4>${Object.keys(data.cluster_analysis || {}).length}</h4>
                        <p>Clusters</p>
                    </div>
                </div>
            </div>
            
            ${data.search_intent_breakdown ? `
            <div class="research-section-card">
                <h4>🎯 Search Intent Breakdown</h4>
                <div class="intent-stats">
                    ${Object.entries(data.search_intent_breakdown).map(([intent, count]) => `
                        <div class="intent-item">
                            <span class="intent-badge intent-${intent}">${intent}</span>
                            <span class="intent-count">${count} keywords</span>
                        </div>
                    `).join('')}
                </div>
            </div>
            ` : ''}
        </div>
    `;
}

function displayContentBriefs(data) {
    const container = document.getElementById('seo-insights-content');
    
    if (!data || !data.content_briefs) {
        container.innerHTML = '<p class="seo-placeholder">No content briefs available. Generate briefs first.</p>';
        return;
    }
    
    container.innerHTML = `
        <div style="width: 100%;">
            <div class="research-section-card">
                <h4>📋 Generated Content Briefs</h4>
                <div class="briefs-list">
                    ${data.content_briefs.map(brief => `
                        <div class="brief-item">
                            <div class="brief-item-header">
                                <h5>${brief.target_keyword}</h5>
                                <span class="brief-meta">${brief.target_word_count} words • ${brief.intent} intent</span>
                            </div>
                            <p class="brief-description">${brief.meta_description}</p>
                            <div class="brief-stats">
                                <span>Volume: ${brief.search_volume.toLocaleString()}</span>
                                <span>Difficulty: ${brief.difficulty}/100</span>
                                <span>Priority: ${(brief.priority_score * 100).toFixed(0)}%</span>
                            </div>
                        </div>
                    `).join('')}
                </div>
            </div>
        </div>
    `;
}

async function viewBrief(briefId) {
    try {
        const response = await fetch(`/api/seo/brief/${briefId}`);
        const result = await response.json();
        
        if (result.status === 'success') {
            const brief = result.data;
            const modal = document.getElementById('contentModal');
            const modalTitle = document.getElementById('contentModalTitle');
            const modalBody = document.getElementById('contentModalBody');

            modalTitle.textContent = `Content Brief: ${brief.target_keyword}`;
            modalBody.innerHTML = `
                <div class="brief-preview">
                    <div class="brief-header">
                        <h3>${brief.target_keyword}</h3>
                        <div class="brief-meta">
                            <span>Priority: ${(brief.priority_score * 100).toFixed(0)}%</span>
                            <span>Volume: ${brief.search_volume.toLocaleString()}</span>
                            <span>Difficulty: ${brief.difficulty}/100</span>
                            <span>Intent: ${brief.intent}</span>
                        </div>
                    </div>
                    <div class="brief-content">
                        <h4>Meta Description</h4>
                        <p>${brief.meta_description}</p>
                        
                        <h4>Target Word Count</h4>
                        <p>${brief.target_word_count} words</p>
                        
                        <h4>Content Structure</h4>
                        <div class="headings-preview">
                            <h5>H1: ${brief.headings.h1[0]}</h5>
                            <h6>H2 Headings:</h6>
                            <ul>
                                ${brief.headings.h2.map(h2 => `<li>${h2}</li>`).join('')}
                            </ul>
                        </div>
                    </div>
                </div>
            `;

            modal.classList.add('active');
        }
    } catch (error) {
        alert('Failed to load brief: ' + error.message);
    }
}

async function downloadBrief(briefId) {
    try {
        const response = await fetch(`/api/seo/brief/${briefId}`);
        const result = await response.json();
        
        if (result.status === 'success') {
            const brief = result.data;
            const blob = new Blob([brief.markdown_version], { type: 'text/markdown' });
            const url = URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = `content-brief-${brief.target_keyword.replace(/\s+/g, '-')}.md`;
            document.body.appendChild(a);
            a.click();
            document.body.removeChild(a);
            URL.revokeObjectURL(url);
        }
    } catch (error) {
        alert('Failed to download brief: ' + error.message);
    }
}