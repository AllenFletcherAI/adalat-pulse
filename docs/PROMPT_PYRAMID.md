# THE PROMPT PYRAMID: OUTCOME-DRIVEN AI ARCHITECTURE
**System:** Adalat-Pulse  
**Author:** Allen Fletcher (Associate Candidate, CTO's Office, Adalat AI)  
**Standard:** ASD-STE100 Simplified Technical English  

---

## 1. Executive Thesis

There is a fundamental divide between how top engineering teams (such as Anthropic) operate autonomous AI systems and how conventional operators use them:

* **The Conventional Approach (Instruction-Heavy):** Operators write massive, brittle prompts detailing every tiny sequential step. When physical realities shift (a monsoon breaks a fiber line, or a rural courtroom fan runs at high speed), rigid instruction sequences break down.
* **The Engineering Approach (Outcome-Driven):** Engineers define the **non-negotiable finished outcome**, grant the agent autonomous research capabilities to survey the ground truth, conduct interactive interviews to resolve ambiguities, and benchmark against a **golden standard exemplar**.

This document details how `Adalat-Pulse` implements the **Prompt Pyramid** across **11 partner states** and **6,000+ judges**.

---

## 2. The 4 Levels of the Prompt Pyramid

```text
               ▲
              / \
             / L4\      LEVEL 4: What Good Looks Like (Golden Exemplars)
            /-----\     • Delhi HC Bench 04 Baseline
           /   L3  \    • District Dual-ISP Baseline
          /---------\   • Rural Taluka 4G Baseline
         /     L2    \
        /-------------\ LEVEL 3: The Interactive Interview
       /       L1      \• Dynamic dialogue resolving degraded edge telemetry
      /-----------------\• Direct operator remediation ("Ceiling fan turned off")
                         
                        LEVEL 2: Autonomous Edge Research
                        • 5-Second real-time FFT noise floor audit
                        • WebSocket burst probe measuring latency, jitter, loss

                        LEVEL 1: Goal First (The Outcome)
                        • "100% Zero-Word-Drop Koyal Indic ASR Guarantee"
```

---

### Level 1: Start with the Goal (Outcome Over Instructions)
Instead of instructing the system with a rigid checklist (*"read latency, then read packet loss, then write to database"*), the operational gateway is anchored to a legal business outcome:

> **The Level 1 Goal:**  
> *"Guarantee uninterrupted, zero-word-drop Indic speech-to-text (Koyal ASR) for the duration of the court session, preventing trial delays, transcription desynchronization, and acoustic hallucinations."*

By anchoring to the outcome, every downstream check exists solely to protect this guarantee.

---

### Level 2: Autonomous Edge Research (Survey Ground Truth First)
Before an agent or gateway proposes a decision, it must inspect the physical environment. In `Adalat-Pulse`, this is accomplished via real hardware and network probing:
1. **Web Audio API Hardware Probe:** Inspects `audioContext.sampleRate` directly from physical microphone hardware (ensuring $\ge 16\text{ kHz}$) and runs an `AnalyserNode` FFT loop to calculate actual ambient room noise floor (SNR in dB).
2. **WebSocket Keepalive Burst Probe:** Transmits 20 timestamped frames over `/ws/probe` to calculate actual round-trip time, packet jitter, and packet drop rates across rural broadband or cellular connections.

---

### Level 3: The Interactive Interview (Clarify Before Deciding)
Conventional systems either silently fail or blindly sound alarms when numbers enter gray areas. The Prompt Pyramid introduces the **Interactive Interview**:
* When telemetry falls into a degraded bracket ($12\text{ dB} \le \text{SNR} < 20\text{ dB}$ or $0.5\% < \text{loss} \le 2.0\%$), the gateway does not guess.
* It presents the courtroom technical officer with a targeted 2-question interview:
  * *Question Q-AUDIO-FAN:* "Is the high-speed ceiling fan or AC running directly above the boundary microphone?"
  * *Options:* `Ceiling Fan Turned Off (Remediation Applied)` | `Fan on Low Speed` | `Cannot Turn Off`
* If the officer selects "Remediation Applied", the engine applies a calibrated $+6.0\text{ dB}$ acoustic clearance and re-evaluates the verdict to `OPTIMAL` without canceling the court hearing.

---

### Level 4: Show What Good Looks Like (Certified Golden Baselines)
Instead of comparing telemetry against arbitrary scalar numbers, `Adalat-Pulse` compares live readings against **Certified Golden Exemplars**:

| Profile ID | Courtroom Tier | Latency Target | Loss Target | SNR Target | Certified Hardware Stack |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **`GOLDEN-HC-FIBER`** | High Court | $\le 35\text{ ms}$ | $0.0\%$ | $\ge 28\text{ dB}$ | Dedicated 1 Gbps Leased Line + Shure MX393 Mics |
| **`GOLDEN-DC-HYBRID`** | District Court | $\le 70\text{ ms}$ | $\le 0.2\%$ | $\ge 22\text{ dB}$ | Dual 100 Mbps (BSNL + Airtel) + Digital Array |
| **`GOLDEN-TL-EDGE`** | Taluka Sub-Division | $\le 110\text{ ms}$ | $\le 0.5\%$ | $\ge 18\text{ dB}$ | Bonded 4G Dongles (Jio + Airtel) + Noise-Canceling Mic |

The system computes a **Golden Alignment Score (0–100%)** displaying live deltas:
$$\Delta_{\text{latency}} = \text{measured} - \text{target}, \quad \Delta_{\text{loss}} = \text{measured} - \text{target}, \quad \Delta_{\text{SNR}} = \text{measured} - \text{target}$$

This gives the CTO's Office an instant visual benchmark of which courtrooms are performing at the gold standard and which require infrastructure upgrades.

---

## 3. Operational Impact for Adalat AI

Across 11 states and 6,000+ judges, applying the Prompt Pyramid transforms field operations:
1. **Reduces False Alarms:** Interactive technician interviews prevent unnecessary session postponements.
2. **Eliminates Hallucinations:** Strict 16 kHz sample rate and 2.0% packet loss gates halt compromised sessions before judges experience transcription lag.
3. **Transparent CTO Telemetry:** Partner state coordinators and CTO leaders view real-time Golden Alignment across every district bench.
