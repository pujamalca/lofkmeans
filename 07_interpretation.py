import json
import sys
from pathlib import Path

import pandas as pd


def ensure_utf8_console() -> None:
    if sys.platform == "win32":
        sys.stdout.reconfigure(encoding="utf-8")


def summarize_clusters(df: pd.DataFrame, config: dict) -> dict:
    df["timestamp_dt"] = pd.to_datetime(df["timestamp"], errors="coerce")
    total = len(df)
    summaries = []

    for cluster_id in sorted(df["cluster"].unique()):
        cluster_data = df[df["cluster"] == cluster_id]
        if cluster_data.empty:
            continue

        peak_hours = cluster_data["timestamp_dt"].dt.hour
        peak_hour = int(peak_hours.mode().iloc[0]) if not peak_hours.empty else None

        dominant_field = config.get("dominant_field")
        dominant_value = (
            cluster_data[dominant_field].mode().iloc[0]
            if dominant_field and dominant_field in cluster_data.columns
            else "N/A"
        )

        metric_values = {}
        for metric in config.get("metric_columns", []):
            if metric in cluster_data.columns:
                metric_values[metric] = float(cluster_data[metric].mean())

        summaries.append(
            {
                "cluster_id": int(cluster_id),
                "count": int(len(cluster_data)),
                "percentage": round(len(cluster_data) / total * 100, 1) if total else 0.0,
                "peak_hour": peak_hour,
                "dominant_value": dominant_value,
                "metric_means": metric_values,
                "top_users": cluster_data["user_id"].value_counts().head(3).to_dict(),
            }
        )

    return {"total_anomalies": total, "clusters": summaries}


def main() -> None:
    ensure_utf8_console()
    print("\n" + "=" * 60)
    print("TAHAP 10: INTERPRETASI CLUSTER & ACTIONABLE INSIGHTS")
    print("=" * 60)

    datasets = [
        {
            "name": "tracker",
            "path": Path("data/anomalies/tracker_anomalies_clustered.csv"),
            "dominant_field": "query_type",
            "metric_columns": ["lof_score", "modification_ratio"],
        },
        {
            "name": "staff",
            "path": Path("data/anomalies/staff_anomalies_clustered.csv"),
            "dominant_field": "name",
            "metric_columns": ["IsAfterWorkHours", "frekuensi_login_per_user"],
        },
    ]

    combined_report = {"generated_at": pd.Timestamp.now().isoformat(), "datasets": {}}

    for dataset in datasets:
        if not dataset["path"].exists():
            print(f"File not found: {dataset['path']} (skipping {dataset['name']}).")
            continue

        df = pd.read_csv(dataset["path"])
        summary = summarize_clusters(df, dataset)
        combined_report["datasets"][dataset["name"]] = summary

        print(f"\nDataset: {dataset['name'].upper()} (Total anomalies: {summary['total_anomalies']})")
        print("-" * 60)
        for cluster in summary["clusters"]:
            print(
                f"Cluster {cluster['cluster_id']}: "
                f"{cluster['count']} anomalies ({cluster['percentage']}%) | "
                f"Peak hour {cluster['peak_hour']} | "
                f"Dominant {dataset.get('dominant_field', 'value')}: {cluster['dominant_value']}"
            )
            for metric, mean_value in cluster["metric_means"].items():
                print(f"  Avg {metric}: {mean_value:.2f}")
            print(f"  Top users: {cluster['top_users']}")

    reports_dir = Path("data/reports")
    reports_dir.mkdir(parents=True, exist_ok=True)
    report_path = reports_dir / "interpretation_report.json"
    with report_path.open("w", encoding="utf-8") as report_file:
        json.dump(combined_report, report_file, indent=2)

    print("\nInterpretation report written to:", report_path)


if __name__ == "__main__":
    main()
