import platform
import re
import subprocess
import time
import statistics
import math
import random

import requests
import streamlit as st
import pandas as pd

st.set_page_config(page_title="NetPulse Enhanced", page_icon="📡", layout="wide")
st.title("📡 NetPulse")
st.caption("Network Performance Measurement | Throughput • Latency • Jitter • Loss-aware reference sampling")

st.info(
    "Live measurements use ping and an HTTP download. The patent-inspired and enhanced "
    "reference-packet sections are simulations; they do not transmit the patent's packet format."
)

def run_ping(host, count=10):
    if platform.system().lower() == "windows":
        cmd = ["ping", "-n", str(count), "-w", "1500", host]
    else:
        cmd = ["ping", "-c", str(count), "-W", "1500", host]
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=25)
        output = result.stdout + "\n" + result.stderr
        values = [
            float(m.group(1))
            for m in re.finditer(r"time\s*[=<]\s*([0-9.]+)\s*ms", output, re.I)
        ]
        return values, output
    except Exception as exc:
        return [], str(exc)

def download_test():
    url = "https://speed.cloudflare.com/__down?bytes=5000000"
    start = time.perf_counter()
    response = requests.get(url, timeout=30)
    response.raise_for_status()
    elapsed = time.perf_counter() - start
    size_bytes = len(response.content)
    mbps = (size_bytes * 8) / elapsed / 1_000_000
    return mbps, size_bytes, elapsed

def mean_abs_jitter(values):
    if len(values) < 2:
        return 0.0
    return statistics.mean(abs(values[i] - values[i-1]) for i in range(1, len(values)))

tabs = st.tabs([
    "Live Network Test",
    "Patent-Inspired Simulation",
    "Enhanced Loss-Aware Simulation",
    "About & Formulas"
])

with tabs[0]:
    st.subheader("Measure your current network connection")
    host = st.text_input("Ping target", "1.1.1.1")
    if st.button("Run Network Test", type="primary"):
        with st.spinner("Measuring latency and jitter..."):
            pings, raw = run_ping(host.strip(), 10)
        if pings:
            avg = statistics.mean(pings)
            jit = mean_abs_jitter(pings)
            c1, c2, c3 = st.columns(3)
            c1.metric("Average latency (RTT)", f"{avg:.2f} ms")
            c2.metric("Average jitter*", f"{jit:.2f} ms")
            c3.metric("Successful replies", len(pings))
            st.line_chart(pd.DataFrame({"RTT (ms)": pings}))
            st.caption("*Jitter here is the mean absolute difference between consecutive RTT samples.")
        else:
            st.warning("No measurable ping replies. Check the host, firewall, or network.")
            st.code(raw)

        st.divider()
        st.subheader("Throughput test")
        st.caption("Downloads a 5 MB test object from Cloudflare; this uses internet data.")
        try:
            with st.spinner("Downloading test data..."):
                mbps, size_bytes, elapsed = download_test()
            st.metric("Measured download throughput", f"{mbps:.2f} Mbps")
            st.write(f"Transferred **{size_bytes / 1_000_000:.2f} MB** in **{elapsed:.2f} seconds**.")
        except Exception as exc:
            st.error(f"Throughput test could not complete: {exc}")

with tabs[1]:
    st.subheader("Reference Packet Probing — simplified patent-inspired demonstration")
    st.markdown(
        "Patent **WO2008127154A1** describes sending payload and reference packets in connection "
        "with one another and using send/receive information to estimate network performance. "
        "This tab is a teaching simulation, not a reproduction of the full patent."
    )
    count = st.slider("Number of payload packets", 5, 100, 20, key="base_count")
    interval = st.slider("Send one reference packet after every N payload packets", 1, 10, 5, key="base_interval")
    if st.button("Run Patent-Inspired Simulation"):
        ref_count = math.ceil(count / interval)
        ref_bytes = ref_count * 32
        conventional_bytes = count * 64
        reduction = (1 - ref_bytes / conventional_bytes) * 100 if conventional_bytes else 0
        rows = []
        for i in range(count):
            send = i * 0.010
            delay = 24 + (i % 4) * 1.5
            rows.append({
                "Payload ID": i + 1,
                "Send time (s)": round(send, 4),
                "Receive time (s)": round(send + delay / 1000, 4),
                "Illustrative delay (ms)": delay
            })
        a, b, c = st.columns(3)
        a.metric("Payload packets", count)
        b.metric("Reference packets", ref_count)
        c.metric("Reference overhead", f"{ref_bytes} bytes")
        st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)
        st.line_chart(pd.DataFrame(rows).set_index("Payload ID")[["Illustrative delay (ms)"]])
        st.markdown("**Illustrative overhead comparison**")
        st.write(f"- Conventional dedicated probes: {conventional_bytes} bytes")
        st.write(f"- Reference packets: {ref_bytes} bytes")
        st.write(f"- Modelled reduction: **{reduction:.1f}%**")
        st.caption("The result depends entirely on the assumed packet sizes and selected interval.")

with tabs[2]:
    st.subheader("Proposed improvement: Loss-aware adaptive reference sampling")
    st.markdown(
        """
        **Research gap addressed:** the selected patent explains the payload/reference-packet
        measurement mechanism and discusses packet identifiers that can help identify loss or
        reordering. This prototype adds an explicit, user-visible policy for changing the reference
        sampling interval according to simulated network instability. It compares a fixed interval
        with an adaptive interval. This is a proposed extension for this student prototype, not a
        claim that the patent or all later research lacks adaptive methods.
        """
    )
    st.caption("All values in this tab are generated in a controlled simulation; they are not live packet captures.")
    n = st.slider("Payload packets to simulate", 20, 200, 60, 10, key="enh_n")
    loss_pct = st.slider("Simulated packet loss (%)", 0, 30, 5, key="enh_loss")
    jitter_level = st.slider("Simulated delay variation (ms)", 1, 40, 8, key="enh_jitter")
    seed = st.number_input("Repeatable simulation seed", min_value=1, max_value=99999, value=42, key="enh_seed")

    # Explicit adaptive rule: sample more often when the simulated path is unstable.
    if loss_pct >= 10 or jitter_level >= 20:
        adaptive_interval = 1
        condition = "High instability: reference every payload"
    elif loss_pct >= 5 or jitter_level >= 10:
        adaptive_interval = 2
        condition = "Moderate instability: reference every 2 payloads"
    else:
        adaptive_interval = 5
        condition = "Stable condition: reference every 5 payloads"

    if st.button("Run Enhanced Simulation", type="primary"):
        rng = random.Random(int(seed))
        received = []
        records = []
        base_delay = 35.0

        for seq in range(1, n + 1):
            lost = rng.random() < (loss_pct / 100.0)
            noise = rng.uniform(-jitter_level, jitter_level)
            delay = max(1.0, base_delay + noise)
            send_time = seq * 0.010
            arrival_time = send_time + delay / 1000.0
            if not lost:
                received.append((arrival_time, seq, delay))
            records.append({
                "Sequence ID": seq,
                "Status": "Lost" if lost else "Received",
                "Illustrative delay (ms)": None if lost else round(delay, 2),
                "Arrival time (s)": None if lost else round(arrival_time, 5)
            })

        # Determine reordering by comparing arrival sequence with original sequence.
        arrival_order = [seq for _, seq, _ in sorted(received)]
        reordering_events = sum(
            1 for i in range(1, len(arrival_order)) if arrival_order[i] < arrival_order[i-1]
        )
        received_delays = [d for _, _, d in received]
        observed_jitter = mean_abs_jitter(received_delays)
        actual_lost = n - len(received)
        measured_loss_pct = (actual_lost / n) * 100

        fixed_interval = 5
        fixed_refs = math.ceil(n / fixed_interval)
        adaptive_refs = math.ceil(n / adaptive_interval)
        reference_size = 32
        fixed_overhead = fixed_refs * reference_size
        adaptive_overhead = adaptive_refs * reference_size
        conventional_overhead = n * 64
        adaptive_vs_fixed = (
            (1 - adaptive_overhead / fixed_overhead) * 100 if fixed_overhead else 0
        )
        adaptive_vs_conventional = (
            (1 - adaptive_overhead / conventional_overhead) * 100
            if conventional_overhead else 0
        )

        st.success(f"Simulation completed. Policy selected: {condition}.")
        m1, m2, m3, m4 = st.columns(4)
        m1.metric("Received packets", len(received))
        m2.metric("Detected lost packets", actual_lost)
        m3.metric("Observed delay variation*", f"{observed_jitter:.2f} ms")
        m4.metric("Reordering events", reordering_events)

        st.markdown("**Adaptive policy decision**")
        st.write(f"Selected reference interval: **1 reference packet per {adaptive_interval} payload packet(s)**.")
        st.write(f"Fixed policy: one reference packet per {fixed_interval} payload packets.")

        comparison = pd.DataFrame([
            {"Method": "Conventional dedicated probes", "Probe/reference bytes": conventional_overhead},
            {"Method": "Fixed reference interval (5)", "Probe/reference bytes": fixed_overhead},
            {"Method": f"Adaptive reference interval ({adaptive_interval})", "Probe/reference bytes": adaptive_overhead}
        ])
        st.dataframe(comparison, use_container_width=True, hide_index=True)
        st.bar_chart(comparison.set_index("Method"))
        st.write(f"Adaptive overhead vs fixed interval: **{adaptive_vs_fixed:.1f}%** (positive means fewer bytes; negative means more bytes).")
        st.write(f"Adaptive overhead vs conventional baseline: **{adaptive_vs_conventional:.1f}%** (under the model assumptions).")

        st.markdown("**Packet sequence log**")
        st.dataframe(pd.DataFrame(records), use_container_width=True, hide_index=True)
        st.caption(
            "*Delay variation is calculated as the mean absolute difference between consecutive "
            "received-packet delay samples in this simulation. Reordering is estimated by comparing "
            "arrival order with sequence-ID order. This is an educational model, not a live network experiment."
        )
        st.warning(
            "Interpretation: the adaptive policy increases reference frequency when loss or delay "
            "variation is high. This can improve observation granularity, but it also increases "
            "measurement overhead. The trade-off must be tested on real sender/receiver endpoints "
            "before making performance claims."
        )

with tabs[3]:
    st.subheader("Definitions and formulas")
    st.markdown("""
    **Throughput**

    `Throughput (Mbps) = downloaded bytes × 8 / elapsed seconds / 1,000,000`

    **Average round-trip latency**

    `Average RTT = sum of successful RTT samples / number of successful replies`

    **Jitter used by this application**

    `Mean absolute consecutive RTT difference = mean(abs(RTT[i] - RTT[i-1]))`

    **Packet loss rate**

    `Loss rate (%) = lost packets / transmitted packets × 100`

    **Probe overhead**

    `Probe overhead (bytes) = number of measurement packets × assumed bytes per packet`
    """)
    st.markdown(
        "The selected patent describes payload/reference packet timing and identifiers. "
        "The IETF also distinguishes active, passive, and hybrid measurement methods (RFC 7799). "
        "RFC 3393 defines IP packet delay variation and notes that 'jitter' is used inconsistently."
    )
    st.caption("Patent: WO2008127154A1. Standards references: RFC 7799 and RFC 3393.")
