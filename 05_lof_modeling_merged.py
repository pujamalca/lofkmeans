import pandas as pd
import numpy as np
from sklearn.neighbors import LocalOutlierFactor
import joblib
import json
import sys

# Set UTF-8 encoding for Windows console
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')

print("\n" + "="*80)
print("TAHAP 5-6: LOF ANOMALY DETECTION - MERGED DATASET")
print("="*80)

# Load normalized merged data
print("\n[5.1] Memuat data normalized...")
merged_df = pd.read_csv('data/normalized/merged_normalized.csv')
print(f"  Data dimuat: {len(merged_df)} baris")

# Show distribution by source
source_counts = merged_df['dataset_source'].value_counts()
print(f"\n  Distribusi berdasarkan source:")
for source, count in source_counts.items():
    print(f"    {source}: {count} ({count/len(merged_df)*100:.2f}%)")

# Load feature info
with open('models/feature_info_merged.json', 'r') as f:
    feature_info = json.load(f)

feature_cols = feature_info['feature_columns']
print(f"\n[5.2] Fitur untuk modeling: {len(feature_cols)}")
for i, col in enumerate(feature_cols, 1):
    print(f"  {i:>2}. {col}")

# Extract features
X = merged_df[feature_cols].values
print(f"\n  Matriks fitur: {X.shape}")

# ============================================================================
# GRID SEARCH FOR OPTIMAL K
# ============================================================================
print("\n" + "="*80)
print("[5.3] GRID SEARCH - Mencari k optimal")
print("="*80)

contamination = 0.05  # 5% expected anomalies
k_values = [5, 10, 15, 20, 25, 30]

grid_results = []

print(f"\nTarget contamination: {contamination*100}%")
print(f"Testing k values: {k_values}\n")
print(f"{'k':<5} {'Anomalies':<12} {'Percentage':<12} {'Diff from Target':<18}")
print("-" * 50)

best_k = None
best_diff = float('inf')

for k in k_values:
    # Train LOF
    lof = LocalOutlierFactor(n_neighbors=k, contamination=contamination)
    y_pred = lof.fit_predict(X)

    # Calculate stats
    anomalies = (y_pred == -1).sum()
    percentage = (anomalies / len(X)) * 100
    diff = abs(percentage - (contamination * 100))

    # Store results
    grid_results.append({
        'k': k,
        'anomalies_detected': int(anomalies),
        'anomaly_percentage': float(percentage),
        'lof_score_min': float(lof.negative_outlier_factor_.min()),
        'lof_score_max': float(lof.negative_outlier_factor_.max()),
        'lof_score_mean': float(lof.negative_outlier_factor_.mean())
    })

    # Track best k
    if diff < best_diff:
        best_diff = diff
        best_k = k

    print(f"{k:<5} {anomalies:<12} {percentage:<12.2f} {diff:<18.2f}")

print("-" * 50)
print(f"\n✓ Optimal k dipilih: {best_k} (paling dekat dengan target {contamination*100}%)")

# ============================================================================
# TRAIN FINAL LOF MODEL
# ============================================================================
print("\n" + "="*80)
print(f"[5.4] Training LOF dengan k={best_k}")
print("="*80)

lof_model = LocalOutlierFactor(n_neighbors=best_k, contamination=contamination)
y_pred = lof_model.fit_predict(X)

# Get LOF scores (negative outlier factor)
lof_scores = -lof_model.negative_outlier_factor_  # Convert to positive

# Add LOF scores to dataframe
merged_df['lof_score'] = lof_scores
merged_df['is_anomaly'] = (y_pred == -1).astype(int)

# Statistics
total_anomalies = merged_df['is_anomaly'].sum()
anomaly_pct = (total_anomalies / len(merged_df)) * 100

print(f"\n[5.5] Hasil deteksi anomali:")
print(f"  Total records: {len(merged_df):,}")
print(f"  Anomalies detected: {total_anomalies} ({anomaly_pct:.2f}%)")
print(f"  Normal data: {len(merged_df) - total_anomalies} ({100-anomaly_pct:.2f}%)")

# Distribution by source
print(f"\n[5.6] Distribusi anomali berdasarkan source:")
for source in merged_df['dataset_source'].unique():
    source_df = merged_df[merged_df['dataset_source'] == source]
    source_anomalies = source_df['is_anomaly'].sum()
    source_pct = (source_anomalies / len(source_df)) * 100
    print(f"  {source}: {source_anomalies}/{len(source_df)} ({source_pct:.2f}%)")

# Top anomalies
print(f"\n[5.7] Top 10 anomali (berdasarkan LOF score):")
top_anomalies = merged_df[merged_df['is_anomaly']==1].nlargest(10, 'lof_score')
print(f"{'User':<8} {'Source':<10} {'LOF Score':<15} {'Timestamp':<20}")
print("-" * 60)
for idx, row in top_anomalies.iterrows():
    print(f"{row['user_id']:<8} {row['dataset_source']:<10} {row['lof_score']:<15.2e} {row['timestamp'][:19]}")

# ============================================================================
# SAVE RESULTS
# ============================================================================
print("\n" + "="*80)
print("[5.8] Menyimpan hasil")
print("="*80)

# Save anomalies with LOF scores
output_path = 'data/anomalies/merged_with_lof_scores.csv'
merged_df.to_csv(output_path, index=False)
print(f"✓ Data dengan LOF scores tersimpan: {output_path}")

# Save LOF model
joblib.dump(lof_model, 'models/lof_model_merged.pkl')
print(f"✓ Model LOF tersimpan: models/lof_model_merged.pkl")

# Save configuration
config = {
    'optimal_k': best_k,
    'contamination': contamination,
    'n_features': len(feature_cols),
    'feature_names': feature_cols,
    'model_type': 'LocalOutlierFactor',
    'grid_search_results': grid_results,
    'final_anomalies_count': int(total_anomalies),
    'final_anomaly_percentage': float(anomaly_pct),
    'source_distribution': {
        source: {
            'total': int(len(merged_df[merged_df['dataset_source']==source])),
            'anomalies': int(merged_df[merged_df['dataset_source']==source]['is_anomaly'].sum())
        }
        for source in merged_df['dataset_source'].unique()
    }
}

with open('models/lof_config_merged.json', 'w') as f:
    json.dump(config, f, indent=2)
print(f"✓ Konfigurasi tersimpan: models/lof_config_merged.json")

# ============================================================================
# SUMMARY
# ============================================================================
print("\n" + "="*80)
print("TAHAP 5-6 SELESAI - RINGKASAN LOF ANOMALY DETECTION")
print("="*80)

print(f"\nModel: Local Outlier Factor")
print(f"Optimal k: {best_k}")
print(f"Contamination: {contamination*100}%")
print(f"Total fitur: {len(feature_cols)}")

print(f"\nHasil deteksi:")
print(f"  Total records: {len(merged_df):,}")
print(f"  Anomalies: {total_anomalies} ({anomaly_pct:.2f}%)")
print(f"  Normal: {len(merged_df) - total_anomalies} ({100-anomaly_pct:.2f}%)")

print(f"\nPer source:")
for source in merged_df['dataset_source'].unique():
    source_df = merged_df[merged_df['dataset_source'] == source]
    source_anomalies = source_df['is_anomaly'].sum()
    source_pct = (source_anomalies / len(source_df)) * 100
    print(f"  {source}: {source_anomalies}/{len(source_df)} ({source_pct:.2f}%)")

print(f"\nFile output:")
print(f"  - {output_path}")
print(f"  - models/lof_model_merged.pkl")
print(f"  - models/lof_config_merged.json")

print("\n" + "="*80)
