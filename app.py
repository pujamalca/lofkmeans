import json
from pathlib import Path
from typing import Dict, Tuple, Optional, List
import pandas as pd
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime

# ============================================================================
# PAGE CONFIGURATION
# ============================================================================

st.set_page_config(
    page_title="LOF + K-Means Pipeline - Deteksi Anomali",
    layout="wide",
    initial_sidebar_state="expanded",
    page_icon="🔍"
)

# ============================================================================
# TAILWIND CSS & CUSTOM STYLES
# ============================================================================

def load_custom_css():
    """Load Tailwind CSS and custom styles"""
    st.markdown("""
    <link href="https://cdn.jsdelivr.net/npm/tailwindcss@2.2.19/dist/tailwind.min.css" rel="stylesheet">
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap" rel="stylesheet">

    <style>
        /* Global Styles */
        * {
            font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
        }

        /* Hide Streamlit branding */
        #MainMenu {visibility: hidden;}
        footer {visibility: hidden;}
        header {visibility: hidden;}

        /* Custom Scrollbar */
        ::-webkit-scrollbar {
            width: 8px;
            height: 8px;
        }
        ::-webkit-scrollbar-track {
            background: #f1f1f1;
        }
        ::-webkit-scrollbar-thumb {
            background: #888;
            border-radius: 4px;
        }
        ::-webkit-scrollbar-thumb:hover {
            background: #555;
        }

        /* Streamlit overrides */
        .stButton>button {
            background: linear-gradient(135deg, #3B82F6 0%, #2563EB 100%);
            color: white;
            border: none;
            padding: 0.75rem 2rem;
            border-radius: 0.5rem;
            font-weight: 600;
            transition: all 0.3s ease;
            box-shadow: 0 4px 6px rgba(59, 130, 246, 0.3);
        }
        .stButton>button:hover {
            transform: translateY(-2px);
            box-shadow: 0 6px 12px rgba(59, 130, 246, 0.4);
        }

        /* Card Styles */
        .stage-card {
            background: white;
            border-radius: 1rem;
            padding: 2rem;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.07);
            border: 1px solid #E5E7EB;
            margin-bottom: 1.5rem;
            transition: all 0.3s ease;
        }
        .stage-card:hover {
            box-shadow: 0 8px 16px rgba(0, 0, 0, 0.1);
        }

        .metric-card {
            background: linear-gradient(135deg, #F9FAFB 0%, #FFFFFF 100%);
            border-radius: 0.75rem;
            padding: 1.5rem;
            border-left: 4px solid #3B82F6;
            box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
        }

        .metric-value {
            font-size: 2rem;
            font-weight: 700;
            color: #1F2937;
            margin: 0.5rem 0;
        }

        .metric-label {
            font-size: 0.875rem;
            color: #6B7280;
            font-weight: 500;
            text-transform: uppercase;
            letter-spacing: 0.05em;
        }

        /* Progress Stepper */
        .progress-stepper {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin: 2rem 0;
            padding: 0 1rem;
        }

        .step {
            display: flex;
            flex-direction: column;
            align-items: center;
            position: relative;
            flex: 1;
        }

        .step-circle {
            width: 48px;
            height: 48px;
            border-radius: 50%;
            display: flex;
            align-items: center;
            justify-content: center;
            font-weight: 700;
            font-size: 1rem;
            z-index: 2;
            transition: all 0.3s ease;
        }

        .step-circle.active {
            background: linear-gradient(135deg, #3B82F6 0%, #2563EB 100%);
            color: white;
            box-shadow: 0 4px 12px rgba(59, 130, 246, 0.4);
            transform: scale(1.1);
        }

        .step-circle.completed {
            background: linear-gradient(135deg, #10B981 0%, #059669 100%);
            color: white;
        }

        .step-circle.pending {
            background: #E5E7EB;
            color: #9CA3AF;
        }

        .step-label {
            margin-top: 0.5rem;
            font-size: 0.75rem;
            font-weight: 600;
            color: #6B7280;
            text-align: center;
        }

        .step-line {
            position: absolute;
            top: 24px;
            left: 50%;
            right: -50%;
            height: 3px;
            background: #E5E7EB;
            z-index: 1;
        }

        .step-line.completed {
            background: linear-gradient(90deg, #10B981 0%, #059669 100%);
        }

        /* Alert Boxes */
        .alert {
            padding: 1rem 1.5rem;
            border-radius: 0.5rem;
            margin: 1rem 0;
            display: flex;
            align-items: start;
        }

        .alert-info {
            background: #EFF6FF;
            border-left: 4px solid #3B82F6;
            color: #1E40AF;
        }

        .alert-success {
            background: #ECFDF5;
            border-left: 4px solid #10B981;
            color: #065F46;
        }

        .alert-warning {
            background: #FFFBEB;
            border-left: 4px solid #F59E0B;
            color: #92400E;
        }

        .alert-danger {
            background: #FEF2F2;
            border-left: 4px solid #EF4444;
            color: #991B1B;
        }

        /* Table Styles */
        .dataframe {
            border-radius: 0.5rem;
            overflow: hidden;
        }

        /* Header Styles */
        .main-header {
            background: linear-gradient(135deg, #1E40AF 0%, #3B82F6 100%);
            color: white;
            padding: 2rem;
            border-radius: 1rem;
            margin-bottom: 2rem;
            box-shadow: 0 8px 16px rgba(30, 64, 175, 0.2);
        }

        .main-title {
            font-size: 2.5rem;
            font-weight: 800;
            margin: 0;
            text-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
        }

        .main-subtitle {
            font-size: 1.125rem;
            opacity: 0.9;
            margin-top: 0.5rem;
        }

        /* Badge */
        .badge {
            display: inline-block;
            padding: 0.25rem 0.75rem;
            border-radius: 9999px;
            font-size: 0.75rem;
            font-weight: 600;
        }

        .badge-blue {
            background: #DBEAFE;
            color: #1E40AF;
        }

        .badge-green {
            background: #D1FAE5;
            color: #065F46;
        }

        .badge-yellow {
            background: #FEF3C7;
            color: #92400E;
        }

        .badge-red {
            background: #FEE2E2;
            color: #991B1B;
        }

        /* Loading Spinner */
        .spinner {
            border: 4px solid #E5E7EB;
            border-top: 4px solid #3B82F6;
            border-radius: 50%;
            width: 40px;
            height: 40px;
            animation: spin 1s linear infinite;
            margin: 2rem auto;
        }

        @keyframes spin {
            0% { transform: rotate(0deg); }
            100% { transform: rotate(360deg); }
        }
    </style>
    """, unsafe_allow_html=True)

# ============================================================================
# REUSABLE COMPONENTS
# ============================================================================

def render_header():
    """Render main header"""
    st.markdown("""
    <div class="main-header">
        <h1 class="main-title">🔍 Pipeline Deteksi Anomali</h1>
        <p class="main-subtitle">LOF (Local Outlier Factor) + K-Means Clustering untuk Analisis Anomali Data</p>
    </div>
    """, unsafe_allow_html=True)

def render_progress_stepper(current_stage: int, completed_stages: List[int]):
    """Render progress stepper for 7 stages"""
    stages = [
        {"num": 1, "label": "Load"},
        {"num": 2, "label": "Prep"},
        {"num": 3, "label": "Feature"},
        {"num": 4, "label": "Norm"},
        {"num": 5, "label": "LOF"},
        {"num": 6, "label": "K-Means"},
        {"num": 7, "label": "Result"}
    ]

    html = '<div class="progress-stepper">'

    for i, stage in enumerate(stages):
        stage_num = stage["num"]

        # Determine state
        if stage_num in completed_stages:
            state = "completed"
            icon = "✓"
        elif stage_num == current_stage:
            state = "active"
            icon = str(stage_num)
        else:
            state = "pending"
            icon = str(stage_num)

        html += f'''
        <div class="step">
            <div class="step-circle {state}">{icon}</div>
            <div class="step-label">{stage["label"]}</div>
            {f'<div class="step-line {state}"></div>' if i < len(stages) - 1 else ''}
        </div>
        '''

    html += '</div>'
    st.markdown(html, unsafe_allow_html=True)

def render_metric_card(label: str, value: str, color: str = "blue"):
    """Render a metric card"""
    colors = {
        "blue": "#3B82F6",
        "green": "#10B981",
        "yellow": "#F59E0B",
        "red": "#EF4444",
        "purple": "#8B5CF6"
    }

    border_color = colors.get(color, colors["blue"])

    st.markdown(f"""
    <div class="metric-card" style="border-left-color: {border_color};">
        <div class="metric-label">{label}</div>
        <div class="metric-value">{value}</div>
    </div>
    """, unsafe_allow_html=True)

def render_alert(message: str, type: str = "info"):
    """Render alert box"""
    icons = {
        "info": "ℹ️",
        "success": "✅",
        "warning": "⚠️",
        "danger": "❌"
    }

    icon = icons.get(type, icons["info"])

    st.markdown(f"""
    <div class="alert alert-{type}">
        <span style="margin-right: 0.75rem; font-size: 1.25rem;">{icon}</span>
        <span>{message}</span>
    </div>
    """, unsafe_allow_html=True)

def render_badge(text: str, color: str = "blue"):
    """Render badge"""
    st.markdown(f'<span class="badge badge-{color}">{text}</span>', unsafe_allow_html=True)

# ============================================================================
# DATA CONFIGURATIONS
# ============================================================================

DATASETS = {
    "tracker": {
        "label": "📊 Tracker - Aktivitas Database",
        "raw_path": Path("data/raw/tracker_raw.csv"),
        "cleaned_path": Path("data/cleaned/tracker_cleaned.csv"),
        "transformed_path": Path("data/transformed/tracker_transformed.csv"),
        "normalized_path": Path("data/normalized/tracker_normalized.csv"),
        "anomalies_path": Path("data/anomalies/tracker_with_lof_scores.csv"),
        "clustered_path": Path("data/anomalies/tracker_anomalies_clustered.csv"),
        "lof_config": Path("models/lof_config_tracker.json"),
        "kmeans_config": Path("models/kmeans_config_tracker.json"),
        "feature_info": Path("models/feature_info_tracker.json"),
        "description": "Log aktivitas database dengan query type, timestamp, dan user information"
    },
    "staff": {
        "label": "👥 Staff - Master Login",
        "raw_path": Path("data/raw/staff_raw.csv"),
        "cleaned_path": Path("data/cleaned/staff_cleaned.csv"),
        "transformed_path": Path("data/transformed/staff_transformed.csv"),
        "normalized_path": Path("data/normalized/staff_normalized.csv"),
        "anomalies_path": Path("data/anomalies/staff_with_lof_scores.csv"),
        "clustered_path": Path("data/anomalies/staff_anomalies_clustered.csv"),
        "lof_config": Path("models/lof_config_staff.json"),
        "kmeans_config": Path("models/kmeans_config_staff.json"),
        "feature_info": Path("models/feature_info_staff.json"),
        "description": "Data login staff dengan informasi waktu akses dan pola login"
    }
}

# ============================================================================
# UTILITY FUNCTIONS
# ============================================================================

@st.cache_data(ttl=3600)
def load_data(path: Path) -> Optional[pd.DataFrame]:
    """Load CSV data with error handling and caching"""
    if not path.exists():
        return None
    try:
        return pd.read_csv(path)
    except Exception as e:
        st.error(f"Error loading {path}: {str(e)}")
        return None

@st.cache_data(ttl=3600)
def load_config(path: Path) -> Optional[Dict]:
    """Load JSON config with error handling and caching"""
    if not path.exists():
        return None
    try:
        with open(path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        st.error(f"Error loading {path}: {str(e)}")
        return None

def format_number(num: int) -> str:
    """Format number with thousand separator"""
    return f"{num:,}"

def get_file_info(path: Path) -> Dict:
    """Get file information"""
    if not path.exists():
        return {"exists": False}

    stat = path.stat()
    return {
        "exists": True,
        "size_mb": round(stat.st_size / (1024 * 1024), 2),
        "modified": datetime.fromtimestamp(stat.st_mtime).strftime("%Y-%m-%d %H:%M")
    }

# ============================================================================
# SESSION STATE INITIALIZATION
# ============================================================================

def init_session_state():
    """Initialize session state variables"""
    if 'current_stage' not in st.session_state:
        st.session_state.current_stage = 1

    if 'completed_stages' not in st.session_state:
        st.session_state.completed_stages = []

    if 'selected_dataset' not in st.session_state:
        st.session_state.selected_dataset = "tracker"

    if 'lof_params' not in st.session_state:
        st.session_state.lof_params = {
            'n_neighbors': 5,
            'contamination': 0.05
        }

    if 'kmeans_params' not in st.session_state:
        st.session_state.kmeans_params = {
            'n_clusters': 3
        }

# ============================================================================
# ADVANCED VISUALIZATIONS
# ============================================================================

def create_lof_score_scatter(df: pd.DataFrame, dataset_name: str) -> go.Figure:
    """Create scatter plot of LOF scores"""
    if 'lof_score' not in df.columns:
        return None

    # Add index for x-axis
    df_plot = df.copy()
    df_plot['index'] = range(len(df_plot))

    fig = go.Figure()

    # Separate anomalies and normal data
    if 'is_anomaly' in df.columns:
        anomalies = df_plot[df_plot['is_anomaly'] == -1]
        normal = df_plot[df_plot['is_anomaly'] == 1]

        # Plot normal data
        fig.add_trace(go.Scatter(
            x=normal['index'],
            y=normal['lof_score'],
            mode='markers',
            name='Normal',
            marker=dict(color='#10B981', size=4, opacity=0.6)
        ))

        # Plot anomalies
        fig.add_trace(go.Scatter(
            x=anomalies['index'],
            y=anomalies['lof_score'],
            mode='markers',
            name='Anomaly',
            marker=dict(color='#EF4444', size=6, opacity=0.8)
        ))
    else:
        fig.add_trace(go.Scatter(
            x=df_plot['index'],
            y=df_plot['lof_score'],
            mode='markers',
            name='LOF Score',
            marker=dict(color='#3B82F6', size=4, opacity=0.6)
        ))

    fig.update_layout(
        title=f"LOF Score Distribution - {dataset_name}",
        xaxis_title="Data Point Index",
        yaxis_title="LOF Score",
        hovermode='closest',
        showlegend=True
    )

    return fig

def create_cluster_scatter_2d(df: pd.DataFrame, dataset_name: str) -> go.Figure:
    """Create 2D scatter plot of clusters using first two features"""
    if 'cluster' not in df.columns:
        return None

    # Get numeric columns (excluding cluster and lof_score)
    numeric_cols = df.select_dtypes(include=['float64', 'int64']).columns.tolist()
    exclude_cols = ['cluster', 'lof_score', 'is_anomaly']
    feature_cols = [col for col in numeric_cols if col not in exclude_cols]

    if len(feature_cols) < 2:
        return None

    # Use first two features for visualization
    x_col = feature_cols[0]
    y_col = feature_cols[1]

    fig = px.scatter(
        df,
        x=x_col,
        y=y_col,
        color='cluster',
        title=f"Cluster Visualization (2D) - {dataset_name}",
        labels={'cluster': 'Cluster'},
        color_continuous_scale='viridis'
    )

    fig.update_traces(marker=dict(size=8, opacity=0.7))

    return fig

def create_temporal_heatmap(df: pd.DataFrame, dataset_name: str) -> go.Figure:
    """Create heatmap of anomalies by hour and day of week"""
    if 'timestamp' not in df.columns:
        return None

    try:
        df_temp = df.copy()
        df_temp['timestamp'] = pd.to_datetime(df_temp['timestamp'], errors='coerce')
        df_temp = df_temp.dropna(subset=['timestamp'])

        df_temp['hour'] = df_temp['timestamp'].dt.hour
        df_temp['day_of_week'] = df_temp['timestamp'].dt.dayofweek

        # Create pivot table
        heatmap_data = df_temp.groupby(['day_of_week', 'hour']).size().unstack(fill_value=0)

        # Day names
        day_names = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']

        fig = go.Figure(data=go.Heatmap(
            z=heatmap_data.values,
            x=list(range(24)),
            y=[day_names[i] for i in heatmap_data.index],
            colorscale='Blues',
            text=heatmap_data.values,
            texttemplate='%{text}',
            textfont={"size": 10},
            colorbar=dict(title="Count")
        ))

        fig.update_layout(
            title=f"Anomaly Distribution by Time - {dataset_name}",
            xaxis_title="Hour of Day",
            yaxis_title="Day of Week",
            height=400
        )

        return fig
    except Exception as e:
        st.warning(f"Could not create temporal heatmap: {str(e)}")
        return None

def create_comparison_metrics(dataset1_name: str, dataset2_name: str) -> pd.DataFrame:
    """Create comparison table between two datasets"""
    datasets_data = []

    for ds_key in [dataset1_name, dataset2_name]:
        dataset_info = DATASETS[ds_key]

        # Load configs
        lof_config = load_config(dataset_info["lof_config"])
        kmeans_config = load_config(dataset_info["kmeans_config"])
        df_clustered = load_data(dataset_info["clustered_path"])

        if df_clustered is not None and lof_config and kmeans_config:
            datasets_data.append({
                'Dataset': DATASETS[ds_key]['label'],
                'Total Anomalies': len(df_clustered),
                'Clusters': df_clustered['cluster'].nunique() if 'cluster' in df_clustered.columns else 'N/A',
                'LOF K': lof_config.get('optimal_k', 'N/A'),
                'Anomaly Rate (%)': round(lof_config.get('final_anomaly_percentage', 0), 2),
                'Silhouette Score': round(kmeans_config.get('silhouette_score', 0), 3),
                'Davies-Bouldin': round(kmeans_config.get('davies_bouldin_index', 0), 3),
            })

    return pd.DataFrame(datasets_data)

# ============================================================================
# STAGE IMPLEMENTATIONS
# ============================================================================

def render_stage_01():
    """Stage 01: Load & Explore"""
    st.markdown('<div class="stage-card">', unsafe_allow_html=True)
    st.markdown("### 📁 Stage 01: Load & Explore Data")

    # Dataset selection
    col1, col2 = st.columns([2, 3])

    with col1:
        dataset_key = st.selectbox(
            "Pilih Dataset",
            options=list(DATASETS.keys()),
            format_func=lambda x: DATASETS[x]["label"],
            key="dataset_selector"
        )
        st.session_state.selected_dataset = dataset_key

    with col2:
        dataset_info = DATASETS[dataset_key]
        st.markdown(f"**Deskripsi:** {dataset_info['description']}")

    # Load raw data
    raw_path = dataset_info["raw_path"]
    file_info = get_file_info(raw_path)

    if not file_info["exists"]:
        render_alert(f"File {raw_path} tidak ditemukan. Pastikan data sudah ada di folder data/raw/", "warning")
        st.markdown('</div>', unsafe_allow_html=True)
        return

    df_raw = load_data(raw_path)

    if df_raw is None:
        render_alert("Gagal memuat data", "danger")
        st.markdown('</div>', unsafe_allow_html=True)
        return

    # Display metrics
    st.markdown("#### 📊 Informasi Dataset")

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        render_metric_card("Total Rows", format_number(len(df_raw)), "blue")

    with col2:
        render_metric_card("Columns", str(df_raw.shape[1]), "green")

    with col3:
        render_metric_card("File Size", f"{file_info['size_mb']} MB", "purple")

    with col4:
        render_metric_card("Missing Values", str(df_raw.isnull().sum().sum()), "yellow")

    # Data preview
    st.markdown("#### 🔍 Preview Data (10 baris pertama)")
    st.dataframe(df_raw.head(10), use_container_width=True)

    # Basic statistics
    with st.expander("📈 Statistik Deskriptif"):
        st.dataframe(df_raw.describe(), use_container_width=True)

    # Column info
    with st.expander("📋 Informasi Kolom"):
        col_info = pd.DataFrame({
            'Column': df_raw.columns,
            'Type': df_raw.dtypes.values,
            'Non-Null': df_raw.count().values,
            'Null': df_raw.isnull().sum().values
        })
        st.dataframe(col_info, use_container_width=True)

    # Navigation
    st.markdown("<br>", unsafe_allow_html=True)
    if st.button("▶ Lanjut ke Stage 02: Preprocessing", type="primary"):
        st.session_state.current_stage = 2
        if 1 not in st.session_state.completed_stages:
            st.session_state.completed_stages.append(1)
        st.rerun()

    st.markdown('</div>', unsafe_allow_html=True)

def render_stage_02():
    """Stage 02: Preprocessing"""
    st.markdown('<div class="stage-card">', unsafe_allow_html=True)
    st.markdown("### 🧹 Stage 02: Preprocessing & Data Cleaning")

    dataset_key = st.session_state.selected_dataset
    dataset_info = DATASETS[dataset_key]

    # Load data
    df_raw = load_data(dataset_info["raw_path"])
    df_cleaned = load_data(dataset_info["cleaned_path"])

    if df_raw is None:
        render_alert("Data raw tidak ditemukan. Kembali ke Stage 01.", "warning")
        st.markdown('</div>', unsafe_allow_html=True)
        return

    if df_cleaned is None:
        render_alert("Data cleaned belum tersedia. Jalankan script 02_preprocessing.py terlebih dahulu.", "warning")
        st.markdown('</div>', unsafe_allow_html=True)
        return

    # Show before/after comparison
    st.markdown("#### ⚖️ Perbandingan Before/After")

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("**📥 Before Preprocessing**")
        render_metric_card("Total Rows", format_number(len(df_raw)), "red")
        render_metric_card("Missing Values", str(df_raw.isnull().sum().sum()), "yellow")
        render_metric_card("Duplicates", str(df_raw.duplicated().sum()), "yellow")

    with col2:
        st.markdown("**✅ After Preprocessing**")
        render_metric_card("Total Rows", format_number(len(df_cleaned)), "green")
        render_metric_card("Missing Values", str(df_cleaned.isnull().sum().sum()), "green")
        render_metric_card("Duplicates", str(df_cleaned.duplicated().sum()), "green")

    # Retention rate
    retention = (len(df_cleaned) / len(df_raw)) * 100
    st.markdown("#### 📊 Data Retention")

    if retention >= 95:
        color = "green"
    elif retention >= 90:
        color = "yellow"
    else:
        color = "red"

    render_metric_card("Data Retained", f"{retention:.1f}%", color)

    # Rows removed breakdown
    rows_removed = len(df_raw) - len(df_cleaned)
    st.markdown(f"**Rows Removed:** {format_number(rows_removed)} ({100-retention:.1f}%)")

    # Preview cleaned data
    st.markdown("#### 🔍 Preview Cleaned Data")
    st.dataframe(df_cleaned.head(10), use_container_width=True)

    # Navigation
    st.markdown("<br>", unsafe_allow_html=True)
    col1, col2 = st.columns([1, 1])

    with col1:
        if st.button("◀ Kembali ke Stage 01", key="back_to_01"):
            st.session_state.current_stage = 1
            st.rerun()

    with col2:
        if st.button("▶ Lanjut ke Stage 03: Feature Engineering", type="primary"):
            st.session_state.current_stage = 3
            if 2 not in st.session_state.completed_stages:
                st.session_state.completed_stages.append(2)
            st.rerun()

    st.markdown('</div>', unsafe_allow_html=True)

def render_stage_03():
    """Stage 03: Feature Engineering"""
    st.markdown('<div class="stage-card">', unsafe_allow_html=True)
    st.markdown("### ⚙️ Stage 03: Feature Engineering")

    dataset_key = st.session_state.selected_dataset
    dataset_info = DATASETS[dataset_key]

    # Load data
    df_transformed = load_data(dataset_info["transformed_path"])
    feature_info = load_config(dataset_info["feature_info"])

    if df_transformed is None:
        render_alert("Data transformed belum tersedia. Jalankan script 03_feature_engineering.py terlebih dahulu.", "warning")
        st.markdown('</div>', unsafe_allow_html=True)
        return

    # Total features
    total_features = df_transformed.shape[1]

    st.markdown("#### 📊 Feature Summary")
    render_metric_card("Total Features Created", str(total_features), "blue")

    # Feature categories for tracker
    if dataset_key == "tracker":
        st.markdown("#### 🏷️ Feature Categories")

        col1, col2, col3 = st.columns(3)

        with col1:
            st.markdown("**🕐 Temporal Features (7)**")
            st.markdown("""
            - hour
            - day_of_week
            - month
            - day_of_month
            - IsOutsideWorkHours
            - IsWeekend
            - NightShift
            """)

        with col2:
            st.markdown("**🏷️ Categorical Features (3)**")
            st.markdown("""
            - op_DELETE
            - op_INSERT
            - op_UPDATE
            """)

        with col3:
            st.markdown("**📊 Behavioral Features (4)**")
            st.markdown("""
            - frequency
            - operation_diversity
            - modification_ratio
            - access_time_variation
            """)

    # Feature categories for staff
    else:
        st.markdown("#### 🏷️ Feature Categories")

        col1, col2 = st.columns(2)

        with col1:
            st.markdown("**🕐 Temporal Features (8)**")
            st.markdown("""
            - hour
            - day_of_week
            - month
            - day_of_month
            - IsEarlyLogin
            - IsLateLogin
            - IsAfterWorkHours
            - IsWeekend
            """)

        with col2:
            st.markdown("**📊 Behavioral Features (3)**")
            st.markdown("""
            - login_frequency
            - login_time_variation
            - weekend_login_ratio
            """)

    # Preview features
    st.markdown("#### 🔍 Preview Transformed Data")
    st.dataframe(df_transformed.head(10), use_container_width=True)

    # Feature statistics
    with st.expander("📈 Feature Statistics"):
        st.dataframe(df_transformed.describe(), use_container_width=True)

    # Navigation
    st.markdown("<br>", unsafe_allow_html=True)
    col1, col2 = st.columns([1, 1])

    with col1:
        if st.button("◀ Kembali ke Stage 02", key="back_to_02"):
            st.session_state.current_stage = 2
            st.rerun()

    with col2:
        if st.button("▶ Lanjut ke Stage 04: Normalization", type="primary"):
            st.session_state.current_stage = 4
            if 3 not in st.session_state.completed_stages:
                st.session_state.completed_stages.append(3)
            st.rerun()

    st.markdown('</div>', unsafe_allow_html=True)

def render_stage_04():
    """Stage 04: Normalization"""
    st.markdown('<div class="stage-card">', unsafe_allow_html=True)
    st.markdown("### 📊 Stage 04: Normalization")

    dataset_key = st.session_state.selected_dataset
    dataset_info = DATASETS[dataset_key]

    # Load data
    df_normalized = load_data(dataset_info["normalized_path"])
    df_transformed = load_data(dataset_info["transformed_path"])

    if df_normalized is None:
        render_alert("Data normalized belum tersedia. Jalankan script 04_normalization.py terlebih dahulu.", "warning")
        st.markdown('</div>', unsafe_allow_html=True)
        return

    st.markdown("#### ⚙️ Normalization Method")
    render_alert("Menggunakan StandardScaler (Z-score normalization): z = (x - mean) / std", "info")

    # Verification
    st.markdown("#### ✅ Verification")

    mean_val = df_normalized.mean().mean()
    std_val = df_normalized.std().mean()

    col1, col2 = st.columns(2)

    with col1:
        color = "green" if abs(mean_val) < 0.01 else "yellow"
        render_metric_card("Mean ≈ 0", f"{mean_val:.6f}", color)

    with col2:
        color = "green" if abs(std_val - 1.0) < 0.01 else "yellow"
        render_metric_card("Std Dev ≈ 1", f"{std_val:.6f}", color)

    # Before/After comparison with visualization
    if df_transformed is not None:
        st.markdown("#### 📊 Distribution Before/After")

        # Select a sample column for visualization
        numeric_cols = df_transformed.select_dtypes(include=['float64', 'int64']).columns
        if len(numeric_cols) > 0:
            sample_col = numeric_cols[0]

            col1, col2 = st.columns(2)

            with col1:
                st.markdown("**Before Normalization**")
                fig_before = px.histogram(
                    df_transformed,
                    x=sample_col,
                    title=f"Distribution of {sample_col}",
                    color_discrete_sequence=['#EF4444']
                )
                st.plotly_chart(fig_before, use_container_width=True)

            with col2:
                st.markdown("**After Normalization**")
                fig_after = px.histogram(
                    df_normalized,
                    x=sample_col,
                    title=f"Normalized Distribution of {sample_col}",
                    color_discrete_sequence=['#10B981']
                )
                st.plotly_chart(fig_after, use_container_width=True)

    # Preview normalized data
    st.markdown("#### 🔍 Preview Normalized Data")
    st.dataframe(df_normalized.head(10), use_container_width=True)

    # Navigation
    st.markdown("<br>", unsafe_allow_html=True)
    col1, col2 = st.columns([1, 1])

    with col1:
        if st.button("◀ Kembali ke Stage 03", key="back_to_03"):
            st.session_state.current_stage = 3
            st.rerun()

    with col2:
        if st.button("▶ Lanjut ke Stage 05: LOF Detection", type="primary"):
            st.session_state.current_stage = 5
            if 4 not in st.session_state.completed_stages:
                st.session_state.completed_stages.append(4)
            st.rerun()

    st.markdown('</div>', unsafe_allow_html=True)

def render_stage_05():
    """Stage 05: LOF Anomaly Detection"""
    st.markdown('<div class="stage-card">', unsafe_allow_html=True)
    st.markdown("### 🔍 Stage 05: LOF Anomaly Detection")

    dataset_key = st.session_state.selected_dataset
    dataset_info = DATASETS[dataset_key]

    # Load data
    df_anomalies = load_data(dataset_info["anomalies_path"])
    lof_config = load_config(dataset_info["lof_config"])

    if df_anomalies is None or lof_config is None:
        render_alert("Data LOF belum tersedia. Jalankan script 05_lof_modeling.py terlebih dahulu.", "warning")
        st.markdown('</div>', unsafe_allow_html=True)
        return

    # LOF Parameters
    st.markdown("#### ⚙️ LOF Parameters (dari Grid Search)")

    col1, col2, col3 = st.columns(3)

    with col1:
        render_metric_card("Optimal K", str(lof_config.get('optimal_k', 'N/A')), "blue")

    with col2:
        render_metric_card("Contamination", f"{lof_config.get('contamination', 0)*100:.0f}%", "purple")

    with col3:
        render_metric_card("Features Used", str(lof_config.get('n_features', 'N/A')), "green")

    # Results
    st.markdown("#### 📊 Detection Results")

    total_data = len(df_anomalies[df_anomalies['is_anomaly'].isin([-1, 1])]) if 'is_anomaly' in df_anomalies.columns else len(df_anomalies)
    anomalies = df_anomalies[df_anomalies['is_anomaly'] == -1] if 'is_anomaly' in df_anomalies.columns else df_anomalies
    num_anomalies = len(anomalies)
    anomaly_rate = (num_anomalies / total_data * 100) if total_data > 0 else 0

    col1, col2, col3 = st.columns(3)

    with col1:
        render_metric_card("Total Data", format_number(total_data), "blue")

    with col2:
        render_metric_card("Anomalies Detected", format_number(num_anomalies), "red")

    with col3:
        color = "green" if 4 <= anomaly_rate <= 6 else "yellow"
        render_metric_card("Anomaly Rate", f"{anomaly_rate:.2f}%", color)

    # LOF Score Distribution
    st.markdown("#### 📈 LOF Score Distribution")

    if 'lof_score' in df_anomalies.columns:
        col1, col2 = st.columns(2)

        with col1:
            # Histogram
            fig_hist = px.histogram(
                df_anomalies,
                x='lof_score',
                nbins=50,
                title="Distribution of LOF Scores (Histogram)",
                color_discrete_sequence=['#3B82F6'],
                labels={'lof_score': 'LOF Score', 'count': 'Frequency'}
            )
            fig_hist.update_layout(showlegend=False)
            st.plotly_chart(fig_hist, use_container_width=True)

        with col2:
            # Scatter plot
            fig_scatter = create_lof_score_scatter(df_anomalies, DATASETS[dataset_key]['label'])
            if fig_scatter:
                st.plotly_chart(fig_scatter, use_container_width=True)

        # LOF Score statistics
        col1, col2, col3, col4 = st.columns(4)

        with col1:
            render_metric_card("Min LOF", f"{df_anomalies['lof_score'].min():.2f}", "blue")
        with col2:
            render_metric_card("Max LOF", f"{df_anomalies['lof_score'].max():.2f}", "red")
        with col3:
            render_metric_card("Mean LOF", f"{df_anomalies['lof_score'].mean():.2f}", "purple")
        with col4:
            render_metric_card("Median LOF", f"{df_anomalies['lof_score'].median():.2f}", "green")

    # Top anomalies
    st.markdown("#### 🚨 Top 10 Anomalies (Highest LOF Scores)")

    if 'lof_score' in anomalies.columns:
        top_anomalies = anomalies.nlargest(10, 'lof_score')
        display_cols = [col for col in ['timestamp', 'user_id', 'query_type', 'name', 'lof_score'] if col in top_anomalies.columns]
        st.dataframe(top_anomalies[display_cols], use_container_width=True)

    # Grid search results
    if 'grid_search_results' in lof_config:
        with st.expander("🔬 Grid Search Results"):
            grid_results = pd.DataFrame(lof_config['grid_search_results'])
            st.dataframe(grid_results, use_container_width=True)

    # Navigation
    st.markdown("<br>", unsafe_allow_html=True)
    col1, col2 = st.columns([1, 1])

    with col1:
        if st.button("◀ Kembali ke Stage 04", key="back_to_04"):
            st.session_state.current_stage = 4
            st.rerun()

    with col2:
        if st.button("▶ Lanjut ke Stage 06: K-Means Clustering", type="primary"):
            st.session_state.current_stage = 6
            if 5 not in st.session_state.completed_stages:
                st.session_state.completed_stages.append(5)
            st.rerun()

    st.markdown('</div>', unsafe_allow_html=True)

def render_stage_06():
    """Stage 06: K-Means Clustering"""
    st.markdown('<div class="stage-card">', unsafe_allow_html=True)
    st.markdown("### 🎯 Stage 06: K-Means Clustering")

    dataset_key = st.session_state.selected_dataset
    dataset_info = DATASETS[dataset_key]

    # Load data
    df_clustered = load_data(dataset_info["clustered_path"])
    kmeans_config = load_config(dataset_info["kmeans_config"])

    if df_clustered is None or kmeans_config is None:
        render_alert("Data K-Means belum tersedia. Jalankan script 06_kmeans_modeling.py terlebih dahulu.", "warning")
        st.markdown('</div>', unsafe_allow_html=True)
        return

    # K-Means Parameters
    st.markdown("#### ⚙️ K-Means Parameters (dari Grid Search)")

    col1, col2, col3 = st.columns(3)

    with col1:
        render_metric_card("Optimal K", str(kmeans_config.get('optimal_k', 'N/A')), "blue")

    with col2:
        silhouette = kmeans_config.get('silhouette_score', 0)
        color = "green" if silhouette > 0.3 else "yellow"
        render_metric_card("Silhouette Score", f"{silhouette:.3f}", color)

    with col3:
        db_index = kmeans_config.get('davies_bouldin_index', 0)
        color = "green" if db_index < 1.5 else "yellow"
        render_metric_card("Davies-Bouldin", f"{db_index:.3f}", color)

    # Cluster distribution
    st.markdown("#### 📊 Cluster Distribution & Visualization")

    if 'cluster' in df_clustered.columns:
        cluster_counts = df_clustered['cluster'].value_counts().sort_index()

        col1, col2 = st.columns(2)

        with col1:
            # Bar chart
            fig_bar = px.bar(
                x=cluster_counts.index,
                y=cluster_counts.values,
                labels={'x': 'Cluster', 'y': 'Count'},
                title='Anomalies per Cluster',
                color=cluster_counts.values,
                color_continuous_scale='blues'
            )
            st.plotly_chart(fig_bar, use_container_width=True)

        with col2:
            # 2D scatter plot of clusters
            fig_scatter = create_cluster_scatter_2d(df_clustered, DATASETS[dataset_key]['label'])
            if fig_scatter:
                st.plotly_chart(fig_scatter, use_container_width=True)
            else:
                st.info("2D cluster visualization requires at least 2 features")

        # Temporal heatmap
        st.markdown("#### 🕐 Temporal Analysis")
        fig_heatmap = create_temporal_heatmap(df_clustered, DATASETS[dataset_key]['label'])
        if fig_heatmap:
            st.plotly_chart(fig_heatmap, use_container_width=True)

        # Cluster summary table
        st.markdown("#### 📋 Cluster Summary")

        cluster_summary = df_clustered.groupby('cluster').agg({
            'cluster': 'size',
            'user_id': 'nunique',
            'lof_score': 'mean'
        }).rename(columns={
            'cluster': 'Count',
            'user_id': 'Unique Users',
            'lof_score': 'Avg LOF Score'
        })

        cluster_summary['Percentage'] = (cluster_summary['Count'] / len(df_clustered) * 100).round(1)

        st.dataframe(cluster_summary, use_container_width=True)

        # Cluster characteristics
        st.markdown("#### 🔍 Cluster Characteristics")

        for cluster_id in sorted(df_clustered['cluster'].unique()):
            cluster_data = df_clustered[df_clustered['cluster'] == cluster_id]

            with st.expander(f"Cluster {cluster_id} ({len(cluster_data)} anomalies)"):
                col1, col2 = st.columns(2)

                with col1:
                    render_metric_card("Total Anomalies", format_number(len(cluster_data)), "blue")
                    render_metric_card("Unique Users", str(cluster_data['user_id'].nunique()), "green")

                with col2:
                    render_metric_card("Avg LOF Score", f"{cluster_data['lof_score'].mean():.2f}", "purple")

                    # Peak hour
                    if 'timestamp' in cluster_data.columns:
                        try:
                            timestamps = pd.to_datetime(cluster_data['timestamp'], errors='coerce')
                            if not timestamps.isna().all():
                                peak_hour = timestamps.dt.hour.mode().iloc[0] if not timestamps.dt.hour.mode().empty else 'N/A'
                                render_metric_card("Peak Hour", f"{peak_hour}:00", "yellow")
                        except:
                            pass

                # Top users in cluster
                st.markdown("**Top 5 Users in this Cluster:**")
                top_users = cluster_data['user_id'].value_counts().head(5)
                st.dataframe(pd.DataFrame({
                    'User ID': top_users.index,
                    'Anomaly Count': top_users.values
                }), use_container_width=True)

    # Navigation
    st.markdown("<br>", unsafe_allow_html=True)
    col1, col2 = st.columns([1, 1])

    with col1:
        if st.button("◀ Kembali ke Stage 05", key="back_to_05"):
            st.session_state.current_stage = 5
            st.rerun()

    with col2:
        if st.button("▶ Lanjut ke Stage 07: Results & Interpretation", type="primary"):
            st.session_state.current_stage = 7
            if 6 not in st.session_state.completed_stages:
                st.session_state.completed_stages.append(6)
            st.rerun()

    st.markdown('</div>', unsafe_allow_html=True)

def render_stage_07():
    """Stage 07: Results & Interpretation"""
    st.markdown('<div class="stage-card">', unsafe_allow_html=True)
    st.markdown("### 📈 Stage 07: Results & Interpretation")

    dataset_key = st.session_state.selected_dataset
    dataset_info = DATASETS[dataset_key]

    # Load all data
    df_clustered = load_data(dataset_info["clustered_path"])
    lof_config = load_config(dataset_info["lof_config"])
    kmeans_config = load_config(dataset_info["kmeans_config"])

    if df_clustered is None:
        render_alert("Data tidak tersedia. Pastikan semua pipeline sudah dijalankan.", "warning")
        st.markdown('</div>', unsafe_allow_html=True)
        return

    render_alert("Pipeline berhasil diselesaikan! Berikut adalah ringkasan hasil analisis.", "success")

    # Dataset comparison option
    st.markdown("#### 📊 Dataset Comparison")
    show_comparison = st.checkbox("Show comparison with other dataset", value=False)

    if show_comparison:
        other_dataset = 'staff' if dataset_key == 'tracker' else 'tracker'
        comparison_df = create_comparison_metrics(dataset_key, other_dataset)

        if not comparison_df.empty:
            st.dataframe(comparison_df, use_container_width=True)

            # Side-by-side visualization
            st.markdown("#### 📈 Side-by-Side Comparison")

            col1, col2 = st.columns(2)

            for idx, ds_key in enumerate([dataset_key, other_dataset]):
                ds_info = DATASETS[ds_key]
                df_comp = load_data(ds_info["clustered_path"])

                if df_comp is not None and 'cluster' in df_comp.columns:
                    cluster_counts = df_comp['cluster'].value_counts().sort_index()

                    fig = px.bar(
                        x=cluster_counts.index,
                        y=cluster_counts.values,
                        labels={'x': 'Cluster', 'y': 'Count'},
                        title=ds_info['label'],
                        color_discrete_sequence=['#3B82F6' if idx == 0 else '#10B981']
                    )

                    if idx == 0:
                        col1.plotly_chart(fig, use_container_width=True)
                    else:
                        col2.plotly_chart(fig, use_container_width=True)
        else:
            st.warning("Comparison data not available. Ensure both datasets have been processed.")

    st.markdown("---")

    # Overall summary
    st.markdown("#### 🎯 Overall Summary")

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        render_metric_card("Total Anomalies", format_number(len(df_clustered)), "red")

    with col2:
        if 'cluster' in df_clustered.columns:
            render_metric_card("Total Clusters", str(df_clustered['cluster'].nunique()), "blue")

    with col3:
        if lof_config:
            render_metric_card("LOF K-Value", str(lof_config.get('optimal_k', 'N/A')), "purple")

    with col4:
        if kmeans_config:
            render_metric_card("K-Means K-Value", str(kmeans_config.get('optimal_k', 'N/A')), "green")

    # Performance metrics
    st.markdown("#### 📊 Model Performance")

    col1, col2 = st.columns(2)

    with col1:
        if lof_config:
            anomaly_rate = lof_config.get('final_anomaly_percentage', 0)
            render_metric_card("Anomaly Rate", f"{anomaly_rate:.2f}%", "blue")

    with col2:
        if kmeans_config:
            silhouette = kmeans_config.get('silhouette_score', 0)
            render_metric_card("Silhouette Score", f"{silhouette:.3f}", "green")

    # Complete dataset view
    st.markdown("#### 📋 Complete Anomaly Dataset")

    # Filter options
    col1, col2 = st.columns(2)

    with col1:
        if 'cluster' in df_clustered.columns:
            selected_cluster = st.selectbox(
                "Filter by Cluster",
                options=['All'] + sorted(df_clustered['cluster'].unique().tolist()),
                key="cluster_filter"
            )

    with col2:
        sort_by = st.selectbox(
            "Sort by",
            options=['lof_score', 'cluster', 'user_id', 'timestamp'] if all(col in df_clustered.columns for col in ['lof_score', 'cluster', 'user_id', 'timestamp']) else df_clustered.columns.tolist(),
            key="sort_filter"
        )

    # Filter data
    display_df = df_clustered.copy()
    if selected_cluster != 'All' and 'cluster' in df_clustered.columns:
        display_df = display_df[display_df['cluster'] == selected_cluster]

    # Sort data
    if sort_by in display_df.columns:
        display_df = display_df.sort_values(by=sort_by, ascending=False)

    # Display
    st.dataframe(display_df, use_container_width=True, height=400)

    # Export options
    st.markdown("#### 📥 Export Results")

    col1, col2, col3 = st.columns(3)

    with col1:
        csv = df_clustered.to_csv(index=False).encode('utf-8')
        st.download_button(
            label="📥 Download CSV",
            data=csv,
            file_name=f"{dataset_key}_anomalies_results.csv",
            mime="text/csv"
        )

    with col2:
        json_data = df_clustered.to_json(orient='records', indent=2)
        st.download_button(
            label="📥 Download JSON",
            data=json_data,
            file_name=f"{dataset_key}_anomalies_results.json",
            mime="application/json"
        )

    with col3:
        # Summary report
        summary = {
            "dataset": dataset_key,
            "total_anomalies": len(df_clustered),
            "lof_config": lof_config,
            "kmeans_config": kmeans_config,
            "generated_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        summary_json = json.dumps(summary, indent=2)
        st.download_button(
            label="📥 Download Report",
            data=summary_json,
            file_name=f"{dataset_key}_summary_report.json",
            mime="application/json"
        )

    # Navigation
    st.markdown("<br>", unsafe_allow_html=True)
    col1, col2 = st.columns([1, 1])

    with col1:
        if st.button("◀ Kembali ke Stage 06", key="back_to_06"):
            st.session_state.current_stage = 6
            st.rerun()

    with col2:
        if st.button("🔄 Start Over", key="restart"):
            st.session_state.current_stage = 1
            st.session_state.completed_stages = []
            st.rerun()

    st.markdown('</div>', unsafe_allow_html=True)

# ============================================================================
# MAIN APP
# ============================================================================

def main():
    # Load custom CSS
    load_custom_css()

    # Initialize session state
    init_session_state()

    # Render header
    render_header()

    # Render progress stepper
    render_progress_stepper(
        current_stage=st.session_state.current_stage,
        completed_stages=st.session_state.completed_stages
    )

    # Display current dataset info in sidebar
    st.sidebar.markdown("### 📊 Current Dataset")
    dataset_info = DATASETS[st.session_state.selected_dataset]
    st.sidebar.info(f"**{dataset_info['label']}**\n\n{dataset_info['description']}")

    st.sidebar.markdown("---")
    st.sidebar.markdown("### 🎯 Progress")
    st.sidebar.markdown(f"**Current Stage:** {st.session_state.current_stage}/7")
    st.sidebar.markdown(f"**Completed:** {len(st.session_state.completed_stages)}/7")

    # Quick stats in sidebar
    st.sidebar.markdown("---")
    st.sidebar.markdown("### 📈 Quick Stats")

    try:
        dataset_key = st.session_state.selected_dataset
        ds_info = DATASETS[dataset_key]

        # Load final results
        df_final = load_data(ds_info["clustered_path"])
        lof_conf = load_config(ds_info["lof_config"])
        kmeans_conf = load_config(ds_info["kmeans_config"])

        if df_final is not None and lof_conf and kmeans_conf:
            st.sidebar.metric("Total Anomalies", format_number(len(df_final)))
            st.sidebar.metric("Clusters", df_final['cluster'].nunique() if 'cluster' in df_final.columns else 'N/A')
            st.sidebar.metric("Anomaly Rate", f"{lof_conf.get('final_anomaly_percentage', 0):.2f}%")
            st.sidebar.metric("Silhouette", f"{kmeans_conf.get('silhouette_score', 0):.3f}")
        else:
            st.sidebar.info("Run pipeline to see stats")
    except Exception as e:
        st.sidebar.info("Stats will appear after running pipeline")

    # Stage navigation in sidebar
    st.sidebar.markdown("---")
    st.sidebar.markdown("### 🚀 Quick Navigation")

    for i in range(1, 8):
        stage_names = ["Load", "Prep", "Feature", "Norm", "LOF", "K-Means", "Results"]
        if i in st.session_state.completed_stages:
            status = "✅"
        elif i == st.session_state.current_stage:
            status = "▶"
        else:
            status = "⭕"

        if st.sidebar.button(f"{status} Stage {i:02d}: {stage_names[i-1]}", key=f"nav_{i}"):
            st.session_state.current_stage = i
            st.rerun()

    # Render current stage
    stage_renderers = {
        1: render_stage_01,
        2: render_stage_02,
        3: render_stage_03,
        4: render_stage_04,
        5: render_stage_05,
        6: render_stage_06,
        7: render_stage_07
    }

    current_stage = st.session_state.current_stage
    if current_stage in stage_renderers:
        stage_renderers[current_stage]()

    # Footer
    st.markdown("---")
    st.markdown("""
    <div style="text-align: center; color: #6B7280; font-size: 0.875rem; padding: 1rem;">
        🔍 LOF + K-Means Anomaly Detection Pipeline | Built with Streamlit & Tailwind CSS
    </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()
