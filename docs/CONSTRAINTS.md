# SAFETY CONSTRAINTS & THRESHOLDS: ADALAT-PULSE
**Standard:** ASD-STE100 Simplified Technical English  
**System:** Adalat-Pulse  

---

## 1. Hard Safety Rules

1. **NEVER** clear a courtroom session (`can_start_session = True`) if any single metric breaches the `CRITICAL` boundary.
2. **NEVER** accept audio sample rates below `16000 Hz`. The Koyal Indic acoustic models cannot extract phonetic features below 16 kHz.
3. **NEVER** store plain-text API keys or webhook secrets in public git commits. All secrets must reside in `.env`.
4. **ALWAYS** enforce Write-Ahead Logging (`PRAGMA journal_mode=WAL;`) on SQLite connections to prevent lock contention.
5. **ALWAYS** sanitize and uppercase courtroom identification codes (e.g. `DL-HC-CRT04`).
6. **ONLY** accept state codes registered in the 11 partner state directory (`KL`, `KA`, `AP`, `MH`, `DL`, `TN`, `UP`, `WB`, `GJ`, `RJ`, `MP`).
7. **ONLY** dispatch high-priority Slack and Linear incidents when a deterministic quality gate is breached.

---

## 2. Telemetry Quality Gate Thresholds (Koyal Indic ASR)

| Metric | Optimal Gate | Degraded Warning | Critical Breach | Root Cause & Operational Impact |
| :--- | :--- | :--- | :--- | :--- |
| **Packet Loss** | $\le 0.5\%$ | $0.51\% - 2.0\%$ | $> 2.0\%$ | WebSocket drops audio frames; ASR halts or produces hallucinations. |
| **Network Latency** | $\le 120\text{ ms}$ | $121 - 300\text{ ms}$ | $> 300\text{ ms}$ | Sub-second live transcription turns into unacceptable lag for stenographer. |
| **Packet Jitter** | $\le 15\text{ ms}$ | $16 - 40\text{ ms}$ | $> 40\text{ ms}$ | Audio buffer underflow causes choppy phoneme input. |
| **WebSocket RTT** | $\le 150\text{ ms}$ | $151 - 350\text{ ms}$ | $> 350\text{ ms}$ | Heartbeat timeout risk; edge gateway disconnects. |
| **Mic Sample Rate**| $16\text{ kHz}$ or $48\text{ kHz}$ | Non-standard rate | $< 16\text{ kHz}$ | Acoustic models fail to extract phonetic features below 16 kHz. |
| **Ambient Noise (SNR)**| $\ge 20\text{ dB}$ | $12.0 - 19.9\text{ dB}$ | $< 12.0\text{ dB}$ | Ceiling fans and courtroom chatter mask speech signals. |
