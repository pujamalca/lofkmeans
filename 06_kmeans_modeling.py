import json
import sys

import joblib
import pandas as pd
from sklearn.cluster import KMeans
from sklearn.metrics import davies_bouldin_score, silhouette_score


if sys.platform == "win32":  # ensure UTF-8 output on Windows
    sys.stdout.reconfigure(encoding="utf-8")


WORK_START = 8
WORK_END = 19


def attach_timestamp(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    if "date" in df.columns and df["date"].notnull().any():
        ts_series = df["date"].astype(str).str.strip() + " " + df["timestamp"].astype(str).str.strip()
    else:
        ts_series = df["timestamp"].astype(str).str.strip()

    df["timestamp_dt"] = pd.to_datetime(ts_series, errors="coerce")
    df["hour_actual"] = df["timestamp_dt"].dt.hour.fillna(0).astype(int)
    df["day_of_week_actual"] = df["timestamp_dt"].dt.dayofweek.fillna(0).astype(int)
    df["day_of_month_actual"] = df["timestamp_dt"].dt.day.fillna(1).astype(int)
    df["month_actual"] = df["timestamp_dt"].dt.month.fillna(1).astype(int)

    df["is_outside_work_hours"] = (
        (df["hour_actual"] < WORK_START) | (df["hour_actual"] >= WORK_END)
    ).astype(int)
    df["is_weekend_flag"] = df["day_of_week_actual"].isin([5, 6]).astype(int)
    df["night_shift_flag"] = ((df["hour_actual"] >= 21) | (df["hour_actual"] < 6)).astype(int)

    return df


def build_tracker_features(df: pd.DataFrame) -> tuple[pd.DataFrame, list[str]]:
    df = df.copy()
    df = attach_timestamp(df)

    df["query_text"] = df["query_info"].fillna("")
    df["query_length"] = df["query_text"].str.len()
    length_std = df["query_length"].std()
    if length_std > 0:
        df["query_length_normalized"] = (
            df["query_length"] - df["query_length"].mean()
        ) / length_std
    else:
        df["query_length_normalized"] = 0

    df["ip_address"] = df["query_text"].str.extract(r"(\d{1,3}(?:\.\d{1,3}){3})", expand=False).fillna("0.0.0.0")
    df["ip_last_octet"] = df["ip_address"].apply(lambda ip: int(ip.split(".")[-1]) if pd.notna(ip) and "." in ip else 0)

    daily_counts = df.groupby(["user_id", df["timestamp_dt"].dt.date]).size()
    daily_avg = daily_counts.groupby(level=0).mean()
    df["user_avg_daily_activity"] = df["user_id"].map(daily_avg).fillna(0)

    diversity = df.groupby("user_id")["query_type"].nunique()
    df["user_query_diversity"] = df["user_id"].map(diversity).fillna(0)

    delete_counts = df[df["query_type"] == "DELETE"].groupby("user_id").size()
    df["delete_operation_count"] = df["user_id"].map(delete_counts).fillna(0)

    df["modification_ratio"] = df["rasio_operasi_modifikasi"].fillna(0)

    for op in ["op_DELETE", "op_INSERT", "op_UPDATE"]:
        if op in df.columns:
            df[op] = df[op].astype(int)
        else:
            df[op] = 0

    feature_cols = [
        "hour_actual",
        "day_of_week_actual",
        "day_of_month_actual",
        "month_actual",
        "is_outside_work_hours",
        "is_weekend_flag",
        "night_shift_flag",
        "op_DELETE",
        "op_INSERT",
        "op_UPDATE",
        "ip_last_octet",
        "user_avg_daily_activity",
        "user_query_diversity",
        "modification_ratio",
        "delete_operation_count",
        "query_length_normalized",
        "lof_score",
    ]

    # compute IP hits per hour for anomalies later on
    df["hour_bucket"] = df["timestamp_dt"].dt.floor("h")

    return df, feature_cols


def build_staff_features(df: pd.DataFrame) -> tuple[pd.DataFrame, list[str]]:
    df = df.copy()
    df = attach_timestamp(df)

    df["date_str"] = df["date"].astype(str).str.strip()
    daily_counts = df.groupby(["user_id", df["date_str"]]).size()
    daily_avg = daily_counts.groupby(level=0).mean()
    df["user_avg_daily_activity"] = df["user_id"].map(daily_avg).fillna(0)

    df["login_day_diversity"] = df.groupby("user_id")["date_str"].transform("nunique")

    feature_cols = [
        "hour_actual",
        "day_of_week_actual",
        "day_of_month_actual",
        "month_actual",
        "is_outside_work_hours",
        "is_weekend_flag",
        "night_shift_flag",
        "IsEarlyLogin",
        "IsLateLogin",
        "IsAfterWorkHours",
        "IsWeekend",
        "frekuensi_login_per_user",
        "pola_waktu_login",
        "rasio_login_weekend",
        "user_avg_daily_activity",
        "login_day_diversity",
        "lof_score",
    ]

    # ensure metrics exist
    for col in feature_cols:
        if col not in df.columns:
            df[col] = 0

    df["hour_bucket"] = df["timestamp_dt"].dt.floor("h")

    return df, feature_cols


def run_clustering(
    name: str,
    df: pd.DataFrame,
    feature_cols: list[str],
    config: dict,
) -> None:
    anomalies_df = df[df["is_anomaly"] == 1].copy()
    print("\n" + "=" * 60)
    print(f"DATASET: {name.upper()} (Anomalies: {len(anomalies_df)})")
    print("=" * 60)

    if len(anomalies_df) < 2:
        print("  Tidak cukup anomali untuk membangun cluster.")
        return

    # IP hits per hour (only for tracker, staff will ignore gracefully)
    ip_hour_counts = (
        anomalies_df.groupby(["ip_address", "hour_bucket"]).size().to_dict()
        if "ip_address" in anomalies_df.columns
        else {}
    )

    if "ip_hits_per_hour" not in anomalies_df.columns:
        anomalies_df["ip_hits_per_hour"] = anomalies_df.apply(
            lambda row: ip_hour_counts.get((row.get("ip_address", ""), row["hour_bucket"]), 0),
            axis=1,
        )

    feature_cols_extended = feature_cols.copy()
    if "ip_hits_per_hour" in anomalies_df.columns and "ip_hits_per_hour" not in feature_cols_extended:
        feature_cols_extended.append("ip_hits_per_hour")

    X = (
        anomalies_df[feature_cols_extended]
        .fillna(0)
        .astype(float)
        .to_numpy()
    )

    max_k = min(8, len(anomalies_df) - 1)
    if max_k < 2:
        print("  Data anomali tidak memungkinkan untuk grid search k >= 2.")
        return

    print("\n[7.1] GRID SEARCH UNTUK k OPTIMAL:")
    print(f"  Menguji nilai k: {list(range(2, max_k + 1))}")

    cluster_results = []
    for k in range(2, max_k + 1):
        kmeans = KMeans(n_clusters=k, init="k-means++", n_init=10, random_state=42)
        labels = kmeans.fit_predict(X)

        inertia = float(kmeans.inertia_)
        silhouette = float(silhouette_score(X, labels))
        davies = float(davies_bouldin_score(X, labels))

        print(f"\n  k={k}: Inertia={inertia:.0f}, Silhouette={silhouette:.3f}, Davies-Bouldin={davies:.3f}")

        cluster_results.append(
            {"k": k, "inertia": inertia, "silhouette": silhouette, "davies_bouldin": davies}
        )

    results_df = pd.DataFrame(cluster_results)
    print("\n[7.2] HASIL GRID SEARCH:")
    print(results_df.to_string(index=False))

    optimal_idx = results_df["silhouette"].idxmax()
    optimal_k = int(results_df.loc[optimal_idx, "k"])
    optimal_silhouette = results_df.loc[optimal_idx, "silhouette"]
    optimal_db = results_df.loc[optimal_idx, "davies_bouldin"]

    print(f"\nOptimal k selected: {optimal_k}")
    print(f"  Silhouette terbaik: {optimal_silhouette:.3f}")
    print(f"  Davies-Bouldin: {optimal_db:.3f}")

    print(f"\n[7.3] FIT FINAL K-MEANS MODEL dengan k={optimal_k}:")
    final_kmeans = KMeans(
        n_clusters=optimal_k,
        init="k-means++",
        n_init=10,
        random_state=42,
        verbose=0,
    )
    cluster_labels = final_kmeans.fit_predict(X)
    anomalies_df["cluster"] = cluster_labels

    final_silhouette = float(silhouette_score(X, cluster_labels))
    final_db = float(davies_bouldin_score(X, cluster_labels))

    print("\n[7.4] CLUSTER DISTRIBUTION:")
    for cluster_id in range(optimal_k):
        count = int((cluster_labels == cluster_id).sum())
        pct = count / len(cluster_labels) * 100
        print(f"  Cluster {cluster_id}: {count} anomalies ({pct:.1f}%)")

    print("\n[7.5] KARAKTERISTIK SETIAP CLUSTER:")
    for cluster_id in range(optimal_k):
        cluster_data = anomalies_df[anomalies_df["cluster"] == cluster_id]
        if cluster_data.empty:
            print(f"\n  Cluster {cluster_id}: kosong")
            continue

        dominant_field = config.get("dominant_field")
        dominant_value = (
            cluster_data[dominant_field].mode().iloc[0]
            if dominant_field and dominant_field in cluster_data.columns and not cluster_data[dominant_field].empty
            else "N/A"
        )

        peak_hour_series = cluster_data["timestamp_dt"].dt.hour
        peak_hour = int(peak_hour_series.mode().iloc[0]) if not peak_hour_series.empty else "N/A"
        outside_pct = cluster_data["is_outside_work_hours"].mean() * 100

        print(f"\n  CLUSTER {cluster_id} ({len(cluster_data)} anomalies):")
        print(f"    Dominant {dominant_field or 'label'}: {dominant_value}")
        print(f"    Peak hour: {peak_hour}")
        print(f"    Outside work hours rate: {outside_pct:.1f}%")

        for metric_col, label in config.get("metric_columns", []):
            if metric_col in cluster_data.columns:
                value = cluster_data[metric_col].mean()
                print(f"    {label}: {value:.2f}")

        top_users = cluster_data["user_id"].value_counts().head(3).to_dict()
        print(f"    Top user_id: {top_users}")
        name_column = config.get("name_column")
        if name_column and name_column in cluster_data.columns:
            top_names = cluster_data[name_column].value_counts().head(3).to_dict()
            print(f"    Top {name_column}: {top_names}")

    anomalies_df.to_csv(config["clustered_csv"], index=False)
    joblib.dump(final_kmeans, config["model_path"])

    cluster_config = {
        "optimal_k": optimal_k,
        "silhouette_score": final_silhouette,
        "davies_bouldin_index": final_db,
        "inertia": float(final_kmeans.inertia_),
        "feature_names": feature_cols_extended,
        "model_type": "KMeans",
    }

    with open(config["config_path"], "w", encoding="utf-8") as cfg:
        json.dump(cluster_config, cfg, indent=2)

    print(f"\nSaved clustered data to {config['clustered_csv']}")
    print(f"Saved K-Means model to {config['model_path']}")
    print(f"Saved config to {config['config_path']}")


def main() -> None:
    datasets = [
        {
            "name": "tracker",
            "input": "data/anomalies/tracker_with_lof_scores.csv",
            "model_path": "models/kmeans_model_tracker.pkl",
            "config_path": "models/kmeans_config_tracker.json",
            "clustered_csv": "data/anomalies/tracker_anomalies_clustered.csv",
            "builder": build_tracker_features,
            "dominant_field": "query_type",
            "metric_columns": [
                ("modification_ratio", "Avg modification ratio"),
                ("lof_score", "Avg LOF score"),
            ],
        },
        {
            "name": "staff",
            "input": "data/anomalies/staff_with_lof_scores.csv",
            "model_path": "models/kmeans_model_staff.pkl",
            "config_path": "models/kmeans_config_staff.json",
            "clustered_csv": "data/anomalies/staff_anomalies_clustered.csv",
            "builder": build_staff_features,
            "dominant_field": "name",
            "name_column": "name",
            "metric_columns": [
                ("IsAfterWorkHours", "Avg after-work flag"),
                ("frekuensi_login_per_user", "Avg login frequency"),
            ],
        },
    ]

    for dataset in datasets:
        df = pd.read_csv(dataset["input"])
        enriched_df, feature_cols = dataset["builder"](df)

        config = {
            "model_path": dataset["model_path"],
            "config_path": dataset["config_path"],
            "clustered_csv": dataset["clustered_csv"],
            "dominant_field": dataset.get("dominant_field"),
            "metric_columns": dataset.get("metric_columns", []),
            "name_column": dataset.get("name_column"),
        }

        run_clustering(dataset["name"], enriched_df, feature_cols, config)


if __name__ == "__main__":
    main()
