import pandas as pd
import numpy as np
import re
import sys

# Set UTF-8 encoding for Windows console
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')

print("\n" + "="*60)
print("TAHAP 2: PREPROCESSING & FEATURE EXTRACTION")
print("="*60)

# ========================================================
# PART 1: PREPROCESSING TRACKER DATA (LOG AKTIVITAS)
# ========================================================
print("\n" + "="*60)
print("PART 1: PREPROCESSING TRACKER DATA (LOG AKTIVITAS)")
print("="*60)

# Load raw tracker data
tracker_df = pd.read_csv('data/raw/tracker_raw.csv')
tracker_initial_count = len(tracker_df)
print(f"\n[2.1.A] Data tracker awal: {tracker_initial_count} rows")

# 2.1.1 Remove Missing Values
print("\n[2.1.1.A] Cek Missing Values (Tracker):")
missing = tracker_df.isnull().sum()
print(f"  Missing values per column:")
print(missing)

missing_rows = tracker_df[tracker_df[['timestamp', 'user_id', 'query_info']].isnull().any(axis=1)]
print(f"  Rows with missing critical data: {len(missing_rows)}")

tracker_df = tracker_df[tracker_df[['timestamp', 'user_id', 'query_info']].notna().all(axis=1)]
tracker_after_missing = len(tracker_df)
print(f"  [OK] Data setelah removing missing values: {tracker_after_missing} rows")

# 2.1.2 Remove Duplicates
print("\n[2.1.2.A] Cek Duplikasi (Tracker):")
duplicates = tracker_df[tracker_df.duplicated(subset=['timestamp', 'query_info', 'user_id'], keep=False)]
duplicate_count = len(duplicates)
print(f"  Duplicate rows found: {duplicate_count}")

tracker_df = tracker_df.drop_duplicates(subset=['timestamp', 'query_info', 'user_id'], keep='first')
tracker_after_duplicates = len(tracker_df)
print(f"  [OK] Data setelah removing duplicates: {tracker_after_duplicates} rows")

# 2.1.3 Remove Extreme Outliers
print("\n[2.1.3.A] Identifikasi Extreme Outliers (Tracker):")

# Extract query length as numeric feature
tracker_df['query_length'] = tracker_df['query_info'].str.len()

# Find outliers using IQR
Q1 = tracker_df['query_length'].quantile(0.25)
Q3 = tracker_df['query_length'].quantile(0.75)
IQR = Q3 - Q1
lower_bound = Q1 - 1.5 * IQR
upper_bound = Q3 + 1.5 * IQR

print(f"  Query length - Q1: {Q1}, Q3: {Q3}, IQR: {IQR}")
print(f"  Bounds: [{lower_bound:.0f}, {upper_bound:.0f}]")

outlier_rows = tracker_df[(tracker_df['query_length'] < lower_bound) | (tracker_df['query_length'] > upper_bound)]
outlier_count = len(outlier_rows)
print(f"  Extreme outliers found: {outlier_count}")

tracker_df = tracker_df[(tracker_df['query_length'] >= lower_bound) & (tracker_df['query_length'] <= upper_bound)]
tracker_after_outliers = len(tracker_df)
print(f"  [OK] Data setelah removing outliers: {tracker_after_outliers} rows")

# Summary Tracker
print("\n" + "-"*60)
print("PREPROCESSING SUMMARY (TRACKER - LOG AKTIVITAS):")
print(f"  Data awal: {tracker_initial_count} rows")
print(f"  Missing values removed: {tracker_initial_count - tracker_after_missing} rows")
print(f"  Duplikasi removed: {tracker_after_missing - tracker_after_duplicates} rows")
print(f"  Outliers removed: {tracker_after_duplicates - tracker_after_outliers} rows")
print(f"  Data final: {tracker_after_outliers} rows ({tracker_after_outliers/tracker_initial_count*100:.1f}% retained)")
print("-"*60)

tracker_df.to_csv('data/cleaned/tracker_cleaned.csv', index=False)
print("\n[OK] Cleaned tracker data saved to data/cleaned/tracker_cleaned.csv")


# ========================================================
# PART 2: PREPROCESSING STAFF DATA (MASTER LOGIN)
# ========================================================
print("\n\n" + "="*60)
print("PART 2: PREPROCESSING STAFF DATA (MASTER LOGIN)")
print("="*60)

# Load raw staff data
staff_df = pd.read_csv('data/raw/staff_raw.csv')
staff_initial_count = len(staff_df)
print(f"\n[2.1.B] Data staff awal: {staff_initial_count} rows")

# 2.1.1 Remove Missing Values
print("\n[2.1.1.B] Cek Missing Values (Staff):")
missing_staff = staff_df.isnull().sum()
print(f"  Missing values per column:")
print(missing_staff)

missing_staff_rows = staff_df[staff_df[['user_id', 'date', 'timestamp', 'name']].isnull().any(axis=1)]
print(f"  Rows with missing critical data: {len(missing_staff_rows)}")

staff_df = staff_df[staff_df[['user_id', 'date', 'timestamp', 'name']].notna().all(axis=1)]
staff_after_missing = len(staff_df)
print(f"  [OK] Data setelah removing missing values: {staff_after_missing} rows")

# 2.1.2 Remove Duplicates
print("\n[2.1.2.B] Cek Duplikasi (Staff):")
duplicates_staff = staff_df[staff_df.duplicated(subset=['user_id', 'date', 'timestamp'], keep=False)]
duplicate_staff_count = len(duplicates_staff)
print(f"  Duplicate rows found: {duplicate_staff_count}")

staff_df = staff_df.drop_duplicates(subset=['user_id', 'date', 'timestamp'], keep='first')
staff_after_duplicates = len(staff_df)
print(f"  [OK] Data setelah removing duplicates: {staff_after_duplicates} rows")

# 2.1.3 Data Validation
print("\n[2.1.3.B] Validasi Data (Staff):")
print(f"  Unique users: {staff_df['user_id'].nunique()}")
print(f"  Date range: {staff_df['date'].min()} to {staff_df['date'].max()}")
print(f"  Sample users:")
print(staff_df[['user_id', 'name']].drop_duplicates().head(5))

# Summary Staff
print("\n" + "-"*60)
print("PREPROCESSING SUMMARY (STAFF - MASTER LOGIN):")
print(f"  Data awal: {staff_initial_count} rows")
print(f"  Missing values removed: {staff_initial_count - staff_after_missing} rows")
print(f"  Duplikasi removed: {staff_after_missing - staff_after_duplicates} rows")
print(f"  Data final: {staff_after_duplicates} rows ({staff_after_duplicates/staff_initial_count*100:.1f}% retained)")
print("-"*60)

staff_df.to_csv('data/cleaned/staff_cleaned.csv', index=False)
print("\n[OK] Cleaned staff data saved to data/cleaned/staff_cleaned.csv")


# ========================================================
# FINAL SUMMARY
# ========================================================
print("\n\n" + "="*60)
print("TAHAP 2 SELESAI - FINAL SUMMARY")
print("="*60)
print(f"\n1. TRACKER (LOG AKTIVITAS):")
print(f"   - File: data/cleaned/tracker_cleaned.csv")
print(f"   - Rows: {tracker_after_outliers} ({tracker_after_outliers/tracker_initial_count*100:.1f}% retained)")

print(f"\n2. STAFF (MASTER LOGIN):")
print(f"   - File: data/cleaned/staff_cleaned.csv")
print(f"   - Rows: {staff_after_duplicates} ({staff_after_duplicates/staff_initial_count*100:.1f}% retained)")

print("\n" + "="*60)
