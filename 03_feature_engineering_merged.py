import pandas as pd
import numpy as np
import sys

# Set UTF-8 encoding for Windows console
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')

print("\n" + "="*80)
print("TAHAP 3: FEATURE ENGINEERING MERGED DATASET")
print("="*80)

# Load cleaned merged data
print("\n[3.1] Memuat data cleaned...")
merged_df = pd.read_csv('data/cleaned/merged_cleaned.csv')
print(f"  Data dimuat: {len(merged_df)} baris, {merged_df.shape[1]} kolom")

# Show distribution by source
source_counts = merged_df['dataset_source'].value_counts()
print(f"\n[3.2] Distribusi berdasarkan source:")
for source, count in source_counts.items():
    print(f"  {source}: {count} baris ({count/len(merged_df)*100:.2f}%)")

# Parse datetime
print(f"\n[3.3] Parsing datetime...")
merged_df['datetime'] = pd.to_datetime(merged_df['timestamp'])
print(f"  Datetime parsed: {merged_df['datetime'].notna().sum()} baris")

# ============================================================================
# D. TRANSFORMASI ATRIBUT TEMPORAL
# ============================================================================
print(f"\n[3.4] D. Transformasi Atribut Temporal...")

# Extract temporal features
merged_df['hour'] = merged_df['datetime'].dt.hour
merged_df['day_of_week'] = merged_df['datetime'].dt.dayofweek  # 0=Monday, 6=Sunday
merged_df['month'] = merged_df['datetime'].dt.month
merged_df['day_of_month'] = merged_df['datetime'].dt.day

print(f"  ✓ hour, day_of_week, month, day_of_month")

# Binary temporal flags
WORK_START = 8
WORK_END = 19  # 08:00-18:30 (hour >= 19 adalah di luar jam kerja)

merged_df['IsOutsideWorkHours'] = ((merged_df['hour'] < WORK_START) | (merged_df['hour'] >= WORK_END)).astype(int)
merged_df['IsWeekend'] = (merged_df['day_of_week'] >= 5).astype(int)  # Saturday=5, Sunday=6
merged_df['NightShift'] = ((merged_df['hour'] >= 0) & (merged_df['hour'] < 6)).astype(int)  # 00:00-06:00

print(f"  ✓ IsOutsideWorkHours, IsWeekend, NightShift")

# Summary temporal features
print(f"\n  Ringkasan fitur temporal:")
print(f"    Aktivitas di luar jam kerja: {merged_df['IsOutsideWorkHours'].sum()} ({merged_df['IsOutsideWorkHours'].mean()*100:.1f}%)")
print(f"    Aktivitas di weekend: {merged_df['IsWeekend'].sum()} ({merged_df['IsWeekend'].mean()*100:.1f}%)")
print(f"    Aktivitas night shift: {merged_df['NightShift'].sum()} ({merged_df['NightShift'].mean()*100:.1f}%)")

# ============================================================================
# E. ENCODING KATEGORI (untuk dataset_source)
# ============================================================================
print(f"\n[3.5] E. Encoding Kategori...")

# One-hot encode dataset_source
merged_df['source_tracker'] = (merged_df['dataset_source'] == 'tracker').astype(int)
merged_df['source_staff'] = (merged_df['dataset_source'] == 'staff').astype(int)

print(f"  ✓ source_tracker, source_staff")
print(f"    Tracker: {merged_df['source_tracker'].sum()}")
print(f"    Staff: {merged_df['source_staff'].sum()}")

# ============================================================================
# F. FITUR PERILAKU (BEHAVIORAL FEATURES)
# ============================================================================
print(f"\n[3.6] F. Fitur Perilaku...")

# 1. Frekuensi aktivitas per user (overall)
user_activity_count = merged_df.groupby('user_id').size()
merged_df['frekuensi_aktivitas_per_user'] = merged_df['user_id'].map(user_activity_count)
print(f"  ✓ frekuensi_aktivitas_per_user")

# 2. Frekuensi per user per source
user_source_count = merged_df.groupby(['user_id', 'dataset_source']).size()
merged_df['frekuensi_per_user_per_source'] = merged_df.apply(
    lambda row: user_source_count.get((row['user_id'], row['dataset_source']), 0), axis=1
)
print(f"  ✓ frekuensi_per_user_per_source")

# 3. Pola waktu akses (variasi jam akses per user)
user_hour_std = merged_df.groupby('user_id')['hour'].std().fillna(0)
merged_df['pola_waktu_akses'] = merged_df['user_id'].map(user_hour_std)
print(f"  ✓ pola_waktu_akses")

# 4. Rasio aktivitas weekend per user
user_weekend_ratio = merged_df.groupby('user_id')['IsWeekend'].mean()
merged_df['rasio_weekend_per_user'] = merged_df['user_id'].map(user_weekend_ratio)
print(f"  ✓ rasio_weekend_per_user")

# 5. Rasio aktivitas di luar jam kerja per user
user_outside_hours_ratio = merged_df.groupby('user_id')['IsOutsideWorkHours'].mean()
merged_df['rasio_outside_hours_per_user'] = merged_df['user_id'].map(user_outside_hours_ratio)
print(f"  ✓ rasio_outside_hours_per_user")

print(f"\n  Statistik fitur perilaku:")
print(f"    Frekuensi aktivitas - Mean: {merged_df['frekuensi_aktivitas_per_user'].mean():.2f}, "
      f"Max: {merged_df['frekuensi_aktivitas_per_user'].max()}")
print(f"    Pola waktu akses - Mean: {merged_df['pola_waktu_akses'].mean():.2f}, "
      f"Std: {merged_df['pola_waktu_akses'].std():.2f}")

# ============================================================================
# FINAL COLUMN SELECTION
# ============================================================================
print(f"\n[3.7] Seleksi kolom final...")

# Define feature columns for modeling
feature_cols = [
    # Original columns
    'user_id', 'timestamp', 'dataset_source',
    # D. Temporal features (10)
    'hour', 'day_of_week', 'month', 'day_of_month',
    'IsOutsideWorkHours', 'IsWeekend', 'NightShift',
    # E. Categorical encoding (2)
    'source_tracker', 'source_staff',
    # F. Behavioral features (5)
    'frekuensi_aktivitas_per_user', 'frekuensi_per_user_per_source',
    'pola_waktu_akses', 'rasio_weekend_per_user', 'rasio_outside_hours_per_user'
]

# Keep only selected columns
merged_transformed = merged_df[feature_cols].copy()

print(f"  Total kolom dipilih: {len(feature_cols)}")
print(f"  Kolom: {feature_cols}")

# ============================================================================
# SAVE TRANSFORMED DATA
# ============================================================================
output_path = 'data/transformed/merged_transformed.csv'
merged_transformed.to_csv(output_path, index=False)
print(f"\n[OK] Data transformed tersimpan: {output_path}")

# ============================================================================
# SUMMARY
# ============================================================================
print("\n" + "="*80)
print("TAHAP 3 SELESAI - RINGKASAN FEATURE ENGINEERING MERGED")
print("="*80)

print(f"\nInput: data/cleaned/merged_cleaned.csv ({len(merged_df)} baris)")
print(f"Output: {output_path} ({len(merged_transformed)} baris)")

print(f"\nFitur yang dibuat:")
print(f"  D. Temporal Features: 7")
print(f"    - hour, day_of_week, month, day_of_month")
print(f"    - IsOutsideWorkHours, IsWeekend, NightShift")
print(f"\n  E. Categorical Encoding: 2")
print(f"    - source_tracker, source_staff")
print(f"\n  F. Behavioral Features: 5")
print(f"    - frekuensi_aktivitas_per_user")
print(f"    - frekuensi_per_user_per_source")
print(f"    - pola_waktu_akses")
print(f"    - rasio_weekend_per_user")
print(f"    - rasio_outside_hours_per_user")

print(f"\nTotal fitur untuk modeling: {len(feature_cols) - 3} (exclude user_id, timestamp, dataset_source)")

print(f"\nDistribusi final berdasarkan source:")
final_source_counts = merged_transformed['dataset_source'].value_counts()
for source, count in final_source_counts.items():
    print(f"  {source}: {count} ({count/len(merged_transformed)*100:.2f}%)")

print("\n" + "="*80)
