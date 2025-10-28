import paramiko
import streamlit as st

from orchestration.flow import CephAgentsFlow


def process_query(prompt: str):
    flow = st.session_state.get("flow")
    if flow is None:
        flow = CephAgentsFlow()
        st.session_state.flow = flow

    if flow is not None:
        try:
            # Clear logs from previous query
            flow.state.logs = []

            result = flow.kickoff(inputs={"topic": prompt})

            # Store logs in session state for UI access
            st.session_state.current_logs = flow.state.logs
        except Exception as e:
            result = f"Error during flow execution: {e}"
            st.session_state.current_logs = []
    else:
        result = "Flow is not initialized."
        st.session_state.current_logs = []

    return result


def test_ssh_connection(ip, username, password):
    """Attempts SSH connection to a given Ceph cluster IP."""
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

    try:
        ssh.connect(ip, username=username, password=password, timeout=5)
        ssh.close()
        return True
    except Exception as e:
        return str(e)  # Return the error message


# Custom chat message function
def chat_message(role, content):
    if role == "user":
        st.markdown(
            f"""
        <div class="chat-bubble user-bubble">
            <strong>👤 You:</strong><br> {content}
        </div>
        """,
            unsafe_allow_html=True,
        )
    elif role == "assistant":
        st.markdown(
            f"""
        <div class="chat-bubble bot-bubble">
            <strong>🤖 Bot:</strong><br> {content}
        </div>
        """,
            unsafe_allow_html=True,
        )
