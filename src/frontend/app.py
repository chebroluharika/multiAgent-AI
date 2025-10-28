import sys
from pathlib import Path

import streamlit as st
import torch

torch.classes.__path__ = []  # add this line to manually set it to empty.

sys.path.append(str(Path(__file__).parent.parent))

from cephviz.agent import connect_cluster
from observability.backend.scrape_metricsdata import scrape_metrics

from frontend.helpers import (
    process_query,
    test_ssh_connection,
)
from orchestration.flow import Memory


def format_log_icon(log_level: str, agent_name: str) -> str:
    """Return appropriate icon based on log level and agent name."""
    if log_level == "success":
        return "✅"
    elif log_level == "error":
        return "❌"
    elif log_level == "warning":
        return "⚠️"
    elif agent_name == "Orchestrator":
        return "🔍"
    elif agent_name == "Report Generator":
        return "📝"
    else:
        return "🤖"


# Class to handle individual chat sessions
class ChatSession:
    def __init__(self, session_name):
        self.session_name = session_name
        self.messages = self.get_default_messages()

    def get_default_messages(self):
        return []

    def reset_user_messages(self):
        self.messages = self.get_default_messages()


# Class to manage chat history
class ChatHistory:
    def __init__(self):
        if "chat_sessions" not in st.session_state:
            st.session_state["chat_sessions"] = {"default": ChatSession("default")}
        if "current_chat" not in st.session_state:
            st.session_state["current_chat"] = "default"


# Initialize chat history and session
chat_history = ChatHistory()


# Streamlit page configuration
st.set_page_config(
    page_title="Ceph Orchestrator Intelligence", page_icon="🤖", layout="wide"
)

# Custom CSS for a more attractive UI
st.markdown(
    """
    <style>
        body { font-family: 'Arial', sans-serif; }
        .sidebar .sidebar-content { background-color: #1E1E1E; color: white; }
        .sidebar h2 { color: #4CAF50; }
        .chat-bubble { padding: 10px; border-radius: 10px; margin: 5px; }
        .user-bubble { background-color: #E3F2FD; }
        .bot-bubble { background-color: #D9F7BE; }
    </style>
""",
    unsafe_allow_html=True,
)

# Display the main title
st.markdown(
    """
    <h1 style='text-align: center; color: #4CAF50; font-size: 36px;'>🤖 Ceph Observability Orchestrator</h1>
    <p style='text-align: center; font-size: 18px; color: gray;'>Monitor and manage your Ceph cluster effortlessly</p>
    <hr style='border: 1px solid #ccc;'>
""",
    unsafe_allow_html=True,
)

# Initialize session state for storing cluster data
if "cluster_data" not in st.session_state:
    st.session_state.cluster_data = {}  # Stores {"Cluster 1": "192.168.1.10", ...}
if "flow" not in st.session_state:
    st.session_state.flow = None

# Sidebar: Ceph SSH Authentication Panel
st.sidebar.markdown("<h2>🔐 Ceph SSH Authentication</h2>", unsafe_allow_html=True)

with st.sidebar.expander("⚙️ SSH Configuration", expanded=True):
    ssh_username = st.text_input("👤 SSH Username", placeholder="Enter SSH username")
    ssh_password = st.text_input(
        "🔒 SSH Password", placeholder="Enter SSH password", type="password"
    )

    # Add multiple cluster IPs dynamically
    cluster_ips = st.text_area(
        "🌍 Ceph Cluster IPs", placeholder="Enter IPs, one per line", height=100
    )

    connect_button = st.button("🔗 Connect to Clusters")

# Handle SSH authentication
if connect_button:
    if ssh_username and ssh_password and cluster_ips.strip():
        ip_list = [
            ip.strip() for ip in cluster_ips.split("\n") if ip.strip()
        ]  # Remove empty lines

        failed_ips = {}

        for ip in ip_list:
            connect_cluster("Cluster 1", ip)
            scrape_metrics(ip, ssh_username, ssh_password)
            if (
                ip in st.session_state.cluster_data.values()
            ):  # Skip already connected IPs
                continue

            result = test_ssh_connection(ip, ssh_username, ssh_password)
            if result is True:
                # Find the next available cluster name
                existing_numbers = [
                    int(name.split(" ")[1]) for name in st.session_state.cluster_data
                ]
                next_cluster_number = max(existing_numbers, default=0) + 1
                cluster_name = f"Cluster {next_cluster_number}"

                st.session_state.cluster_data[cluster_name] = ip  # Store correctly
            else:
                failed_ips[ip] = result  # Store error message per IP

        if failed_ips:
            for ip, error in failed_ips.items():
                st.sidebar.error(f"❌ Failed to connect to {ip}: {error}")
        elif ip_list:
            st.sidebar.success(
                f"✅ Successfully connected to {len(ip_list) - len(failed_ips)} new cluster(s)!"
            )
    else:
        st.sidebar.error("❌ Please fill in all fields before connecting.")

# Show connected clusters at the left bottom
if st.session_state.cluster_data:
    with st.sidebar.expander("🔗 Connected Ceph Clusters", expanded=True):
        selected_clusters = st.multiselect(
            "Select clusters to disconnect:",
            list(st.session_state.cluster_data.keys()),
            key="selected_disconnect",
        )

        if st.button("❌ Disconnect Selected"):
            for cluster_name in selected_clusters:
                del st.session_state.cluster_data[
                    cluster_name
                ]  # Remove from session state

            st.sidebar.success(f"✅ Disconnected {len(selected_clusters)} cluster(s)!")
            st.rerun()  # Refresh UI after removal

        for cluster_name, ip in st.session_state.cluster_data.items():
            st.markdown(f"✅ **{cluster_name}: {ip}**")


# Agent Memory Expander
with st.sidebar.expander("🕵️ Agent Memory", expanded=False):
    flow = st.session_state.get("flow")
    if flow and flow.state.memory:
        for i, mem in enumerate(reversed(flow.state.memory)):
            mem = Memory(**mem)
            st.markdown(f"**Memory {len(flow.state.memory) - i}**")
            st.text_area("Query", mem.query, disabled=True, key=f"mem_q_{i}")
            st.text_area("Response", mem.response, disabled=True, key=f"mem_r_{i}")
            st.text_area(
                "Agents", "\n".join(mem.agents), disabled=True, key=f"mem_a_{i}"
            )

            # Display logs if available
            if mem.logs:
                show_logs = st.checkbox(
                    "📋 Show Logs", key=f"mem_logs_toggle_{i}", value=False
                )
                if show_logs:
                    for log_idx, log in enumerate(mem.logs):
                        log_level = log.get("level", "info")
                        agent_name = log.get("agent_name", "")
                        log_message = log.get("message", "")
                        timestamp = log.get("timestamp", "")
                        icon = format_log_icon(log_level, agent_name)
                        st.write(
                            f"{icon} **{agent_name}** ({timestamp}): {log_message}"
                        )
            st.divider()
    else:
        st.write("No memory to display yet.")


# Display the main title
st.markdown(
    "<h1 style='text-align: center;'>🤖 Welcome to Ceph Intelligence Orchestrator!</h1>",
    unsafe_allow_html=True,
)


# Get current chat session
current_chat_name = st.session_state.current_chat
current_chat = st.session_state.chat_sessions[current_chat_name]

# Check if user has entered any message
user_has_entered_message = any(
    msg["role"] in ["user", "assistant"] for msg in current_chat.messages
)

# Display chat history
for message in current_chat.messages:
    role = message.get("role", "system")
    if role == "user":
        with st.chat_message("user"):
            st.markdown(message["content"])
    elif role == "assistant":
        with st.chat_message("assistant"):
            # Display logs if available in the message
            logs = message.get("logs", [])
            if logs:
                with st.status("🔄 Agent Processing", expanded=False, state="complete"):
                    for log in logs:
                        log_level = log.get("level", "info")
                        agent_name = log.get("agent_name", "")
                        log_message = log.get("message", "")
                        timestamp = log.get("timestamp", "")
                        icon = format_log_icon(log_level, agent_name)
                        st.write(
                            f"{icon} **{agent_name}** ({timestamp}): {log_message}"
                        )

            st.markdown(message["content"])
    else:
        st.markdown(message["content"], unsafe_allow_html=True)

# Chat input
if prompt := st.chat_input("Type your message here..."):
    current_chat.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):  # noqa: SIM117
        with st.spinner("🤔 Thinking..."):
            response = process_query(prompt)

            # Get logs from session state
            logs = st.session_state.get("current_logs", [])

            # Display logs in a status container if available
            if logs:
                with st.status("🔄 Agent Processing", expanded=True, state="complete"):
                    for log in logs:
                        log_level = log.get("level", "info")
                        agent_name = log.get("agent_name", "")
                        message = log.get("message", "")
                        timestamp = log.get("timestamp", "")
                        icon = format_log_icon(log_level, agent_name)
                        st.write(f"{icon} **{agent_name}** ({timestamp}): {message}")

            st.markdown(response)

            # Store response with logs in chat history
            current_chat.messages.append(
                {"role": "assistant", "content": response, "logs": logs}
            )

    st.rerun()


# Show "Clear Chat" button if messages exist
if user_has_entered_message:  # noqa: SIM102
    if st.button(
        f"🗑️ Clear {current_chat_name} Chat", key=f"clear_chat_{current_chat_name}"
    ):
        st.session_state.chat_sessions[current_chat_name].reset_user_messages()
        if flow := st.session_state.flow:
            flow.clear_memory()
        st.rerun()
