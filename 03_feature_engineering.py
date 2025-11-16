import pandas as pd
import numpy as np
import re
from datetime import datetime
import sys

# Set UTF-8 encoding for Windows console
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')

print("\n" + "="*60)
print("TAHAP 3: FEATURE ENGINEERING & TRANSFORMATION")
print("="*60)

# ========================================================
# PART 1: FEATURE ENGINEERING - TRACKER (LOG AKTIVITAS)
# ========================================================
print("\n" + "="*60)
print("PART 1: FEATURE ENGINEERING - TRACKER (LOG AKTIVITAS)")
print("="*60)

tracker_df = pd.read_csv('data/cleaned/tracker_cleaned.csv')
print(f"\nData input: {len(tracker_df)} baris")

# ========================================================
# D. TRANSFORMASI ATRIBUT TEMPORAL
# ========================================================
print("\n[D] TRANSFORMASI ATRIBUT TEMPORAL:")

tracker_df['datetime'] = pd.to_datetime(tracker_df['datetime'])

# Fitur numerik dari timestamp
tracker_df['hour'] = tracker_df['datetime'].dt.hour              # 0-23
tracker_df['day_of_week'] = tracker_df['datetime'].dt.dayofweek  # 0=Senin, 6=Minggu
tracker_df['month'] = tracker_df['datetime'].dt.month            # 1-12
tracker_df['day_of_month'] = tracker_df['datetime'].dt.day       # 1-31

# Binary flags untuk pola temporal anomali
WORK_START = 8
WORK_END = 19  # Jam kerja: 08:00-18:30, maka hour >= 19 adalah di luar jam kerja
tracker_df['IsOutsideWorkHours'] = ((tracker_df['hour'] < WORK_START) | (tracker_df['hour'] >= WORK_END)).astype(int)
tracker_df['IsWeekend'] = tracker_df['day_of_week'].isin([5, 6]).astype(int)  # Sabtu=5, Minggu=6
tracker_df['NightShift'] = ((tracker_df['hour'] >= 21) | (tracker_df['hour'] < 6)).astype(int)

print(f"  ✓ Fitur temporal numerik: hour (0-23), day_of_week (0-6), month (1-12), day_of_month (1-31)")
print(f"  ✓ Binary flags: IsOutsideWorkHours, IsWeekend, NightShift")
print(f"    - Jam kerja: {WORK_START}:00 - 18:30 (hour >= {WORK_END} = di luar jam kerja)")
print(f"    - Aktivitas di luar jam kerja: {tracker_df['IsOutsideWorkHours'].sum()} ({tracker_df['IsOutsideWorkHours'].sum()/len(tracker_df)*100:.1f}%)")
print(f"    - Aktivitas weekend: {tracker_df['IsWeekend'].sum()} ({tracker_df['IsWeekend'].sum()/len(tracker_df)*100:.1f}%)")
print(f"    - Aktivitas malam: {tracker_df['NightShift'].sum()} ({tracker_df['NightShift'].sum()/len(tracker_df)*100:.1f}%)")

# ========================================================
# E. ENCODING ATRIBUT KATEGORI
# ========================================================
print("\n[E] ENCODING ATRIBUT KATEGORI (One-Hot Encoding):")

# Pastikan kolom query_type ada
if 'query_type' not in tracker_df.columns:
    tracker_df['query_type'] = tracker_df['query_info'].str.extract(r'(insert|update|delete|select)', expand=False, flags=2).fillna('other').str.upper()

# One-hot encoding untuk jenis operasi
query_dummies = pd.get_dummies(tracker_df['query_type'], prefix='op')
tracker_df = pd.concat([tracker_df, query_dummies], axis=1)

query_types = tracker_df['query_type'].unique()
print(f"  ✓ Jenis operasi ditemukan: {list(query_types)}")
print(f"  ✓ One-hot encoding diterapkan: {list(query_dummies.columns)}")
print(f"  ✓ Distribusi:")
for qtype in query_types:
    count = (tracker_df['query_type'] == qtype).sum()
    print(f"    - {qtype}: {count} ({count/len(tracker_df)*100:.1f}%)")

# ========================================================
# F. EKSTRAKSI FITUR-FITUR PERILAKU
# ========================================================
print("\n[F] EKSTRAKSI FITUR-FITUR PERILAKU:")

# Fitur 1: Frekuensi aktivitas per pengguna
user_activity_count = tracker_df.groupby('user_id').size()
tracker_df['frekuensi_aktivitas_per_user'] = tracker_df['user_id'].map(user_activity_count)

print(f"  ✓ Fitur 1: frekuensi_aktivitas_per_user")
print(f"    - Min: {tracker_df['frekuensi_aktivitas_per_user'].min():.0f}, Max: {tracker_df['frekuensi_aktivitas_per_user'].max():.0f}")

# Fitur 2: Jumlah tipe operasi unik per pengguna
user_op_diversity = tracker_df.groupby('user_id')['query_type'].nunique()
tracker_df['jumlah_tipe_operasi_unik'] = tracker_df['user_id'].map(user_op_diversity)

print(f"  ✓ Fitur 2: jumlah_tipe_operasi_unik")
print(f"    - Min: {tracker_df['jumlah_tipe_operasi_unik'].min():.0f}, Max: {tracker_df['jumlah_tipe_operasi_unik'].max():.0f}")

# Fitur 3: Rasio operasi modifikasi data (INSERT+UPDATE+DELETE / total)
modify_ops = tracker_df[tracker_df['query_type'].isin(['INSERT', 'UPDATE', 'DELETE'])].groupby('user_id').size()
total_ops = tracker_df.groupby('user_id').size()
mod_ratio = modify_ops / total_ops
tracker_df['rasio_operasi_modifikasi'] = tracker_df['user_id'].map(mod_ratio).fillna(0)

print(f"  ✓ Fitur 3: rasio_operasi_modifikasi")
print(f"    - Mean: {tracker_df['rasio_operasi_modifikasi'].mean():.3f}")

# Fitur 4: Pola waktu akses (standar deviasi jam akses per user)
user_hour_std = tracker_df.groupby('user_id')['hour'].std().fillna(0)
tracker_df['pola_waktu_akses'] = tracker_df['user_id'].map(user_hour_std)

print(f"  ✓ Fitur 4: pola_waktu_akses (variasi jam akses)")
print(f"    - Mean std: {tracker_df['pola_waktu_akses'].mean():.2f}")

# ========================================================
# SIMPAN HASIL - HANYA KOLOM YANG DIPERLUKAN
# ========================================================
print("\n[SELEKSI FITUR UNTUK MODELING]:")

# Kolom metadata (untuk referensi, tidak digunakan modeling)
metadata_cols = ['timestamp', 'user_id', 'query_info', 'query_type']

# Kolom fitur (untuk modeling)
temporal_cols = ['hour', 'day_of_week', 'month', 'day_of_month',
                 'IsOutsideWorkHours', 'IsWeekend', 'NightShift']

# One-hot encoding columns (dinamis)
encoding_cols = [col for col in tracker_df.columns if col.startswith('op_')]

behavioral_cols = ['frekuensi_aktivitas_per_user', 'jumlah_tipe_operasi_unik',
                   'rasio_operasi_modifikasi', 'pola_waktu_akses']

# Gabungkan semua kolom yang akan disimpan
all_cols = metadata_cols + temporal_cols + encoding_cols + behavioral_cols

# Filter hanya kolom yang diperlukan
tracker_transformed = tracker_df[all_cols].copy()

print(f"  Total kolom yang disimpan: {len(all_cols)}")
print(f"    - Metadata: {len(metadata_cols)} kolom")
print(f"    - Fitur temporal: {len(temporal_cols)} kolom")
print(f"    - Fitur encoding: {len(encoding_cols)} kolom")
print(f"    - Fitur behavioral: {len(behavioral_cols)} kolom")
print(f"  Total fitur untuk modeling: {len(temporal_cols) + len(encoding_cols) + len(behavioral_cols)}")

tracker_transformed.to_csv('data/transformed/tracker_transformed.csv', index=False)
print(f"\n✓ Data tersimpan: data/transformed/tracker_transformed.csv")

# ========================================================
# PART 2: FEATURE ENGINEERING - STAFF (MASTER LOGIN)
# ========================================================
print("\n\n" + "="*60)
print("PART 2: FEATURE ENGINEERING - STAFF (MASTER LOGIN)")
print("="*60)

staff_df = pd.read_csv('data/cleaned/staff_cleaned.csv')
print(f"\nData input: {len(staff_df)} baris")

# ========================================================
# D. TRANSFORMASI ATRIBUT TEMPORAL
# ========================================================
print("\n[D] TRANSFORMASI ATRIBUT TEMPORAL:")

# Gabungkan date dan timestamp
staff_df['datetime'] = pd.to_datetime(staff_df['date'].astype(str) + ' ' + staff_df['timestamp'].astype(str))

# Fitur numerik dari timestamp
staff_df['hour'] = staff_df['datetime'].dt.hour
staff_df['day_of_week'] = staff_df['datetime'].dt.dayofweek
staff_df['month'] = staff_df['datetime'].dt.month
staff_df['day_of_month'] = staff_df['datetime'].dt.day

# Binary flags untuk pola temporal login (jam kerja: 08:00-18:30)
staff_df['IsEarlyLogin'] = (staff_df['hour'] < 8).astype(int)      # Login sebelum jam 8
staff_df['IsLateLogin'] = (staff_df['hour'] >= 10).astype(int)     # Login setelah jam 10 (terlambat mulai kerja)
staff_df['IsAfterWorkHours'] = (staff_df['hour'] >= 19).astype(int)  # Login setelah jam kerja (>= 19:00)
staff_df['IsWeekend'] = staff_df['day_of_week'].isin([5, 6]).astype(int)

print(f"  ✓ Fitur temporal numerik: hour (0-23), day_of_week (0-6), month (1-12), day_of_month (1-31)")
print(f"  ✓ Binary flags: IsEarlyLogin, IsLateLogin, IsAfterWorkHours, IsWeekend")
print(f"    - Jam kerja: 08:00 - 18:30")
print(f"    - Login pagi (< 8 AM): {staff_df['IsEarlyLogin'].sum()} ({staff_df['IsEarlyLogin'].sum()/len(staff_df)*100:.1f}%)")
print(f"    - Login terlambat (>= 10 AM): {staff_df['IsLateLogin'].sum()} ({staff_df['IsLateLogin'].sum()/len(staff_df)*100:.1f}%)")
print(f"    - Login setelah jam kerja (>= 19:00): {staff_df['IsAfterWorkHours'].sum()} ({staff_df['IsAfterWorkHours'].sum()/len(staff_df)*100:.1f}%)")
print(f"    - Login weekend: {staff_df['IsWeekend'].sum()} ({staff_df['IsWeekend'].sum()/len(staff_df)*100:.1f}%)")

# ========================================================
# F. EKSTRAKSI FITUR-FITUR PERILAKU (LOGIN)
# ========================================================
print("\n[F] EKSTRAKSI FITUR-FITUR PERILAKU LOGIN:")

# Fitur 1: Frekuensi login per pengguna
user_login_count = staff_df.groupby('user_id').size()
staff_df['frekuensi_login_per_user'] = staff_df['user_id'].map(user_login_count)

print(f"  ✓ Fitur 1: frekuensi_login_per_user")
print(f"    - Min: {staff_df['frekuensi_login_per_user'].min():.0f}, Max: {staff_df['frekuensi_login_per_user'].max():.0f}")

# Fitur 2: Pola waktu login (standar deviasi jam login)
user_login_hour_std = staff_df.groupby('user_id')['hour'].std().fillna(0)
staff_df['pola_waktu_login'] = staff_df['user_id'].map(user_login_hour_std)

print(f"  ✓ Fitur 2: pola_waktu_login (variasi jam login)")
print(f"    - Mean std: {staff_df['pola_waktu_login'].mean():.2f}")

# Fitur 3: Rasio login weekend
weekend_logins = staff_df[staff_df['IsWeekend'] == 1].groupby('user_id').size()
total_logins = staff_df.groupby('user_id').size()
weekend_ratio = weekend_logins / total_logins
staff_df['rasio_login_weekend'] = staff_df['user_id'].map(weekend_ratio).fillna(0)

print(f"  ✓ Fitur 3: rasio_login_weekend")
print(f"    - Mean: {staff_df['rasio_login_weekend'].mean():.3f}")

# ========================================================
# SIMPAN HASIL - HANYA KOLOM YANG DIPERLUKAN
# ========================================================
print("\n[SELEKSI FITUR UNTUK MODELING]:")

# Kolom metadata
staff_metadata_cols = ['user_id', 'date', 'timestamp', 'name']

# Kolom fitur
staff_temporal_cols = ['hour', 'day_of_week', 'month', 'day_of_month',
                       'IsEarlyLogin', 'IsLateLogin', 'IsAfterWorkHours', 'IsWeekend']

staff_behavioral_cols = ['frekuensi_login_per_user', 'pola_waktu_login', 'rasio_login_weekend']

# Gabungkan
staff_all_cols = staff_metadata_cols + staff_temporal_cols + staff_behavioral_cols

# Filter hanya kolom yang diperlukan
staff_transformed = staff_df[staff_all_cols].copy()

print(f"  Total kolom yang disimpan: {len(staff_all_cols)}")
print(f"    - Metadata: {len(staff_metadata_cols)} kolom")
print(f"    - Fitur temporal: {len(staff_temporal_cols)} kolom")
print(f"    - Fitur behavioral: {len(staff_behavioral_cols)} kolom")
print(f"  Total fitur untuk modeling: {len(staff_temporal_cols) + len(staff_behavioral_cols)}")

staff_transformed.to_csv('data/transformed/staff_transformed.csv', index=False)
print(f"\n✓ Data tersimpan: data/transformed/staff_transformed.csv")

# ========================================================
# RINGKASAN AKHIR
# ========================================================
print("\n\n" + "="*60)
print("TAHAP 3 SELESAI - RINGKASAN FEATURE ENGINEERING")
print("="*60)

print(f"\n1. TRACKER (LOG AKTIVITAS):")
print(f"   File: data/transformed/tracker_transformed.csv")
print(f"   Baris: {len(tracker_transformed)}")
print(f"   Total kolom: {len(all_cols)}")
print(f"   Fitur modeling: {len(temporal_cols) + len(encoding_cols) + len(behavioral_cols)}")
print(f"   Rincian fitur:")
print(f"     - D. Transformasi Temporal: {len(temporal_cols)} fitur")
print(f"     - E. Encoding Kategori: {len(encoding_cols)} fitur")
print(f"     - F. Fitur Perilaku: {len(behavioral_cols)} fitur")

print(f"\n2. STAFF (MASTER LOGIN):")
print(f"   File: data/transformed/staff_transformed.csv")
print(f"   Baris: {len(staff_transformed)}")
print(f"   Total kolom: {len(staff_all_cols)}")
print(f"   Fitur modeling: {len(staff_temporal_cols) + len(staff_behavioral_cols)}")
print(f"   Rincian fitur:")
print(f"     - D. Transformasi Temporal: {len(staff_temporal_cols)} fitur")
print(f"     - F. Fitur Perilaku: {len(staff_behavioral_cols)} fitur")

print("\n" + "="*60)
