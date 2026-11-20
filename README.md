# NetPulse — Network Performance Measurement Tool

## Features
1. Live latency measurement using system ping (10 requests).
2. Jitter calculated as the mean absolute difference between consecutive RTT samples.
3. Download throughput measured using a 5 MB HTTP download from Cloudflare.
4. Patent-inspired reference-packet simulation with timestamp records and a simplified probe-overhead comparison.

## Patent reference
WO2008127154A1 — "Measuring network performance with reference packet probing"
Google Patents: https://patents.google.com/patent/WO2008127154A1/en

The patent describes sending a payload packet and a related reference packet, recording send/receive timing information, and using it to estimate network performance with reduced dedicated probing overhead.

IMPORTANT: The simulation is an educational simplification inspired by the published patent. It is not a reproduction of the complete patented system. Register the patent number with your instructor before final submission.

## Requirements
- Python 3.9+
- Internet connection for the live throughput test
- Ping utility available on the operating system

## Installation
Open Terminal / Command Prompt in this folder:

```bash
python -m venv venv
```

Activate the environment:

macOS/Linux:
```bash
source venv/bin/activate
```

Windows:
```bash
venv\\Scripts\\activate
```

Install packages:
```bash
pip install -r requirements.txt
```

Run:
```bash
streamlit run app.py
```

A browser tab should open. If not, visit http://localhost:8501.

## How to demonstrate
1. Open Live Network Test.
2. Keep target as 1.1.1.1 and click Run Network Test.
3. Show average RTT and jitter, then throughput.
4. Open Patent-Inspired Simulation.
5. Change the reference packet interval and run the simulation.
6. Explain that reference packets carry timing/identification information associated with payload packets, helping estimate performance with lower dedicated probe overhead.

## Limitations
- Ping may be blocked by some networks or firewalls.
- Throughput depends on internet conditions and the remote test server.
- RTT is round-trip time, not one-way latency.
- The patent demonstration is a simplified simulation, not a complete implementation of the patent claims.
