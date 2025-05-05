import requests
import json
import re
import paramiko

from backend.connection import get_db_conn

# Function to parse labels
def parse_labels(label_str):
    labels = {}
    # Match key="value" pairs including those with spaces
    label_pattern = r'([a-zA-Z0-9_]+)="([^"]+)"'
    matches = re.findall(label_pattern, label_str)
    for match in matches:
        labels[match[0]] = match[1]
    return labels

def get_active_mgr_ip(cluster_ip):
    try:
        # Establish SSH connection
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect(cluster_ip, username="root", password="passwd")

        # Run the Ceph command to get manager details
        stdin, stdout, stderr = ssh.exec_command("ceph mgr dump -f json")
        output = stdout.read().decode()

        # Close SSH connection
        ssh.close()

        # Parse JSON output
        mgr_data = json.loads(output)

        # Extract active manager name
        active_addr = mgr_data.get("active_addr", None)
        if not active_addr:
            print("No active mgr found")
            return None
        else:
            active_addr = active_addr.split(":")[0]
            return active_addr

    except Exception as e:
        print(f"Error: {e}")
        return None


# Fetch Prometheus metrics
def scrape_metrics(cluster_ip):
    ip = get_active_mgr_ip(cluster_ip)
    url = f"http://{ip}:9283/metrics"
    response = requests.get(url)
    metrics_data = response.text.splitlines()
    metrics_data = [line for line in metrics_data if line.strip()]

    # Connect to PostgreSQL once
    conn = get_db_conn()
    if not conn:
        print("Database connection failed. Exiting...")
        exit()

    # Parse metrics and process each line
    for line in metrics_data:
        if line.startswith("#"):  # Skip comment lines
            continue

        # Example line format:
        # ceph_mon_metadata{ceph_daemon="mon.ceph-sangadi-nvme-ixwhtf-node1-installer",hostname="ceph-sangadi-nvme-ixwhtf-node1-installer",public_addr="10.0.65.187",rank="0",ceph_version="ceph version 19.2.0-79.el9cp (4f3da703296998ada04b48f8565da9952ce77eb8) squid (stable)"} 1.0

        print("=================================")
        print(line)
        metric_parts = line.rsplit(" ", 1)  # Split only on the last space to separate the value
        metric_name_and_labels = metric_parts[0]
        metric_value_str = metric_parts[1]

        # Extract metric name and labels
        metric_name = metric_name_and_labels.split("{")[0]  # Extract metric name before '{'
        metric_labels_str = metric_name_and_labels.split("{")[1][:-1] if "{" in metric_name_and_labels else ""  # Extract labels inside '{}'

        # Parse the labels into a dictionary
        metric_labels = parse_labels(metric_labels_str)

        # Convert the metric value to float
        try:
            metric_value = float(metric_value_str)
        except ValueError:
            print(f"Error converting '{metric_value_str}' to float")
            continue

        # Create table name dynamically from metric name
        table_name = f"{metric_name.lower().replace('_', '')}"  # e.g., ceph_mon_quorum_status_metrics

        # Create the table dynamically based on the metric name if it doesn't exist
        create_table_query = f"""
        CREATE TABLE IF NOT EXISTS {table_name} (
            metric_name VARCHAR NOT NULL,
            labels JSONB,
            value DOUBLE PRECISION,
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        """

        # Prepare labels as JSONB
        labels_json = json.dumps(metric_labels)

        cur = conn.cursor()
        try:
            # Create the table if it doesn't exist
            cur.execute(create_table_query)
            conn.commit()  # Commit the table creation

            # Execute insert query
            insert_query = f"INSERT INTO {table_name} (metric_name, labels, value) VALUES (%s, %s, %s)"
            cur.execute(insert_query, (metric_name, labels_json, metric_value))
            conn.commit()
            print(f"Inserted {metric_name} with labels {labels_json} and value {metric_value} into {table_name}")

        except Exception as err:
            print(f"Database error: {err}")
            conn.rollback()
        finally:
            cur.close()

    # Close the connection
    conn.close()