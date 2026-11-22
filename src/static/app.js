/**
 * Adalat-Pulse: Frontend Diagnostic Engine & Operations Visualizer
 * Zero external bloat: Pure Vanilla ES6 + Web Audio API + WebSockets
 */

let audioContext = null;
let analyser = null;
let micStream = null;
let currentSampleRate = 48000;
let currentSnrDb = 26.5;
let micDeviceLabel = "Default Audio Device";

// 1. Live IST Clock
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
        document.getElementById('live-sample-rate').textContent = `${currentSampleRate} Hz`;

        if (!micStream) {
            micStream = await navigator.mediaDevices.getUserMedia({ audio: true, video: false });
            const tracks = micStream.getAudioTracks();
            if (tracks.length > 0) {
                micDeviceLabel = tracks[0].label || "Integrated Microphone";
                document.getElementById('mic-status-label').textContent = micDeviceLabel.slice(0, 32);
            }

            analyser = audioContext.createAnalyser();
            analyser.fftSize = 512;
            const source = audioContext.createMediaStreamSource(micStream);
            source.connect(analyser);

            sampleAudioLoop();
        }
    } catch (err) {
        console.warn("Browser mic access not granted or not supported:", err.message);
        document.getElementById('mic-status-label').textContent = "Simulated / Fallback Mode";
        document.getElementById('live-sample-rate').textContent = "16000 Hz";
        document.getElementById('live-snr-db').textContent = "24.5 dB";
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
    if (snrEl) snrEl.textContent = `${currentSnrDb} dB`;

    const levelBar = document.getElementById('audio-level-bar');
    if (levelBar) {
        levelBar.style.width = `${Math.min(average * 1.5, 100)}%`;
    }

    requestAnimationFrame(sampleAudioLoop);
}

// 3. Preset Scenarios Handler
document.querySelectorAll('.preset-btn').forEach(btn => {
    btn.addEventListener('click', (e) => {
        const preset = e.target.getAttribute('data-preset');
        applyPreset(preset);
    });
});

function applyPreset(preset) {
    const latIn = document.getElementById('in-latency');
    const lossIn = document.getElementById('in-loss');
    const jitIn = document.getElementById('in-jitter');
    const rttIn = document.getElementById('in-ws-rtt');

    if (preset === 'optimal') {
        latIn.value = 35.0;
        lossIn.value = 0.0;
        jitIn.value = 4.2;
        rttIn.value = 45.0;
        currentSampleRate = 48000;
        currentSnrDb = 28.5;
        document.getElementById('input-courtroom-id').value = "KL-HC-CRT01";
        document.getElementById('input-state').value = "KL";
        document.getElementById('input-bench-name').value = "Kerala High Court Bench 01 (Digital Benches)";
    } else if (preset === 'monsoon') {
        latIn.value = 380.0;
        lossIn.value = 3.8;
        jitIn.value = 38.0;
        rttIn.value = 390.0;
        currentSampleRate = 16000;
        currentSnrDb = 21.0;
        document.getElementById('input-courtroom-id').value = "RJ-DC-JPR02";
        document.getElementById('input-state').value = "RJ";
        document.getElementById('input-bench-name').value = "Jaipur District & Sessions Court 02";
    } else if (preset === 'fan_noise') {
        latIn.value = 65.0;
        lossIn.value = 0.1;
        jitIn.value = 7.5;
        rttIn.value = 75.0;
        currentSampleRate = 16000;
        currentSnrDb = 9.2; // Critical SNR (< 12 dB)
        document.getElementById('input-courtroom-id').value = "UP-DC-LKO05";
        document.getElementById('input-state').value = "UP";
        document.getElementById('input-bench-name').value = "Lucknow District Court Hall 05";
    } else if (preset === 'edge_lag') {
        latIn.value = 340.0; // Critical Latency (> 300 ms)
        lossIn.value = 1.4;
        jitIn.value = 45.0;
        rttIn.value = 360.0;
        currentSampleRate = 16000;
        currentSnrDb = 17.5;
        document.getElementById('input-courtroom-id').value = "MP-DC-BPL03";
        document.getElementById('input-state').value = "MP";
        document.getElementById('input-bench-name').value = "Bhopal District Court Room 03";
    }

    document.getElementById('live-sample-rate').textContent = `${currentSampleRate} Hz`;
    document.getElementById('live-snr-db').textContent = `${currentSnrDb} dB`;
}

// 4. Run 5-Second Live Pre-Flight Diagnostic Check
document.getElementById('btn-run-diagnostic').addEventListener('click', async () => {
    await initAudioHardware();

    const btn = document.getElementById('btn-run-diagnostic');
    const progressContainer = document.getElementById('progress-container');
    const progressBar = document.getElementById('progress-bar');
    const progressPct = document.getElementById('progress-pct');
    const badge = document.getElementById('diagnostic-badge');
    const verdictCard = document.getElementById('verdict-card');

    btn.disabled = true;
    btn.classList.add('opacity-50', 'cursor-not-allowed');
    progressContainer.classList.remove('hidden');
    verdictCard.classList.add('hidden');
    badge.textContent = "PROBING (5s)";
    badge.className = "px-2.5 py-1 text-xs font-mono font-medium rounded-full bg-amber-500/20 text-amber-400 border border-amber-500/30 animate-pulse";

    const totalSteps = 50; // 50 * 100ms = 5000ms
    let currentStep = 0;

    const interval = setInterval(async () => {
        currentStep++;
        const pct = Math.round((currentStep / totalSteps) * 100);
        progressBar.style.width = `${pct}%`;
        progressPct.textContent = `${pct}%`;

        if (currentStep >= totalSteps) {
            clearInterval(interval);
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
        app_version: "1.0.0"
    };

    try {
        const res = await fetch('/api/v1/telemetry/report', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(payload)
        });

        if (!res.ok) {
            const err = await res.json();
            alert(`Error: ${JSON.stringify(err.detail || err)}`);
            return;
        }

        const data = await res.json();
        renderVerdict(data);
        pollFleetOverview();
        pollIncidents();
    } catch (e) {
        alert("Failed to submit telemetry report: " + e.message);
    }
}

function renderVerdict(data) {
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

    card.classList.remove('hidden');

    if (data.verdict === 'OPTIMAL') {
        card.className = "mt-6 border border-emerald-500/40 bg-emerald-950/20 rounded-xl p-5 space-y-3";
        badge.className = "px-2.5 py-1 text-xs font-mono font-medium rounded-full bg-emerald-500/20 text-emerald-400 border border-emerald-500/30";
        badge.textContent = "OPTIMAL";
        icon.textContent = "🟢";
        title.textContent = "OPTIMAL — SESSION APPROVED";
        title.className = "text-base font-bold text-emerald-400";
        verdictBadge.textContent = "SESSION CLEARED";
        verdictBadge.className = "px-3 py-1 rounded-full text-xs font-mono font-bold bg-emerald-500/20 text-emerald-400 border border-emerald-500/30";
    } else if (data.verdict === 'DEGRADED') {
        card.className = "mt-6 border border-amber-500/40 bg-amber-950/20 rounded-xl p-5 space-y-3";
        badge.className = "px-2.5 py-1 text-xs font-mono font-medium rounded-full bg-amber-500/20 text-amber-400 border border-amber-500/30";
        badge.textContent = "DEGRADED";
        icon.textContent = "🟡";
        title.textContent = "DEGRADED — PROCEED WITH CAUTION";
        title.className = "text-base font-bold text-amber-400";
        verdictBadge.textContent = "MONITORING ACTIVE";
        verdictBadge.className = "px-3 py-1 rounded-full text-xs font-mono font-bold bg-amber-500/20 text-amber-400 border border-amber-500/30";
    } else {
        card.className = "mt-6 border border-rose-500/40 bg-rose-950/20 rounded-xl p-5 space-y-3";
        badge.className = "px-2.5 py-1 text-xs font-mono font-medium rounded-full bg-rose-500/20 text-rose-400 border border-rose-500/30";
        badge.textContent = "CRITICAL BREACH";
        icon.textContent = "🔴";
        title.textContent = "CRITICAL — SESSION HALTED";
        title.className = "text-base font-bold text-rose-400";
        verdictBadge.textContent = "GATE BLOCKED";
        verdictBadge.className = "px-3 py-1 rounded-full text-xs font-mono font-bold bg-rose-500/20 text-rose-400 border border-rose-500/30";
    }

    crText.textContent = `${data.courtroom_id} (${data.state}) • Snapshot #${data.snapshot_id}`;
    summary.innerHTML = `<strong>${data.evaluation.summary}</strong><br>` +
        data.evaluation.reason_codes.map(r => `• ${r}`).join('<br>');

    // Update Receipts
    receiptAirtable.querySelector('span:last-child').textContent = data.airtable_synced ? "✅ Synced" : "Pending";
    receiptAirtable.querySelector('span:last-child').className = data.airtable_synced ? "font-semibold text-emerald-400" : "font-semibold text-slate-400";

    receiptSlack.querySelector('span:last-child').textContent = data.slack_alert_sent ? "🚨 Sent (#all-alerts)" : "Standby";
    receiptSlack.querySelector('span:last-child').className = data.slack_alert_sent ? "font-semibold text-rose-400" : "font-semibold text-slate-400";

    receiptLinear.querySelector('span:last-child').textContent = data.linear_ticket_created ? "🎫 Created (P0)" : "None";
    receiptLinear.querySelector('span:last-child').className = data.linear_ticket_created ? "font-semibold text-blue-400" : "font-semibold text-slate-400";
}

// 5. Poll Fleet Status Overview
async function pollFleetOverview() {
    try {
        const res = await fetch('/api/v1/courtrooms/status');
        if (!res.ok) return;
        const data = await res.json();

        document.getElementById('stat-total-courtrooms').textContent = data.total_active_courtrooms;
        document.getElementById('stat-fleet-health').textContent = `${data.fleet_health_pct}%`;
        document.getElementById('stat-optimal-sessions').textContent = data.verdict_breakdown.OPTIMAL || 0;
        document.getElementById('stat-incidents-count').textContent = data.recent_critical_incidents || 0;

        // Render 11 State Cards
        const container = document.getElementById('regions-container');
        if (container) {
            container.innerHTML = data.regions.map(r => {
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
                <div class="bg-slate-950 p-2.5 rounded-lg border border-slate-800 flex flex-col justify-between">
                    <div class="flex items-center justify-between">
                        <span class="font-bold text-xs text-white">${r.state}</span>
                        <span class="w-2 h-2 rounded-full ${dotColor}"></span>
                    </div>
                    <p class="text-xs text-slate-400 truncate mt-0.5">${r.state_name}</p>
                    <div class="flex justify-between items-center text-[10px] text-slate-500 mt-2 pt-1 border-t border-slate-900">
                        <span>Active: <strong class="text-slate-300">${r.total_courtrooms}</strong></span>
                        <span class="font-mono text-emerald-400">${r.healthy_pct}%</span>
                    </div>
                </div>
                `;
            }).join('');
        }
    } catch (e) {
        console.warn("Fleet poll failed:", e.message);
    }
}

// 6. Poll Incidents Feed
async function pollIncidents() {
    try {
        const res = await fetch('/api/v1/incidents?limit=10');
        if (!res.ok) return;
        const data = await res.json();
        const container = document.getElementById('incidents-container');

        if (container && data.incidents && data.incidents.length > 0) {
            container.innerHTML = data.incidents.map(inc => {
                const dateStr = inc.created_at ? new Date(inc.created_at).toLocaleTimeString() : "--";
                return `
                <div class="bg-slate-950 border border-slate-800 rounded-lg p-2.5 space-y-1 text-xs">
                    <div class="flex justify-between items-center">
                        <span class="font-mono font-semibold text-rose-400">${inc.courtroom_id}</span>
                        <span class="text-[10px] text-slate-500">${dateStr}</span>
                    </div>
                    <p class="text-slate-300 font-medium truncate">${inc.title}</p>
                    <div class="flex items-center space-x-2 text-[10px] pt-1">
                        <span class="px-1.5 py-0.5 rounded bg-slate-900 text-slate-400 border border-slate-800">Slack: ${inc.slack_status}</span>
                        <span class="px-1.5 py-0.5 rounded bg-slate-900 text-slate-400 border border-slate-800">Linear: ${inc.linear_status}</span>
                    </div>
                </div>
                `;
            }).join('');
        }
    } catch (e) {
        console.warn("Incident poll failed:", e.message);
    }
}

// 7. Manual Airtable Sync Button
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

// Initial boot
pollFleetOverview();
pollIncidents();
setInterval(pollFleetOverview, 5000);
setInterval(pollIncidents, 5000);
