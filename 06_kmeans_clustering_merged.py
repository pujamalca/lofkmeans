import pandas as pd
import numpy as np
from sklearn.cluster import KMeans
from sklearn.metrics import silhouette_score
import json
import sys

# Set UTF-8 encoding for Windows console
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')

print("\n" + "="*80)
print("TAHAP 7: K-MEANS CLUSTERING - MERGED DATASET ANOMALIES")
print("="*80)

# Load anomalies data
print("\n[7.1] Memuat data anomali...")
merged_df = pd.read_csv('data/anomalies/merged_with_lof_scores.csv')
print(f"  Total data: {len(merged_df):,} baris")

# Filter only anomalies
anomalies_df = merged_df[merged_df['is_anomaly'] == 1].copy()
print(f"  Anomali terdeteksi: {len(anomalies_df):,} baris ({len(anomalies_df)/len(merged_df)*100:.2f}%)")

if len(anomalies_df) < 3:
    print("\n  [ERROR] Tidak cukup anomali untuk clustering (minimal 3 data)")
    print("  Silakan adjust contamination atau gunakan dataset lebih besar")
    exit(1)

# Show distribution by source
source_counts = anomalies_df['dataset_source'].value_counts()
print(f"\n  Distribusi anomali berdasarkan source:")
for source, count in source_counts.items():
    print(f"    {source}: {count} ({count/len(anomalies_df)*100:.2f}%)")

# Load feature info
with open('models/feature_info_merged.json', 'r') as f:
    feature_info = json.load(f)

feature_cols = feature_info['feature_columns']
print(f"\n[7.2] Fitur untuk clustering: {len(feature_cols)}")

# Extract features (already normalized)
X_anomalies = anomalies_df[feature_cols].values
print(f"  Matriks fitur anomali: {X_anomalies.shape}")

# ============================================================================
# DETERMINE OPTIMAL NUMBER OF CLUSTERS
# ============================================================================
print("\n" + "="*80)
print("[7.3] ELBOW METHOD & SILHOUETTE SCORE - Mencari jumlah cluster optimal")
print("="*80)

# Determine max clusters based on data size
max_clusters = min(10, len(anomalies_df) // 3)  # At least 3 data points per cluster
if max_clusters < 2:
    max_clusters = 2

k_range = range(2, max_clusters + 1)

inertias = []
silhouette_scores = []

print(f"\nTesting k from 2 to {max_clusters}...")
print(f"{'k':<5} {'Inertia':<15} {'Silhouette Score':<20}")
print("-" * 45)

for k in k_range:
    # Train K-Means
    kmeans = KMeans(n_clusters=k, random_state=42, n_init=10)
    cluster_labels = kmeans.fit_predict(X_anomalies)

    # Calculate metrics
    inertia = kmeans.inertia_
    sil_score = silhouette_score(X_anomalies, cluster_labels)

    inertias.append(inertia)
    silhouette_scores.append(sil_score)

    print(f"{k:<5} {inertia:<15.2f} {sil_score:<20.4f}")

# Find optimal k using silhouette score (higher is better)
optimal_k_silhouette = k_range[np.argmax(silhouette_scores)]
max_silhouette = max(silhouette_scores)

print("-" * 45)
print(f"\n✓ Optimal k berdasarkan Silhouette Score: {optimal_k_silhouette} (score: {max_silhouette:.4f})")

# Use silhouette-based optimal k
optimal_k = optimal_k_silhouette

# ============================================================================
# TRAIN FINAL K-MEANS MODEL
# ============================================================================
print("\n" + "="*80)
print(f"[7.4] Training K-Means dengan k={optimal_k}")
print("="*80)

kmeans_final = KMeans(n_clusters=optimal_k, random_state=42, n_init=10)
anomalies_df['cluster'] = kmeans_final.fit_predict(X_anomalies)

print(f"\n[7.5] Hasil clustering:")
print(f"  Total clusters: {optimal_k}")
print(f"  Inertia: {kmeans_final.inertia_:.2f}")

# Cluster distribution
print(f"\n  Distribusi per cluster:")
cluster_counts = anomalies_df['cluster'].value_counts().sort_index()
for cluster_id, count in cluster_counts.items():
    pct = (count / len(anomalies_df)) * 100
    print(f"    Cluster {cluster_id}: {count:>4} anomali ({pct:>5.1f}%)")

# ============================================================================
# ANALYZE EACH CLUSTER
# ============================================================================
print("\n" + "="*80)
print("[7.6] ANALISIS KARAKTERISTIK SETIAP CLUSTER")
print("="*80)

for cluster_id in range(optimal_k):
    cluster_data = anomalies_df[anomalies_df['cluster'] == cluster_id]

    print(f"\n{'='*80}")
    print(f"CLUSTER {cluster_id} - {len(cluster_data)} anomali ({len(cluster_data)/len(anomalies_df)*100:.1f}%)")
    print(f"{'='*80}")

    # Source distribution
    print(f"\n  Distribusi Source:")
    cluster_sources = cluster_data['dataset_source'].value_counts()
    for source, count in cluster_sources.items():
        print(f"    {source}: {count} ({count/len(cluster_data)*100:.1f}%)")

    # User distribution (top 5)
    print(f"\n  Top 5 User:")
    user_counts = cluster_data['user_id'].value_counts().head(5)
    for user_id, count in user_counts.items():
        print(f"    User {user_id}: {count} anomali")

    # LOF score statistics
    print(f"\n  LOF Score Statistics:")
    print(f"    Min  : {cluster_data['lof_score'].min():.2e}")
    print(f"    Max  : {cluster_data['lof_score'].max():.2e}")
    print(f"    Mean : {cluster_data['lof_score'].mean():.2e}")
    print(f"    Median: {cluster_data['lof_score'].median():.2e}")

    # Temporal patterns
    print(f"\n  Pola Temporal:")
    print(f"    Hour - Mean: {cluster_data['hour'].mean():.1f}, Std: {cluster_data['hour'].std():.1f}")
    print(f"    Weekend: {cluster_data['IsWeekend'].sum()} ({cluster_data['IsWeekend'].mean()*100:.1f}%)")
    print(f"    Outside Work Hours: {cluster_data['IsOutsideWorkHours'].sum()} ({cluster_data['IsOutsideWorkHours'].mean()*100:.1f}%)")

    # Behavioral patterns
    print(f"\n  Pola Perilaku:")
    print(f"    Frekuensi Aktivitas - Mean: {cluster_data['frekuensi_aktivitas_per_user'].mean():.2f}")
    print(f"    Pola Waktu Akses - Mean: {cluster_data['pola_waktu_akses'].mean():.2f}")

    # Sample data
    print(f"\n  Contoh 3 Anomali Teratas (LOF Score):")
    top_samples = cluster_data.nlargest(3, 'lof_score')
    for idx, row in top_samples.iterrows():
        print(f"    User {row['user_id']} | {row['timestamp'][:19]} | LOF: {row['lof_score']:.2e}")

# ============================================================================
# CLUSTER INTERPRETATIONS
# ============================================================================
print("\n" + "="*80)
print("[7.7] INTERPRETASI & LABEL CLUSTER")
print("="*80)

cluster_interpretations = {}

for cluster_id in range(optimal_k):
    cluster_data = anomalies_df[anomalies_df['cluster'] == cluster_id]

    # Analyze characteristics to give meaningful label
    avg_hour = cluster_data['hour'].mean()
    weekend_pct = cluster_data['IsWeekend'].mean() * 100
    outside_hours_pct = cluster_data['IsOutsideWorkHours'].mean() * 100
    avg_freq = cluster_data['frekuensi_aktivitas_per_user'].mean()
    avg_lof = cluster_data['lof_score'].mean()

    # Determine cluster label based on characteristics
    label = f"Cluster {cluster_id}"
    description = []

    if outside_hours_pct > 50:
        description.append("Aktivitas di Luar Jam Kerja")
    if weekend_pct > 50:
        description.append("Aktivitas Weekend")
    if avg_freq > anomalies_df['frekuensi_aktivitas_per_user'].median():
        description.append("Frekuensi Tinggi")
    else:
        description.append("Frekuensi Rendah")
    if avg_lof > anomalies_df['lof_score'].median():
        description.append("Anomali Kuat")

    if not description:
        description.append("Anomali Umum")

    label_desc = " - ".join(description)

    cluster_interpretations[cluster_id] = {
        'label': label_desc,
        'count': int(len(cluster_data)),
        'percentage': float(len(cluster_data) / len(anomalies_df) * 100),
        'avg_hour': float(avg_hour),
        'weekend_pct': float(weekend_pct),
        'outside_hours_pct': float(outside_hours_pct),
        'avg_frequency': float(avg_freq),
        'avg_lof_score': float(avg_lof),
        'top_users': cluster_data['user_id'].value_counts().head(3).to_dict()
    }

    print(f"\nCluster {cluster_id}: {label_desc}")
    print(f"  Jumlah: {len(cluster_data)} anomali ({len(cluster_data)/len(anomalies_df)*100:.1f}%)")
    print(f"  Karakteristik:")
    print(f"    - Rata-rata jam: {avg_hour:.1f}")
    print(f"    - Weekend: {weekend_pct:.1f}%")
    print(f"    - Di luar jam kerja: {outside_hours_pct:.1f}%")
    print(f"    - Frekuensi aktivitas: {avg_freq:.1f}")
    print(f"    - LOF score rata-rata: {avg_lof:.2e}")

# ============================================================================
# SAVE RESULTS
# ============================================================================
print("\n" + "="*80)
print("[7.8] Menyimpan hasil clustering")
print("="*80)

# Add cluster labels to full dataset
merged_df['cluster'] = -1  # Default: not anomaly
merged_df.loc[merged_df['is_anomaly'] == 1, 'cluster'] = anomalies_df['cluster'].values

# Save clustered data
output_path = 'data/anomalies/merged_anomalies_clustered.csv'
merged_df.to_csv(output_path, index=False)
print(f"✓ Data dengan cluster labels tersimpan: {output_path}")

# Save K-Means configuration
kmeans_config = {
    'optimal_k': optimal_k,
    'method': 'silhouette_score',
    'n_anomalies': int(len(anomalies_df)),
    'feature_columns': feature_cols,
    'inertia': float(kmeans_final.inertia_),
    'silhouette_score': float(max_silhouette),
    'cluster_centers': kmeans_final.cluster_centers_.tolist(),
    'elbow_analysis': {
        'k_range': list(k_range),
        'inertias': [float(x) for x in inertias],
        'silhouette_scores': [float(x) for x in silhouette_scores]
    },
    'cluster_distribution': {int(k): int(v) for k, v in cluster_counts.items()},
    'cluster_interpretations': cluster_interpretations
}

with open('models/kmeans_config_merged.json', 'w') as f:
    json.dump(kmeans_config, f, indent=2)
print(f"✓ Konfigurasi K-Means tersimpan: models/kmeans_config_merged.json")

# ============================================================================
# SUMMARY
# ============================================================================
print("\n" + "="*80)
print("TAHAP 7 SELESAI - RINGKASAN K-MEANS CLUSTERING")
print("="*80)

print(f"\nModel: K-Means Clustering")
print(f"Optimal k: {optimal_k} (berdasarkan Silhouette Score)")
print(f"Silhouette Score: {max_silhouette:.4f}")
print(f"Inertia: {kmeans_final.inertia_:.2f}")

print(f"\nData:")
print(f"  Total anomali: {len(anomalies_df):,}")
print(f"  Jumlah cluster: {optimal_k}")

print(f"\nDistribusi cluster:")
for cluster_id, count in cluster_counts.items():
    label = cluster_interpretations[cluster_id]['label']
    pct = count / len(anomalies_df) * 100
    print(f"  Cluster {cluster_id} ({label}): {count} ({pct:.1f}%)")

print(f"\nFile output:")
print(f"  - {output_path}")
print(f"  - models/kmeans_config_merged.json")

print("\n" + "="*80)
print("Pipeline LOF + K-Means selesai!")
print("Anomali sudah terdeteksi dan dikategorikan.")
print("="*80 + "\n")
