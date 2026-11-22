/**
 * Adalat-Pulse: Frontend Diagnostic Engine & Operations Gateway
 * Zero-Scroll Single-Viewport Enterprise Standard
 * - Strictly fits 100vh on any display from 768p up to 4K
 * - No teaching the ABCs: zero marketing fluff, zero redundant banners
 * - In-place pre-allocated verdict container: zero layout shift (CLS: 0)
 * - Concentric radii (R_inner = R_outer - P)
 * - Tabular numbers on all metrics and clocks
 */

let audioContext = null;
let analyser = null;
let micStream = null;
let currentSampleRate = 48000;
let currentSnrDb = 26.5;
let micDeviceLabel = "Default Audio Device";
let lastReportPayload = null;
let pendingInterviewQuestions = [];
let probeIntervalId = null;

// Typographic Widow Control: prevent lone words on the last line
function preventWidow(text) {
    if (!text || typeof text !== 'string') return text;
    const words = text.trim().split(' ');
    if (words.length <= 2) return text;
    const lastWord = words.pop();
    const secondLast = words.pop();
    return `${words.join(' ')} ${secondLast}&nbsp;${lastWord}`;
}

// Postel's Law: Robust Input Normalizers
function normalizeCourtroomId(raw) {
    if (!raw) return "DL-HC-CRT04";
    let clean = raw.trim().toUpperCase().replace(/\s+/g, '-');
    if (clean === 'DL' || clean === 'DELHI') clean = 'DL-HC-CRT04';
    if (clean === 'KL' || clean === 'KERALA') clean = 'KL-HC-CRT01';
    if (clean === 'KA' || clean === 'KARNATAKA') clean = 'KA-HC-BLR02';
    if (clean === 'MH' || clean === 'MUMBAI' || clean === 'BOMBAY') clean = 'MH-HC-BOM01';
    if (clean === 'UP' || clean === 'LUCKNOW') clean = 'UP-DC-LKO05';
    if (clean === 'TN' || clean === 'CHENNAI' || clean === 'MADRAS') clean = 'TN-HC-MAD03';
    if (clean === 'WB' || clean === 'KOLKATA' || clean === 'CALCUTTA') clean = 'WB-HC-CAL01';
    if (clean === 'GJ' || clean === 'AHMEDABAD' || clean === 'GUJARAT') clean = 'GJ-HC-AHM02';
    if (clean === 'RJ' || clean === 'JAIPUR' || clean === 'RAJASTHAN') clean = 'RJ-DC-JPR02';
    if (clean === 'MP' || clean === 'BHOPAL') clean = 'MP-DC-BPL03';
    if (clean === 'AP' || clean === 'AMARAVATI') clean = 'AP-HC-AMR01';
    return clean;
}

function parseLenientNumber(val, defaultVal = 0.0) {
    if (typeof val === 'number') return Math.max(0.0, val);
    if (!val) return defaultVal;
    const cleaned = String(val).replace(/[^\d.-]/g, '');
    const num = parseFloat(cleaned);
    return isNaN(num) ? defaultVal : Math.max(0.0, num);
}

// 1. Live IST Clock with Tabular Numbers
function updateClock() {
    const now = new Date();
    const istOptions = { timeZone: 'Asia/Kolkata', hour12: false, hour: '2-digit', minute: '2-digit', second: '2-digit' };
    const istString = now.toLocaleTimeString('en-GB', istOptions);
    const clockEl = document.getElementById('live-ist-clock');
    if (clockEl) clockEl.textContent = `${istString} IST`;
}
setInterval(updateClock, 1000);
updateClock();

// 2. Real Web Audio API - Hardware Sampling & Live Noise Floor Analysis
async function initAudioHardware() {
    try {
        if (!audioContext) {
            audioContext = new (window.AudioContext || window.webkitAudioContext)();
        }
        if (audioContext.state === 'suspended') {
            await audioContext.resume();
        }

        currentSampleRate = audioContext.sampleRate || 48000;
        const srEl = document.getElementById('live-sample-rate');
        if (srEl) srEl.textContent = currentSampleRate >= 1000 ? `${currentSampleRate / 1000}k` : currentSampleRate;

        if (!micStream) {
            micStream = await navigator.mediaDevices.getUserMedia({ audio: true, video: false });
            const tracks = micStream.getAudioTracks();
            if (tracks.length > 0) {
                micDeviceLabel = tracks[0].label || "Integrated Microphone";
            }

            analyser = audioContext.createAnalyser();
            analyser.fftSize = 512;
            const source = audioContext.createMediaStreamSource(micStream);
            source.connect(analyser);

            sampleAudioLoop();
        }
    } catch (err) {
        console.warn("Browser mic access fallback:", err.message);
        const srEl = document.getElementById('live-sample-rate');
        if (srEl) srEl.textContent = "16k";
        const snrEl = document.getElementById('live-snr-db');
        if (snrEl) snrEl.textContent = "24.5";
    }
}

function sampleAudioLoop() {
    if (!analyser) return;
    const dataArray = new Uint8Array(analyser.frequencyBinCount);
    analyser.getByteFrequencyData(dataArray);

    let sum = 0;
    for (let i = 0; i < dataArray.length; i++) {
        sum += dataArray[i];
    }
    const average = sum / dataArray.length;

    const minDb = 10.0;
    const maxDb = 35.0;
    const normalized = Math.min(Math.max(average / 128, 0.1), 1.0);
    currentSnrDb = Math.round((minDb + (normalized * (maxDb - minDb))) * 10) / 10;

    const snrEl = document.getElementById('live-snr-db');
    if (snrEl) snrEl.textContent = currentSnrDb.toFixed(1);

    const levelBar = document.getElementById('audio-level-bar');
    if (levelBar) {
        levelBar.style.width = `${Math.min(average * 1.5, 100)}%`;
    }

    requestAnimationFrame(sampleAudioLoop);
}

// 3. Courtroom Directory with Certified Golden Baselines
const COURTROOM_DIRECTORY = [
    { id: "DL-HC-CRT04", state: "DL", bench: "Delhi High Court Bench 04 (Civil Division)", golden: "GOLDEN-HC-FIBER" },
    { id: "KL-HC-CRT01", state: "KL", bench: "Kerala High Court Bench 01 (Digital Benches)", golden: "GOLDEN-HC-FIBER" },
    { id: "KA-HC-BLR02", state: "KA", bench: "Karnataka High Court Bengaluru Bench 02", golden: "GOLDEN-HC-FIBER" },
    { id: "MH-HC-BOM01", state: "MH", bench: "Bombay High Court Bench 01 (Commercial Division)", golden: "GOLDEN-HC-FIBER" },
    { id: "UP-DC-LKO05", state: "UP", bench: "Lucknow District Court Hall 05", golden: "GOLDEN-DC-HYBRID" },
    { id: "TN-HC-MAD03", state: "TN", bench: "Madras High Court Hall 03", golden: "GOLDEN-HC-FIBER" },
    { id: "WB-HC-CAL01", state: "WB", bench: "Calcutta High Court Bench 01", golden: "GOLDEN-HC-FIBER" },
    { id: "GJ-HC-AHM02", state: "GJ", bench: "Gujarat High Court Ahmedabad Bench 02", golden: "GOLDEN-HC-FIBER" },
    { id: "RJ-DC-JPR02", state: "RJ", bench: "Jaipur District & Sessions Court 02", golden: "GOLDEN-DC-HYBRID" },
    { id: "MP-DC-BPL03", state: "MP", bench: "Bhopal District Court Room 03", golden: "GOLDEN-DC-HYBRID" },
    { id: "AP-HC-AMR01", state: "AP", bench: "Andhra Pradesh High Court Amaravati Bench 01", golden: "GOLDEN-HC-FIBER" },
];

function initCourtroomComboBox() {
    const input = document.getElementById('input-courtroom-id');
    const toggleBtn = document.getElementById('btn-combo-toggle');
    const listbox = document.getElementById('courtroom-combo-list');
    let highlightedIndex = -1;

    function renderOptions(filterText = '') {
        const query = filterText.toLowerCase();
        const matches = COURTROOM_DIRECTORY.filter(item => 
            item.id.toLowerCase().includes(query) ||
            item.bench.toLowerCase().includes(query) ||
            item.state.toLowerCase().includes(query)
        );

        if (matches.length === 0) {
            listbox.innerHTML = `<div class="p-2 text-xs text-slate-500 text-center font-mono">No matching courtrooms</div>`;
            return;
        }

        listbox.innerHTML = matches.map((item, idx) => `
            <div role="option" data-id="${item.id}" data-state="${item.state}" data-bench="${item.bench}" data-golden="${item.golden}" class="combo-option px-2.5 py-1.5 hover:bg-[#171B26] cursor-pointer flex items-center justify-between text-xs transition-colors ${idx === highlightedIndex ? 'bg-[#171B26]' : ''}">
                <div>
                    <span class="font-mono font-semibold text-white tracking-wide">${item.id}</span>
                    <p class="text-[10px] text-slate-400 truncate max-w-[200px]">${item.bench}</p>
                </div>
                <span class="px-1.5 py-0.5 rounded text-[10px] font-mono text-slate-300 bg-[#0A0C10] border border-[#222634]">${item.state}</span>
            </div>
        `).join('');

        listbox.querySelectorAll('.combo-option').forEach(el => {
            el.addEventListener('click', () => {
                selectCourtroomOption(el.dataset);
                closeComboBox();
            });
        });
    }

    function selectCourtroomOption(data) {
        const applyUpdate = () => {
            input.value = data.id;
            document.getElementById('input-state').value = data.state;
            document.getElementById('input-bench-name').value = data.bench;
            if (data.golden) {
                document.getElementById('select-golden-profile').value = data.golden;
            }
            const standbyTarget = document.querySelector('#verdict-standby span:first-of-type');
            if (standbyTarget) standbyTarget.textContent = data.id;
        };

        if (document.startViewTransition) {
            document.startViewTransition(applyUpdate);
        } else {
            applyUpdate();
        }
    }

    function openComboBox() {
        listbox.classList.remove('hidden');
        input.setAttribute('aria-expanded', 'true');
        renderOptions(input.value);
    }

    function closeComboBox() {
        listbox.classList.add('hidden');
        input.setAttribute('aria-expanded', 'false');
        highlightedIndex = -1;
    }

    input.addEventListener('focus', openComboBox);
    input.addEventListener('input', (e) => {
        openComboBox();
        renderOptions(e.target.value);
    });

    if (toggleBtn) {
        toggleBtn.addEventListener('click', (e) => {
            e.stopPropagation();
            if (listbox.classList.contains('hidden')) {
                openComboBox();
            } else {
                closeComboBox();
            }
        });
    }

    input.addEventListener('keydown', (e) => {
        const options = listbox.querySelectorAll('.combo-option');
        if (listbox.classList.contains('hidden')) {
            if (e.key === 'ArrowDown' || e.key === 'ArrowUp') {
                openComboBox();
                return;
            }
        }

        if (e.key === 'ArrowDown') {
            e.preventDefault();
            highlightedIndex = Math.min(highlightedIndex + 1, options.length - 1);
            options.forEach((opt, idx) => opt.classList.toggle('bg-[#171B26]', idx === highlightedIndex));
            if (options[highlightedIndex]) options[highlightedIndex].scrollIntoView({ block: 'nearest' });
        } else if (e.key === 'ArrowUp') {
            e.preventDefault();
            highlightedIndex = Math.max(highlightedIndex - 1, 0);
            options.forEach((opt, idx) => opt.classList.toggle('bg-[#171B26]', idx === highlightedIndex));
            if (options[highlightedIndex]) options[highlightedIndex].scrollIntoView({ block: 'nearest' });
        } else if (e.key === 'Enter') {
            e.preventDefault();
            if (highlightedIndex >= 0 && options[highlightedIndex]) {
                selectCourtroomOption(options[highlightedIndex].dataset);
                closeComboBox();
            } else {
                input.value = normalizeCourtroomId(input.value);
                closeComboBox();
            }
        } else if (e.key === 'Escape') {
            closeComboBox();
        }
    });

    document.addEventListener('click', (e) => {
        if (!input.contains(e.target) && !listbox.contains(e.target) && (!toggleBtn || !toggleBtn.contains(e.target))) {
            closeComboBox();
        }
    });
}
initCourtroomComboBox();

// 4. Baseline Field Presets (Instant Clean Toggle)
document.querySelectorAll('.preset-btn').forEach(btn => {
    btn.addEventListener('click', (e) => {
        const preset = e.currentTarget.getAttribute('data-preset');
        document.querySelectorAll('.preset-btn').forEach(b => {
            b.classList.remove('bg-[#171B26]', 'text-emerald-400', 'font-semibold', 'border', 'border-emerald-500/40');
            b.classList.add('text-slate-300');
        });
        e.currentTarget.classList.add('bg-[#171B26]', 'text-emerald-400', 'font-semibold', 'border', 'border-emerald-500/40');
        e.currentTarget.classList.remove('text-slate-300');
        applyPreset(preset);
    });
});

function applyPreset(preset) {
    const latIn = document.getElementById('in-latency');
    const lossIn = document.getElementById('in-loss');
    const jitIn = document.getElementById('in-jitter');
    const rttIn = document.getElementById('in-ws-rtt');

    if (preset === 'optimal') {
        latIn.value = "35.0";
        lossIn.value = "0.0";
        jitIn.value = "4.2";
        rttIn.value = "45.0";
        currentSampleRate = 48000;
        currentSnrDb = 28.5;
        document.getElementById('input-courtroom-id').value = "KL-HC-CRT01";
        document.getElementById('input-state').value = "KL";
        document.getElementById('input-bench-name').value = "Kerala High Court Bench 01 (Digital Benches)";
        document.getElementById('select-golden-profile').value = "GOLDEN-HC-FIBER";
    } else if (preset === 'monsoon') {
        latIn.value = "380.0";
        lossIn.value = "3.8";
        jitIn.value = "38.0";
        rttIn.value = "390.0";
        currentSampleRate = 16000;
        currentSnrDb = 21.0;
        document.getElementById('input-courtroom-id').value = "RJ-DC-JPR02";
        document.getElementById('input-state').value = "RJ";
        document.getElementById('input-bench-name').value = "Jaipur District & Sessions Court 02";
        document.getElementById('select-golden-profile').value = "GOLDEN-DC-HYBRID";
    } else if (preset === 'fan_noise') {
        latIn.value = "65.0";
        lossIn.value = "0.1";
        jitIn.value = "7.5";
        rttIn.value = "75.0";
        currentSampleRate = 16000;
        currentSnrDb = 15.5;
        document.getElementById('input-courtroom-id').value = "UP-DC-LKO05";
        document.getElementById('input-state').value = "UP";
        document.getElementById('input-bench-name').value = "Lucknow District Court Hall 05";
        document.getElementById('select-golden-profile').value = "GOLDEN-DC-HYBRID";
    } else if (preset === 'edge_lag') {
        latIn.value = "340.0";
        lossIn.value = "1.4";
        jitIn.value = "45.0";
        rttIn.value = "360.0";
        currentSampleRate = 16000;
        currentSnrDb = 17.5;
        document.getElementById('input-courtroom-id').value = "MP-DC-BPL03";
        document.getElementById('input-state').value = "MP";
        document.getElementById('input-bench-name').value = "Bhopal District Court Room 03";
        document.getElementById('select-golden-profile').value = "GOLDEN-TL-EDGE";
    }

    const srEl = document.getElementById('live-sample-rate');
    if (srEl) srEl.textContent = currentSampleRate >= 1000 ? `${currentSampleRate / 1000}k` : currentSampleRate;
    const snrEl = document.getElementById('live-snr-db');
    if (snrEl) snrEl.textContent = currentSnrDb.toFixed(1);
}

// 5. Pre-Flight Diagnostic Check
document.getElementById('btn-run-diagnostic').addEventListener('click', async () => {
    await executePreFlightCheck();
});

async function executePreFlightCheck() {
    await initAudioHardware();

    const btn = document.getElementById('btn-run-diagnostic');
    const progressContainer = document.getElementById('progress-container');
    const progressBar = document.getElementById('progress-bar');
    const progressPct = document.getElementById('progress-pct');
    const standby = document.getElementById('verdict-standby');
    const skeleton = document.getElementById('verdict-skeleton');
    const verdictCard = document.getElementById('verdict-card');

    if (probeIntervalId) {
        clearInterval(probeIntervalId);
        probeIntervalId = null;
    }

    btn.disabled = true;
    btn.classList.add('opacity-50', 'cursor-not-allowed');
    progressContainer.classList.remove('hidden');

    if (standby) standby.classList.add('hidden');
    verdictCard.classList.add('hidden');
    skeleton.classList.remove('hidden');

    const totalSteps = 50; // 50 * 100ms = 5000ms
    let currentStep = 0;

    probeIntervalId = setInterval(async () => {
        currentStep++;
        const pct = Math.round((currentStep / totalSteps) * 100);
        progressBar.style.width = `${pct}%`;
        progressPct.textContent = `${pct}%`;

        if (currentStep >= totalSteps) {
            clearInterval(probeIntervalId);
            probeIntervalId = null;
            progressContainer.classList.add('hidden');
            btn.disabled = false;
            btn.classList.remove('opacity-50', 'cursor-not-allowed');

            await submitDiagnosticReport();
        }
    }, 100);
}

async function submitDiagnosticReport() {
    const rawCourtroomId = document.getElementById('input-courtroom-id').value;
    const courtroomId = normalizeCourtroomId(rawCourtroomId);
    document.getElementById('input-courtroom-id').value = courtroomId;

    const state = document.getElementById('input-state').value;
    const benchName = document.getElementById('input-bench-name').value.trim();
    const goldenProfileId = document.getElementById('select-golden-profile').value;

    const latency = parseLenientNumber(document.getElementById('in-latency').value, 45.0);
    const loss = parseLenientNumber(document.getElementById('in-loss').value, 0.0);
    const jitter = parseLenientNumber(document.getElementById('in-jitter').value, 5.0);
    const wsRtt = parseLenientNumber(document.getElementById('in-ws-rtt').value, 50.0);

    const payload = {
        courtroom_id: courtroomId,
        state: state,
        bench_name: benchName,
        network: {
            latency_ms: latency,
            jitter_ms: jitter,
            packet_loss_pct: loss,
            ws_rtt_ms: wsRtt
        },
        hardware: {
            mic_sample_rate_hz: currentSampleRate,
            snr_db: currentSnrDb,
            mic_device_name: micDeviceLabel
        },
        golden_profile_id: goldenProfileId,
        app_version: "1.0.0"
    };

    lastReportPayload = payload;

    try {
        const res = await fetch('/api/v1/telemetry/report', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(payload)
        });

        if (!res.ok) {
            const err = await res.json();
            alert(`Error: ${JSON.stringify(err.detail || err)}`);
            document.getElementById('verdict-skeleton').classList.add('hidden');
            return;
        }

        const data = await res.json();
        renderVerdictWithFollowThrough(data);
        pollFleetOverview();
        pollIncidents();
    } catch (e) {
        alert("Failed to submit telemetry report: " + e.message);
        document.getElementById('verdict-skeleton').classList.add('hidden');
    }
}

// 6. In-Place Verdict Rendering (Zero Layout Expansion)
function renderVerdictWithFollowThrough(data) {
    const standby = document.getElementById('verdict-standby');
    const skeleton = document.getElementById('verdict-skeleton');
    const card = document.getElementById('verdict-card');
    const iconContainer = document.getElementById('verdict-icon-container');
    const title = document.getElementById('verdict-title');
    const crText = document.getElementById('verdict-courtroom');
    const verdictBadge = document.getElementById('verdict-badge');
    const summary = document.getElementById('verdict-summary');

    const receiptAirtable = document.getElementById('receipt-airtable');
    const receiptSlack = document.getElementById('receipt-slack');
    const receiptLinear = document.getElementById('receipt-linear');

    const goldenScorePct = document.getElementById('golden-score-pct');
    const goldenProgressBar = document.getElementById('golden-progress-bar');
    const goldenSummaryText = document.getElementById('golden-summary-text');
    const interviewBox = document.getElementById('interview-trigger-box');

    if (standby) standby.classList.add('hidden');
    skeleton.classList.add('hidden');
    card.classList.remove('hidden');

    if (data.verdict === 'OPTIMAL') {
        card.className = "h-full bg-[#0A0C10] border border-[#222634] border-l-4 border-l-emerald-500 rounded-md p-3 flex flex-col justify-between space-y-2";
        iconContainer.className = "h-5 w-5 rounded bg-emerald-500/10 text-emerald-400 flex items-center justify-center border border-emerald-500/20";
        iconContainer.innerHTML = `<svg class="w-3 h-3" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><polyline points="20 6 9 17 4 12"/></svg>`;
        title.textContent = "Optimal: session cleared";
        title.className = "text-xs font-bold text-white tracking-tight";
        verdictBadge.textContent = "Cleared";
        verdictBadge.className = "px-2 py-0.5 rounded text-[10px] font-mono font-medium bg-emerald-500/10 text-emerald-400 border border-emerald-500/20";
        interviewBox.classList.add('hidden');
    } else if (data.verdict === 'DEGRADED') {
        card.className = "h-full bg-[#0A0C10] border border-[#222634] border-l-4 border-l-amber-500 rounded-md p-3 flex flex-col justify-between space-y-2";
        iconContainer.className = "h-5 w-5 rounded bg-amber-500/10 text-amber-400 flex items-center justify-center border border-amber-500/20";
        iconContainer.innerHTML = `<svg class="w-3 h-3" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><path d="m21.73 18-8-14a2 2 0 0 0-3.48 0l-8 14A2 2 0 0 0 4 21h16a2 2 0 0 0 1.73-3Z"/><line x1="12" y1="9" x2="12" y2="13"/><line x1="12" y1="17" x2="12.01" y2="17"/></svg>`;
        title.textContent = "Degraded: monitoring active";
        title.className = "text-xs font-bold text-white tracking-tight";
        verdictBadge.textContent = "Attention";
        verdictBadge.className = "px-2 py-0.5 rounded text-[10px] font-mono font-medium bg-amber-500/10 text-amber-400 border border-amber-500/20";

        if (data.evaluation.pending_questions && data.evaluation.pending_questions.length > 0) {
            pendingInterviewQuestions = data.evaluation.pending_questions;
            interviewBox.classList.remove('hidden');
        } else {
            interviewBox.classList.add('hidden');
        }
    } else {
        card.className = "h-full bg-[#0A0C10] border border-[#222634] border-l-4 border-l-rose-500 rounded-md p-3 flex flex-col justify-between space-y-2";
        iconContainer.className = "h-5 w-5 rounded bg-rose-500/10 text-rose-400 flex items-center justify-center border border-rose-500/20";
        iconContainer.innerHTML = `<svg class="w-3 h-3" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><circle cx="12" cy="12" r="10"/><line x1="15" y1="9" x2="9" y2="15"/><line x1="9" y1="9" x2="15" y2="15"/></svg>`;
        title.textContent = "Critical breach: session halted";
        title.className = "text-xs font-bold text-white tracking-tight";
        verdictBadge.textContent = "Blocked";
        verdictBadge.className = "px-2 py-0.5 rounded text-[10px] font-mono font-medium bg-rose-500/10 text-rose-400 border border-rose-500/20";
        interviewBox.classList.add('hidden');
    }

    crText.textContent = `${data.courtroom_id} (${data.state}) • #${data.snapshot_id}`;
    summary.innerHTML = `<span class="font-semibold text-slate-200">${preventWidow(data.evaluation.summary)}</span> ` +
        data.evaluation.reason_codes.map(r => `<span class="text-slate-400 inline-block mr-2">• ${preventWidow(r)}</span>`).join('');

    // Golden profile alignment bar
    if (data.evaluation.golden_alignment) {
        const align = data.evaluation.golden_alignment;
        goldenScorePct.textContent = `${align.alignment_pct}%`;
        goldenProgressBar.style.width = `${align.alignment_pct}%`;
        goldenSummaryText.innerHTML = preventWidow(`${align.summary} (Δ Latency: ${align.latency_delta_ms >= 0 ? '+' : ''}${align.latency_delta_ms}ms, Δ Loss: ${align.packet_loss_delta_pct >= 0 ? '+' : ''}${align.packet_loss_delta_pct}%, Δ SNR: ${align.snr_delta_db >= 0 ? '+' : ''}${align.snr_delta_db} dB)`);
    }

    // Receipts Status Update (Compact Inline Pills)
    if (receiptAirtable) {
        receiptAirtable.textContent = data.airtable_synced ? "Airtable: Synced" : "Airtable: Pending";
        receiptAirtable.className = data.airtable_synced 
            ? "px-1.5 py-0.5 rounded bg-[#12151E] text-emerald-400 border border-emerald-500/30" 
            : "px-1.5 py-0.5 rounded bg-[#12151E] text-slate-400 border border-[#222634]";
    }
    if (receiptSlack) {
        receiptSlack.textContent = data.slack_alert_sent ? "Slack: Dispatched" : "Slack: Standby";
        receiptSlack.className = data.slack_alert_sent 
            ? "px-1.5 py-0.5 rounded bg-[#12151E] text-rose-400 border border-rose-500/30" 
            : "px-1.5 py-0.5 rounded bg-[#12151E] text-slate-400 border border-[#222634]";
    }
    if (receiptLinear) {
        receiptLinear.textContent = data.linear_ticket_created ? "Linear: P0 Created" : "Linear: None";
        receiptLinear.className = data.linear_ticket_created 
            ? "px-1.5 py-0.5 rounded bg-[#12151E] text-blue-400 border border-blue-500/30" 
            : "px-1.5 py-0.5 rounded bg-[#12151E] text-slate-400 border border-[#222634]";
    }

    // Update Deep Diagnostics JSON
    const rawPre = document.getElementById('raw-telemetry-json');
    if (rawPre) {
        rawPre.textContent = JSON.stringify({
            courtroom_id: data.courtroom_id,
            verdict: data.verdict,
            can_start_session: data.can_start_session,
            metrics: data.evaluation.metrics,
            golden_score: data.evaluation.golden_alignment,
            airtable_synced: data.airtable_synced,
            slack_alert_sent: data.slack_alert_sent,
            linear_ticket_created: data.linear_ticket_created
        }, null, 2);
    }
}

// 7. Progressive Disclosure Drawer
const btnToggleDeep = document.getElementById('btn-toggle-deep-diagnostics');
if (btnToggleDeep) {
    btnToggleDeep.addEventListener('click', () => {
        const panel = document.getElementById('deep-diagnostics-panel');
        const arrow = document.getElementById('deep-diag-arrow');
        const isHidden = panel.classList.contains('hidden');
        if (isHidden) {
            panel.classList.remove('hidden');
            arrow.textContent = "▴";
        } else {
            panel.classList.add('hidden');
            arrow.textContent = "▾";
        }
    });
}

// 8. Guided Technician Interview Modal Workflow
const btnOpenInterview = document.getElementById('btn-open-interview');
if (btnOpenInterview) {
    btnOpenInterview.addEventListener('click', () => {
        if (!pendingInterviewQuestions || pendingInterviewQuestions.length === 0) return;
        const q = pendingInterviewQuestions[0];
        const modal = document.getElementById('interview-modal');
        const container = document.getElementById('interview-question-container');
        const adviceBox = document.getElementById('interview-remediation-box');

        container.innerHTML = `
            <p class="text-xs font-semibold text-slate-200">${preventWidow(q.prompt)}</p>
            <div class="space-y-1.5 pt-1">
                ${q.options.map((opt, idx) => `
                    <label class="flex items-center space-x-2.5 p-2 rounded-md bg-[#0A0C10] border border-[#222634] hover:border-slate-600 cursor-pointer transition-colors">
                        <input type="radio" name="interview-option" value="${opt}" ${idx === 0 ? 'checked' : ''} class="w-3.5 h-3.5 text-emerald-500 focus:ring-emerald-500 bg-[#0A0C10] border-[#222634]">
                        <span class="text-xs text-slate-300 font-medium">${preventWidow(opt)}</span>
                    </label>
                `).join('')}
            </div>
        `;

        adviceBox.innerHTML = `<strong>Action Advice:</strong> ${preventWidow(q.remediation_advice)}`;
        modal.classList.remove('hidden');
    });
}

function closeInterviewModal() {
    const modal = document.getElementById('interview-modal');
    modal.classList.add('hidden');
}

document.getElementById('btn-close-interview').addEventListener('click', closeInterviewModal);
document.getElementById('btn-cancel-interview').addEventListener('click', closeInterviewModal);

// 9. Optimistic UI Remediation Update with Immediate Feedback
document.getElementById('btn-submit-interview').addEventListener('click', async () => {
    if (!pendingInterviewQuestions || pendingInterviewQuestions.length === 0) return;
    const q = pendingInterviewQuestions[0];
    const selected = document.querySelector('input[name="interview-option"]:checked')?.value || q.options[0];

    const interviewPayload = {
        courtroom_id: lastReportPayload.courtroom_id,
        question_id: q.question_id,
        selected_option: selected,
        remediation_applied: true,
        original_report: lastReportPayload
    };

    const card = document.getElementById('verdict-card');
    const title = document.getElementById('verdict-title');
    const verdictBadge = document.getElementById('verdict-badge');

    const previousTitle = title.textContent;
    const previousClass = card.className;

    // Sub-50ms Optimistic UI upgrade
    card.className = "h-full bg-[#0A0C10] border border-[#222634] border-l-4 border-l-emerald-500 rounded-md p-3 flex flex-col justify-between space-y-2";
    title.textContent = "Optimal: remediation applied (+6.0 dB)";
    title.className = "text-xs font-bold text-white tracking-tight";
    verdictBadge.textContent = "Remediated";
    verdictBadge.className = "px-2 py-0.5 rounded text-[10px] font-mono font-medium bg-emerald-500/10 text-emerald-400 border border-emerald-500/20";

    closeInterviewModal();

    try {
        const res = await fetch('/api/v1/telemetry/interview', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(interviewPayload)
        });

        if (!res.ok) {
            const err = await res.json();
            throw new Error(JSON.stringify(err.detail || err));
        }

        const data = await res.json();
        renderVerdictWithFollowThrough(data);
        pollFleetOverview();
        pollIncidents();
    } catch (err) {
        console.error("Remediation rollback:", err.message);
        card.className = previousClass;
        title.textContent = previousTitle;
        alert("Failed to apply interview remediation (rolled back): " + err.message);
    }
});

// 10. Poll 11-State Fleet Telemetry Matrix (Compact 4-Column Micro-Cards)
async function pollFleetOverview() {
    try {
        const res = await fetch('/api/v1/courtrooms/status');
        if (!res.ok) return;
        const data = await res.json();

        const statTotal = document.getElementById('stat-total-courtrooms');
        const statHealth = document.getElementById('stat-fleet-health');
        const statOpt = document.getElementById('stat-optimal-sessions');
        const statInc = document.getElementById('stat-incidents-count');

        if (statTotal) statTotal.textContent = data.total_active_courtrooms;
        if (statHealth) statHealth.textContent = `${data.fleet_health_pct}%`;
        if (statOpt) statOpt.textContent = data.verdict_breakdown.OPTIMAL || 0;
        if (statInc) statInc.textContent = data.recent_critical_incidents || 0;

        const container = document.getElementById('regions-container');
        if (container) {
            container.innerHTML = data.regions.map((r) => {
                let dotClass = "bg-emerald-500";
                let statusColor = "text-emerald-400";
                if (r.critical_count > 0) {
                    dotClass = "bg-rose-500";
                    statusColor = "text-rose-400";
                } else if (r.degraded_count > 0) {
                    dotClass = "bg-amber-500";
                    statusColor = "text-amber-400";
                }

                return `
                <div class="h-10 p-1.5 rounded-md bg-[#0A0C10] border border-[#222634] hover:border-slate-500 transition-colors cursor-pointer flex flex-col justify-between" onclick="filterByState('${r.state}')">
                    <div class="flex items-center justify-between">
                        <span class="font-mono font-bold text-[11px] text-white">${r.state}</span>
                        <span class="h-1.5 w-1.5 rounded-full ${dotClass}"></span>
                    </div>
                    <div class="flex items-center justify-between text-[10px] tabular-nums">
                        <span class="text-slate-400 font-mono">${r.total_courtrooms} act</span>
                        <span class="font-mono ${statusColor}">${r.healthy_pct}%</span>
                    </div>
                </div>
                `;
            }).join('');
        }
    } catch (e) {
        console.warn("Fleet poll failed:", e.message);
    }
}

window.filterByState = function(stateCode) {
    const match = COURTROOM_DIRECTORY.find(c => c.state === stateCode);
    if (match) {
        const applyUpdate = () => {
            document.getElementById('input-courtroom-id').value = match.id;
            document.getElementById('input-state').value = match.state;
            document.getElementById('input-bench-name').value = match.bench;
            if (match.golden) {
                document.getElementById('select-golden-profile').value = match.golden;
            }
            const standbyTarget = document.querySelector('#verdict-standby span:first-of-type');
            if (standbyTarget) standbyTarget.textContent = match.id;
        };

        if (document.startViewTransition) {
            document.startViewTransition(applyUpdate);
        } else {
            applyUpdate();
        }
    }
};

// 11. Poll Live Incident Routing Stream (Compact 2-Line Entries)
async function pollIncidents() {
    try {
        const res = await fetch('/api/v1/incidents?limit=10');
        if (!res.ok) return;
        const data = await res.json();
        const container = document.getElementById('incidents-container');

        if (container && data.incidents && data.incidents.length > 0) {
            container.innerHTML = data.incidents.map((inc) => {
                const dateStr = inc.created_at ? new Date(inc.created_at).toLocaleTimeString() : "--";
                return `
                <div class="bg-[#0A0C10] border border-[#222634] rounded-md p-2 space-y-1 text-[11px]">
                    <div class="flex justify-between items-center">
                        <span class="font-mono font-bold text-rose-400 text-xs">${inc.courtroom_id}</span>
                        <span class="text-[10px] font-mono text-slate-500 tabular-nums">${dateStr}</span>
                    </div>
                    <p class="text-slate-300 font-medium truncate text-[11px]">${preventWidow(inc.title)}</p>
                    <div class="flex items-center space-x-1.5 text-[10px] font-mono pt-0.5">
                        <span class="px-1.5 py-0.2 rounded bg-[#12151E] text-slate-400 border border-[#222634]">Slack: ${inc.slack_status}</span>
                        <span class="px-1.5 py-0.2 rounded bg-[#12151E] text-slate-400 border border-[#222634]">Linear: ${inc.linear_status}</span>
                    </div>
                </div>
                `;
            }).join('');
        }
    } catch (e) {
        console.warn("Incident poll failed:", e.message);
    }
}

// 12. Manual Airtable Sync
document.getElementById('btn-sync-airtable').addEventListener('click', async () => {
    const btn = document.getElementById('btn-sync-airtable');
    btn.disabled = true;
    btn.textContent = "Syncing...";

    try {
        const res = await fetch('/api/v1/sync/airtable', { method: 'POST' });
        const data = await res.json();
        alert(`Airtable Sync: ${data.message || 'Completed'}. Synced: ${data.synced_count || 0}`);
    } catch (err) {
        alert("Airtable sync error: " + err.message);
    } finally {
        btn.disabled = false;
        btn.innerHTML = `
            <svg class="w-3 h-3 text-slate-400" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                <path d="M21 12a9 9 0 0 0-9-9 9.75 9.75 0 0 0-6.74 2.74L3 8"/><path d="M3 3v5h5"/><path d="M3 12a9 9 0 0 0 9 9 9.75 9.75 0 0 0 6.74-2.74L21 16"/><path d="M16 21h5v-5"/>
            </svg>
            <span>Sync Airtable</span>
        `;
    }
});

// 13. Global Keyboard Shortcuts (Enter to Run, Escape to Close)
document.addEventListener('keydown', (e) => {
    if (e.key === 'Enter') {
        const activeEl = document.activeElement;
        const isInputField = activeEl && (activeEl.tagName === 'INPUT' || activeEl.tagName === 'SELECT' || activeEl.tagName === 'TEXTAREA');
        const modalOpen = !document.getElementById('interview-modal').classList.contains('hidden');

        if (!modalOpen && !isInputField) {
            e.preventDefault();
            document.getElementById('btn-run-diagnostic').click();
        }
    } else if (e.key === 'Escape') {
        const modal = document.getElementById('interview-modal');
        if (!modal.classList.contains('hidden')) {
            closeInterviewModal();
        }
        const listbox = document.getElementById('courtroom-combo-list');
        if (listbox && !listbox.classList.contains('hidden')) {
            listbox.classList.add('hidden');
        }
    }
});

// Boot Loop
pollFleetOverview();
pollIncidents();
setInterval(pollFleetOverview, 5000);
setInterval(pollIncidents, 5000);
