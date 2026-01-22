const API_BASE = '/api/v1';

// Toast notification system
function showToast(message, type = 'info') {
    const container = document.getElementById('toast-container');
    const toast = document.createElement('div');
    toast.className = `toast ${type}`;
    toast.textContent = message;
    container.appendChild(toast);
    
    setTimeout(() => {
        toast.style.animation = 'toastSlideIn 0.3s ease-out reverse';
        setTimeout(() => toast.remove(), 300);
    }, 3000);
}

// Tab switching
function showTab(tabName, clickedBtn) {
    // Hide all tabs
    document.querySelectorAll('.tab-content').forEach(tab => {
        tab.classList.remove('active');
    });
    document.querySelectorAll('.tab-btn').forEach(btn => {
        btn.classList.remove('active');
    });

    // Show selected tab
    document.getElementById(`${tabName}-tab`).classList.add('active');
    if (clickedBtn) {
        clickedBtn.classList.add('active');
    } else {
        // Find the button by text content
        document.querySelectorAll('.tab-btn').forEach(btn => {
            if (btn.textContent.includes(tabName === 'generate' ? 'Veri Oluştur' : 
                                         tabName === 'top-papers' ? 'En Çok Atıf' : 'İstatistikler')) {
                btn.classList.add('active');
            }
        });
    }
}

// Generate data
async function generateData() {
    const btn = document.getElementById('generate-btn');
    const status = document.getElementById('generate-status');
    const progress = document.getElementById('generate-progress');
    
    btn.disabled = true;
    btn.textContent = 'Oluşturuluyor...';
    status.className = 'status info';
    status.textContent = 'Veri oluşturuluyor, lütfen bekleyin... Bu işlem 5-10 dakika sürebilir.';
    status.style.display = 'block';
    progress.style.display = 'block';
    
    // Animate progress bar
    let progressWidth = 0;
    const progressFill = document.getElementById('progress-fill');
    const progressText = document.getElementById('progress-text');
    const progressInterval = setInterval(() => {
        progressWidth += 2;
        if (progressWidth > 90) progressWidth = 90;
        progressFill.style.width = progressWidth + '%';
        progressText.textContent = Math.round(progressWidth) + '%';
    }, 1000);

    try {
        const response = await fetch(`${API_BASE}/generate`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            }
        });

        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }

        const data = await response.json();
        
        clearInterval(progressInterval);
        progressFill.style.width = '100%';
        progressText.textContent = '100%';
        
        status.className = 'status success';
        status.innerHTML = `
            <strong>✅ Başarılı!</strong><br>
            ${data.papers_created.toLocaleString()} makale ve ${data.citations_created.toLocaleString()} atıf oluşturuldu.
        `;
        
        showToast(`✅ ${data.papers_created.toLocaleString()} makale ve ${data.citations_created.toLocaleString()} atıf oluşturuldu!`, 'success');
        
        btn.disabled = false;
        btn.innerHTML = '<span class="btn-icon">🚀</span><span>Veri Oluştur</span>';
        
        setTimeout(() => {
            progress.style.display = 'none';
        }, 2000);
    } catch (error) {
        clearInterval(progressInterval);
        status.className = 'status error';
        status.textContent = `❌ Hata: ${error.message}`;
        btn.disabled = false;
        btn.textContent = 'Veri Oluştur';
    }
}

// Get top papers from database (bypass cache)
async function getTopPapersFromDB() {
    const topic = document.getElementById('topic-select').value;
    const limit = document.getElementById('limit-input').value;
    const resultDiv = document.getElementById('top-papers-result');
    const cacheIndicator = document.getElementById('cache-indicator');
    
    resultDiv.innerHTML = '<p>Yükleniyor...</p>';
    cacheIndicator.className = 'cache-indicator';
    cacheIndicator.style.display = 'none';

    try {
        const startTime = performance.now();
        const response = await fetch(`${API_BASE}/top-papers-db?topic=${encodeURIComponent(topic)}&limit=${limit}`);
        const endTime = performance.now();
        const responseTime = (endTime - startTime).toFixed(2);

        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }

        const data = await response.json();
        
        const cacheStatus = response.headers.get('X-Cache-Status') || 'BYPASS';
        const source = response.headers.get('X-Source') || 'DATABASE';
        
        // Display cache indicator
        cacheIndicator.className = 'cache-indicator miss';
        cacheIndicator.innerHTML = `
            <div class="cache-header">
                <strong>🔄 CACHE BYPASS</strong>
                <span class="cache-badge miss-badge">DATABASE</span>
            </div>
            <div class="cache-details">
                <p>💾 Veri PostgreSQL veritabanından geldi (Cache atlandı)</p>
                <p>⚡ Yanıt süresi: <strong>${responseTime}ms</strong></p>
                <p>📊 Kaynak: <strong>${source}</strong></p>
            </div>
        `;
        cacheIndicator.style.display = 'block';

        if (data.length === 0) {
            resultDiv.innerHTML = '<p class="status info">Bu konu için henüz veri yok. Önce "Veri Oluştur" sekmesinden veri oluşturun.</p>';
            return;
        }

        displayTopPapers(data, resultDiv);
    } catch (error) {
        resultDiv.innerHTML = `<p class="status error">❌ Hata: ${error.message}</p>`;
    }
}

// Get top papers (with cache)
async function getTopPapers() {
    const topic = document.getElementById('topic-select').value;
    const limit = document.getElementById('limit-input').value;
    const resultDiv = document.getElementById('top-papers-result');
    const cacheIndicator = document.getElementById('cache-indicator');
    
    resultDiv.innerHTML = '<p>Yükleniyor...</p>';
    cacheIndicator.className = 'cache-indicator';
    cacheIndicator.style.display = 'none';

    try {
        const startTime = performance.now();
        const response = await fetch(`${API_BASE}/top-papers?topic=${encodeURIComponent(topic)}&limit=${limit}`);
        const endTime = performance.now();
        const responseTime = (endTime - startTime).toFixed(2);

        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }

        const data = await response.json();
        
        // Get cache status from response header
        const cacheStatus = response.headers.get('X-Cache-Status') || 'UNKNOWN';
        const cacheKey = response.headers.get('X-Cache-Key') || '';
        
        // Display cache indicator with clear visual distinction
        if (cacheStatus === 'HIT') {
            cacheIndicator.className = 'cache-indicator hit';
            cacheIndicator.innerHTML = `
                <div class="cache-header">
                    <strong>✅ CACHE HIT</strong>
                    <span class="cache-badge hit-badge">REDIS</span>
                </div>
                <div class="cache-details">
                    <p>📦 Veri Redis cache'inden geldi</p>
                    <p>⚡ Yanıt süresi: <strong>${responseTime}ms</strong></p>
                    <p>🔑 Cache Key: <code>${cacheKey}</code></p>
                </div>
            `;
        } else {
            cacheIndicator.className = 'cache-indicator miss';
            cacheIndicator.innerHTML = `
                <div class="cache-header">
                    <strong>⚠️ CACHE MISS</strong>
                    <span class="cache-badge miss-badge">DATABASE</span>
                </div>
                <div class="cache-details">
                    <p>💾 Veri PostgreSQL veritabanından geldi</p>
                    <p>⚡ Yanıt süresi: <strong>${responseTime}ms</strong></p>
                    <p>🔑 Cache Key: <code>${cacheKey}</code></p>
                    <p>💡 <em>Sonraki sorgu cache'den gelecek (60 saniye TTL)</em></p>
                </div>
            `;
        }
        cacheIndicator.style.display = 'block';

        if (data.length === 0) {
            resultDiv.innerHTML = '<p class="status info">Bu konu için henüz veri yok. Önce "Veri Oluştur" sekmesinden veri oluşturun.</p>';
            return;
        }

        displayTopPapers(data, resultDiv);
    } catch (error) {
        resultDiv.innerHTML = `<p class="status error">❌ Hata: ${error.message}</p>`;
    }
}

// Load statistics
async function loadStats() {
    const resultDiv = document.getElementById('stats-result');
    resultDiv.innerHTML = '<p>📊 İstatistikler yükleniyor...</p>';

    try {
        const response = await fetch(`${API_BASE}/stats`);
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }

        const data = await response.json();

        let html = `
            <div class="stats-grid">
                <div class="stat-card">
                    <div class="stat-icon">📄</div>
                    <div class="stat-value">${data.total_papers.toLocaleString()}</div>
                    <div class="stat-label">Toplam Makale</div>
                </div>
                <div class="stat-card">
                    <div class="stat-icon">🔗</div>
                    <div class="stat-value">${data.total_citations.toLocaleString()}</div>
                    <div class="stat-label">Toplam Atıf</div>
                </div>
                <div class="stat-card">
                    <div class="stat-icon">📊</div>
                    <div class="stat-value">${data.average_citations_per_paper}</div>
                    <div class="stat-label">Ortalama Atıf/Makale</div>
                </div>
            </div>
        `;

        // Topic distribution with chart
        if (data.topic_distribution && data.topic_distribution.length > 0) {
            html += `
                <div class="card" style="margin-top: 24px;">
                    <h3 style="margin-bottom: 20px;">📚 Konu Dağılımı</h3>
                    <div style="margin-bottom: 20px;">
                        <canvas id="topicChart" height="80"></canvas>
                    </div>
                    <div class="table-container">
                        <table>
                            <thead>
                                <tr>
                                    <th>Konu</th>
                                    <th>Makale Sayısı</th>
                                    <th>Yüzde</th>
                                </tr>
                            </thead>
                            <tbody>
            `;
            
            const total = data.topic_distribution.reduce((sum, t) => sum + t.count, 0);
            data.topic_distribution.forEach(topic => {
                const percentage = total > 0 ? ((topic.count / total) * 100).toFixed(1) : 0;
                html += `
                    <tr>
                        <td><span class="badge badge-primary">${topic.topic}</span></td>
                        <td><strong>${topic.count.toLocaleString()}</strong></td>
                        <td>${percentage}%</td>
                    </tr>
                `;
            });
            
            html += `
                            </tbody>
                        </table>
                    </div>
                </div>
            `;
        }

        // Most cited topics with chart
        if (data.most_cited_topics && data.most_cited_topics.length > 0) {
            html += `
                <div class="card" style="margin-top: 24px;">
                    <h3 style="margin-bottom: 20px;">🏆 En Çok Atıf Alan Konular</h3>
                    <div style="margin-bottom: 20px;">
                        <canvas id="citationsChart" height="80"></canvas>
                    </div>
                    <div class="table-container">
                        <table>
                            <thead>
                                <tr>
                                    <th>Konu</th>
                                    <th>Toplam Atıf Sayısı</th>
                                </tr>
                            </thead>
                            <tbody>
            `;
            
            data.most_cited_topics.forEach(topic => {
                html += `
                    <tr>
                        <td><span class="badge badge-primary">${topic.topic}</span></td>
                        <td><strong>${topic.citation_count.toLocaleString()}</strong></td>
                    </tr>
                `;
            });
            
            html += `
                            </tbody>
                        </table>
                    </div>
                </div>
            `;
        }

        // Year distribution (last 10 years)
        if (data.year_distribution && data.year_distribution.length > 0) {
            const recentYears = data.year_distribution.slice(0, 10);
            html += `
                <div class="card" style="margin-top: 20px;">
                    <h3>📅 Yıl Bazlı Dağılım (Son 10 Yıl)</h3>
                    <div class="table-container">
                        <table>
                            <thead>
                                <tr>
                                    <th>Yıl</th>
                                    <th>Makale Sayısı</th>
                                </tr>
                            </thead>
                            <tbody>
            `;
            
            recentYears.forEach(year => {
                html += `
                    <tr>
                        <td><strong>${year.year}</strong></td>
                        <td>${year.count.toLocaleString()}</td>
                    </tr>
                `;
            });
            
            html += `
                            </tbody>
                        </table>
                    </div>
                </div>
            `;
        }

        resultDiv.innerHTML = html;
        
        // Create charts after HTML is inserted
        if (data.topic_distribution && data.topic_distribution.length > 0) {
            createTopicChart(data.topic_distribution);
        }
        
        if (data.most_cited_topics && data.most_cited_topics.length > 0) {
            createCitationsChart(data.most_cited_topics);
        }
    } catch (error) {
        resultDiv.innerHTML = `<p class="status error">❌ Hata: ${error.message}</p>`;
    }
}

// Display top papers in table
function displayTopPapers(data, resultDiv) {
    let html = `
        <div class="table-container">
            <table>
                <thead>
                    <tr>
                        <th>#</th>
                        <th>Başlık</th>
                        <th>Konu</th>
                        <th>Yıl</th>
                        <th>Atıf Sayısı</th>
                        <th>Büyüme Oranı (%)</th>
                    </tr>
                </thead>
                <tbody>
    `;

    data.forEach((paper, index) => {
        html += `
            <tr>
                <td>${index + 1}</td>
                <td>${paper.title}</td>
                <td><span class="badge badge-primary">${paper.topic}</span></td>
                <td>${paper.published_year}</td>
                <td><strong>${paper.citation_count.toLocaleString()}</strong></td>
                <td><span class="badge badge-success">${paper.citation_growth_rate}%</span></td>
            </tr>
        `;
    });

    html += `
                </tbody>
            </table>
        </div>
        <p style="margin-top: 15px; color: #666; font-size: 0.9em;">
            Toplam ${data.length} makale gösteriliyor
        </p>
    `;

    resultDiv.innerHTML = html;
}

// Create topic distribution chart
function createTopicChart(topicData) {
    const ctx = document.getElementById('topicChart');
    if (!ctx) return;
    
    new Chart(ctx, {
        type: 'doughnut',
        data: {
            labels: topicData.map(t => t.topic),
            datasets: [{
                data: topicData.map(t => t.count),
                backgroundColor: [
                    '#667eea', '#764ba2', '#f093fb', '#4facfe',
                    '#00f2fe', '#43e97b', '#fa709a', '#fee140',
                    '#30cfd0', '#330867'
                ],
                borderWidth: 2,
                borderColor: '#fff'
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: true,
            plugins: {
                legend: {
                    position: 'right',
                    labels: {
                        padding: 15,
                        font: {
                            size: 12
                        }
                    }
                }
            }
        }
    });
}

// Create citations chart
function createCitationsChart(citationsData) {
    const ctx = document.getElementById('citationsChart');
    if (!ctx) return;
    
    new Chart(ctx, {
        type: 'bar',
        data: {
            labels: citationsData.map(t => t.topic),
            datasets: [{
                label: 'Atıf Sayısı',
                data: citationsData.map(t => t.citation_count),
                backgroundColor: 'rgba(102, 126, 234, 0.8)',
                borderColor: '#667eea',
                borderWidth: 2,
                borderRadius: 8
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: true,
            plugins: {
                legend: {
                    display: false
                }
            },
            scales: {
                y: {
                    beginAtZero: true,
                    ticks: {
                        callback: function(value) {
                            return value.toLocaleString();
                        }
                    }
                }
            }
        }
    });
}

// Auto-load stats on page load
window.addEventListener('load', () => {
    loadStats();
});

