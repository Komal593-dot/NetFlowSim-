import time
import random
import json
import streamlit as st
import plotly.graph_objects as go
import pandas as pd
import networkx as nx

from backend.network_manager import NetworkManager
from backend.simulation_engine import SimulationEngine
from algorithms.routing import RoutingEngine
from database.db import DatabaseManager

# --- PAGE INITIALIZATION ---
st.set_page_config(
    page_title="NetFlowSim — Enterprise NOC Dashboard",
    page_icon="📡",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- ADVANCED GRAFANA / DATADOG NOC DARK STYLING ---
st.markdown("""
<style>
    /* Dark Theme Core Base */
    .stApp {
        background-color: #030712 !important;
        color: #f8fafc !important;
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif !important;
    }
    
    /* Header Hide */
    header[data-testid="stHeader"] {
        background-color: rgba(3, 7, 18, 0.95) !important;
        backdrop-filter: blur(10px);
    }
    .block-container {
        padding-top: 1.5rem !important;
        padding-bottom: 2rem !important;
    }

    /* Enterprise NOC Header Banner */
    .noc-banner {
        background: linear-gradient(135deg, #0f172a 0%, #1e293b 100%);
        border: 1px solid #334155;
        border-left: 6px solid #38bdf8;
        padding: 20px 26px;
        border-radius: 12px;
        margin-bottom: 22px;
        box-shadow: 0 10px 25px -5px rgba(0, 0, 0, 0.6);
    }
    .noc-title {
        font-size: 24px;
        font-weight: 800;
        color: #38bdf8;
        letter-spacing: 0.8px;
        margin: 0;
        display: flex;
        align-items: center;
        gap: 12px;
    }
    .noc-subtitle {
        font-size: 13px;
        color: #94a3b8;
        margin-top: 4px;
    }

    /* Sidebar Navigation Button Cards */
    div[data-testid="stSidebar"] {
        background-color: #0b0f19 !important;
        border-right: 1px solid #1e293b;
    }
    
    div[data-testid="stSidebar"] .stButton > button {
        background: #1e293b !important;
        color: #94a3b8 !important;
        border: 1px solid #334155 !important;
        border-radius: 8px !important;
        padding: 12px 16px !important;
        font-weight: 600 !important;
        font-size: 13px !important;
        text-align: left !important;
        justify-content: flex-start !important;
        transition: all 0.2s ease-in-out !important;
        margin-bottom: 4px !important;
        box-shadow: 0 2px 4px rgba(0,0,0,0.2) !important;
    }
    div[data-testid="stSidebar"] .stButton > button:hover {
        background: #334155 !important;
        color: #38bdf8 !important;
        border-color: #38bdf8 !important;
        transform: translateX(4px) !important;
    }

    /* KPI Glassmorphism Metric Cards */
    [data-testid="stMetricValue"] {
        font-size: 32px !important;
        font-weight: 800 !important;
        color: #f8fafc !important;
    }
    [data-testid="stMetricLabel"] {
        font-size: 11px !important;
        font-weight: 700 !important;
        color: #64748b !important;
        text-transform: uppercase;
        letter-spacing: 0.8px;
    }
    [data-testid="stMetric"] {
        background: #0f172a !important;
        border: 1px solid #1e293b !important;
        padding: 18px !important;
        border-radius: 12px !important;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.4) !important;
    }

    /* Live Pulse Indicators */
    .pulse-green {
        display: inline-block;
        width: 10px;
        height: 10px;
        border-radius: 50%;
        background: #22c55e;
        box-shadow: 0 0 10px #22c55e;
        margin-right: 6px;
    }
    .pulse-red {
        display: inline-block;
        width: 10px;
        height: 10px;
        border-radius: 50%;
        background: #ef4444;
        box-shadow: 0 0 10px #ef4444;
        margin-right: 6px;
    }

    /* Router CLI Terminal Window */
    .cli-terminal {
        background-color: #020617;
        border: 1px solid #1e293b;
        border-top: 3px solid #38bdf8;
        border-radius: 8px;
        padding: 14px;
        font-family: 'Fira Code', 'Courier New', monospace;
        font-size: 12px;
        color: #38bdf8;
        height: 180px;
        overflow-y: auto;
        box-shadow: inset 0 2px 4px rgba(0,0,0,0.8);
    }
    .cli-line-info { color: #38bdf8; }
    .cli-line-warn { color: #facc15; }
    .cli-line-err { color: #f87171; }
    .cli-line-success { color: #4ade80; }

    /* Subsystem Status Panel */
    .status-panel {
        background-color: #0f172a;
        border: 1px solid #1e293b;
        border-radius: 10px;
        padding: 16px;
    }
    .status-row {
        display: flex;
        justify-content: space-between;
        align-items: center;
        padding: 8px 0;
        border-bottom: 1px solid #1e293b;
    }
    .status-row:last-child {
        border-bottom: none;
    }
    .badge-online {
        background-color: rgba(34, 197, 94, 0.15);
        color: #4ade80;
        border: 1px solid #22c55e;
        padding: 3px 8px;
        border-radius: 20px;
        font-size: 11px;
        font-weight: 700;
    }

    /* Alert Banner Boxes */
    .alert-banner-critical {
        background-color: rgba(239, 68, 68, 0.1);
        border: 1px solid #ef4444;
        border-left: 4px solid #ef4444;
        color: #fca5a5;
        padding: 14px 18px;
        border-radius: 8px;
        font-weight: 600;
        margin-bottom: 16px;
    }
    .alert-banner-normal {
        background-color: rgba(56, 189, 248, 0.1);
        border: 1px solid #38bdf8;
        border-left: 4px solid #38bdf8;
        color: #7dd3fc;
        padding: 14px 18px;
        border-radius: 8px;
        font-weight: 600;
        margin-bottom: 16px;
    }
</style>
""", unsafe_allow_html=True)


# --- INITIALIZE SESSION STATE & NETWORK BACKEND ---
if "network_mgr" not in st.session_state:
    nm = NetworkManager()
    nm.add_node("PC1", node_type="client")
    nm.add_node("Router1", node_type="router")
    nm.add_node("Router2", node_type="router")
    nm.add_node("Router3", node_type="router")
    nm.add_node("Server", node_type="server")

    nm.add_link("PC1", "Router1", bandwidth=100, delay=10)
    nm.add_link("Router1", "Router2", bandwidth=100, delay=20)
    nm.add_link("Router2", "Server", bandwidth=100, delay=15)
    nm.add_link("Router1", "Router3", bandwidth=100, delay=30)
    nm.add_link("Router3", "Server", bandwidth=100, delay=20)

    st.session_state.network_mgr = nm

if "active_tab" not in st.session_state:
    st.session_state.active_tab = "Dashboard"

if "cli_logs" not in st.session_state:
    st.session_state.cli_logs = [
        "[00:00:01] INFO  [NetFlowSim] NOC Subsystem initialized successfully.",
        "[00:00:02] INFO  [RoutingEngine] Topology map loaded. OSPF link state active.",
        "[00:00:02] SUCCESS [Database] Connected to SQLite backend data/netflowsim.db"
    ]

def add_cli_log(level, msg):
    timestamp = time.strftime("%H:%M:%S")
    st.session_state.cli_logs.append(f"[{timestamp}] {level} {msg}")
    if len(st.session_state.cli_logs) > 15:
        st.session_state.cli_logs.pop(0)

nm = st.session_state.network_mgr
sim_engine = SimulationEngine(nm)
db_mgr = DatabaseManager()


# --- SIDEBAR NAVIGATION ---
with st.sidebar:
    st.markdown("""
    <div style="padding: 10px 0 15px 0; text-align: left;">
        <div style="font-size: 22px; font-weight: 900; color: #38bdf8; letter-spacing: 1px;">NetFlowSim NOC</div>
        <div style="font-size: 11px; color: #64748b; font-weight: 700; letter-spacing: 0.5px; margin-top: 2px;">REALTIME INTELLIGENCE</div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("<div style='font-size: 10px; font-weight: 700; color: #64748b; margin-bottom: 6px;'>NOC MODULES</div>", unsafe_allow_html=True)

    modules = [
        ("Dashboard", "🖥️  Dashboard"),
        ("Simulation Console", "⚡  Simulation Console"),
        ("Network Topology", "🌐  Network Topology"),
        ("Traffic Analytics", "📊  Traffic Analytics"),
        ("Adaptive Routing", "🔀  Adaptive Routing"),
        ("Simulation Logs", "📜  Simulation Logs")
    ]

    for key, label in modules:
        is_active = (st.session_state.active_tab == key)
        if st.button(
            label,
            key=f"nav_{key}",
            use_container_width=True,
            type="primary" if is_active else "secondary"
        ):
            st.session_state.active_tab = key
            st.rerun()

    st.divider()
    
    st.markdown("<div style='font-size: 10px; font-weight: 700; color: #64748b; margin-bottom: 6px;'>REALTIME AUTOMATION</div>", unsafe_allow_html=True)
    live_mode = st.toggle("● LIVE NOC TELEMETRY", value=False)

    st.divider()
    st.markdown("<div style='font-size: 10px; font-weight: 700; color: #64748b; margin-bottom: 6px;'>QUICK CONTROLS</div>", unsafe_allow_html=True)
    if st.button("Reset Baseline State", use_container_width=True):
        for s, d, data in nm.get_network().edges(data=True):
            data["utilization"] = 0
            data["packet_loss"] = 0
            data["congestion"] = "LOW"
            data["traffic_mbps"] = 0
            data["queue_size"] = 0
            data["bandwidth"] = 100
        add_cli_log("WARN ", "[NetworkManager] All link utilization and physical states reset to baseline.")
        st.toast("Network baseline restored.", icon="⚙️")
        st.rerun()


# --- DYNAMIC TOPOLOGY RENDERER WITH GLOW & LOAD THICKNESS ---
def draw_interactive_topology(network, active_path=None):
    pos = {
        "PC1": (0, 1),
        "Router1": (1, 1),
        "Router2": (2, 2),
        "Router3": (2, 0),
        "Server": (3, 1)
    }

    traces = []

    for u, v, data in network.edges(data=True):
        x0, y0 = pos[u]
        x1, y1 = pos[v]
        
        util = data.get("utilization", 0)
        bw = data.get("bandwidth", 100)

        if bw == 0:
            color = '#ef4444'
            width = 1
        elif util >= 90:
            color = '#f87171'
            width = 6
        elif util >= 70:
            color = '#fbbf24'
            width = 4
        elif util >= 40:
            color = '#38bdf8'
            width = 3
        else:
            color = '#334155'
            width = 2

        edge_trace = go.Scatter(
            x=[x0, x1, None],
            y=[y0, y1, None],
            line=dict(width=width, color=color),
            hoverinfo='text',
            hovertext=f"Link: {u} ↔ {v}<br>Bandwidth: {bw} Mbps<br>Utilization: {util:.1f}%",
            mode='lines'
        )
        traces.append(edge_trace)

    node_x, node_y, node_labels, node_colors, hover_texts = [], [], [], [], []

    for node in network.nodes():
        x, y = pos[node]
        node_x.append(x)
        node_y.append(y)
        node_labels.append(node)
        
        ntype = network.nodes[node].get('type', 'router')
        if ntype == 'client':
            node_colors.append('#10b981')
        elif ntype == 'server':
            node_colors.append('#a855f7')
        else:
            node_colors.append('#0284c7')

        hover_texts.append(f"Node: <b>{node}</b><br>Type: {ntype.capitalize()}")

    node_trace = go.Scatter(
        x=node_x, y=node_y,
        mode='markers+text',
        hoverinfo='text',
        hovertext=hover_texts,
        text=[f"<b>{n}</b>" for n in node_labels],
        textposition="top center",
        marker=dict(
            size=36,
            color=node_colors,
            line=dict(width=3, color='#f8fafc')
        )
    )
    traces.append(node_trace)

    if active_path and len(active_path) > 1:
        path_x, path_y = [], []
        for i in range(len(active_path) - 1):
            u, v = active_path[i], active_path[i+1]
            x0, y0 = pos[u]
            x1, y1 = pos[v]
            path_x.extend([x0, x1, None])
            path_y.extend([path_y[0] if path_y else y0, y1, None]) if False else path_y.extend([y0, y1, None])

        path_trace = go.Scatter(
            x=path_x, y=path_y,
            line=dict(width=6, color='#22c55e'),
            hoverinfo='none',
            mode='lines'
        )
        traces.append(path_trace)

    fig = go.Figure(data=traces)
    fig.update_layout(
        showlegend=False,
        hovermode='closest',
        margin=dict(b=0, l=0, r=0, t=0),
        xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
        yaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        height=380
    )
    return fig


# CLI TERMINAL RENDERER WITH FAST INSTANT CALLBACK
def render_cli_terminal():
    st.subheader("Router Console & Event Stream")
    logs_formatted = ""
    for log in st.session_state.cli_logs:
        if "CRITICAL" in log or "ERR" in log or "OFFLINE" in log:
            cls = "cli-line-err"
        elif "WARN" in log or "HIGH" in log:
            cls = "cli-line-warn"
        elif "SUCCESS" in log or "ONLINE" in log or "diverted" in log:
            cls = "cli-line-success"
        else:
            cls = "cli-line-info"
        logs_formatted += f'<div class="{cls}">{log}</div>'
    
    st.markdown(f'<div class="cli-terminal">{logs_formatted}</div>', unsafe_allow_html=True)

    def process_cli():
        cli_cmd = st.session_state.get("cli_input_key", "").strip()
        if cli_cmd:
            cmd_clean = cli_cmd.lower()
            if cmd_clean == "clear logs":
                st.session_state.cli_logs = ["[00:00:00] INFO  [Console] Terminal log stream cleared."]
            elif "ping" in cmd_clean:
                target = cli_cmd.split(" ")[-1].capitalize()
                add_cli_log("EXEC ", f"[ICMP] Ping echo request sent to {target} -> 64 bytes, RTT = 12ms (0% loss)")
            elif "status" in cmd_clean:
                add_cli_log("INFO ", f"[NOC] Active Nodes: {len(nm.get_nodes())} | Core Links: {len(nm.get_links())} | Status: NOMINAL")
            else:
                add_cli_log("EXEC ", f"[Console] Command executed: '{cli_cmd}' -> Status OK.")
            st.session_state["cli_input_key"] = ""

    st.text_input(
        "Console Input Prompt",
        placeholder="Type command (e.g., 'show status', 'ping Router2', 'clear logs') and press Enter...",
        key="cli_input_key",
        on_change=process_cli,
        label_visibility="collapsed"
    )


active_tab = st.session_state.active_tab

# ==========================================
# 1. DASHBOARD MODULE
# ==========================================
if active_tab == "Dashboard":
    st.markdown("""
    <div class="noc-banner">
        <div class="noc-title">
            <span class="pulse-green"></span> Live NOC Infrastructure Monitor
        </div>
        <div class="noc-subtitle">Real-time virtual telemetry, automated link monitoring, and adaptive congestion intelligence</div>
    </div>
    """, unsafe_allow_html=True)

    links_status = sim_engine.get_network_status()
    total_links = len(links_status)
    avg_util = sum(l['utilization'] for l in links_status) / total_links if total_links else 0
    critical_links = sum(1 for l in links_status if l['congestion'] == "CRITICAL")

    m1, m2, m3, m4 = st.columns(4)
    with m1:
        st.metric(label="Total Network Nodes", value=len(nm.get_nodes()))
    with m2:
        st.metric(label="Active Links", value=total_links)
    with m3:
        st.metric(label="Avg Link Load", value=f"{avg_util:.1f}%")
    with m4:
        st.metric(label="Critical Bottlenecks", value=critical_links)

    st.markdown("---")

    col_topo, col_status = st.columns([2, 1])

    with col_topo:
        st.subheader("Live Network Infrastructure Map")
        st.plotly_chart(draw_interactive_topology(nm.get_network()), use_container_width=True)

    with col_status:
        st.subheader("System Health")
        if critical_links > 0:
            st.markdown("""
            <div class="alert-banner-critical">
                <span class="pulse-red"></span> CRITICAL BOTTLENECK DETECTED<br>
                <span style="font-size: 12px; font-weight: normal;">
                    Adaptive routing engine is diverting packet flows away from overloaded links.
                </span>
            </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown("""
            <div class="alert-banner-normal">
                <span class="pulse-green"></span> ALL SYSTEMS NOMINAL<br>
                <span style="font-size: 12px; font-weight: normal;">
                    Network links are performing within baseline bandwidth utilization limits.
                </span>
            </div>
            """, unsafe_allow_html=True)

        st.subheader("Subsystem State")
        st.markdown("""
        <div class="status-panel">
            <div class="status-row">
                <span style="font-size: 13px; font-weight: 600;">Routing Engine</span>
                <span class="badge-online">ONLINE</span>
            </div>
            <div class="status-row">
                <span style="font-size: 13px; font-weight: 600;">Traffic Monitor</span>
                <span class="badge-online">ONLINE</span>
            </div>
            <div class="status-row">
                <span style="font-size: 13px; font-weight: 600;">Congestion Model</span>
                <span class="badge-online">NOMINAL</span>
            </div>
            <div class="status-row">
                <span style="font-size: 13px; font-weight: 600;">SQLite Database</span>
                <span class="badge-online">CONNECTED</span>
            </div>
        </div>
        """, unsafe_allow_html=True)

    render_cli_terminal()

    st.subheader("Real-time Link Telemetry Table")
    df_status = pd.DataFrame(links_status)
    if not df_status.empty:
        df_status.columns = ["Source", "Destination", "Bandwidth (Mbps)", "Traffic (Mbps)", "Utilization (%)", "Congestion", "Loss (%)", "Queue Size"]
        st.dataframe(df_status, use_container_width=True)


# ==========================================
# 2. SIMULATION CONSOLE MODULE
# ==========================================
elif active_tab == "Simulation Console":
    st.markdown("""
    <div class="noc-banner">
        <div class="noc-title">Traffic Simulation Console</div>
        <div class="noc-subtitle">Inject synthetic packet bursts and analyze real-time path routing</div>
    </div>
    """, unsafe_allow_html=True)

    nodes = [n[0] for n in nm.get_nodes()]

    c_inputs, c_output = st.columns([1, 2])

    with c_inputs:
        st.subheader("Simulation Parameters")
        src = st.selectbox("Source Endpoint", nodes, index=0)
        dst = st.selectbox("Destination Endpoint", nodes, index=len(nodes)-1)
        pkt_count = st.slider("Packet Burst Count", 100, 10000, 2500, step=100)
        pkt_size = st.slider("Average Packet Size (Bytes)", 64, 1500, 1024)
        protocol = st.selectbox("Protocol Standard", ["TCP", "UDP", "ICMP"])

        btn_run = st.button("RUN NETWORK SIMULATION", type="primary", use_container_width=True)

    with c_output:
        st.subheader("Execution Results")
        if btn_run:
            if src == dst:
                st.error("Source and Destination endpoints must be distinct.")
            else:
                res = sim_engine.simulate_link_traffic(src, dst, pkt_count, pkt_size)
                
                routing_engine = RoutingEngine(nm.get_network())
                route_res = routing_engine.find_intelligent_route(src, dst)

                if route_res:
                    sim_engine.save_route_result(
                        src, dst, route_res,
                        traffic_mbps=res['traffic_mbps'] if res else 0,
                        utilization=res['utilization'] if res else 0,
                        congestion=res['congestion'] if res else "LOW",
                        packet_loss=res['packet_loss'] if res else 0
                    )

                    add_cli_log("EXEC ", f"[SimEngine] Sent {pkt_count} pkts from {src} to {dst} via {'->'.join(route_res['path'])}")

                    r1, r2, r3 = st.columns(3)
                    with r1:
                        st.metric("Total Path Delay", f"{route_res['delay']} ms")
                    with r2:
                        st.metric("Route Cost Index", f"{route_res.get('cost', 0):.2f}")
                    with r3:
                        st.metric("Selected Route", " → ".join(route_res['path']))

                    st.plotly_chart(draw_interactive_topology(nm.get_network(), active_path=route_res['path']), use_container_width=True)
                else:
                    st.error("No valid route available between the selected endpoints.")
        else:
            st.info("Configure parameters on the left and click **RUN NETWORK SIMULATION**.")

    render_cli_terminal()


# ==========================================
# 3. NETWORK TOPOLOGY MODULE
# ==========================================
elif active_tab == "Network Topology":
    st.markdown("""
    <div class="noc-banner">
        <div class="noc-title">Network Infrastructure Topology & Inspector</div>
        <div class="noc-subtitle">Physical interconnect layer mapping, queue buffers, and link telemetry inspector</div>
    </div>
    """, unsafe_allow_html=True)

    st.plotly_chart(draw_interactive_topology(nm.get_network()), use_container_width=True)

    st.subheader("Live Link Bandwidth Modifier & Telemetry Inspector")
    links_list = [f"{e[0]} ↔ {e[1]}" for e in nm.get_links()]
    selected_link_str = st.selectbox("Select Network Link Segment", links_list)

    if selected_link_str:
        u_sel, v_sel = selected_link_str.split(" ↔ ")
        edge_data = nm.get_network().get_edge_data(u_sel, v_sel)

        c_mod1, c_mod2 = st.columns([1, 2])
        with c_mod1:
            st.markdown("**Link Capacity Control**")
            new_bw = st.slider("Adjust Link Bandwidth (Mbps)", 10, 500, int(edge_data.get("bandwidth", 100)), step=10)
            if st.button("Apply Bandwidth Change", use_container_width=True):
                nm.get_network()[u_sel][v_sel]["bandwidth"] = new_bw
                add_cli_log("WARN ", f"[Config] Bandwidth on link {u_sel} <-> {v_sel} reconfigured to {new_bw} Mbps.")
                st.toast(f"Bandwidth updated to {new_bw} Mbps!", icon="⚡")
                st.rerun()

        with c_mod2:
            st.markdown("**Real-Time Link Metrics**")
            q1, q2, q3, q4 = st.columns(4)
            with q1:
                st.metric("Link Bandwidth", f"{edge_data.get('bandwidth', 100)} Mbps")
            with q2:
                st.metric("Current Load", f"{edge_data.get('utilization', 0):.1f}%")
            with q3:
                st.metric("Drop Loss Rate", f"{edge_data.get('packet_loss', 0)}%")
            with q4:
                st.metric("Queue Buffer Depth", f"{edge_data.get('queue_size', 0)} / 50 pkts")


# ==========================================
# 4. TRAFFIC ANALYTICS MODULE
# ==========================================
elif active_tab == "Traffic Analytics":
    st.markdown("""
    <div class="noc-banner">
        <div class="noc-title">Traffic Analytics & Performance Metrics</div>
        <div class="noc-subtitle">Capacity utilization metrics, queue lengths, and packet loss monitoring</div>
    </div>
    """, unsafe_allow_html=True)

    status = sim_engine.get_network_status()
    df = pd.DataFrame(status)

    if not df.empty:
        df["Link"] = df["source"] + " → " + df["destination"]

        fig = go.Figure(data=[
            go.Bar(name='Utilization (%)', x=df['Link'], y=df['utilization'], marker_color='#38bdf8'),
            go.Bar(name='Packet Loss (%)', x=df['Link'], y=df['packet_loss'], marker_color='#ef4444')
        ])
        fig.update_layout(
            barmode='group',
            title="Link Load vs. Packet Loss Probability",
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            font=dict(color='#f1f5f9')
        )
        st.plotly_chart(fig, use_container_width=True)

        st.subheader("Detailed Link Telemetry Logs")
        df_display = df[["Link", "bandwidth", "traffic_mbps", "utilization", "congestion", "packet_loss", "queue_size"]].copy()
        df_display.columns = ["Link Segment", "Bandwidth (Mbps)", "Traffic Load (Mbps)", "Utilization (%)", "Congestion State", "Loss (%)", "Queue Depth"]
        st.dataframe(df_display, use_container_width=True)

    render_cli_terminal()


# ==========================================
# 5. ADAPTIVE ROUTING & CHAOS SCENARIOS
# ==========================================
elif active_tab == "Adaptive Routing":
    st.markdown("""
    <div class="noc-banner">
        <div class="noc-title">Adaptive Dynamic Routing & Chaos Engineering</div>
        <div class="noc-subtitle">Simulate DDoS floods, fiber cuts, and test real-time OSPF rerouting</div>
    </div>
    """, unsafe_allow_html=True)

    st.subheader("Chaos Attack & Scenario Generators")
    sc1, sc2, sc3 = st.columns(3)

    with sc1:
        if st.button("⚡ Trigger DDoS Attack", use_container_width=True):
            sim_engine.simulate_link_traffic("Router1", "Router2", 15000, 1500)
            sim_engine.simulate_link_traffic("Router2", "Server", 15000, 1500)
            add_cli_log("CRITICAL", "[DDoS] High volume packet flood detected on Router1 -> Router2 -> Server (100% capacity)!")
            st.toast("DDoS Attack Active on primary path!", icon="⚠️")
            st.rerun()

    with sc2:
        if st.button("💥 Cut Fiber Link (Router1-Router2)", use_container_width=True):
            nm.get_network()["Router1"]["Router2"]["bandwidth"] = 0
            nm.get_network()["Router1"]["Router2"]["utilization"] = 100
            add_cli_log("ERR   ", "[FiberCut] Physical link failure between Router1 <-> Router2! Interface DOWN.")
            st.toast("Fiber Link cut between Router1 and Router2!", icon="💥")
            st.rerun()

    with sc3:
        if st.button("📈 Peak Hour Traffic Surge", use_container_width=True):
            for u, v, data in nm.get_network().edges(data=True):
                data["utilization"] = random.randint(65, 88)
            add_cli_log("WARN  ", "[TrafficSurge] Global traffic surge across all core router interconnects.")
            st.toast("Global Peak Hour Traffic Surge injected.", icon="📈")
            st.rerun()

    st.markdown("---")
    
    st.subheader("Routing Engine Decision Evaluation")
    
    routing = RoutingEngine(nm.get_network())
    std_route = routing.find_best_route("PC1", "Server")
    intel_route = routing.find_intelligent_route("PC1", "Server")

    c_std, c_intel = st.columns(2)
    with c_std:
        st.markdown("**Static Dijkstra Route (Delay-only)**")
        st.info(f"Path: {' → '.join(std_route['path'])}\nDelay: {std_route['delay']} ms")

    with c_intel:
        st.markdown("**Intelligent Congestion-Aware Route (Delay + Load + Loss)**")
        st.success(f"Path: {' → '.join(intel_route['path'])}\nDelay: {intel_route['delay']} ms | Route Cost Index: {intel_route['cost']:.2f}")

    st.markdown("### Algorithmic Comparison Matrix")
    cmp_df = pd.DataFrame([
        {
            "Routing Engine": "Static Shortest-Path (Dijkstra)",
            "Selected Path": " → ".join(std_route['path']),
            "Path Latency (ms)": std_route['delay'],
            "Congestion Avoidance": "DISABLED",
            "Cost Metric": f"{std_route['delay']:.2f}"
        },
        {
            "Routing Engine": "Intelligent Congestion-Aware",
            "Selected Path": " → ".join(intel_route['path']),
            "Path Latency (ms)": intel_route['delay'],
            "Congestion Avoidance": "ACTIVE",
            "Cost Metric": f"{intel_route['cost']:.2f}"
        }
    ])
    st.dataframe(cmp_df, use_container_width=True)

    if std_route['path'] != intel_route['path']:
        st.success("⚡ Traffic diverted away from congested link to secondary path!")

    st.plotly_chart(draw_interactive_topology(nm.get_network(), active_path=intel_route['path']), use_container_width=True)

    render_cli_terminal()


# ==========================================
# 6. SIMULATION LOGS & REPORT EXPORT
# ==========================================
elif active_tab == "Simulation Logs":
    st.markdown("""
    <div class="noc-banner">
        <div class="noc-title">Simulation History & Telemetry Audit Store</div>
        <div class="noc-subtitle">Historical evaluation data persisted in SQLite backend</div>
    </div>
    """, unsafe_allow_html=True)

    records = db_mgr.get_simulations()

    if records:
        cols = ["ID", "Source", "Destination", "Route", "Delay (ms)", "Traffic (Mbps)", "Utilization (%)", "Congestion", "Packet Loss (%)", "Timestamp"]
        df_history = pd.DataFrame(records, columns=cols)

        c_flt1, c_flt2 = st.columns([1, 2])
        with c_flt1:
            congestion_filter = st.selectbox("Filter by Congestion Level", ["ALL", "CRITICAL", "HIGH", "MEDIUM", "LOW"])
        with c_flt2:
            search_query = st.text_input("Search Route Logs", placeholder="Type route or node name...")

        filtered_df = df_history.copy()
        if congestion_filter != "ALL":
            filtered_df = filtered_df[filtered_df["Congestion"] == congestion_filter]
        if search_query:
            filtered_df = filtered_df[filtered_df["Route"].str.contains(search_query, case=False, na=False)]

        st.dataframe(filtered_df, use_container_width=True)

        exp_col1, exp_col2, clr_col = st.columns([1, 1, 1])
        with exp_col1:
            csv_data = filtered_df.to_csv(index=False).encode('utf-8')
            st.download_button(
                label="📥 Export CSV Telemetry Report",
                data=csv_data,
                file_name="netflowsim_telemetry_report.csv",
                mime="text/csv",
                use_container_width=True
            )
        with exp_col2:
            json_data = filtered_df.to_json(orient="records", indent=2)
            st.download_button(
                label="📄 Export JSON Audit Log",
                data=json_data,
                file_name="netflowsim_audit_log.json",
                mime="application/json",
                use_container_width=True
            )
        with clr_col:
            if st.button("Clear Log Database", use_container_width=True):
                conn = db_mgr.connect()
                conn.cursor().execute("DELETE FROM simulations")
                conn.commit()
                conn.close()
                add_cli_log("WARN  ", "[Database] SQLite simulation history log cleared.")
                st.success("Database logs cleared.")
                st.rerun()
    else:
        st.info("No historical simulation records found in SQLite database.")


# --- AUTOMATED REAL-TIME NOC TELEMETRY LOOP ---
if live_mode:
    time.sleep(3)
    for u, v, data in nm.get_network().edges(data=True):
        if data.get("bandwidth", 100) > 0:
            delta = random.uniform(-3.5, 4.0)
            data["utilization"] = max(0, min(100, data.get("utilization", 20) + delta))
    add_cli_log("INFO  ", "[LiveTelemetry] Polled link metrics across 5 active topology nodes.")
    st.rerun()