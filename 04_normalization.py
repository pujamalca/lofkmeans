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
print("TAHAP 4: NORMALISASI DATA")
print("="*60)

# ========================================================
# PART 1: NORMALISASI TRACKER (LOG AKTIVITAS)
# ========================================================
print("\n" + "="*60)
print("PART 1: NORMALISASI TRACKER (LOG AKTIVITAS)")
print("="*60)

tracker_df = pd.read_csv('data/transformed/tracker_transformed.csv')
print(f"\n[4.1.A] Data tracker dimuat: {len(tracker_df)} baris")

# Definisi kolom fitur untuk modeling
tracker_feature_cols = [
    # D. Transformasi Temporal (7 fitur)
    'hour', 'day_of_week', 'month', 'day_of_month',
    'IsOutsideWorkHours', 'IsWeekend', 'NightShift',
    # E. Encoding Kategori (3 fitur)
    'op_DELETE', 'op_INSERT', 'op_UPDATE',
    # F. Fitur Perilaku (4 fitur)
    'frekuensi_aktivitas_per_user', 'jumlah_tipe_operasi_unik',
    'rasio_operasi_modifikasi', 'pola_waktu_akses'
]

print(f"  Fitur untuk normalisasi: {len(tracker_feature_cols)} kolom")

# Verifikasi semua kolom ada
missing_cols = [col for col in tracker_feature_cols if col not in tracker_df.columns]
if missing_cols:
    print(f"  [ERROR] Kolom tidak ditemukan: {missing_cols}")
    exit(1)

X_tracker = tracker_df[tracker_feature_cols].values
print(f"  Matriks fitur: {X_tracker.shape}")

# Statistik sebelum normalisasi
print(f"\n[4.2.A] Statistik SEBELUM normalisasi:")
print(f"  Mean: {X_tracker.mean():.6f}")
print(f"  Std: {X_tracker.std():.6f}")
print(f"  Range: [{X_tracker.min():.2f}, {X_tracker.max():.2f}]")

# Terapkan StandardScaler
print(f"\n[4.3.A] Menerapkan StandardScaler:")
print(f"  Formula: z = (x - mean) / std")

scaler_tracker = StandardScaler()
X_tracker_normalized = scaler_tracker.fit_transform(X_tracker)

print(f"  ✓ Normalisasi selesai")

# Verifikasi hasil normalisasi
print(f"\n[4.4.A] Statistik SETELAH normalisasi:")
means = X_tracker_normalized.mean(axis=0)
stds = X_tracker_normalized.std(axis=0)

print(f"  Mean seluruh fitur: {means.mean():.10f} (target: ~0)")
print(f"  Std seluruh fitur: {stds.mean():.6f} (target: ~1)")
print(f"  Range: [{X_tracker_normalized.min():.2f}, {X_tracker_normalized.max():.2f}]")

if abs(means.mean()) < 1e-8 and 0.5 < stds.mean() < 1.5:
    print(f"  ✓ Normalisasi berhasil!")
else:
    print(f"  [WARNING] Normalisasi mungkin ada masalah")

# Simpan data normalized
tracker_normalized = tracker_df.copy()
tracker_normalized[tracker_feature_cols] = X_tracker_normalized

tracker_normalized.to_csv('data/normalized/tracker_normalized.csv', index=False)
print(f"\n✓ Data tersimpan: data/normalized/tracker_normalized.csv")

# Simpan scaler
joblib.dump(scaler_tracker, 'models/scaler_tracker.pkl')
print(f"✓ Scaler tersimpan: models/scaler_tracker.pkl")

# Simpan metadata fitur
tracker_feature_info = {
    'feature_columns': tracker_feature_cols,
    'n_features': len(tracker_feature_cols),
    'n_samples': len(X_tracker),
    'scaler_params': {
        'mean': scaler_tracker.mean_.tolist(),
        'scale': scaler_tracker.scale_.tolist(),
        'var': scaler_tracker.var_.tolist()
    }
}

with open('models/feature_info_tracker.json', 'w') as f:
    json.dump(tracker_feature_info, f, indent=2)
print(f"✓ Metadata fitur tersimpan: models/feature_info_tracker.json")

# ========================================================
# PART 2: NORMALISASI STAFF (MASTER LOGIN)
# ========================================================
print("\n\n" + "="*60)
print("PART 2: NORMALISASI STAFF (MASTER LOGIN)")
print("="*60)

staff_df = pd.read_csv('data/transformed/staff_transformed.csv')
print(f"\n[4.1.B] Data staff dimuat: {len(staff_df)} baris")

# Definisi kolom fitur untuk modeling
staff_feature_cols = [
    # D. Transformasi Temporal (8 fitur)
    'hour', 'day_of_week', 'month', 'day_of_month',
    'IsEarlyLogin', 'IsLateLogin', 'IsAfterWorkHours', 'IsWeekend',
    # F. Fitur Perilaku (3 fitur)
    'frekuensi_login_per_user', 'pola_waktu_login', 'rasio_login_weekend'
]

print(f"  Fitur untuk normalisasi: {len(staff_feature_cols)} kolom")

# Verifikasi kolom
missing_cols = [col for col in staff_feature_cols if col not in staff_df.columns]
if missing_cols:
    print(f"  [ERROR] Kolom tidak ditemukan: {missing_cols}")
    exit(1)

X_staff = staff_df[staff_feature_cols].values
print(f"  Matriks fitur: {X_staff.shape}")

# Statistik sebelum normalisasi
print(f"\n[4.2.B] Statistik SEBELUM normalisasi:")
print(f"  Mean: {X_staff.mean():.6f}")
print(f"  Std: {X_staff.std():.6f}")
print(f"  Range: [{X_staff.min():.2f}, {X_staff.max():.2f}]")

# Terapkan StandardScaler
print(f"\n[4.3.B] Menerapkan StandardScaler:")

scaler_staff = StandardScaler()
X_staff_normalized = scaler_staff.fit_transform(X_staff)

print(f"  ✓ Normalisasi selesai")

# Verifikasi hasil normalisasi
print(f"\n[4.4.B] Statistik SETELAH normalisasi:")
means_staff = X_staff_normalized.mean(axis=0)
stds_staff = X_staff_normalized.std(axis=0)

print(f"  Mean seluruh fitur: {means_staff.mean():.10f} (target: ~0)")
print(f"  Std seluruh fitur: {stds_staff.mean():.6f} (target: ~1)")
print(f"  Range: [{X_staff_normalized.min():.2f}, {X_staff_normalized.max():.2f}]")

if abs(means_staff.mean()) < 1e-8 and 0.5 < stds_staff.mean() < 1.5:
    print(f"  ✓ Normalisasi berhasil!")
else:
    print(f"  [WARNING] Normalisasi mungkin ada masalah")

# Simpan data normalized
staff_normalized = staff_df.copy()
staff_normalized[staff_feature_cols] = X_staff_normalized

staff_normalized.to_csv('data/normalized/staff_normalized.csv', index=False)
print(f"\n✓ Data tersimpan: data/normalized/staff_normalized.csv")

# Simpan scaler
joblib.dump(scaler_staff, 'models/scaler_staff.pkl')
print(f"✓ Scaler tersimpan: models/scaler_staff.pkl")

# Simpan metadata fitur
staff_feature_info = {
    'feature_columns': staff_feature_cols,
    'n_features': len(staff_feature_cols),
    'n_samples': len(X_staff),
    'scaler_params': {
        'mean': scaler_staff.mean_.tolist(),
        'scale': scaler_staff.scale_.tolist(),
        'var': scaler_staff.var_.tolist()
    }
}

with open('models/feature_info_staff.json', 'w') as f:
    json.dump(staff_feature_info, f, indent=2)
print(f"✓ Metadata fitur tersimpan: models/feature_info_staff.json")

# ========================================================
# RINGKASAN AKHIR
# ========================================================
print("\n\n" + "="*60)
print("TAHAP 4 SELESAI - RINGKASAN NORMALISASI")
print("="*60)

print(f"\n1. TRACKER (LOG AKTIVITAS):")
print(f"   File normalized: data/normalized/tracker_normalized.csv")
print(f"   Baris: {len(tracker_normalized)}")
print(f"   Fitur dinormalisasi: {len(tracker_feature_cols)}")
print(f"   Mean (normalized): {means.mean():.10f}")
print(f"   Std (normalized): {stds.mean():.6f}")
print(f"   File pendukung:")
print(f"     - models/scaler_tracker.pkl")
print(f"     - models/feature_info_tracker.json")

print(f"\n2. STAFF (MASTER LOGIN):")
print(f"   File normalized: data/normalized/staff_normalized.csv")
print(f"   Baris: {len(staff_normalized)}")
print(f"   Fitur dinormalisasi: {len(staff_feature_cols)}")
print(f"   Mean (normalized): {means_staff.mean():.10f}")
print(f"   Std (normalized): {stds_staff.mean():.6f}")
print(f"   File pendukung:")
print(f"     - models/scaler_staff.pkl")
print(f"     - models/feature_info_staff.json")

print("\n" + "="*60)
