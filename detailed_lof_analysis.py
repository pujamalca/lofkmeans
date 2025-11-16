import pandas as pd
import numpy as np
import json
import sys

# Set UTF-8 encoding for Windows console
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')

print("\n" + "="*80)
print("ANALISIS LENGKAP TAHAP 5-6: LOF ANOMALY DETECTION")
print("="*80)

# Load configuration files
with open('models/lof_config_tracker.json', 'r') as f:
    tracker_config = json.load(f)

with open('models/lof_config_staff.json', 'r') as f:
    staff_config = json.load(f)

# Load anomaly data
tracker = pd.read_csv('data/anomalies/tracker_with_lof_scores.csv')
staff = pd.read_csv('data/anomalies/staff_with_lof_scores.csv')

print("\n" + "="*80)
print("BAGIAN 1: PROSES GRID SEARCH UNTUK PARAMETER OPTIMAL")
print("="*80)

print("\n[A] TRACKER - Grid Search k-neighbors:")
print("-" * 80)
print(f"{'k':<5} {'Anomalies':<12} {'Percentage':<12} {'LOF Min':<20} {'LOF Mean':<20}")
print("-" * 80)
for result in tracker_config['grid_search_results']:
    print(f"{result['k']:<5} {result['anomalies_detected']:<12} {result['anomaly_percentage']:<12.2f} "
          f"{result['lof_score_min']:<20.2e} {result['lof_score_mean']:<20.2e}")
print("-" * 80)
print(f"✓ OPTIMAL: k={tracker_config['optimal_k']} dipilih karena paling mendekati contamination 5%")
print(f"  Hasil: {tracker_config['final_anomalies_count']} anomalies ({tracker_config['final_anomaly_percentage']:.2f}%)")

print("\n[B] STAFF - Grid Search k-neighbors:")
print("-" * 80)
print(f"{'k':<5} {'Anomalies':<12} {'Percentage':<12} {'LOF Min':<20} {'LOF Mean':<20}")
print("-" * 80)
for result in staff_config['grid_search_results']:
    print(f"{result['k']:<5} {result['anomalies_detected']:<12} {result['anomaly_percentage']:<12.2f} "
          f"{result['lof_score_min']:<20.2e} {result['lof_score_mean']:<20.2e}")
print("-" * 80)
print(f"✓ OPTIMAL: k={staff_config['optimal_k']} dipilih karena paling mendekati contamination 5%")
print(f"  Hasil: {staff_config['final_anomalies_count']} anomalies ({staff_config['final_anomaly_percentage']:.2f}%)")

print("\n" + "="*80)
print("BAGIAN 2: FITUR YANG DIGUNAKAN DALAM MODEL")
print("="*80)

print("\n[A] TRACKER - 14 Fitur:")
print("-" * 80)
for i, feature in enumerate(tracker_config['feature_names'], 1):
    print(f"  {i:>2}. {feature}")
print("\nKategori:")
print("  - Temporal (7): hour, day_of_week, month, day_of_month, IsOutsideWorkHours, IsWeekend, NightShift")
print("  - Operasi (3): op_DELETE, op_INSERT, op_UPDATE")
print("  - Behavioral (4): frekuensi, tipe operasi, rasio modifikasi, pola waktu")

print("\n[B] STAFF - 11 Fitur:")
print("-" * 80)
for i, feature in enumerate(staff_config['feature_names'], 1):
    print(f"  {i:>2}. {feature}")
print("\nKategori:")
print("  - Temporal (8): hour, day_of_week, month, day_of_month, IsEarlyLogin, IsLateLogin, IsAfterWorkHours, IsWeekend")
print("  - Behavioral (3): frekuensi login, pola waktu, rasio weekend")

print("\n" + "="*80)
print("BAGIAN 3: STATISTIK LOF SCORE")
print("="*80)

# Tracker LOF statistics
tracker_anomalies = tracker[tracker['is_anomaly']==1]
tracker_normal = tracker[tracker['is_anomaly']==0]

print("\n[A] TRACKER:")
print("-" * 80)
print(f"Total Data: {len(tracker):,} records")
print(f"\nANOMALI ({len(tracker_anomalies)} records - {len(tracker_anomalies)/len(tracker)*100:.2f}%):")
print(f"  LOF Score Min    : {tracker_anomalies['lof_score'].min():.4e}")
print(f"  LOF Score Max    : {tracker_anomalies['lof_score'].max():.4e}")
print(f"  LOF Score Mean   : {tracker_anomalies['lof_score'].mean():.4e}")
print(f"  LOF Score Median : {tracker_anomalies['lof_score'].median():.4e}")
print(f"  LOF Score Std    : {tracker_anomalies['lof_score'].std():.4e}")

print(f"\nNORMAL ({len(tracker_normal)} records - {len(tracker_normal)/len(tracker)*100:.2f}%):")
print(f"  LOF Score Min    : {tracker_normal['lof_score'].min():.4e}")
print(f"  LOF Score Max    : {tracker_normal['lof_score'].max():.4e}")
print(f"  LOF Score Mean   : {tracker_normal['lof_score'].mean():.4e}")
print(f"  LOF Score Median : {tracker_normal['lof_score'].median():.4e}")
print(f"  LOF Score Std    : {tracker_normal['lof_score'].std():.4e}")

# Staff LOF statistics
staff_anomalies = staff[staff['is_anomaly']==1]
staff_normal = staff[staff['is_anomaly']==0]

print("\n[B] STAFF:")
print("-" * 80)
print(f"Total Data: {len(staff):,} records")
print(f"\nANOMALI ({len(staff_anomalies)} records - {len(staff_anomalies)/len(staff)*100:.2f}%):")
print(f"  LOF Score Min    : {staff_anomalies['lof_score'].min():.4e}")
print(f"  LOF Score Max    : {staff_anomalies['lof_score'].max():.4e}")
print(f"  LOF Score Mean   : {staff_anomalies['lof_score'].mean():.4e}")
print(f"  LOF Score Median : {staff_anomalies['lof_score'].median():.4e}")
print(f"  LOF Score Std    : {staff_anomalies['lof_score'].std():.4e}")

print(f"\nNORMAL ({len(staff_normal)} records - {len(staff_normal)/len(staff)*100:.2f}%):")
print(f"  LOF Score Min    : {staff_normal['lof_score'].min():.4e}")
print(f"  LOF Score Max    : {staff_normal['lof_score'].max():.4e}")
print(f"  LOF Score Mean   : {staff_normal['lof_score'].mean():.4e}")
print(f"  LOF Score Median : {staff_normal['lof_score'].median():.4e}")
print(f"  LOF Score Std    : {staff_normal['lof_score'].std():.4e}")

print("\n" + "="*80)
print("BAGIAN 4: DISTRIBUSI ANOMALI PER USER")
print("="*80)

print("\n[A] TRACKER - Top 10 User dengan Anomali Terbanyak:")
print("-" * 80)
print(f"{'User ID':<10} {'Anomali':<10} {'% dari Total Anomali':<25} {'% dari Aktivitas User':<25}")
print("-" * 80)
anomaly_by_user = tracker[tracker['is_anomaly']==1].groupby('user_id').size().sort_values(ascending=False).head(10)
for user, count in anomaly_by_user.items():
    pct_of_anomalies = count/len(tracker_anomalies)*100
    total_user_activities = len(tracker[tracker['user_id']==user])
    pct_of_user = count/total_user_activities*100
    print(f"{user:<10} {count:<10} {pct_of_anomalies:<25.2f} {pct_of_user:<25.2f}")

print("\n[B] STAFF - Top 10 User dengan Anomali Terbanyak:")
print("-" * 80)
print(f"{'User':<6} {'Nama':<30} {'Anomali':<10} {'% Anomali':<12} {'% User':<12}")
print("-" * 80)
anomaly_by_user = staff[staff['is_anomaly']==1].groupby('user_id').size().sort_values(ascending=False).head(10)
for user, count in anomaly_by_user.items():
    name = staff[staff['user_id']==user]['name'].iloc[0]
    pct_of_anomalies = count/len(staff_anomalies)*100
    total_user_logins = len(staff[staff['user_id']==user])
    pct_of_user = count/total_user_logins*100
    print(f"{user:<6} {name:<30} {count:<10} {pct_of_anomalies:<12.2f} {pct_of_user:<12.2f}")

print("\n" + "="*80)
print("BAGIAN 5: CONTOH ANOMALI DENGAN LOF SCORE TERTINGGI")
print("="*80)

print("\n[A] TRACKER - 10 Anomali Teratas:")
print("-" * 80)
top_anomalies = tracker[tracker['is_anomaly']==1].nlargest(10, 'lof_score')
for i, (idx, row) in enumerate(top_anomalies.iterrows(), 1):
    print(f"\n{i}. User: {row['user_id']} | Timestamp: {row['timestamp']}")
    print(f"   LOF Score: {row['lof_score']:.4e}")
    print(f"   Query Type: {row['query_type']}")
    print(f"   Hour: {row['hour']:.2f} | Day of Week: {row['day_of_week']:.2f}")
    print(f"   Frekuensi Aktivitas: {row['frekuensi_aktivitas_per_user']:.4f}")
    print(f"   Pola Waktu Akses: {row['pola_waktu_akses']:.4f}")

print("\n[B] STAFF - 10 Anomali Teratas:")
print("-" * 80)
top_anomalies = staff[staff['is_anomaly']==1].nlargest(10, 'lof_score')
for i, (idx, row) in enumerate(top_anomalies.iterrows(), 1):
    print(f"\n{i}. User {row['user_id']}: {row['name']}")
    print(f"   Timestamp: {row['timestamp']}")
    print(f"   LOF Score: {row['lof_score']:.4e}")
    print(f"   Hour: {row['hour']:.2f} | Day of Week: {row['day_of_week']:.2f}")
    print(f"   Frekuensi Login: {row['frekuensi_login_per_user']:.4f}")
    print(f"   Pola Waktu Login: {row['pola_waktu_login']:.4f}")
    print(f"   IsEarlyLogin: {row['IsEarlyLogin']} | IsLateLogin: {row['IsLateLogin']} | IsWeekend: {row['IsWeekend']}")

print("\n" + "="*80)
print("BAGIAN 6: INTERPRETASI LOF SCORE")
print("="*80)

print("""
LOF (Local Outlier Factor) Score Interpretation:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

• LOF Score ≈ -1.0 : Data point NORMAL (densitas lokal sama dengan neighbors)
• LOF Score < -1.0 : Semakin kecil (lebih negatif), semakin ANOMALI
• LOF Score < -10  : ANOMALI KUAT (sangat berbeda dari neighbors)
• LOF Score < -100 : ANOMALI EKSTREM (pola sangat tidak biasa)

Pada hasil ini:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

TRACKER:
  • Data Normal: LOF score berkisar -1.0 hingga -1.2 (perilaku standar)
  • Anomali: LOF score hingga -5.68e+10 (EKSTREM!)
  • Interpretasi: Ada aktivitas yang SANGAT berbeda dari pola umum
  • Kemungkinan: akses di waktu tidak biasa, tipe operasi jarang, atau frekuensi abnormal

STAFF:
  • Data Normal: LOF score berkisar -1.0 hingga -1.3 (perilaku login standar)
  • Anomali: LOF score hingga -9.31e+09 (EKSTREM!)
  • Interpretasi: Ada pola login yang SANGAT tidak biasa
  • Kemungkinan: login di jam aneh, frekuensi tinggi/rendah, atau pola waktu irregular
""")

print("\n" + "="*80)
print("BAGIAN 7: FILE OUTPUT YANG DIHASILKAN")
print("="*80)

print("""
TRACKER Files:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  1. data/anomalies/tracker_with_lof_scores.csv
     ├─ Berisi semua data tracker dengan kolom tambahan:
     │  ├─ lof_score: nilai LOF untuk setiap record
     │  └─ is_anomaly: flag 0/1 (normal/anomaly)
     ├─ Total: 4,684 baris
     └─ Ukuran: ~1.2 MB

  2. models/lof_model_tracker.pkl
     ├─ Model LOF yang sudah di-training
     ├─ Dapat digunakan untuk prediksi data baru
     └─ Parameters: k=5, contamination=0.05

  3. models/feature_info_tracker.json
     ├─ Metadata 14 fitur yang digunakan
     ├─ Scaler parameters (mean, scale, var)
     └─ Informasi untuk reproduksi preprocessing

  4. models/lof_config_tracker.json
     ├─ Konfigurasi lengkap model
     ├─ Hasil grid search semua k
     └─ Statistik anomali detection

STAFF Files:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  1. data/anomalies/staff_with_lof_scores.csv
     ├─ Berisi semua data staff dengan kolom tambahan
     ├─ Total: 810 baris
     └─ Kolom: lof_score, is_anomaly

  2. models/lof_model_staff.pkl
     └─ Model LOF (k=5, contamination=0.05)

  3. models/feature_info_staff.json
     └─ Metadata 11 fitur + scaler params

  4. models/lof_config_staff.json
     └─ Config + grid search results
""")

print("\n" + "="*80)
print("KESIMPULAN TAHAP 5-6")
print("="*80)

print(f"""
✓ LOF Modeling berhasil mendeteksi anomali dengan akurasi target (5%)
✓ Grid search menemukan k=5 sebagai parameter optimal untuk kedua dataset
✓ Anomali yang terdeteksi memiliki LOF score sangat tinggi (ekstrem)
✓ Distribusi anomali tidak merata - beberapa user mendominasi
✓ Total anomali terdeteksi:
  • TRACKER: 235 dari 4,684 ({235/4684*100:.2f}%)
  • STAFF: 41 dari 810 ({41/810*100:.2f}%)

SIAP untuk TAHAP 7-9: K-Means Clustering untuk kategorisasi anomali
""")

print("="*80 + "\n")
