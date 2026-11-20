import platform
import re
import subprocess
import time
import statistics
import requests
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

st.set_page_config(page_title="NetPulse", page_icon="📡", layout="wide")

st.title("📡 NetPulse")
st.caption("Network Performance Measurement Tool | Throughput • Latency • Jitter")
st.info("Educational prototype. Real-network tests use ping and an HTTP download. The patent-inspired reference-packet section is a simulation.")

def run_ping(host, count=10):
    system = platform.system().lower()
    if system == "windows":
        cmd = ["ping", "-n", str(count), "-w", "1500", host]
    else:
        # macOS and Linux use -c for count. -W is supported by Linux;
        # macOS uses -W in milliseconds on current releases.
        cmd = ["ping", "-c", str(count), "-W", "1500", host]
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=25)
        output = result.stdout + "\n" + result.stderr
        # Matches time=12.3 ms, time<1ms and time=12 ms
        values = []
        for match in re.finditer(r"time\s*[=<]\s*([0-9.]+)\s*ms", output, re.I):
            values.append(float(match.group(1)))
        # Windows may report time=12ms without a space
        if not values:
            for match in re.finditer(r"time\s*[=<]\s*([0-9.]+)\s*ms", output, re.I):
                values.append(float(match.group(1)))
        if not values:
            return None, output
        return values, output
    except Exception as exc:
        return None, str(exc)

def download_test():
    url = "https://speed.cloudflare.com/__down?bytes=5000000"
    start = time.perf_counter()
    response = requests.get(url, timeout=30)
    response.raise_for_status()
    elapsed = time.perf_counter() - start
    size_bytes = len(response.content)
    mbps = (size_bytes * 8) / elapsed / 1_000_000
    return mbps, size_bytes, elapsed

tab1, tab2, tab3 = st.tabs(["Live Network Test", "Patent-Inspired Simulation", "About & Formulas"])

with tab1:
    st.subheader("Measure your current network connection")
    host = st.text_input("Ping target", value="1.1.1.1", help="Use a reachable host such as 1.1.1.1 or 8.8.8.8.")
    if st.button("Run Network Test", type="primary"):
        if not host.strip():
            st.error("Please enter a valid host.")
        else:
            with st.spinner("Measuring latency and jitter..."):
                pings, raw = run_ping(host.strip(), 10)
            if pings:
                avg_latency = statistics.mean(pings)
                jitter = statistics.mean(abs(pings[i] - pings[i-1]) for i in range(1, len(pings))) if len(pings) > 1 else 0
                c1, c2 = st.columns(2)
                c1.metric("Average latency", f"{avg_latency:.2f} ms")
                c2.metric("Average jitter", f"{jitter:.2f} ms")
                st.write("Individual round-trip times")
                st.line_chart(pd.DataFrame({"RTT (ms)": pings}))
                st.caption(f"Successful replies: {len(pings)}")
            else:
                st.warning("Ping did not return measurable replies. Check your internet connection, firewall, or target host.")
                with st.expander("Technical output"):
                    st.code(raw)

            st.divider()
            st.subheader("Throughput test")
            st.caption("Downloads a 5 MB test file from Cloudflare. This uses internet data.")
            try:
                with st.spinner("Downloading test data..."):
                    mbps, size_bytes, elapsed = download_test()
                st.metric("Measured download throughput", f"{mbps:.2f} Mbps")
                st.write(f"Transferred **{size_bytes / 1_000_000:.2f} MB** in **{elapsed:.2f} seconds**.")
            except Exception as exc:
                st.error(f"Throughput test could not complete: {exc}")
                st.caption("Check internet access or try again later.")

with tab2:
    st.subheader("Reference Packet Probing — Patent-inspired demonstration")
    st.markdown("""
    The selected published patent, **WO2008127154A1**, describes sending a payload packet
    together with a small reference packet. Send/receive timestamps and packet information
    are compared to estimate network performance while reducing dedicated probing traffic.
    This page is an educational simulation of that principle, not a reproduction of the full patent.
    """)
    payload_count = st.slider("Number of payload packets", 5, 50, 20)
    reference_every = st.slider("Send one reference packet after every N payload packets", 1, 10, 5)
    if st.button("Run Patent-Inspired Simulation"):
        # Deterministic illustrative network: each payload is 1200 bytes;
        # a conventional dedicated probe is 64 bytes; reference is 32 bytes.
        payload_size = 1200
        conventional_probe_size = 64
        reference_size = 32
        payload_total = payload_count * payload_size
        reference_count = (payload_count + reference_every - 1) // reference_every
        standard_probe_total = payload_count * conventional_probe_size
        reference_total = reference_count * reference_size
        reduction = (1 - reference_total / standard_probe_total) * 100 if standard_probe_total else 0

        rows = []
        base_delay = 24.0
        for i in range(payload_count):
            send_t = i * 0.010
            # Small deterministic variation to illustrate arrival-time variation
            network_delay = base_delay + (i % 4) * 1.5
            recv_t = send_t + network_delay / 1000
            rows.append({"Payload ID": i + 1, "Send time (s)": send_t,
                         "Receive time (s)": recv_t, "Illustrative delay (ms)": network_delay})
        df = pd.DataFrame(rows)
        st.success("Simulation completed.")
        a, b, c = st.columns(3)
        a.metric("Payload packets", payload_count)
        b.metric("Reference packets", reference_count)
        c.metric("Reference data overhead", f"{reference_total} bytes")
        st.write("Illustrative packet timestamp records")
        st.dataframe(df, use_container_width=True, hide_index=True)
        st.line_chart(df.set_index("Payload ID")[["Illustrative delay (ms)"]])
        st.markdown("**Overhead comparison (illustrative):**")
        st.write(f"- Conventional dedicated probes: {standard_probe_total} bytes")
        st.write(f"- Reference packets: {reference_total} bytes")
        st.write(f"- Reduction in dedicated probe bytes: **{reduction:.1f}%**")
        st.caption("This overhead comparison is a simplified teaching model. Actual performance depends on packet sizes, traffic patterns, implementation, and network conditions.")

with tab3:
    st.subheader("Measurement formulas")
    st.markdown(r"""
    **Throughput**
    \[
    Throughput = \frac{Data\ transferred\ (bits)}{Time\ (seconds)}
    \]
    **Average latency (RTT)**
    \[
    Average\ RTT = \frac{\sum RTT_i}{n}
    \]
    **Jitter (mean absolute difference of consecutive RTTs)**
    \[
    Jitter = \frac{\sum_{i=2}^{n}|RTT_i-RTT_{i-1}|}{n-1}
    \]
    """)
    st.markdown("""
    **Patent idea in simple words:** A sender transmits a payload packet and a related reference packet.
    The receiver records arrival information. Comparing send-side and receive-side timing information
    helps estimate network characteristics while reducing the need for many separate test packets.
    """)
    st.caption("Patent: WO2008127154A1 — Measuring network performance with reference packet probing.")
    st.caption("Note: RTT ping measurement is round-trip latency. One-way latency requires synchronized clocks or receiver-side timestamping.")
