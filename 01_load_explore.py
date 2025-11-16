import pandas as pd
import numpy as np
import os
from datetime import datetime
import sys

# Set UTF-8 encoding for Windows console
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')

# ============ LOAD DATA ============
print("="*60)
print("TAHAP 1: LOAD & EXPLORATORY DATA ANALYSIS")
print("="*60)

# Load file tracker (log aktivitas)
print("\n[1.1] Loading tracker log file...")
tracker_df = pd.read_csv('tracker januar5000i.csv', sep='\t', header=None)
tracker_df.columns = ['timestamp', 'query_info', 'user_id']
print(f"[OK] Tracker loaded: {len(tracker_df)} rows")
print(f"  Columns: {list(tracker_df.columns)}")
print(f"\n  Sample data:")
print(tracker_df.head(3))

# Load file staff (mapping user_id ke nama)
print("\n[1.2] Loading staff master file...")
staff_df = pd.read_csv('trackerjani.csv', sep='\t', header=None)
staff_df.columns = ['user_id', 'date', 'timestamp', 'name']
print(f"[OK] Staff loaded: {len(staff_df)} rows")
print(f"  Unique users: {staff_df['user_id'].nunique()}")
print(f"\n  Sample data:")
print(staff_df.head(3))

# ============ EXPLORATORY ANALYSIS ============
print("\n" + "="*60)
print("EXPLORATORY DATA ANALYSIS")
print("="*60)

# 1. Temporal Analysis
print("\n[A] Temporal Analysis:")
tracker_df['datetime'] = pd.to_datetime(tracker_df['timestamp'], errors='coerce')
# Remove rows with invalid timestamps
invalid_timestamps = tracker_df['datetime'].isna().sum()
if invalid_timestamps > 0:
    print(f"  [WARNING] Found {invalid_timestamps} rows with invalid timestamps, removing them...")
    tracker_df = tracker_df[tracker_df['datetime'].notna()].copy()
print(f"  Date range: {tracker_df['datetime'].min()} to {tracker_df['datetime'].max()}")
print(f"  Duration: {(tracker_df['datetime'].max() - tracker_df['datetime'].min()).days} days")
print(f"  Peak hour: {tracker_df['datetime'].dt.hour.mode()[0]} (hour)")

# 2. User Activity Distribution
print("\n[B] User Activity Distribution:")
user_activity = tracker_df['user_id'].value_counts()
print(f"  Total unique users: {tracker_df['user_id'].nunique()}")
print(f"  Top 5 most active users:")
print(user_activity.head(5))

# 3. Query Type Analysis
print("\n[C] Query Type Analysis:")
tracker_df['query_type'] = tracker_df['query_info'].str.extract(r'(insert|update|delete|select)', expand=False, flags=2).fillna('other').str.upper()
print(f"  Query types detected:")
print(tracker_df['query_type'].value_counts())

# 4. IP Analysis
print("\n[D] IP Address Analysis:")
tracker_df['ip'] = tracker_df['query_info'].str.extract(r'(192\.168\.[\d.]+)', expand=False)
print(f"  Unique IPs: {tracker_df['ip'].nunique()}")
print(f"  Top 5 most used IPs:")
print(tracker_df['ip'].value_counts().head(5))

# Save for next step
tracker_df.to_csv('data/raw/tracker_raw.csv', index=False)
staff_df.to_csv('data/raw/staff_raw.csv', index=False)

print("\n[OK] Files saved to data/raw/")
