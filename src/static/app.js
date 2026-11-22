/**
 * Adalat-Pulse: Frontend Diagnostic Engine & Operations Visualizer
 * Implements 20-Point Ergonomic Design System:
 * - Typography & Spatial Hierarchy (Kerning, Tracking, Leading, X-Height, Line Length, Widow Control)
 * - Geometry & Viewport Bounds (Optical Center, Zero CLS, Safe Area, Min 44px Touch Targets)
 * - Color Metrics & Numerical Precision (OKLCH, Tabular Numbers)
 * - Interaction Architecture & UX (Affordance, Accessible Combobox, Progressive Disclosure, Optimistic Updates)
 * - Motion Choreography (Origin-Aware Modal, Interruptible Web Animations, Stagger Dynamics, View Transitions)
 */

let audioContext = null;
let analyser = null;
let micStream = null;
let currentSampleRate = 48000;
let currentSnrDb = 26.5;
let micDeviceLabel = "Default Audio Device";
let lastReportPayload = null;
let pendingInterviewQuestions = [];
let activeProbeAnimation = null;
let probeIntervalId = null;

// 12. Helper: Prevent Typographic Widows by Injecting Non-Breaking Space
function preventWidow(text) {
    if (!text || typeof text !== 'string') return text;
    const words = text.trim().split(' ');
    if (words.length <= 2) return text;
    const lastWord = words.pop();
    const secondLast = words.pop();
    return `${words.join(' ')} ${secondLast}&nbsp;${lastWord}`;
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
        if (srEl) srEl.textContent = `${currentSampleRate} Hz`;

        if (!micStream) {
            micStream = await navigator.mediaDevices.getUserMedia({ audio: true, video: false });
            const tracks = micStream.getAudioTracks();
            if (tracks.length > 0) {
                micDeviceLabel = tracks[0].label || "Integrated Microphone";
                const labelEl = document.getElementById('mic-status-label');
                if (labelEl) labelEl.textContent = micDeviceLabel.slice(0, 28);
            }

            analyser = audioContext.createAnalyser();
            analyser.fftSize = 512;
            const source = audioContext.createMediaStreamSource(micStream);
            source.connect(analyser);

            sampleAudioLoop();
        }
    } catch (err) {
        console.warn("Browser mic access not granted or simulated:", err.message);
        const labelEl = document.getElementById('mic-status-label');
        if (labelEl) labelEl.textContent = "Simulated / Fallback Mode";
        const srEl = document.getElementById('live-sample-rate');
        if (srEl) srEl.textContent = "16000 Hz";
        const snrEl = document.getElementById('live-snr-db');
        if (snrEl) snrEl.textContent = "24.5 dB";
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

    // Estimate Signal-to-Noise Ratio (SNR) in dB from input RMS
    const minDb = 10.0;
    const maxDb = 35.0;
    const normalized = Math.min(Math.max(average / 128, 0.1), 1.0);
    currentSnrDb = Math.round((minDb + (normalized * (maxDb - minDb))) * 10) / 10;

    const snrEl = document.getElementById('live-snr-db');
    if (snrEl) snrEl.textContent = `${currentSnrDb.toFixed(1)} dB`;

    const levelBar = document.getElementById('audio-level-bar');
    if (levelBar) {
        levelBar.style.width = `${Math.min(average * 1.5, 100)}%`;
    }

    requestAnimationFrame(sampleAudioLoop);
}

// 17. Accessible Courtroom Search & Combo Box Implementation
const COURTROOM_DIRECTORY = [
    { id: "DL-HC-CRT04", state: "DL", bench: "Delhi High Court Bench 04 (Civil Division)", tier: "HIGH_COURT", golden: "GOLDEN-HC-FIBER" },
    { id: "KL-HC-CRT01", state: "KL", bench: "Kerala High Court Bench 01 (Digital Benches)", tier: "HIGH_COURT", golden: "GOLDEN-HC-FIBER" },
    { id: "KA-HC-BLR02", state: "KA", bench: "Karnataka High Court Bengaluru Bench 02", tier: "HIGH_COURT", golden: "GOLDEN-HC-FIBER" },
    { id: "MH-HC-BOM01", state: "MH", bench: "Bombay High Court Bench 01 (Commercial Division)", tier: "HIGH_COURT", golden: "GOLDEN-HC-FIBER" },
    { id: "UP-DC-LKO05", state: "UP", bench: "Lucknow District Court Hall 05", tier: "DISTRICT_COURT", golden: "GOLDEN-DC-HYBRID" },
    { id: "TN-HC-MAD03", state: "TN", bench: "Madras High Court Hall 03", tier: "HIGH_COURT", golden: "GOLDEN-HC-FIBER" },
    { id: "WB-HC-CAL01", state: "WB", bench: "Calcutta High Court Bench 01", tier: "HIGH_COURT", golden: "GOLDEN-HC-FIBER" },
    { id: "GJ-HC-AHM02", state: "GJ", bench: "Gujarat High Court Ahmedabad Bench 02", tier: "HIGH_COURT", golden: "GOLDEN-HC-FIBER" },
    { id: "RJ-DC-JPR02", state: "RJ", bench: "Jaipur District & Sessions Court 02", tier: "DISTRICT_COURT", golden: "GOLDEN-DC-HYBRID" },
    { id: "MP-DC-BPL03", state: "MP", bench: "Bhopal District Court Room 03", tier: "DISTRICT_COURT", golden: "GOLDEN-DC-HYBRID" },
    { id: "AP-HC-AMR01", state: "AP", bench: "Andhra Pradesh High Court Amaravati Bench 01", tier: "HIGH_COURT", golden: "GOLDEN-HC-FIBER" },
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
            listbox.innerHTML = `<div class="p-3 text-xs text-slate-500 text-center">No matching courtroom benches found</div>`;
            return;
        }

        listbox.innerHTML = matches.map((item, idx) => `
            <div role="option" data-index="${idx}" data-id="${item.id}" data-state="${item.state}" data-bench="${item.bench}" data-golden="${item.golden}" class="combo-option min-h-[44px] px-3.5 py-2.5 hover:bg-slate-800 cursor-pointer flex items-center justify-between text-xs transition-colors ${idx === highlightedIndex ? 'bg-slate-800 ring-1 ring-emerald-500/50' : ''}">
                <div>
                    <span class="font-mono font-bold text-white tracking-wide">${item.id}</span>
                    <p class="text-[11px] text-slate-400 truncate max-w-[280px]">${item.bench}</p>
                </div>
                <span class="px-1.5 py-0.5 rounded text-[10px] font-mono font-semibold bg-slate-800 text-slate-300 border border-slate-700">${item.state}</span>
            </div>
        `).join('');

        // Attach option click handlers
        listbox.querySelectorAll('.combo-option').forEach(el => {
            el.addEventListener('click', () => {
                selectCourtroomOption(el.dataset);
                closeComboBox();
            });
        });
    }

    function selectCourtroomOption(data) {
        // 20. Shared Element Transition wrapper if supported
        const applyUpdate = () => {
            input.value = data.id;
            document.getElementById('input-state').value = data.state;
            document.getElementById('input-bench-name').value = data.bench;
            if (data.golden) {
                document.getElementById('select-golden-profile').value = data.golden;
            }
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

    toggleBtn.addEventListener('click', (e) => {
        e.stopPropagation();
        if (listbox.classList.contains('hidden')) {
            openComboBox();
        } else {
            closeComboBox();
        }
    });

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
            options.forEach((opt, idx) => opt.classList.toggle('bg-slate-800', idx === highlightedIndex));
            if (options[highlightedIndex]) options[highlightedIndex].scrollIntoView({ block: 'nearest' });
        } else if (e.key === 'ArrowUp') {
            e.preventDefault();
            highlightedIndex = Math.max(highlightedIndex - 1, 0);
            options.forEach((opt, idx) => opt.classList.toggle('bg-slate-800', idx === highlightedIndex));
            if (options[highlightedIndex]) options[highlightedIndex].scrollIntoView({ block: 'nearest' });
        } else if (e.key === 'Enter') {
            e.preventDefault();
            if (highlightedIndex >= 0 && options[highlightedIndex]) {
                selectCourtroomOption(options[highlightedIndex].dataset);
                closeComboBox();
            }
        } else if (e.key === 'Escape') {
            closeComboBox();
        }
    });

    document.addEventListener('click', (e) => {
        if (!input.contains(e.target) && !listbox.contains(e.target) && !toggleBtn.contains(e.target)) {
            closeComboBox();
        }
    });
}
initCourtroomComboBox();

// 3. Preset Scenarios Handler
document.querySelectorAll('.preset-btn').forEach(btn => {
    btn.addEventListener('click', (e) => {
        const preset = e.currentTarget.getAttribute('data-preset');
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
        currentSnrDb = 15.5; // Degraded noise floor (15.5 dB) -> Triggers Level 3 Interview
        document.getElementById('input-courtroom-id').value = "UP-DC-LKO05";
        document.getElementById('input-state').value = "UP";
        document.getElementById('input-bench-name').value = "Lucknow District Court Hall 05";
        document.getElementById('select-golden-profile').value = "GOLDEN-DC-HYBRID";
    } else if (preset === 'edge_lag') {
        latIn.value = "340.0"; // Critical Latency (> 300 ms)
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
    if (srEl) srEl.textContent = `${currentSampleRate} Hz`;
    const snrEl = document.getElementById('live-snr-db');
    if (snrEl) snrEl.textContent = `${currentSnrDb.toFixed(1)} dB`;
}

// 4. Run 5-Second Live Pre-Flight Diagnostic Check (Zero CLS & Interruptible Motion)
document.getElementById('btn-run-diagnostic').addEventListener('click', async () => {
    await initAudioHardware();

    const btn = document.getElementById('btn-run-diagnostic');
    const progressContainer = document.getElementById('progress-container');
    const progressBar = document.getElementById('progress-bar');
    const progressPct = document.getElementById('progress-pct');
    const badge = document.getElementById('diagnostic-badge');
    const skeleton = document.getElementById('verdict-skeleton');
    const verdictCard = document.getElementById('verdict-card');

    // 18. Interrupt any currently running probe cleanly
    if (probeIntervalId) {
        clearInterval(probeIntervalId);
        probeIntervalId = null;
    }

    btn.disabled = true;
    btn.classList.add('opacity-50', 'cursor-not-allowed');
    progressContainer.classList.remove('hidden');

    // 8. Zero CLS: Keep the reserved slot occupied with the shimmer skeleton
    verdictCard.classList.add('hidden');
    skeleton.classList.remove('hidden');

    badge.textContent = "PROBING (5s)";
    badge.className = "px-3 py-1 text-xs font-mono font-medium rounded-full bg-amber-500/20 text-amber-400 border border-amber-500/30 animate-pulse tabular-nums";

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
            badge.textContent = "EVALUATING";

            await submitDiagnosticReport();
        }
    }, 100);
});

async function submitDiagnosticReport() {
    const courtroomId = document.getElementById('input-courtroom-id').value.trim();
    const state = document.getElementById('input-state').value;
    const benchName = document.getElementById('input-bench-name').value.trim();
    const goldenProfileId = document.getElementById('select-golden-profile').value;

    const latency = parseFloat(document.getElementById('in-latency').value) || 45.0;
    const loss = parseFloat(document.getElementById('in-loss').value) || 0.0;
    const jitter = parseFloat(document.getElementById('in-jitter').value) || 5.0;
    const wsRtt = parseFloat(document.getElementById('in-ws-rtt').value) || 50.0;

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
        renderVerdict(data);
        pollFleetOverview();
        pollIncidents();
    } catch (e) {
        alert("Failed to submit telemetry report: " + e.message);
        document.getElementById('verdict-skeleton').classList.add('hidden');
    }
}

function renderVerdict(data) {
    const skeleton = document.getElementById('verdict-skeleton');
    const card = document.getElementById('verdict-card');
    const badge = document.getElementById('diagnostic-badge');
    const icon = document.getElementById('verdict-icon');
    const title = document.getElementById('verdict-title');
    const crText = document.getElementById('verdict-courtroom');
    const verdictBadge = document.getElementById('verdict-badge');
    const summary = document.getElementById('verdict-summary');

    const receiptAirtable = document.getElementById('receipt-airtable');
    const receiptSlack = document.getElementById('receipt-slack');
    const receiptLinear = document.getElementById('receipt-linear');

    // Level 4: Golden alignment elements
    const goldenScorePct = document.getElementById('golden-score-pct');
    const goldenProgressBar = document.getElementById('golden-progress-bar');
    const goldenSummaryText = document.getElementById('golden-summary-text');

    // Level 3: Interview elements
    const interviewBox = document.getElementById('interview-trigger-box');

    // Hide skeleton and reveal card smoothly (Zero CLS)
    skeleton.classList.add('hidden');
    card.classList.remove('hidden');

    if (data.verdict === 'OPTIMAL') {
        card.className = "border border-emerald-500/40 bg-emerald-950/20 rounded-xl p-5 space-y-4";
        badge.className = "px-3 py-1 text-xs font-mono font-medium rounded-full bg-emerald-500/20 text-emerald-400 border border-emerald-500/30 tabular-nums";
        badge.textContent = "OPTIMAL";
        icon.textContent = "🟢";
        title.textContent = "OPTIMAL — SESSION APPROVED";
        title.className = "text-base font-bold text-emerald-400 tracking-tight";
        verdictBadge.textContent = "SESSION CLEARED";
        verdictBadge.className = "px-3 py-1.5 rounded-full text-xs font-mono font-bold tracking-wider uppercase bg-emerald-500/20 text-emerald-400 border border-emerald-500/30";
        interviewBox.classList.add('hidden');
    } else if (data.verdict === 'DEGRADED') {
        card.className = "border border-amber-500/40 bg-amber-950/20 rounded-xl p-5 space-y-4";
        badge.className = "px-3 py-1 text-xs font-mono font-medium rounded-full bg-amber-500/20 text-amber-400 border border-amber-500/30 tabular-nums";
        badge.textContent = "DEGRADED";
        icon.textContent = "🟡";
        title.textContent = "DEGRADED — PROCEED WITH CAUTION";
        title.className = "text-base font-bold text-amber-400 tracking-tight";
        verdictBadge.textContent = "MONITORING ACTIVE";
        verdictBadge.className = "px-3 py-1.5 rounded-full text-xs font-mono font-bold tracking-wider uppercase bg-amber-500/20 text-amber-400 border border-amber-500/30";

        if (data.evaluation.pending_questions && data.evaluation.pending_questions.length > 0) {
            pendingInterviewQuestions = data.evaluation.pending_questions;
            interviewBox.classList.remove('hidden');
        } else {
            interviewBox.classList.add('hidden');
        }
    } else {
        card.className = "border border-rose-500/40 bg-rose-950/20 rounded-xl p-5 space-y-4";
        badge.className = "px-3 py-1 text-xs font-mono font-medium rounded-full bg-rose-500/20 text-rose-400 border border-rose-500/30 tabular-nums";
        badge.textContent = "CRITICAL BREACH";
        icon.textContent = "🔴";
        title.textContent = "CRITICAL — SESSION HALTED";
        title.className = "text-base font-bold text-rose-400 tracking-tight";
        verdictBadge.textContent = "GATE BLOCKED";
        verdictBadge.className = "px-3 py-1.5 rounded-full text-xs font-mono font-bold tracking-wider uppercase bg-rose-500/20 text-rose-400 border border-rose-500/30";
        interviewBox.classList.add('hidden');
    }

    crText.textContent = `${data.courtroom_id} (${data.state}) • Snapshot #${data.snapshot_id}`;
    summary.innerHTML = `<strong>${preventWidow(data.evaluation.summary)}</strong><br>` +
        data.evaluation.reason_codes.map(r => `• ${preventWidow(r)}`).join('<br>');

    // Level 4: Render Golden Alignment Score
    if (data.evaluation.golden_alignment) {
        const align = data.evaluation.golden_alignment;
        goldenScorePct.textContent = `${align.alignment_pct}%`;
        goldenProgressBar.style.width = `${align.alignment_pct}%`;
        goldenSummaryText.innerHTML = preventWidow(`${align.summary} (Latency: ${align.latency_delta_ms >= 0 ? '+' : ''}${align.latency_delta_ms}ms, Loss: ${align.packet_loss_delta_pct >= 0 ? '+' : ''}${align.packet_loss_delta_pct}%, SNR: ${align.snr_delta_db >= 0 ? '+' : ''}${align.snr_delta_db} dB)`);
    }

    // Update Receipts
    receiptAirtable.querySelector('span:last-child').textContent = data.airtable_synced ? "✅ Synced" : "Pending";
    receiptAirtable.querySelector('span:last-child').className = data.airtable_synced ? "font-semibold text-emerald-400" : "font-semibold text-slate-400";

    receiptSlack.querySelector('span:last-child').textContent = data.slack_alert_sent ? "🚨 Sent (#all-alerts)" : "Standby";
    receiptSlack.querySelector('span:last-child').className = data.slack_alert_sent ? "font-semibold text-rose-400" : "font-semibold text-slate-400";

    receiptLinear.querySelector('span:last-child').textContent = data.linear_ticket_created ? "🎫 Created (P0)" : "None";
    receiptLinear.querySelector('span:last-child').className = data.linear_ticket_created ? "font-semibold text-blue-400" : "font-semibold text-slate-400";

    // 19. Update Deep Diagnostics Progressive Disclosure Raw JSON
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

// 19. Progressive Disclosure Accordion Toggle
const btnToggleDeep = document.getElementById('btn-toggle-deep-diagnostics');
if (btnToggleDeep) {
    btnToggleDeep.addEventListener('click', () => {
        const panel = document.getElementById('deep-diagnostics-panel');
        const arrow = document.getElementById('deep-diag-arrow');
        const isHidden = panel.classList.contains('hidden');
        if (isHidden) {
            panel.classList.remove('hidden');
            arrow.style.transform = "rotate(180deg)";
        } else {
            panel.classList.add('hidden');
            arrow.style.transform = "rotate(0deg)";
        }
    });
}

// 10. Origin-Aware Animation: Interview Modal Workflow
const btnOpenInterview = document.getElementById('btn-open-interview');
if (btnOpenInterview) {
    btnOpenInterview.addEventListener('click', (e) => {
        if (!pendingInterviewQuestions || pendingInterviewQuestions.length === 0) return;
        const q = pendingInterviewQuestions[0];
        const modal = document.getElementById('interview-modal');
        const dialog = document.getElementById('interview-modal-dialog');
        const container = document.getElementById('interview-question-container');
        const adviceBox = document.getElementById('interview-remediation-box');

        // 10. Calculate origin coordinates relative to button clicked
        const rect = e.currentTarget.getBoundingClientRect();
        const originX = rect.left + rect.width / 2;
        const originY = rect.top + rect.height / 2;
        dialog.style.transformOrigin = `${originX}px ${originY}px`;

        // 14. Assign Stagger Index to Option Cards
        container.innerHTML = `
            <p class="text-sm font-semibold text-slate-200 text-pretty">${preventWidow(q.prompt)}</p>
            <div class="space-y-2.5 pt-2">
                ${q.options.map((opt, idx) => `
                    <label style="--stagger-index: ${idx}" class="stagger-item flex items-center space-x-3 p-3 rounded-lg bg-slate-950 border border-slate-800 hover:border-slate-700 cursor-pointer min-h-[44px] pressable">
                        <input type="radio" name="interview-option" value="${opt}" ${idx === 0 ? 'checked' : ''} class="w-4 h-4 text-emerald-500 focus:ring-emerald-500 bg-slate-900 border-slate-700">
                        <span class="text-xs text-slate-300 font-medium">${preventWidow(opt)}</span>
                    </label>
                `).join('')}
            </div>
        `;

        adviceBox.innerHTML = `<strong>💡 Recommended Operator Action:</strong> ${preventWidow(q.remediation_advice)}`;
        modal.classList.remove('hidden');

        // Play subtle origin expansion animation
        dialog.animate([
            { transform: 'scale(0.88) translateY(12px)', opacity: 0 },
            { transform: 'scale(1) translateY(0)', opacity: 1 }
        ], {
            duration: 260,
            easing: 'cubic-bezier(0.16, 1, 0.3, 1)',
            fill: 'forwards'
        });
    });
}

function closeInterviewModal() {
    const modal = document.getElementById('interview-modal');
    const dialog = document.getElementById('interview-modal-dialog');
    const anim = dialog.animate([
        { transform: 'scale(1)', opacity: 1 },
        { transform: 'scale(0.92) translateY(8px)', opacity: 0 }
    ], {
        duration: 180,
        easing: 'ease-in',
        fill: 'forwards'
    });
    anim.onfinish = () => modal.classList.add('hidden');
}

document.getElementById('btn-close-interview').addEventListener('click', closeInterviewModal);
document.getElementById('btn-cancel-interview').addEventListener('click', closeInterviewModal);

// 6. Level 3: Optimistic Update Handler with Rollback Safety
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

    // Snapshot previous state for rollback
    const previousVerdictTitle = document.getElementById('verdict-title').textContent;
    const previousVerdictClass = document.getElementById('verdict-card').className;

    // 6. Optimistic UI update: immediately upgrade status card visually
    const card = document.getElementById('verdict-card');
    const title = document.getElementById('verdict-title');
    const verdictBadge = document.getElementById('verdict-badge');
    const icon = document.getElementById('verdict-icon');

    card.className = "border border-emerald-500/40 bg-emerald-950/20 rounded-xl p-5 space-y-4";
    icon.textContent = "🟢";
    title.textContent = "OPTIMAL — REMEDIATION CONFIRMED (+6.0 dB)";
    title.className = "text-base font-bold text-emerald-400 tracking-tight";
    verdictBadge.textContent = "REMEDIATED";
    verdictBadge.className = "px-3 py-1.5 rounded-full text-xs font-mono font-bold tracking-wider uppercase bg-emerald-500/20 text-emerald-400 border border-emerald-500/30";

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
        renderVerdict(data);
        pollFleetOverview();
        pollIncidents();
    } catch (err) {
        // Rollback optimistic update
        console.error("Remediation submission failed, rolling back:", err.message);
        card.className = previousVerdictClass;
        title.textContent = previousVerdictTitle;
        alert("Failed to apply interview remediation (rolled back): " + err.message);
    }
});

// 7. Poll Fleet Status Overview (Choreographed Stagger Motion & Tabular Numbers)
async function pollFleetOverview() {
    try {
        const res = await fetch('/api/v1/courtrooms/status');
        if (!res.ok) return;
        const data = await res.json();

        document.getElementById('stat-total-courtrooms').textContent = data.total_active_courtrooms;
        document.getElementById('stat-fleet-health').textContent = `${data.fleet_health_pct}%`;
        document.getElementById('stat-optimal-sessions').textContent = data.verdict_breakdown.OPTIMAL || 0;
        document.getElementById('stat-incidents-count').textContent = data.recent_critical_incidents || 0;

        // Render 11 State Cards with dynamic --stagger-index
        const container = document.getElementById('regions-container');
        if (container) {
            container.innerHTML = data.regions.map((r, idx) => {
                let badgeColor = "bg-emerald-500/10 text-emerald-400 border-emerald-500/20";
                let dotColor = "bg-emerald-400";
                if (r.critical_count > 0) {
                    badgeColor = "bg-rose-500/10 text-rose-400 border-rose-500/20";
                    dotColor = "bg-rose-400";
                } else if (r.degraded_count > 0) {
                    badgeColor = "bg-amber-500/10 text-amber-400 border-amber-500/20";
                    dotColor = "bg-amber-400";
                }

                return `
                <div style="--stagger-index: ${idx}" class="stagger-item bg-slate-950 p-3 rounded-lg border border-slate-800 hover:border-slate-700 flex flex-col justify-between min-h-[72px] pressable cursor-pointer" onclick="filterByState('${r.state}')">
                    <div class="flex items-center justify-between">
                        <span class="font-bold text-xs text-white tracking-wide font-mono">${r.state}</span>
                        <span class="w-2.5 h-2.5 rounded-full ${dotColor}"></span>
                    </div>
                    <p class="text-[11px] text-slate-400 truncate mt-1">${r.state_name}</p>
                    <div class="flex justify-between items-center text-[10px] text-slate-500 mt-2 pt-1 border-t border-slate-900 tabular-nums">
                        <span>Active: <strong class="text-slate-300 font-mono">${r.total_courtrooms}</strong></span>
                        <span class="font-mono text-emerald-400 font-semibold">${r.healthy_pct}%</span>
                    </div>
                </div>
                `;
            }).join('');
        }
    } catch (e) {
        console.warn("Fleet poll failed:", e.message);
    }
}

// Quick filter state helper
window.filterByState = function(stateCode) {
    const stateSelect = document.getElementById('input-state');
    if (stateSelect) {
        stateSelect.value = stateCode;
    }
    const match = COURTROOM_DIRECTORY.find(c => c.state === stateCode);
    if (match) {
        document.getElementById('input-courtroom-id').value = match.id;
        document.getElementById('input-bench-name').value = match.bench;
    }
};

// 8. Poll Incidents Feed (Tabular Numbers & Widow Balancing)
async function pollIncidents() {
    try {
        const res = await fetch('/api/v1/incidents?limit=10');
        if (!res.ok) return;
        const data = await res.json();
        const container = document.getElementById('incidents-container');

        if (container && data.incidents && data.incidents.length > 0) {
            container.innerHTML = data.incidents.map((inc, idx) => {
                const dateStr = inc.created_at ? new Date(inc.created_at).toLocaleTimeString() : "--";
                return `
                <div style="--stagger-index: ${idx}" class="stagger-item bg-slate-950 border border-slate-800 rounded-lg p-3 space-y-1.5 text-xs">
                    <div class="flex justify-between items-center">
                        <span class="font-mono font-semibold text-rose-400 tracking-wide">${inc.courtroom_id}</span>
                        <span class="text-[10px] text-slate-500 tabular-nums font-mono">${dateStr}</span>
                    </div>
                    <p class="text-slate-300 font-medium truncate text-pretty">${preventWidow(inc.title)}</p>
                    <div class="flex items-center space-x-2 text-[10px] pt-1 font-mono">
                        <span class="px-2 py-0.5 rounded bg-slate-900 text-slate-400 border border-slate-800">Slack: ${inc.slack_status}</span>
                        <span class="px-2 py-0.5 rounded bg-slate-900 text-slate-400 border border-slate-800">Linear: ${inc.linear_status}</span>
                    </div>
                </div>
                `;
            }).join('');
        }
    } catch (e) {
        console.warn("Incident poll failed:", e.message);
    }
}

// 9. Manual Airtable Sync Button (44px Touch Target)
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
        btn.innerHTML = '<span>🔄</span><span>Sync Airtable</span>';
    }
});

// Boot operations
pollFleetOverview();
pollIncidents();
setInterval(pollFleetOverview, 5000);
setInterval(pollIncidents, 5000);
