import pandas as pd
import numpy as np
from sklearn.preprocessing import StandardScaler
import joblib
import json
import sys

# Set UTF-8 encoding for Windows console
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')

print("\n" + "="*60)
print("TAHAP 4: NORMALISASI MERGED DATASET")
print("="*60)

# Load transformed merged data
print("\n[4.1] Memuat data transformed...")
merged_df = pd.read_csv('data/transformed/merged_transformed.csv')
print(f"  Data dimuat: {len(merged_df)} baris, {merged_df.shape[1]} kolom")

# Show distribution by source
source_counts = merged_df['dataset_source'].value_counts()
print(f"\n  Distribusi berdasarkan source:")
for source, count in source_counts.items():
    print(f"    {source}: {count} ({count/len(merged_df)*100:.2f}%)")

# Define feature columns for modeling (exclude metadata)
feature_cols = [
    # D. Temporal (7)
    'hour', 'day_of_week', 'month', 'day_of_month',
    'IsOutsideWorkHours', 'IsWeekend', 'NightShift',
    # E. Categorical (2)
    'source_tracker', 'source_staff',
    # F. Behavioral (5)
    'frekuensi_aktivitas_per_user', 'frekuensi_per_user_per_source',
    'pola_waktu_akses', 'rasio_weekend_per_user', 'rasio_outside_hours_per_user'
]

print(f"\n[4.2] Fitur untuk normalisasi: {len(feature_cols)} kolom")

# Verify all columns exist
missing_cols = [col for col in feature_cols if col not in merged_df.columns]
if missing_cols:
    print(f"  [ERROR] Kolom tidak ditemukan: {missing_cols}")
    exit(1)

# Extract features
X_merged = merged_df[feature_cols].values
print(f"  Matriks fitur: {X_merged.shape}")

# Statistics before normalization
print(f"\n[4.3] Statistik SEBELUM normalisasi:")
print(f"  Mean: {X_merged.mean():.6f}")
print(f"  Std: {X_merged.std():.6f}")
print(f"  Range: [{X_merged.min():.2f}, {X_merged.max():.2f}]")

# Apply StandardScaler
print(f"\n[4.4] Menerapkan StandardScaler:")
print(f"  Formula: z = (x - mean) / std")

scaler_merged = StandardScaler()
X_merged_normalized = scaler_merged.fit_transform(X_merged)

print(f"  ✓ Normalisasi selesai")

# Verify normalization
print(f"\n[4.5] Statistik SETELAH normalisasi:")
means = X_merged_normalized.mean(axis=0)
stds = X_merged_normalized.std(axis=0)

print(f"  Mean seluruh fitur: {means.mean():.10f} (target: ~0)")
print(f"  Std seluruh fitur: {stds.mean():.6f} (target: ~1)")
print(f"  Range: [{X_merged_normalized.min():.2f}, {X_merged_normalized.max():.2f}]")

if abs(means.mean()) < 1e-8 and 0.5 < stds.mean() < 1.5:
    print(f"  ✓ Normalisasi berhasil!")
else:
    print(f"  [WARNING] Normalisasi mungkin ada masalah")

# Save normalized data
merged_normalized = merged_df.copy()
merged_normalized[feature_cols] = X_merged_normalized

output_path = 'data/normalized/merged_normalized.csv'
merged_normalized.to_csv(output_path, index=False)
print(f"\n✓ Data tersimpan: {output_path}")

# Save scaler
joblib.dump(scaler_merged, 'models/scaler_merged.pkl')
print(f"✓ Scaler tersimpan: models/scaler_merged.pkl")

# Save metadata
merged_feature_info = {
    'feature_columns': feature_cols,
    'n_features': len(feature_cols),
    'n_samples': len(X_merged),
    'source_distribution': {
        source: int(count) for source, count in source_counts.items()
    },
    'scaler_params': {
        'mean': scaler_merged.mean_.tolist(),
        'scale': scaler_merged.scale_.tolist(),
        'var': scaler_merged.var_.tolist()
    }
}

with open('models/feature_info_merged.json', 'w') as f:
    json.dump(merged_feature_info, f, indent=2)
print(f"✓ Metadata fitur tersimpan: models/feature_info_merged.json")

# ============================================================================
# SUMMARY
# ============================================================================
print("\n" + "="*60)
print("TAHAP 4 SELESAI - RINGKASAN NORMALISASI MERGED")
print("="*60)

print(f"\nFile normalized: {output_path}")
print(f"Baris: {len(merged_normalized)}")
print(f"Fitur dinormalisasi: {len(feature_cols)}")
print(f"Mean (normalized): {means.mean():.10f}")
print(f"Std (normalized): {stds.mean():.6f}")

print(f"\nDistribusi berdasarkan source:")
for source, count in source_counts.items():
    print(f"  {source}: {count} ({count/len(merged_df)*100:.2f}%)")

print(f"\nFile pendukung:")
print(f"  - models/scaler_merged.pkl")
print(f"  - models/feature_info_merged.json")

print("\n" + "="*60)
