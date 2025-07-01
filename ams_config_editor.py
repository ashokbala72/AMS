
import streamlit as st
import sqlite3
import json

# DB connection
conn = sqlite3.connect("ams_config.db")
cursor = conn.cursor()

# Create table if not exists
cursor.execute("""
CREATE TABLE IF NOT EXISTS config_sources (
    source_name TEXT PRIMARY KEY,
    enabled INTEGER DEFAULT 0,
    priority INTEGER,
    config TEXT
)
""")
conn.commit()

st.set_page_config(page_title="AMS Config Editor")
st.title("🔧 AMS Input System Configuration")

sources = ["servicenow", "jira", "sap", "csv"]

selected_source = st.selectbox("Select Source to Configure", sources)

# Load existing config if present
cursor.execute("SELECT * FROM config_sources WHERE source_name=?", (selected_source,))
data = cursor.fetchone()

enabled = False
priority = 1
config_dict = {}

if data:
    enabled = bool(data[1])
    priority = data[2]
    config_dict = json.loads(data[3]) if data[3] else {}

st.checkbox("Enable this source", value=enabled, key="enabled")
st.number_input("Priority (lower = higher)", min_value=1, max_value=10, value=priority, key="priority")

st.subheader(f"🔧 Configuration for {selected_source}")

if selected_source == "servicenow":
    config_dict["base_url"] = st.text_input("Base URL", value=config_dict.get("base_url", "https://instance.service-now.com"))
    config_dict["username"] = st.text_input("Username", value=config_dict.get("username", "admin"))
    config_dict["password"] = st.text_input("Password", value=config_dict.get("password", "password"), type="password")
    config_dict["table"] = st.text_input("Table", value=config_dict.get("table", "incident"))

elif selected_source == "jira":
    config_dict["base_url"] = st.text_input("Base URL", value=config_dict.get("base_url", "https://yourcompany.atlassian.net"))
    config_dict["email"] = st.text_input("Email", value=config_dict.get("email", "user@example.com"))
    config_dict["api_token"] = st.text_input("API Token", value=config_dict.get("api_token", "apitoken123"), type="password")
    config_dict["project_key"] = st.text_input("Project Key", value=config_dict.get("project_key", "PROJ"))

elif selected_source == "sap":
    config_dict["endpoint"] = st.text_input("SAP Endpoint URL", value=config_dict.get("endpoint", "https://sap.example.com/api"))
    config_dict["api_key"] = st.text_input("API Key", value=config_dict.get("api_key", "sapapikey"), type="password")

elif selected_source == "csv":
    config_dict["path"] = st.text_input("CSV File Path", value=config_dict.get("path", "sap_ticket_combined_allinfo.csv"))

# Save to DB
if st.button("💾 Save Configuration"):
    cursor.execute("""
        INSERT INTO config_sources (source_name, enabled, priority, config)
        VALUES (?, ?, ?, ?)
        ON CONFLICT(source_name) DO UPDATE SET
            enabled=excluded.enabled,
            priority=excluded.priority,
            config=excluded.config
    """, (selected_source, int(st.session_state.enabled), st.session_state.priority, json.dumps(config_dict)))
    conn.commit()
    st.success(f"✅ Configuration for {selected_source} saved.")
