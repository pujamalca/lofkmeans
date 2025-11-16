import pandas as pd
import sys

# Set UTF-8 encoding for Windows console
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')

# Load data
tracker = pd.read_csv('data/anomalies/tracker_with_lof_scores.csv')
staff = pd.read_csv('data/anomalies/staff_with_lof_scores.csv')

print("\n" + "="*70)
print("HASIL TAHAP 5-6: LOF ANOMALY DETECTION")
print("="*70)

# TRACKER SUMMARY
print("\n1. TRACKER (LOG AKTIVITAS):")
print(f"   Total records: {len(tracker):,}")
print(f"   Anomalies: {tracker['is_anomaly'].sum()} ({tracker['is_anomaly'].sum()/len(tracker)*100:.2f}%)")
print(f"   Normal: {(~tracker['is_anomaly'].astype(bool)).sum()} ({(~tracker['is_anomaly'].astype(bool)).sum()/len(tracker)*100:.2f}%)")
print(f"   Optimal k (neighbors): 5")
print(f"   Contamination: 5%")

print("\n   Distribusi Anomali per User (Top 10):")
print("   " + "-"*56)
anomaly_by_user = tracker[tracker['is_anomaly']==1].groupby('user_id').size().sort_values(ascending=False).head(10)
for user, count in anomaly_by_user.items():
    pct = count/tracker['is_anomaly'].sum()*100
    print(f"   User ID {user:>3}: {count:>3} anomali ({pct:>5.2f}%)")

print("\n   Contoh 5 Anomali Tertinggi (LOF Score):")
print("   " + "-"*56)
top_anomalies = tracker[tracker['is_anomaly']==1].nlargest(5, 'lof_score')
for idx, row in top_anomalies.iterrows():
    print(f"   - User: {row['user_id']} | {row['timestamp']}")
    query_preview = str(row['query_type'])[:40] if pd.notna(row['query_type']) else 'N/A'
    print(f"     LOF Score: {row['lof_score']:.2e} | Query: {query_preview}")

# STAFF SUMMARY
print("\n2. STAFF (MASTER LOGIN):")
print(f"   Total records: {len(staff):,}")
print(f"   Anomalies: {staff['is_anomaly'].sum()} ({staff['is_anomaly'].sum()/len(staff)*100:.2f}%)")
print(f"   Normal: {(~staff['is_anomaly'].astype(bool)).sum()} ({(~staff['is_anomaly'].astype(bool)).sum()/len(staff)*100:.2f}%)")
print(f"   Optimal k (neighbors): 5")
print(f"   Contamination: 5%")

print("\n   Distribusi Anomali per User (Top 10):")
print("   " + "-"*56)
anomaly_by_user = staff[staff['is_anomaly']==1].groupby('user_id').size().sort_values(ascending=False).head(10)
for user, count in anomaly_by_user.items():
    name = staff[staff['user_id']==user]['name'].iloc[0]
    pct = count/staff['is_anomaly'].sum()*100
    print(f"   User {user:>2} ({name:<25}): {count:>2} anomali ({pct:>5.2f}%)")

print("\n   Contoh 5 Anomali Tertinggi (LOF Score):")
print("   " + "-"*56)
top_anomalies = staff[staff['is_anomaly']==1].nlargest(5, 'lof_score')
for idx, row in top_anomalies.iterrows():
    print(f"   - User {row['user_id']} ({row['name']})")
    print(f"     {row['timestamp']} | LOF Score: {row['lof_score']:.2e}")

# FILES GENERATED
print("\n" + "="*70)
print("FILE YANG DIHASILKAN:")
print("="*70)
print("\nTRACKER:")
print("  - data/anomalies/tracker_with_lof_scores.csv")
print("  - models/lof_model_tracker.pkl")
print("  - models/lof_config_tracker.json")

print("\nSTAFF:")
print("  - data/anomalies/staff_with_lof_scores.csv")
print("  - models/lof_model_staff.pkl")
print("  - models/lof_config_staff.json")

print("\n" + "="*70)
