import pandas as pd
import numpy as np
import sys

# Set UTF-8 encoding for Windows console
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')

print("\n" + "="*60)
print("TAHAP 2: PREPROCESSING MERGED DATASET")
print("="*60)

# Load merged raw data
print("\n[2.1] Memuat data merged...")
merged_df = pd.read_csv('data/raw/merged_raw.csv')
print(f"  Data dimuat: {len(merged_df)} baris, {merged_df.shape[1]} kolom")
print(f"  Kolom: {merged_df.columns.tolist()}")

# Show source distribution
print(f"\n[2.2] Distribusi berdasarkan source:")
source_counts = merged_df['dataset_source'].value_counts()
for source, count in source_counts.items():
    print(f"  {source}: {count} baris ({count/len(merged_df)*100:.2f}%)")

# Parse timestamp column
print(f"\n[2.3] Parsing kolom timestamp...")
merged_df['datetime'] = pd.to_datetime(merged_df['timestamp'], errors='coerce')

# Check for invalid timestamps
invalid_timestamps = merged_df['datetime'].isna().sum()
if invalid_timestamps > 0:
    print(f"  [WARNING] Ditemukan {invalid_timestamps} timestamp invalid")
    print(f"  Menghapus baris dengan timestamp invalid...")
    merged_df = merged_df[merged_df['datetime'].notna()].copy()
    print(f"  Baris tersisa: {len(merged_df)}")

# Step 1: Handle Missing Values
print(f"\n[2.4] Menangani missing values...")
print(f"  Missing values sebelum:")
missing_before = merged_df.isnull().sum()
for col, count in missing_before.items():
    if count > 0:
        print(f"    {col}: {count} ({count/len(merged_df)*100:.2f}%)")

# Remove rows with missing critical values
critical_cols = ['user_id', 'timestamp', 'dataset_source']
merged_df = merged_df.dropna(subset=critical_cols)
print(f"  Baris setelah drop missing critical cols: {len(merged_df)}")

# Step 2: Remove Duplicates
print(f"\n[2.5] Menghapus duplikasi...")
print(f"  Baris sebelum: {len(merged_df)}")
duplicates = merged_df.duplicated().sum()
print(f"  Duplikasi ditemukan: {duplicates}")

if duplicates > 0:
    merged_df = merged_df.drop_duplicates()
    print(f"  Baris setelah: {len(merged_df)}")

# Step 3: Handle Outliers (if applicable)
# For merged data, we'll skip outlier removal since it might affect legitimate data
print(f"\n[2.6] Outlier handling...")
print(f"  [INFO] Outlier removal skipped for merged dataset")
print(f"  [INFO] Outlier detection akan dilakukan di tahap LOF")

# Step 4: Data Type Conversion
print(f"\n[2.7] Konversi tipe data...")
merged_df['user_id'] = merged_df['user_id'].astype(int)
print(f"  user_id → int64")

# Step 5: Sort by datetime
print(f"\n[2.8] Mengurutkan data berdasarkan datetime...")
merged_df = merged_df.sort_values('datetime').reset_index(drop=True)
print(f"  Data diurutkan")

# Final Statistics
print(f"\n[2.9] Statistik akhir:")
print(f"  Total baris: {len(merged_df)}")
print(f"  Total kolom: {merged_df.shape[1]}")
print(f"  Missing values:")
final_missing = merged_df.isnull().sum()
if final_missing.sum() == 0:
    print(f"    Tidak ada missing values")
else:
    for col, count in final_missing.items():
        if count > 0:
            print(f"    {col}: {count}")

# Distribution by source after cleaning
print(f"\n  Distribusi final berdasarkan source:")
final_source_counts = merged_df['dataset_source'].value_counts()
for source, count in final_source_counts.items():
    print(f"    {source}: {count} baris ({count/len(merged_df)*100:.2f}%)")

# Save cleaned data
output_path = 'data/cleaned/merged_cleaned.csv'
merged_df.to_csv(output_path, index=False)
print(f"\n[OK] Data cleaned tersimpan: {output_path}")

# Summary
print("\n" + "="*60)
print("TAHAP 2 SELESAI - RINGKASAN PREPROCESSING MERGED")
print("="*60)
print(f"\nInput: data/raw/merged_raw.csv")
print(f"Output: {output_path}")
print(f"\nPerubahan:")
print(f"  Baris awal: {source_counts.sum()}")
print(f"  Baris akhir: {len(merged_df)}")
print(f"  Baris dihapus: {source_counts.sum() - len(merged_df)}")
print(f"\nDistribusi final:")
for source, count in final_source_counts.items():
    print(f"  {source}: {count} ({count/len(merged_df)*100:.2f}%)")

print("\n" + "="*60)
