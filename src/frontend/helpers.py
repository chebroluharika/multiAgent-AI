import paramiko
import streamlit as st

from orchestration.flow import CephAgentsFlow

ceph_agents_flow = CephAgentsFlow()


def process_query(query: str):
    response = ceph_agents_flow.kickoff(inputs={"topic": query})
    return response


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
