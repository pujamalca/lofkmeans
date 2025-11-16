import json
from pathlib import Path

import pandas as pd
import streamlit as st


st.set_page_config(
    page_title="LOF + K-Means Pipeline GUI",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.title("GUI Proses Deteksi Anomali LOF → K-Means")
st.markdown(
    "Fokus pada input dan parameter fase pipeline (LOF & K-Means) agar GUI dapat digunakan "
    "sebagai ilustrasi proses dalam laporan tesis."
)

DATASETS = [
    {
        "name": "tracker",
        "label": "Tracker — Aktivitas Log",
        "path": Path("data/anomalies/tracker_anomalies_clustered.csv"),
        "config": Path("models/kmeans_config_tracker.json"),
        "key_columns": ["timestamp", "user_id", "query_type", "lof_score", "cluster"],
        "description": "Log aktivitas yang sudah memiliki skor LOF dan klaster K-Means.",
    },
    {
        "name": "staff",
        "label": "Staff — Master Login",
        "path": Path("data/anomalies/staff_anomalies_clustered.csv"),
        "config": Path("models/kmeans_config_staff.json"),
        "key_columns": ["timestamp", "user_id", "name", "lof_score", "cluster"],
        "description": "Data login staff yang digunakan untuk mendeteksi pola anomali.",
    },
]


def load_dataset(dataset: dict) -> tuple[pd.DataFrame, dict]:
    dataframe = pd.read_csv(dataset["path"])
    with dataset["config"].open("r", encoding="utf-8") as cfg:
        config = json.load(cfg)
    return dataframe, config


def describe_clusters(df: pd.DataFrame) -> pd.DataFrame:
    summary = (
        df.groupby("cluster")
        .agg(
            count=("cluster", "size"),
            unique_users=("user_id", "nunique"),
            avg_lof=("lof_score", "mean"),
        )
        .reset_index()
    )
    summary["percentage"] = (summary["count"] / len(df) * 100).round(1)
    return summary


if "run_pipeline" not in st.session_state:
    st.session_state.run_pipeline = False
    st.session_state.selected_dataset = DATASETS[0]["name"]
    st.session_state.selected_stage = "LOF"
    st.session_state.selected_k = 5
    st.session_state.selected_contamination = 0.05

with st.sidebar.form("pipeline_form"):
    st.sidebar.header("Input Proses")
    dataset_choice = st.selectbox(
        "Pilih dataset",
        options=[dataset["name"] for dataset in DATASETS],
        format_func=lambda name: next(item["label"] for item in DATASETS if item["name"] == name),
        index=0,
    )
    stage_choice = st.radio("Tahap pipeline", options=["LOF", "K-Means"], index=0)
    k_value = st.slider("K (jumlah tetangga / klaster)", 2, 10, 5)
    contamination_value = st.slider("Kontaminasi (untuk LOF)", 0.01, 0.2, 0.05, step=0.01)
    submit = st.form_submit_button("Jalankan Proses")

if submit:
    st.session_state.run_pipeline = True
    st.session_state.selected_dataset = dataset_choice
    st.session_state.selected_stage = stage_choice
    st.session_state.selected_k = k_value
    st.session_state.selected_contamination = contamination_value

selected_name = st.session_state.selected_dataset
selected_stage = st.session_state.selected_stage
selected_k = st.session_state.selected_k
selected_contamination = st.session_state.selected_contamination

selected = next(dataset for dataset in DATASETS if dataset["name"] == selected_name)

if not selected["path"].exists() or not selected["config"].exists():
    st.warning("File dataset atau konfigurasi belum tersedia. Jalankan 05-06 terlebih dahulu.")
    st.stop()

df, config = load_dataset(selected)

st.sidebar.markdown("#### Parameter aktif")
st.sidebar.write(f"- Dataset: **{selected['label']}**")
st.sidebar.write(f"- Tahap: **{selected_stage}**")
st.sidebar.write(f"- K: **{selected_k}**")
st.sidebar.write(f"- Kontaminasi: **{selected_contamination:.2f}**")

st.subheader("Ringkasan Input Proses")
st.info(
    f"Tahap {selected_stage} siap dijalankan pada dataset **{selected['label']}** "
    f"dengan parameter K = {selected_k} dan kontaminasi = {selected_contamination:.2f}."
    "Tekan tombol “Jalankan Proses” di sidebar untuk menampilkan hasil."
)

if not st.session_state.run_pipeline:
    st.stop()

st.success(
    f"Proses dijalankan: Stage {selected_stage}, K={selected_k}, kontaminasi={selected_contamination:.2f}."
)

st.subheader(selected["label"])
st.caption(selected["description"])

col1, col2, col3 = st.columns(3)
col1.metric("Total Anomali", f"{len(df):,}")
col1.metric("Klaster Teridentifikasi", df["cluster"].nunique())
col2.metric("Silhouette", f"{config.get('silhouette_score', 0):.3f}")
col2.metric("Davies-Bouldin", f"{config.get('davies_bouldin_index', 0):.3f}")
col3.metric("Optimal k", config.get("optimal_k", "-"))
col3.metric("Model type", config.get("model_type", "KMeans"))

with st.expander("Distribusi Klaster"):
    cluster_summary = describe_clusters(df)
    st.bar_chart(
        cluster_summary.set_index("cluster")["count"],
        width="stretch",
    )
    st.dataframe(
        cluster_summary.rename(
            columns={
                "cluster": "Cluster",
                "count": "Jumlah",
                "percentage": "% dari total",
                "unique_users": "Jumlah user unik",
                "avg_lof": "LOF rata-rata",
            }
        ),
        width="stretch",
    )

with st.expander("Kelengkapan Statistik per Klaster"):
    st.table(
        df.groupby("cluster")
        .agg(
            peak_hour=("timestamp", lambda s: pd.to_datetime(s).dt.hour.mode().iloc[0]),
            avg_lof=("lof_score", "mean"),
            avg_cluster_size=("cluster", "count"),
        )
        .reset_index()
        .rename(
            columns={
                "cluster": "Cluster",
                "peak_hour": "Jam puncak",
                "avg_lof": "LOF rata-rata",
                "avg_cluster_size": "Ukuran",
            }
        )
    )

st.markdown("### Contoh Anomali Ekstrem")
st.dataframe(
    df.nlargest(10, "lof_score")[selected["key_columns"]],
    width="stretch",
)

st.markdown("### Daftar Anomali Lengkap")
display_columns = list(dict.fromkeys(selected["key_columns"] + ["cluster"]))
st.dataframe(df[display_columns], width="stretch")
