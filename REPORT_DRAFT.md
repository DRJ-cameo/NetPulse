# NetPulse: Network Performance Measurement Tool

## 1. Abstract
NetPulse is a Python-based educational prototype for measuring network throughput, latency, and jitter. It uses ping requests for round-trip latency, calculates jitter from consecutive RTT samples, and estimates download throughput using an HTTP download. It also contains a simplified simulation inspired by patent WO2008127154A1, which describes reference packet probing to reduce dedicated measurement traffic.

## 2. Introduction
Network performance affects web browsing, video calls, online gaming, and file transfer. Throughput indicates data transfer rate, latency indicates delay, and jitter indicates variation in delay. Measuring these values helps identify network quality issues.

## 3. Objectives
- Measure round-trip latency using ping.
- Calculate jitter from consecutive latency values.
- Estimate download throughput.
- Demonstrate the reference-packet probing concept from a published patent.
- Compare conventional dedicated probe overhead with a simplified reference-packet approach.

## 4. Patent Details
**Title:** Measuring network performance with reference packet probing  
**Publication number:** WO2008127154A1  
**Publication date:** 23 October 2008  
**Assignee:** Telefonaktiebolaget LM Ericsson AB  
**Patent link:** https://patents.google.com/patent/WO2008127154A1/en

The patent describes sending a payload packet and a related reference packet. The receiving side records packet arrival timestamps. Send and receive information, including timestamps, packet size, and packet identifiers, can be used to estimate network performance. The aim is to reduce extra network load caused by dedicated probing packets.

## 5. Methodology
### 5.1 Latency
The application sends 10 ping requests to a target host and collects successful round-trip times. Average RTT is calculated as sum of RTT values divided by number of successful replies.

### 5.2 Jitter
Jitter is calculated as the mean absolute difference between consecutive RTT values:
Jitter = sum(abs(RTT[i] - RTT[i-1])) / (n-1).

### 5.3 Throughput
The application downloads a 5 MB test object. Throughput in Mbps is calculated as (downloaded bytes × 8) / elapsed seconds / 1,000,000.

### 5.4 Patent-inspired simulation
The simulation creates payload packet records and associated reference packet counts. It illustrates timestamp-based measurement and compares the bytes used by dedicated probes with the bytes used by reference packets. This is a simplified educational model, not a full reproduction of the patent.

## 6. Implementation and Results
Insert screenshots of:
1. NetPulse home page.
2. Live latency and jitter results.
3. Throughput result.
4. Reference packet simulation and overhead comparison.

Record your actual measured results here:
- Target host:
- Average latency:
- Average jitter:
- Throughput:
- Payload packet count:
- Reference packet count:
- Simulated overhead reduction:

Do not invent results. Use screenshots and values from your own run.

## 7. Comparison
| Parameter | Conventional measurement | Reference-packet concept |
|---|---|---|
| Measurement traffic | Separate dedicated probes | Payload plus associated reference packet |
| Timing information | Probe timestamps | Send/receive timing associated with payload and reference |
| Main aim | Measure network characteristics | Reduce dedicated probing overhead |
| In this project | Explained as baseline | Demonstrated through simplified simulation |

## 8. Conclusion
NetPulse demonstrates basic network performance measurement. It calculates throughput, round-trip latency, and jitter, and provides an educational simulation of reference packet probing. The project shows how timestamp information associated with payload and reference packets can help estimate network performance while reducing dedicated probe traffic.

## 9. References
1. WO2008127154A1, Measuring network performance with reference packet probing, Google Patents, https://patents.google.com/patent/WO2008127154A1/en
2. Python documentation, https://docs.python.org/3/
3. Streamlit documentation, https://docs.streamlit.io/
