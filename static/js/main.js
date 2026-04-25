/* =============================================
   TARJIM — Frontend Logic
   ============================================= */

let direction = 'auto';
let lastResult = '';
let debounceTimer;

// ─── INIT ───────────────────────────────────────
document.addEventListener('DOMContentLoaded', () => {
    runBootSequence();

    const src = document.getElementById('source');

    src.addEventListener('input', () => {
        updateCounts();
        detectLang();
        clearTimeout(debounceTimer);
        debounceTimer = setTimeout(detectLang, 200);
    });

    document.getElementById('reference').addEventListener('input', () => {
        if (lastResult) doEvaluate();
    });

    document.addEventListener('keydown', e => {
        if ((e.ctrlKey || e.metaKey) && e.key === 'Enter') {
            e.preventDefault();
            doTranslate();
        }
    });

    updateCounts();
    detectLang();
});

// ─── DIRECTION ──────────────────────────────────
function setDir(d) {
    direction = d;
    document.querySelectorAll('.dir-btn').forEach(b => b.classList.remove('active'));
    const map = { auto: 'btn-auto', ar_to_en: 'btn-ar-en', en_to_ar: 'btn-en-ar' };
    document.getElementById(map[d]).classList.add('active');
    detectLang();
}

// ─── COUNTS & DETECTION ─────────────────────────
function updateCounts() {
    const text = document.getElementById('source').value;
    const words = text.trim() ? text.trim().split(/\s+/).length : 0;
    document.getElementById('char-count').textContent = text.length;
    document.getElementById('word-count').textContent = words;
}

function detectLang() {
    const text = document.getElementById('source').value.trim();
    const langName = document.getElementById('lang-name');
    const tagDot = document.querySelector('.tag-dot');

    if (!text) {
        langName.textContent = 'DETECTING...';
        tagDot.style.background = 'var(--blue-bright)';
        return;
    }

    const arabicChars = (text.match(/[\u0600-\u06FF]/g) || []).length;
    const isArabic = arabicChars > text.length * 0.2;

    if (direction === 'auto') {
        langName.textContent = isArabic ? 'ARABIC DETECTED' : 'ENGLISH DETECTED';
        tagDot.style.background = isArabic ? 'var(--warn)' : 'var(--success)';
    } else if (direction === 'ar_to_en') {
        langName.textContent = 'AR → EN MODE';
        tagDot.style.background = 'var(--warn)';
    } else {
        langName.textContent = 'EN → AR MODE';
        tagDot.style.background = 'var(--success)';
    }
}

// ─── TRANSLATE ──────────────────────────────────
async function doTranslate() {
    const text = document.getElementById('source').value.trim();
    if (!text) {
        showToast('NO INPUT TEXT', 'error');
        return;
    }

    const btn = document.getElementById('translate-btn');
    setStatus('loading', 'TRANSLATING...');
    btn.disabled = true;
    btn.classList.add('loading');

    resetOutput();

    try {
        const res = await fetch('/translate', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ text, direction }),
        });
        const data = await res.json();
        if (data.error) throw new Error(data.error);

        lastResult = data.translation;
        showOutput(data.translation, data.direction);
        showQualityScore(data.auto_score);

        // sentence count
        const sc = document.getElementById('sentence-count');
        document.getElementById('sent-num').textContent = data.sentences || 1;
        sc.style.opacity = '1';

        setStatus('ready', 'DONE');
        showToast('TRANSLATION COMPLETE', 'success');

        // auto-evaluate if reference filled
        const ref = document.getElementById('reference').value.trim();
        if (ref) doEvaluate();

    } catch (e) {
        setStatus('error', 'ERROR');
        showToast(e.message.toUpperCase().slice(0, 40), 'error');
        resetOutput();
    } finally {
        btn.disabled = false;
        btn.classList.remove('loading');
    }
}

// ─── EVALUATE BLEU ──────────────────────────────
async function doEvaluate() {
    const reference = document.getElementById('reference').value.trim();
    if (!reference || !lastResult) return;

    try {
        const res = await fetch('/evaluate', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ reference, hypothesis: lastResult }),
        });
        const data = await res.json();
        if (data.error) return;
        showBleu(data.bleu, data.label);
    } catch (_) { }
}

// ─── OUTPUT HELPERS ─────────────────────────────
function resetOutput() {
    const ph = document.getElementById('output-placeholder');
    const out = document.getElementById('output-text');
    const qBar = document.getElementById('quality-bar');
    const bleu = document.getElementById('bleu-display');
    const sc = document.getElementById('sentence-count');

    ph.style.display = 'flex';
    out.style.display = 'none';
    out.textContent = '';
    qBar.style.display = 'none';
    bleu.style.display = 'none';
    sc.style.opacity = '0';
    lastResult = '';
}

function showOutput(text, dir) {
    const ph = document.getElementById('output-placeholder');
    const out = document.getElementById('output-text');

    ph.style.display = 'none';
    out.style.display = 'block';
    out.textContent = text;

    out.className = 'output-text' + (dir === 'en_to_ar' ? ' rtl' : '');
    document.getElementById('copy-btn').style.display = 'flex';
}

function showQualityScore(q) {
    const bar = document.getElementById('quality-bar');
    const fill = document.getElementById('quality-fill');
    const badge = document.getElementById('quality-badge');
    const score = document.getElementById('quality-score');

    bar.style.display = 'block';
    fill.style.width = q.score + '%';
    score.textContent = q.score + '%';

    const cls = q.label === 'Good' ? 'good' : q.label === 'Acceptable' ? 'ok' : 'poor';
    badge.textContent = q.label.toUpperCase();
    badge.className = 'quality-badge ' + cls;
}

function showBleu(bleuScore, label) {
    const display = document.getElementById('bleu-display');
    const numEl = document.getElementById('bleu-num');
    const labelEl = document.getElementById('bleu-label');
    const ring = document.getElementById('ring-fg');

    display.style.display = 'flex';
    numEl.textContent = bleuScore;
    labelEl.textContent = label.toUpperCase();

    // Ring: circumference = 2π × 34 ≈ 213.6
    const circumference = 213.6;
    const offset = circumference - (bleuScore / 100) * circumference;
    ring.style.strokeDashoffset = offset;

    // Color ring by quality
    const colorMap = {
        'Excellent': 'var(--success)',
        'Good': 'var(--blue-bright)',
        'Acceptable': 'var(--warn)',
        'Poor': 'var(--danger)',
    };
    ring.style.stroke = colorMap[label] || 'var(--blue-bright)';
    ring.style.filter = `drop-shadow(0 0 4px ${colorMap[label] || 'var(--blue-bright)'})`;

    labelEl.style.color = colorMap[label] || 'var(--blue-bright)';
}

// ─── STATUS ─────────────────────────────────────
function setStatus(state, label) {
    const dot = document.getElementById('pulse-dot');
    const lbl = document.getElementById('status-label');
    lbl.textContent = label;

    dot.className = 'pulse-dot';
    if (state === 'loading') dot.classList.add('loading');
    if (state === 'error') dot.classList.add('error');

    if (state === 'ready') {
        setTimeout(() => {
            lbl.textContent = 'READY';
            dot.className = 'pulse-dot';
        }, 3000);
    }
}

// ─── CLEAR / COPY / PASTE ───────────────────────
function clearSource() {
    document.getElementById('source').value = '';
    updateCounts();
    detectLang();
    resetOutput();
    document.getElementById('copy-btn').style.display = 'none';
}

async function copyResult() {
    if (!lastResult) return;
    try {
        await navigator.clipboard.writeText(lastResult);
        showToast('COPIED TO CLIPBOARD', 'success');
    } catch (_) {
        showToast('COPY FAILED', 'error');
    }
}

async function pasteClipboard() {
    try {
        const text = await navigator.clipboard.readText();
        const ta = document.getElementById('source');
        ta.value = text;
        updateCounts();
        detectLang();
        showToast('PASTED', 'success');
    } catch (_) {
        showToast('PASTE DENIED', 'error');
    }
}

// ─── TOAST ──────────────────────────────────────
let toastTimer;
function showToast(msg, type = '') {
    const toast = document.getElementById('toast');
    clearTimeout(toastTimer);

    toast.textContent = msg;
    toast.className = 'toast ' + type;

    // Force reflow
    void toast.offsetWidth;
    toast.classList.add('show');

    toastTimer = setTimeout(() => {
        toast.classList.remove('show');
    }, 2400);
}
// ─── SPLASH SCREEN LOGIC ───────────────────────
async function runBootSequence() {
    const logsContainer = document.getElementById('boot-logs');
    const initBtn = document.getElementById('initialize-btn');
    
    const logs = [
        { text: 'INITIALIZING TARJIM CORE...', type: 'wait' },
        { text: 'CONNECTING TO NEURAL LINK...', type: 'wait' },
        { text: 'AUTHENTICATING GROQ API...', type: 'ok' },
        { text: 'LOADING LLAMA-3.3-70B MODEL...', type: 'wait' },
        { text: 'MODEL READY (VRAM: 48GB)', type: 'ok' },
        { text: 'SYNCHRONIZING DICTIONARIES...', type: 'wait' },
        { text: 'LOCAL STORAGE DETECTED', type: 'ok' },
        { text: 'SYSTEM READY.', type: 'ok' }
    ];

    for (const log of logs) {
        await new Promise(r => setTimeout(r, 200 + Math.random() * 400));
        const entry = document.createElement('div');
        entry.className = 'log-entry';
        
        const status = log.type === 'ok' ? '<span class="status-ok">[OK]</span>' : '<span class="status-wait">[WAIT]</span>';
        entry.innerHTML = `${status} ${log.text}`;
        
        logsContainer.appendChild(entry);
        logsContainer.scrollTop = logsContainer.scrollHeight;
    }

    // Show button
    setTimeout(() => {
        initBtn.style.display = 'block';
    }, 500);
}

document.getElementById('initialize-btn').addEventListener('click', () => {
    const splash = document.getElementById('splash-screen');
    splash.classList.add('hidden');
    document.body.classList.remove('is-booting');
    
    // Play a sound effect or just remove from DOM after transition
    setTimeout(() => {
        splash.remove();
    }, 1000);
});
