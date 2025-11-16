import pandas as pd
import numpy as np
from sklearn.neighbors import LocalOutlierFactor
import joblib
import json
import sys

# Set UTF-8 encoding for Windows console
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')

print("\n" + "="*60)
print("TAHAP 5-6: LOF MODELING & PARAMETER TUNING")
print("="*60)

# ========================================================
# PART 1: LOF MODELING - TRACKER (LOG AKTIVITAS)
# ========================================================
print("\n" + "="*60)
print("PART 1: LOF MODELING - TRACKER (LOG AKTIVITAS)")
print("="*60)

# Load data normalized
tracker_df = pd.read_csv('data/normalized/tracker_normalized.csv')
print(f"\n[5.1.A] Data tracker dimuat: {len(tracker_df)} baris")

# Load feature info
with open('models/feature_info_tracker.json', 'r') as f:
    feature_info_tracker = json.load(f)

feature_cols_tracker = feature_info_tracker['feature_columns']
print(f"  Fitur untuk modeling: {len(feature_cols_tracker)} kolom")

X_tracker = tracker_df[feature_cols_tracker].values
print(f"  Matriks fitur: {X_tracker.shape}")

# Grid Search untuk k optimal
print(f"\n[5.2.A] GRID SEARCH UNTUK k OPTIMAL:")
print(f"  Menguji nilai k: {5, 10, 15, 20, 25, 30}")

k_values = [5, 10, 15, 20, 25, 30]
grid_results_tracker = []

for k in k_values:
    print(f"\n  Testing k={k}...")

    lof = LocalOutlierFactor(n_neighbors=k, contamination=0.05)
    predictions = lof.fit_predict(X_tracker)
    scores = lof.negative_outlier_factor_

    num_anomalies = (predictions == -1).sum()

    print(f"    Anomali terdeteksi: {num_anomalies} ({num_anomalies/len(X_tracker)*100:.1f}%)")
    print(f"    LOF score range: [{scores.min():.2f}, {scores.max():.2f}]")

    grid_results_tracker.append({
        'k': k,
        'anomalies_detected': int(num_anomalies),
        'anomaly_percentage': float(num_anomalies/len(X_tracker)*100),
        'lof_score_min': float(scores.min()),
        'lof_score_max': float(scores.max()),
        'lof_score_mean': float(scores.mean())
    })

# Pilih k optimal
print(f"\n[5.3.A] HASIL GRID SEARCH:")
results_df_tracker = pd.DataFrame(grid_results_tracker)
print(results_df_tracker.to_string(index=False))

# Pilih k terdekat dengan target 5%
target_pct = 5.0
results_df_tracker['distance_from_target'] = abs(results_df_tracker['anomaly_percentage'] - target_pct)
optimal_idx_tracker = results_df_tracker['distance_from_target'].idxmin()
optimal_k_tracker = int(results_df_tracker.loc[optimal_idx_tracker, 'k'])

print(f"\n✓ k optimal dipilih: {optimal_k_tracker}")
print(f"  Alasan: Terdekat dengan target 5% kontaminasi")
print(f"  Tingkat anomali: {results_df_tracker.loc[optimal_idx_tracker, 'anomaly_percentage']:.2f}%")

# Fit final model
print(f"\n[5.4.A] FIT FINAL MODEL dengan k={optimal_k_tracker}:")

lof_model_tracker = LocalOutlierFactor(n_neighbors=optimal_k_tracker, contamination=0.05)
predictions_tracker = lof_model_tracker.fit_predict(X_tracker)
lof_scores_tracker = lof_model_tracker.negative_outlier_factor_

# Simpan hasil ke dataframe
tracker_df['lof_score'] = -lof_scores_tracker  # Flip sign: nilai tinggi = lebih anomali
tracker_df['is_anomaly'] = (predictions_tracker == -1).astype(int)

print(f"  Data normal: {(predictions_tracker == 1).sum()}")
print(f"  Data anomali: {(predictions_tracker == -1).sum()}")
print(f"  Distribusi LOF score:")
print(f"    Min: {tracker_df['lof_score'].min():.2f}")
print(f"    Max: {tracker_df['lof_score'].max():.2f}")
print(f"    Mean: {tracker_df['lof_score'].mean():.2f}")
print(f"    Median: {tracker_df['lof_score'].median():.2f}")

# Simpan hasil
tracker_df.to_csv('data/anomalies/tracker_with_lof_scores.csv', index=False)
print(f"\n✓ Hasil disimpan: data/anomalies/tracker_with_lof_scores.csv")

joblib.dump(lof_model_tracker, 'models/lof_model_tracker.pkl')
print(f"✓ Model disimpan: models/lof_model_tracker.pkl")

# Simpan config
config_tracker = {
    'optimal_k': optimal_k_tracker,
    'contamination': 0.05,
    'n_features': len(feature_cols_tracker),
    'feature_names': feature_cols_tracker,
    'model_type': 'LocalOutlierFactor',
    'grid_search_results': grid_results_tracker,
    'final_anomalies_count': int((predictions_tracker == -1).sum()),
    'final_anomaly_percentage': float((predictions_tracker == -1).sum() / len(X_tracker) * 100)
}

with open('models/lof_config_tracker.json', 'w') as f:
    json.dump(config_tracker, f, indent=2)
print(f"✓ Konfigurasi disimpan: models/lof_config_tracker.json")

# Analisis anomali
print(f"\n[5.5.A] ANALISIS ANOMALI TRACKER:")

anomalies_tracker = tracker_df[tracker_df['is_anomaly'] == 1].copy()
print(f"\n  Total anomali: {len(anomalies_tracker)} ({len(anomalies_tracker)/len(tracker_df)*100:.1f}%)")

print(f"\n  Top 10 anomali berdasarkan LOF score:")
top_anomalies_tracker = anomalies_tracker.nlargest(10, 'lof_score')[['timestamp', 'user_id', 'query_type', 'lof_score']]
print(top_anomalies_tracker.to_string(index=False))

print(f"\n  Distribusi anomali per tipe operasi:")
print(anomalies_tracker['query_type'].value_counts())

print(f"\n  Distribusi anomali per user:")
print(anomalies_tracker['user_id'].value_counts().head(10))

# ========================================================
# PART 2: LOF MODELING - STAFF (MASTER LOGIN)
# ========================================================
print("\n\n" + "="*60)
print("PART 2: LOF MODELING - STAFF (MASTER LOGIN)")
print("="*60)

# Load data normalized
staff_df = pd.read_csv('data/normalized/staff_normalized.csv')
print(f"\n[5.1.B] Data staff dimuat: {len(staff_df)} baris")

# Load feature info
with open('models/feature_info_staff.json', 'r') as f:
    feature_info_staff = json.load(f)

feature_cols_staff = feature_info_staff['feature_columns']
print(f"  Fitur untuk modeling: {len(feature_cols_staff)} kolom")

X_staff = staff_df[feature_cols_staff].values
print(f"  Matriks fitur: {X_staff.shape}")

# Grid Search untuk k optimal
print(f"\n[5.2.B] GRID SEARCH UNTUK k OPTIMAL:")
print(f"  Menguji nilai k: {5, 10, 15, 20, 25, 30}")

grid_results_staff = []

for k in k_values:
    print(f"\n  Testing k={k}...")

    lof = LocalOutlierFactor(n_neighbors=k, contamination=0.05)
    predictions = lof.fit_predict(X_staff)
    scores = lof.negative_outlier_factor_

    num_anomalies = (predictions == -1).sum()

    print(f"    Anomali terdeteksi: {num_anomalies} ({num_anomalies/len(X_staff)*100:.1f}%)")
    print(f"    LOF score range: [{scores.min():.2f}, {scores.max():.2f}]")

    grid_results_staff.append({
        'k': k,
        'anomalies_detected': int(num_anomalies),
        'anomaly_percentage': float(num_anomalies/len(X_staff)*100),
        'lof_score_min': float(scores.min()),
        'lof_score_max': float(scores.max()),
        'lof_score_mean': float(scores.mean())
    })

# Pilih k optimal
print(f"\n[5.3.B] HASIL GRID SEARCH:")
results_df_staff = pd.DataFrame(grid_results_staff)
print(results_df_staff.to_string(index=False))

# Pilih k terdekat dengan target 5%
results_df_staff['distance_from_target'] = abs(results_df_staff['anomaly_percentage'] - target_pct)
optimal_idx_staff = results_df_staff['distance_from_target'].idxmin()
optimal_k_staff = int(results_df_staff.loc[optimal_idx_staff, 'k'])

print(f"\n✓ k optimal dipilih: {optimal_k_staff}")
print(f"  Alasan: Terdekat dengan target 5% kontaminasi")
print(f"  Tingkat anomali: {results_df_staff.loc[optimal_idx_staff, 'anomaly_percentage']:.2f}%")

# Fit final model
print(f"\n[5.4.B] FIT FINAL MODEL dengan k={optimal_k_staff}:")

lof_model_staff = LocalOutlierFactor(n_neighbors=optimal_k_staff, contamination=0.05)
predictions_staff = lof_model_staff.fit_predict(X_staff)
lof_scores_staff = lof_model_staff.negative_outlier_factor_

# Simpan hasil ke dataframe
staff_df['lof_score'] = -lof_scores_staff
staff_df['is_anomaly'] = (predictions_staff == -1).astype(int)

print(f"  Data normal: {(predictions_staff == 1).sum()}")
print(f"  Data anomali: {(predictions_staff == -1).sum()}")
print(f"  Distribusi LOF score:")
print(f"    Min: {staff_df['lof_score'].min():.2f}")
print(f"    Max: {staff_df['lof_score'].max():.2f}")
print(f"    Mean: {staff_df['lof_score'].mean():.2f}")
print(f"    Median: {staff_df['lof_score'].median():.2f}")

# Simpan hasil
staff_df.to_csv('data/anomalies/staff_with_lof_scores.csv', index=False)
print(f"\n✓ Hasil disimpan: data/anomalies/staff_with_lof_scores.csv")

joblib.dump(lof_model_staff, 'models/lof_model_staff.pkl')
print(f"✓ Model disimpan: models/lof_model_staff.pkl")

# Simpan config
config_staff = {
    'optimal_k': optimal_k_staff,
    'contamination': 0.05,
    'n_features': len(feature_cols_staff),
    'feature_names': feature_cols_staff,
    'model_type': 'LocalOutlierFactor',
    'grid_search_results': grid_results_staff,
    'final_anomalies_count': int((predictions_staff == -1).sum()),
    'final_anomaly_percentage': float((predictions_staff == -1).sum() / len(X_staff) * 100)
}

with open('models/lof_config_staff.json', 'w') as f:
    json.dump(config_staff, f, indent=2)
print(f"✓ Konfigurasi disimpan: models/lof_config_staff.json")

# Analisis anomali
print(f"\n[5.5.B] ANALISIS ANOMALI STAFF:")

anomalies_staff = staff_df[staff_df['is_anomaly'] == 1].copy()
print(f"\n  Total anomali: {len(anomalies_staff)} ({len(anomalies_staff)/len(staff_df)*100:.1f}%)")

print(f"\n  Top 10 anomali berdasarkan LOF score:")
top_anomalies_staff = anomalies_staff.nlargest(10, 'lof_score')[['date', 'timestamp', 'user_id', 'name', 'lof_score']]
print(top_anomalies_staff.to_string(index=False))

print(f"\n  Distribusi anomali per user:")
print(anomalies_staff['user_id'].value_counts().head(10))

# ========================================================
# RINGKASAN AKHIR
# ========================================================
print("\n\n" + "="*60)
print("TAHAP 5-6 SELESAI - RINGKASAN LOF MODELING")
print("="*60)

print(f"\n1. TRACKER (LOG AKTIVITAS):")
print(f"   k optimal: {optimal_k_tracker}")
print(f"   Kontaminasi: 5%")
print(f"   Total data: {len(tracker_df)}")
print(f"   Anomali terdeteksi: {len(anomalies_tracker)} ({len(anomalies_tracker)/len(tracker_df)*100:.1f}%)")
print(f"   LOF score range: [{tracker_df['lof_score'].min():.2f}, {tracker_df['lof_score'].max():.2f}]")
print(f"   File hasil:")
print(f"     - data/anomalies/tracker_with_lof_scores.csv")
print(f"     - models/lof_model_tracker.pkl")
print(f"     - models/lof_config_tracker.json")

print(f"\n2. STAFF (MASTER LOGIN):")
print(f"   k optimal: {optimal_k_staff}")
print(f"   Kontaminasi: 5%")
print(f"   Total data: {len(staff_df)}")
print(f"   Anomali terdeteksi: {len(anomalies_staff)} ({len(anomalies_staff)/len(staff_df)*100:.1f}%)")
print(f"   LOF score range: [{staff_df['lof_score'].min():.2f}, {staff_df['lof_score'].max():.2f}]")
print(f"   File hasil:")
print(f"     - data/anomalies/staff_with_lof_scores.csv")
print(f"     - models/lof_model_staff.pkl")
print(f"     - models/lof_config_staff.json")

print("\n" + "="*60)
