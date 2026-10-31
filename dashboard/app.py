# -*- coding: utf-8 -*-
import os
import sys
import subprocess
import signal
import pandas as pd
import streamlit as st
import matplotlib.pyplot as plt
from pymongo import MongoClient

PROJECT_DIR = r"C:\Hadoop\web-log-project"
OUTPUT_DIR = os.path.join(PROJECT_DIR, "output")
ALERT_DIR = os.path.join(PROJECT_DIR, "realtime", "alerts")

FEATURE_FILE = os.path.join(OUTPUT_DIR, "ml_features.csv")
ANOMALY_FILE = os.path.join(OUTPUT_DIR, "anomaly_results.csv")
ALERT_FILE = os.path.join(ALERT_DIR, "realtime_alerts.csv")
METRICS_FILE = os.path.join(ALERT_DIR, "realtime_metrics.csv")

MONGODB_URI = "mongodb://127.0.0.1:27017"
MONGODB_DATABASE = "WebLogIntelligence"

st.set_page_config(
    page_title="Web Log Intelligence",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown(
    """
    <style>
    .block-container {padding-top: 1.6rem; padding-bottom: 2rem;}
    [data-testid="stMetric"] {
        background: rgba(120, 120, 120, 0.08);
        border: 1px solid rgba(128, 128, 128, 0.22);
        padding: 16px 18px;
        border-radius: 12px;
    }
    div[data-testid="stDataFrame"] {border-radius: 10px;}
    </style>
    """,
    unsafe_allow_html=True,
)

st.title("📊 Web Log Intelligence")
st.caption("Hadoop MapReduce • Isolation Forest • MongoDB • Simulated real-time monitoring")

SIMULATOR_FILE = os.path.join(
    PROJECT_DIR, "realtime", "live_traffic_simulator.py"
)

if "simulator_process" not in st.session_state:
    st.session_state.simulator_process = None

if "traffic_mode" not in st.session_state:
    st.session_state.traffic_mode = "Normal"


def simulator_is_running():
    process = st.session_state.simulator_process
    return process is not None and process.poll() is None


def stop_simulator():
    process = st.session_state.simulator_process

    if process is not None and process.poll() is None:
        process.terminate()
        try:
            process.wait(timeout=5)
        except subprocess.TimeoutExpired:
            process.kill()
            process.wait()

    st.session_state.simulator_process = None

def numeric_columns(df, columns):
    """Convert CSV-imported MongoDB string values to numeric values where needed."""
    for column in columns:
        if column in df.columns:
            df[column] = pd.to_numeric(df[column], errors="coerce").fillna(0)
    return df



@st.cache_data(ttl=10)
def load_main_data():
    """Load core datasets from MongoDB, falling back to the original CSV files."""
    mongo_error = None
    try:
        with MongoClient(MONGODB_URI, serverSelectionTimeoutMS=2500) as client:
            client.admin.command("ping")
            db = client[MONGODB_DATABASE]
            features = pd.DataFrame(list(db.client_statistics.find({}, {"_id": 0})))
            anomalies = pd.DataFrame(list(db.anomaly_results.find({}, {"_id": 0})))

        if features.empty or anomalies.empty:
            raise ValueError("MongoDB client_statistics or anomaly_results collection is empty.")

        features = numeric_columns(
            features,
            ["Total_Requests", "HTTP_403_Count", "HTTP_404_Count", "HTTP_500_Count",
             "HTTP_501_Count", "Total_Errors", "Error_Rate"],
        )
        anomalies = numeric_columns(anomalies, ["Anomaly_Score"])
        if "Client" in features.columns:
            features["Client"] = features["Client"].astype(str)
        if "Client" in anomalies.columns:
            anomalies["Client"] = anomalies["Client"].astype(str)
        return features, anomalies, "MongoDB"
    except Exception as exc:
        mongo_error = str(exc)

    # Keep the original CSV-based dashboard usable if MongoDB is unavailable.
    try:
        features = pd.read_csv(FEATURE_FILE)
        anomalies = pd.read_csv(ANOMALY_FILE)
        return features, anomalies, f"CSV fallback (MongoDB unavailable: {mongo_error})"
    except Exception as exc:
        raise RuntimeError(
            f"Could not load data from MongoDB ({mongo_error}) or CSV files ({exc})."
        ) from exc


@st.cache_data(ttl=5)
def load_alerts():
    cols = [
        "Detection_Time", "Client", "Reason", "Total_Requests",
        "Selected_HTTP_Errors", "HTTP_Status",
    ]
    if not os.path.exists(ALERT_FILE):
        return pd.DataFrame(columns=cols)
    try:
        df = pd.read_csv(ALERT_FILE)
        for col in cols:
            if col not in df.columns:
                df[col] = pd.NA
        return df[cols]
    except (pd.errors.EmptyDataError, PermissionError):
        return pd.DataFrame(columns=cols)


@st.cache_data(ttl=5)
def load_metrics():
    cols = [
        "Timestamp", "Requests", "Selected_HTTP_Errors",
        "HTTP_403", "HTTP_404", "HTTP_500", "HTTP_501", "Total_Processed",
    ]
    if not os.path.exists(METRICS_FILE):
        return pd.DataFrame(columns=cols)
    try:
        df = pd.read_csv(METRICS_FILE)
        for col in cols:
            if col not in df.columns:
                df[col] = 0 if col != "Timestamp" else pd.NA
        return df[cols]
    except (pd.errors.EmptyDataError, PermissionError):
        return pd.DataFrame(columns=cols)


try:
    features, anomalies, data_source = load_main_data()
except Exception as exc:
    st.error(f"Could not load project data: {exc}")
    st.stop()

if data_source == "MongoDB":
    st.sidebar.success("connected to MongoDB  ✅")
else:
    st.sidebar.warning(f"MongoDB connection failed; using CSV fallback. ({data_source})")

if not {"Client", "Total_Requests", "Total_Errors", "Error_Rate"}.issubset(features.columns):
    st.error("Client statistics data is missing one or more required columns.")
    st.stop()
if not {"Client", "Anomaly_Status", "Anomaly_Score"}.issubset(anomalies.columns):
    st.error("Anomaly results data is missing required columns.")
    st.stop()

# Normalize numeric types and make client keys consistent before joining.
features = numeric_columns(
    features,
    ["Total_Requests", "HTTP_403_Count", "HTTP_404_Count", "HTTP_500_Count",
     "HTTP_501_Count", "Total_Errors", "Error_Rate"],
)
anomalies = numeric_columns(anomalies, ["Anomaly_Score"])
features["Client"] = features["Client"].astype(str)
anomalies["Client"] = anomalies["Client"].astype(str)

merged = features.merge(
    anomalies[["Client", "Anomaly_Status", "Anomaly_Score"]],
    on="Client", how="left",
)

alerts = load_alerts()
metrics = load_metrics()

# Sidebar navigation and shared settings.
st.sidebar.title("Navigation")
page = st.sidebar.radio("Go to", ["Overview", "Anomaly Details", "Live Monitoring"], index=0)
st.sidebar.divider()
st.sidebar.caption("Project data")
st.sidebar.write(f"Data source: **{data_source.split(' (')[0]}**")
st.sidebar.write(f"Clients: **{features['Client'].nunique():,}**")
st.sidebar.write(
    f"Model anomalies: **{(anomalies['Anomaly_Status'] == 'Potential Anomaly').sum():,}**"
)
auto_refresh = st.sidebar.checkbox("Auto-refresh live monitoring", value=True)
refresh_seconds = st.sidebar.selectbox("Refresh interval (seconds)", [5, 10, 15, 30], index=0)
if data_source.startswith("CSV fallback"):
    st.sidebar.warning("MongoDB data could not be loaded; using CSV files instead.")


def overview_page():
    st.header("Overview")
    total_clients = features["Client"].nunique()
    total_requests = int(features["Total_Requests"].sum())
    total_errors = int(features["Total_Errors"].sum())
    model_anomalies = int((anomalies["Anomaly_Status"] == "Potential Anomaly").sum())
    k1, k2, k3, k4 = st.columns(4)
    k1.metric("Unique Clients", f"{total_clients:,}")
    k2.metric("Total Requests", f"{total_requests:,}")
    k3.metric("Selected HTTP Errors", f"{total_errors:,}")
    k4.metric("Model Potential Anomalies", f"{model_anomalies:,}")

    st.divider()
    left, right = st.columns(2)
    with left:
        st.subheader("Top 10 Clients by Requests")
        top = features.nlargest(10, "Total_Requests").sort_values("Total_Requests")
        fig, ax = plt.subplots(figsize=(8, 4.5))
        ax.barh(top["Client"], top["Total_Requests"])
        ax.set_xlabel("Requests")
        ax.set_ylabel("Client")
        fig.tight_layout()
        st.pyplot(fig)
        plt.close(fig)
    with right:
        st.subheader("Model Classification")
        counts = anomalies["Anomaly_Status"].value_counts()
        fig, ax = plt.subplots(figsize=(8, 4.5))
        ax.bar(counts.index.astype(str), counts.values)
        ax.set_ylabel("Clients")
        ax.tick_params(axis="x", rotation=10)
        fig.tight_layout()
        st.pyplot(fig)
        plt.close(fig)

    st.subheader("Request Volume vs Selected HTTP Errors")
    fig, ax = plt.subplots(figsize=(10, 4.5))
    normal = merged[merged["Anomaly_Status"] == "Normal"]
    potential = merged[merged["Anomaly_Status"] == "Potential Anomaly"]
    ax.scatter(normal["Total_Requests"], normal["Total_Errors"], label="Normal", alpha=0.45, s=14)
    ax.scatter(potential["Total_Requests"], potential["Total_Errors"], label="Potential Anomaly", alpha=0.65, s=18)
    ax.set_xlabel("Total Requests")
    ax.set_ylabel("Selected HTTP Errors")
    ax.legend()
    fig.tight_layout()
    st.pyplot(fig)
    plt.close(fig)

    st.subheader("Client Analysis")
    c1, c2 = st.columns(2)
    with c1:
        anomaly_filter = st.selectbox("Classification", ["All", "Potential Anomaly", "Normal"])
    with c2:
        min_requests = st.number_input("Minimum requests", min_value=0, value=0, step=100)
    view = merged[merged["Total_Requests"] >= min_requests].copy()
    if anomaly_filter != "All":
        view = view[view["Anomaly_Status"] == anomaly_filter]
    cols = [c for c in [
        "Client", "Total_Requests", "HTTP_403_Count", "HTTP_404_Count",
        "HTTP_500_Count", "HTTP_501_Count", "Total_Errors", "Error_Rate",
        "Anomaly_Status", "Anomaly_Score",
    ] if c in view.columns]
    st.caption(f"Showing {len(view):,} clients")
    st.dataframe(view[cols], use_container_width=True, hide_index=True)
    st.download_button(
        "Download filtered client results", view.to_csv(index=False).encode("utf-8"),
        "web_log_analysis_results.csv", "text/csv",
    )


def anomaly_details_page():
    st.header("🔎 Anomaly Details")
    st.write("Search for a client to review its request activity, error counts, model classification, and matching real-time alerts.")

    clients = sorted(merged["Client"].dropna().astype(str).unique().tolist())
    if not clients:
        st.warning("No clients are available in the feature dataset.")
        return

    search = st.text_input("Search hostname or IP address", placeholder="Start typing a client name...")
    matches = [client for client in clients if search.lower() in client.lower()] if search else clients
    if not matches:
        st.warning("No matching clients found. Try another hostname or IP address.")
        return

    selected = st.selectbox("Select client", matches)
    row = merged[merged["Client"].astype(str) == selected].iloc[0]
    status = str(row.get("Anomaly_Status", "Unknown"))
    if status == "Potential Anomaly":
        st.warning(f"⚠️ Model classification: {status}")
    else:
        st.success(f"Model classification: {status}")

    a1, a2, a3, a4 = st.columns(4)
    a1.metric("Total Requests", f"{int(row['Total_Requests']):,}")
    a2.metric("Selected HTTP Errors", f"{int(row['Total_Errors']):,}")
    a3.metric("Error Rate", f"{float(row['Error_Rate']):.4f}")
    score = pd.to_numeric(pd.Series([row.get("Anomaly_Score")]), errors="coerce").iloc[0]
    a4.metric("Anomaly Score", f"{score:.4f}" if pd.notna(score) else "N/A")

    st.subheader("HTTP Status Breakdown")
    status_columns = ["HTTP_403_Count", "HTTP_404_Count", "HTTP_500_Count", "HTTP_501_Count"]
    status_labels = {
        "HTTP_403_Count": "HTTP 403", "HTTP_404_Count": "HTTP 404",
        "HTTP_500_Count": "HTTP 500", "HTTP_501_Count": "HTTP 501",
    }
    status_data = {}
    for column in status_columns:
        value = pd.to_numeric(pd.Series([row.get(column, 0)]), errors="coerce").fillna(0).iloc[0]
        status_data[status_labels[column]] = int(value)
    total_selected_errors = sum(status_data.values())
    if total_selected_errors == 0:
        st.success("✅ No selected HTTP errors (403, 404, 500, or 501) were recorded for this client.")
        st.caption("The chart will appear when this client has one or more selected HTTP errors.")
    else:
        status_df = pd.DataFrame({"HTTP Status": list(status_data.keys()), "Error Count": list(status_data.values())})
        chart_df = status_df[status_df["Error Count"] > 0]
        st.bar_chart(chart_df.set_index("HTTP Status"))
        st.dataframe(status_df, use_container_width=True, hide_index=True)

    st.subheader("Client Record")
    client_record = pd.DataFrame([row])
    st.dataframe(client_record, use_container_width=True, hide_index=True)
    st.download_button(
        "Download this client's details", client_record.to_csv(index=False).encode("utf-8"),
        f"client_details_{selected.replace('/', '_')}.csv", "text/csv",
    )

    st.subheader("Matching Real-Time Alerts")
    if alerts.empty:
        st.info("No real-time alerts have been recorded yet.")
    else:
        matching = alerts[alerts["Client"].astype(str) == selected].copy()
        if matching.empty:
            st.info("No recorded real-time alerts match this client.")
        else:
            st.dataframe(matching.iloc[::-1], use_container_width=True, hide_index=True)
            st.download_button(
                "Download this client's alerts", matching.to_csv(index=False).encode("utf-8"),
                f"client_alerts_{selected.replace('/', '_')}.csv", "text/csv",
            )
    st.caption("An anomaly classification indicates an unusual pattern, not proof of malicious activity.")


def live_monitoring_page():
    st.header("🚨 Live Monitoring")
    st.caption("Alerts and metrics written by realtime_monitor.py. The input is simulated traffic, not live internet traffic.")

    st.subheader("🎮 Traffic Simulator Controls")

    mode = st.radio(
        "Select Traffic Mode",
        ["Normal", "Anomaly"],
        horizontal=True,
        key="traffic_mode_selector"
    )

    st.write(f"Selected mode: **{mode}**")

    running = simulator_is_running()

    col1, col2 = st.columns(2)

    with col1:
        if st.button(
            "▶️ Start Simulator",
            disabled=running,
            use_container_width=True
        ):
            try:
                mode_number = "1" if mode == "Normal" else "2"
                st.session_state.simulator_process = subprocess.Popen(
                    [sys.executable, SIMULATOR_FILE],
                    stdin=subprocess.PIPE,
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.PIPE,
                    text=True
                )
                st.session_state.simulator_process.stdin.write(mode_number + "\n")
                st.session_state.simulator_process.stdin.flush()
                st.success(f"{mode} traffic simulator started.")
                st.rerun()
            except Exception as exc:
                st.error(f"Could not start simulator: {exc}")

    with col2:
        if st.button(
            "⏹️ Stop Simulator",
            disabled=not running,
            use_container_width=True
        ):
            stop_simulator()
            st.success("Simulator stopped.")
            st.rerun()

    st.divider()

    @st.fragment(run_every=refresh_seconds if auto_refresh else None)
    def live_content():
        current_alerts = load_alerts()
        current_metrics = load_metrics()
        if current_alerts.empty:
            st.info("No alerts yet. Start realtime_monitor.py, then start log_generator.py.")
        else:
            latest = current_alerts.iloc[-1]
            st.warning(
                f"Latest recorded alert — **{latest['Client']}**: "
                f"{latest['Reason']} (detected {latest['Detection_Time']})"
            )
            reason = current_alerts["Reason"].astype(str)
            rate_count = int(reason.str.contains("requests observed", case=False, na=False).sum())
            error_count = int(reason.str.contains("selected HTTP errors", case=False, na=False).sum())
            c1, c2, c3, c4 = st.columns(4)
            c1.metric("Total Alerts", f"{len(current_alerts):,}")
            c2.metric("Clients with Alerts", f"{current_alerts['Client'].nunique():,}")
            c3.metric("Request-Rate Alerts", f"{rate_count:,}")
            c4.metric("HTTP-Error Alerts", f"{error_count:,}")
            st.subheader("Latest 20 Alerts")
            sort_df = current_alerts.copy()
            sort_df["_sort"] = pd.to_datetime(sort_df["Detection_Time"], errors="coerce")
            st.dataframe(
                sort_df.sort_values("_sort", ascending=False, na_position="last")
                .drop(columns="_sort").head(20),
                use_container_width=True, hide_index=True,
            )
            st.download_button(
                "Download all real-time alerts", current_alerts.to_csv(index=False).encode("utf-8"),
                "realtime_alerts.csv", "text/csv", key="live_alerts_download",
            )

        st.divider()
        st.subheader("Requests Processed per Monitoring Interval")
        if current_metrics.empty:
            st.info("Waiting for metrics. The monitor writes a row approximately every two seconds.")
            return
        current_metrics["Timestamp"] = pd.to_datetime(current_metrics["Timestamp"], errors="coerce")
        for col in ["Requests", "Selected_HTTP_Errors", "HTTP_403", "HTTP_404", "HTTP_500", "HTTP_501"]:
            current_metrics[col] = pd.to_numeric(current_metrics[col], errors="coerce").fillna(0)
        current_metrics = current_metrics.dropna(subset=["Timestamp"]).sort_values("Timestamp").tail(100)
        if current_metrics.empty:
            st.info("No valid metric timestamps are available yet.")
            return
        st.line_chart(current_metrics.set_index("Timestamp")[["Requests"]])
        st.subheader("HTTP Errors per Monitoring Interval")
        st.line_chart(current_metrics.set_index("Timestamp")[["HTTP_403", "HTTP_404", "HTTP_500", "HTTP_501"]])
        st.subheader("Total Selected HTTP Errors per Interval")
        st.area_chart(current_metrics.set_index("Timestamp")[["Selected_HTTP_Errors"]])

    live_content()


if page == "Overview":
    overview_page()
elif page == "Anomaly Details":
    anomaly_details_page()
else:
    live_monitoring_page()

st.divider()
st.caption("Web Log Intelligence Project | Hadoop + Python + Isolation Forest + MongoDB")
