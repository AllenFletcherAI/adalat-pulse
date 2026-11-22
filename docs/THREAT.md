# THREAT MODEL & SECURITY POSTURE: ADALAT-PULSE
**Standard:** ASD-STE100 Simplified Technical English  
**System:** Adalat-Pulse  

---

## 1. The 5 Attacker Profiles & Defensive Countermeasures

| Attacker Profile | Attack Vector / Attempted Door | Potential Damage | Defensive Lock in Adalat-Pulse |
| :--- | :--- | :--- | :--- |
| **1. Rogue Field Operator** | Submits fake "OPTIMAL" telemetry for a degraded courtroom network. | Poor ASR audio; transcription freezes during judge's hearing. | Pre-flight probe requires live WebSocket round-trip verification and Web Audio hardware inspection; audit logs stored immutably in SQLite WAL. |
| **2. Edge Network Hijacker** | Intercepts or tampers with telemetry packets in transit (Man-in-the-Middle). | Spoofed alerts or suppressed failure notices. | Production deployment runs exclusively over TLS (HTTPS/WSS) with strict CORS policies. Payload schemas strictly validated via Pydantic v2. |
| **3. Malicious Scraper / Flooder** | Floods `/api/v1/telemetry/report` with thousands of bogus courtroom requests. | Gateway CPU exhaustion, SQLite database lock contention. | Strict Pydantic boundary validation (e.g. state code validation, string length limits); rate-limiting via reverse proxy; fast rejection of malformed payloads. |
| **4. Database Exfiltrator** | Attempts SQL injection through courtroom ID or bench name parameters. | Unauthorized reading of courtroom metadata. | Zero string concatenation in database queries. Every query uses parameterized SQLite binding (`?` placeholders) and strict type enforcement. |
| **5. Secret Leaker** | Commits API keys or tokens into version control. | Exposure of Airtable, Slack, or Linear tokens to the public. | Comprehensive `.gitignore` covering `.env`, `.env.local`, and SQLite files. Sanitized `.env.example` provided for safe public viewing. |

---

## 2. API Integrity & Authentication Rules

- **Input Sanitization:** Courtroom IDs are strictly normalized and stripped of control characters.
- **State Code Enums:** Only 11 predefined Indian state codes are accepted. Any request containing unregistered states is rejected at the API boundary with HTTP 422.
- **Non-Root Execution:** Docker containers run as a dedicated, unprivileged system user (`adalat_ops`, UID 1001).
- **Graceful Failure Isolation:** Failures in third-party APIs (Slack, Linear, or Airtable) are trapped asynchronously and logged to SQLite without halting the core telemetry ingestion loop.
