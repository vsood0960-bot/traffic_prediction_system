/* ═══════════════════════════════════════════════════════════════
   Urban Traffic Intelligence System — Main JS
   ═══════════════════════════════════════════════════════════════ */

// ── Toast Notifications ──────────────────────────────────────────
function showToast(message, type = 'success') {
    const container = document.getElementById('flash-container');
    if (!container) return;
    const id = 'toast-' + Date.now();
    const icons = { success: 'fa-check-circle', error: 'fa-times-circle', warning: 'fa-exclamation-triangle', info: 'fa-info-circle' };
    const colors = { success: '#10b981', error: '#ef4444', warning: '#f59e0b', info: '#2563eb' };
    const html = `
        <div id="${id}" class="toast show toast-custom ${type} mb-2" role="alert" style="animation:fadeIn 0.3s ease">
            <div class="d-flex align-items-center p-3 gap-3">
                <i class="fas ${icons[type] || icons.info}" style="color:${colors[type]};font-size:1.2rem;"></i>
                <span class="flex-grow-1 fw-500" style="font-size:0.9rem;">${message}</span>
                <button type="button" class="btn-close btn-sm" onclick="document.getElementById('${id}').remove()"></button>
            </div>
        </div>`;
    container.insertAdjacentHTML('beforeend', html);
    setTimeout(() => { const el = document.getElementById(id); if (el) el.remove(); }, 4000);
}

// ── Loading Overlay ──────────────────────────────────────────────
function showLoading(msg = 'Processing...') {
    let el = document.getElementById('loadingOverlay');
    if (!el) {
        el = document.createElement('div');
        el.id = 'loadingOverlay';
        el.className = 'loading-overlay';
        el.innerHTML = `<div class="text-center text-white">
            <div class="spinner-ring mx-auto mb-3"></div>
            <p class="fw-500">${msg}</p>
        </div>`;
        document.body.appendChild(el);
    }
}

function hideLoading() {
    const el = document.getElementById('loadingOverlay');
    if (el) el.remove();
}

// ── API Helper ───────────────────────────────────────────────────
async function apiPost(url, data) {
    const res = await fetch(url, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        credentials: 'include',
        body: JSON.stringify(data)
    });
    return res.json();
}

async function apiGet(url) {
    const res = await fetch(url, { credentials: 'include' });
    return res.json();
}

// ── Badge Helper ─────────────────────────────────────────────────
function congestionBadge(level) {
    const map = { High: 'badge-high', Medium: 'badge-medium', Low: 'badge-low' };
    const icons = { High: 'fa-exclamation-triangle', Medium: 'fa-minus-circle', Low: 'fa-check-circle' };
    return `<span class="badge-congestion ${map[level] || 'badge-low'}">
        <i class="fas ${icons[level] || 'fa-circle'}"></i>${level}
    </span>`;
}

// ── Format Date ──────────────────────────────────────────────────
function fmtDate(str) {
    if (!str) return '—';
    const d = new Date(str);
    return d.toLocaleString('en-IN', { day: '2-digit', month: 'short', year: 'numeric', hour: '2-digit', minute: '2-digit' });
}

// ── Navbar scroll effect ─────────────────────────────────────────
window.addEventListener('scroll', () => {
    const nav = document.getElementById('mainNav');
    if (nav) nav.style.boxShadow = window.scrollY > 20 ? '0 4px 30px rgba(0,0,0,0.4)' : '0 2px 20px rgba(0,0,0,0.3)';
});

// ── Counter Animation ────────────────────────────────────────────
function animateCount(el, target, suffix = '') {
    const start = 0;
    const duration = 1200;
    const step = (timestamp) => {
        if (!start) start = timestamp;
        const progress = Math.min((timestamp - start) / duration, 1);
        el.textContent = Math.floor(progress * target).toLocaleString() + suffix;
        if (progress < 1) requestAnimationFrame(step);
        else el.textContent = target.toLocaleString() + suffix;
    };
    requestAnimationFrame(step);
}

// ── Chart defaults ───────────────────────────────────────────────
if (typeof Chart !== 'undefined') {
    Chart.defaults.font.family = 'Inter, sans-serif';
    Chart.defaults.color = '#64748b';
    Chart.defaults.plugins.legend.position = 'bottom';
    Chart.defaults.plugins.tooltip.backgroundColor = '#0d1b4b';
    Chart.defaults.plugins.tooltip.padding = 12;
    Chart.defaults.plugins.tooltip.cornerRadius = 8;
}

// ── Export helpers ───────────────────────────────────────────────
function exportCSV() { window.location.href = '/api/export-csv'; }
function exportPDF() { window.location.href = '/api/export-pdf'; }
