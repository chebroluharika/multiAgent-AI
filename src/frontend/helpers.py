import paramiko
import streamlit as st

from orchestration.flow import CephAgentsFlow


def process_query(prompt: str, log_container=None):
    flow = st.session_state.get("flow")
    if flow is None:
        flow = CephAgentsFlow()
        st.session_state.flow = flow

    if flow is not None:
        try:
            # Clear logs from previous query
            flow.state.logs = []

            # Monkey patch the add_log method to support real-time logging
            original_add_log = flow.add_log
            def real_time_add_log(level: str, agent_name: str, message: str):
                # Call the original add_log method
                original_add_log(level, agent_name, message)
                
                # Update real-time log container if provided
                if log_container is not None:
                    # Retrieve all logs
                    current_logs = flow.state.logs
                    
                    # Format logs for display
                    log_display = ""
                    for log in current_logs:
                        log_level = log.get("level", "info")
                        log_agent_name = log.get("agent_name", "")
                        log_message = log.get("message", "")
                        timestamp = log.get("timestamp", "")
                        icon = "🤖"  # Default icon
                        
                        # Customize icon based on log level and agent name
                        if log_level == "success":
                            icon = "✅"
                        elif log_level == "error":
                            icon = "❌"
                        elif log_level == "warning":
                            icon = "⚠️"
                        elif log_agent_name == "Orchestrator":
                            icon = "🔍"
                        elif log_agent_name == "Report Generator":
                            icon = "📝"
                        
                        log_display += f"{icon} **{log_agent_name}** ({timestamp}): {log_message}\n\n"
                    
                    # Update the log container
                    log_container.markdown(log_display)

            # Replace add_log method with our real-time version
            flow.add_log = real_time_add_log

            result = flow.kickoff(inputs={"topic": prompt})

            # Restore the original add_log method
            flow.add_log = original_add_log

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
