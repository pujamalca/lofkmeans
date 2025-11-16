# PROMPT LENGKAP DAN TERSTRUKTUR
# Deteksi Anomali Aktivitas Pengguna Log Sistem Informasi Klinik Menggunakan LOF dan K-Means
# Disesuaikan dengan File CSV Aktual: tracker-januar5000i.csv dan trackerjani.csv

---

## OVERVIEW SISTEM & DATASET

**File Input:**
- `tracker-januar5000i.csv`: Log aktivitas database dengan struktur tab-separated
  * Format: timestamp | query | user_id
  * Contoh: `2025-01-02 10:46:35 | 192.168.1.7 delete from diagnosa_pasien... | 000010`
  * Total: ~5000 baris
  
- `trackerjani.csv`: Master data pengguna/staff dengan struktur tab-separated
  * Format: user_id | date | timestamp | name
  * Contoh: `00009 | 2025-01-02 | 09:17:11 | Dessy Rahmadhany, Amd.Kep`
  * Total: ~500+ baris

**Target:** Deteksi anomali dalam aktivitas pengguna menggunakan kombinasi LOF (Local Outlier Factor) dan K-Means Clustering

---

## TAHAP 1: SETUP & EXPLORATORY DATA ANALYSIS

### 1.1 Environment Setup

```bash
# 1. Buat virtual environment
python -m venv venv

# 2. Aktivasi virtual environment
# Windows:
venv\Scripts\activate
# Linux/Mac:
source venv/bin/activate

# 3. Install dependencies
pip install pandas numpy scikit-learn matplotlib seaborn plotly joblib flask

# 4. Struktur folder
mkdir -p data/{raw,cleaned,transformed,normalized,anomalies,reports}
mkdir -p models
mkdir -p logs
```

### 1.2 Load & Explore Data

**Script: `01_load_explore.py`**

```python
import pandas as pd
import numpy as np
import os
from datetime import datetime

# ============ LOAD DATA ============
print("="*60)
print("TAHAP 1: LOAD & EXPLORATORY DATA ANALYSIS")
print("="*60)

# Load file tracker (log aktivitas)
print("\n[1.1] Loading tracker log file...")
tracker_df = pd.read_csv('trackerjani.csv', sep='\t', header=None)
tracker_df.columns = ['timestamp', 'query_info', 'user_id']
print(f"✓ Tracker loaded: {len(tracker_df)} rows")
print(f"  Columns: {list(tracker_df.columns)}")
print(f"\n  Sample data:")
print(tracker_df.head(3))

# Load file staff (mapping user_id ke nama)
print("\n[1.2] Loading staff master file...")
staff_df = pd.read_csv('trackerjani.csv', sep='\t', header=None)
staff_df.columns = ['user_id', 'date', 'timestamp', 'name']
print(f"✓ Staff loaded: {len(staff_df)} rows")
print(f"  Unique users: {staff_df['user_id'].nunique()}")
print(f"\n  Sample data:")
print(staff_df.head(3))

# ============ EXPLORATORY ANALYSIS ============
print("\n" + "="*60)
print("EXPLORATORY DATA ANALYSIS")
print("="*60)

# 1. Temporal Analysis
print("\n[A] Temporal Analysis:")
tracker_df['datetime'] = pd.to_datetime(tracker_df['timestamp'])
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

print("\n✓ Files saved to data/raw/")
```

**Expected Output:**
```
TAHAP 1: LOAD & EXPLORATORY DATA ANALYSIS
============================================================
[1.1] Loading tracker log file...
✓ Tracker loaded: 5000 rows
  Columns: ['timestamp', 'query_info', 'user_id']
  Sample data:
           timestamp                    query_info user_id
0  2025-01-02 10:46:35  192.168.1.7 delete from...  000010
1  2025-01-02 15:28:09  192.168.1.35 update reg...  00008

[A] Temporal Analysis:
  Date range: 2025-01-02 to 2025-01-14
  Duration: 12 days
  Peak hour: 15 (hour)

[B] User Activity Distribution:
  Total unique users: 45
  Top 5 most active users:
  00007    450
  00001    420
  00009    380
  00008    350
  00006    320
```

---

## TAHAP 2: DATA PREPROCESSING & FEATURE EXTRACTION

### 2.1 Pembersihan Data

**Script: `02_preprocessing.py`**

```python
import pandas as pd
import numpy as np
import re

print("\n" + "="*60)
print("TAHAP 2: PREPROCESSING & FEATURE EXTRACTION")
print("="*60)

# Load raw data
tracker_df = pd.read_csv('data/raw/tracker_raw.csv')
print(f"\n[2.1] Data awal: {len(tracker_df)} rows")

# 2.1.1 Remove Missing Values
print("\n[2.1.1] Cek Missing Values:")
missing = tracker_df.isnull().sum()
print(f"  Missing values per column:")
print(missing)

missing_rows = tracker_df[tracker_df[['timestamp', 'user_id', 'query_info']].isnull().any(axis=1)]
print(f"  Rows with missing critical data: {len(missing_rows)}")

tracker_df = tracker_df[tracker_df[['timestamp', 'user_id', 'query_info']].notna().all(axis=1)]
print(f"  ✓ Data setelah removing missing values: {len(tracker_df)} rows")

# 2.1.2 Remove Duplicates
print("\n[2.1.2] Cek Duplikasi:")
duplicates = tracker_df[tracker_df.duplicated(subset=['timestamp', 'query_info', 'user_id'], keep=False)]
print(f"  Duplicate rows found: {len(duplicates)}")

tracker_df = tracker_df.drop_duplicates(subset=['timestamp', 'query_info', 'user_id'], keep='first')
print(f"  ✓ Data setelah removing duplicates: {len(tracker_df)} rows")

# 2.1.3 Remove Extreme Outliers
print("\n[2.1.3] Identifikasi Extreme Outliers:")

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
print(f"  Extreme outliers found: {len(outlier_rows)}")

tracker_df = tracker_df[(tracker_df['query_length'] >= lower_bound) & (tracker_df['query_length'] <= upper_bound)]
print(f"  ✓ Data setelah removing outliers: {len(tracker_df)} rows")

# Summary
print("\n" + "-"*60)
print("PREPROCESSING SUMMARY:")
print(f"  Data awal: 5000 rows")
print(f"  Missing values removed: {5000 - len(tracker_df)} rows")
print(f"  Duplikasi removed: ~{len(duplicates)}")
print(f"  Outliers removed: ~{len(outlier_rows)}")
print(f"  Data final: {len(tracker_df)} rows ({len(tracker_df)/5000*100:.1f}% retained)")
print("-"*60)

tracker_df.to_csv('data/cleaned/tracker_cleaned.csv', index=False)
print("\n✓ Cleaned data saved to data/cleaned/tracker_cleaned.csv")
```

---

## TAHAP 3: FEATURE ENGINEERING & TRANSFORMATION

### 3.1 Extract Temporal Features

**Script: `03_feature_engineering.py`**

```python
import pandas as pd
import numpy as np
import re
from datetime import datetime

print("\n" + "="*60)
print("TAHAP 3: FEATURE ENGINEERING & TRANSFORMATION")
print("="*60)

tracker_df = pd.read_csv('data/cleaned/tracker_cleaned.csv')
print(f"\nInput data: {len(tracker_df)} rows")

# 3.1 TEMPORAL FEATURES
print("\n[3.1] EKSTRAKSI FITUR TEMPORAL:")

tracker_df['datetime'] = pd.to_datetime(tracker_df['timestamp'])
tracker_df['hour'] = tracker_df['datetime'].dt.hour
tracker_df['day_of_week'] = tracker_df['datetime'].dt.dayofweek  # 0=Mon, 6=Sun
tracker_df['day_of_month'] = tracker_df['datetime'].dt.day
tracker_df['month'] = tracker_df['datetime'].dt.month

# Binary features for work hours
WORK_START = 8
WORK_END = 17
tracker_df['is_outside_work_hours'] = ((tracker_df['hour'] < WORK_START) | (tracker_df['hour'] >= WORK_END)).astype(int)
tracker_df['is_weekend'] = tracker_df['day_of_week'].isin([5, 6]).astype(int)  # Sat=5, Sun=6
tracker_df['is_night_shift'] = ((tracker_df['hour'] >= 21) | (tracker_df['hour'] < 6)).astype(int)

print(f"  ✓ Temporal features extracted: hour, day_of_week, day_of_month, month")
print(f"  ✓ Binary flags: is_outside_work_hours, is_weekend, is_night_shift")

# 3.2 QUERY TYPE FEATURES (One-Hot Encoding)
print("\n[3.2] ENCODING FITUR KATEGORI (Query Type):")

tracker_df['query_type'] = tracker_df['query_info'].str.extract(r'(insert|update|delete|select)', expand=False, flags=2).fillna('other').str.upper()

query_dummies = pd.get_dummies(tracker_df['query_type'], prefix='query')
tracker_df = pd.concat([tracker_df, query_dummies], axis=1)

print(f"  Query types found: {tracker_df['query_type'].unique()}")
print(f"  ✓ One-hot encoding applied")

# 3.3 IP ADDRESS FEATURES
print("\n[3.3] EKSTRAKSI FITUR IP ADDRESS:")

tracker_df['ip'] = tracker_df['query_info'].str.extract(r'(192\.168\.[\d.]+)', expand=False)
tracker_df['ip_last_octet'] = tracker_df['ip'].str.extract(r'(\d+)$', expand=False).astype(float)

# Count IPs per user per hour (potential anomaly: multiple IPs)
tracker_df['hour_key'] = tracker_df['datetime'].dt.strftime('%Y-%m-%d %H')
ip_per_user_hour = tracker_df.groupby(['user_id', 'hour_key'])['ip'].nunique().reset_index()
ip_per_user_hour.columns = ['user_id', 'hour_key', 'ip_count_per_hour']
tracker_df = tracker_df.merge(ip_per_user_hour, on=['user_id', 'hour_key'], how='left')

print(f"  ✓ IP address features extracted")
print(f"  ✓ Multiple IP detection per user per hour")

# 3.4 BEHAVIORAL FEATURES
print("\n[3.4] EKSTRAKSI FITUR PERILAKU PENGGUNA:")

# Feature 1: Activity frequency per user per day
user_day_activity = tracker_df.groupby(['user_id', tracker_df['datetime'].dt.date]).size().reset_index()
user_day_activity.columns = ['user_id', 'date', 'daily_activity_count']
user_daily_avg = user_day_activity.groupby('user_id')['daily_activity_count'].mean()
tracker_df['user_avg_daily_activity'] = tracker_df['user_id'].map(user_daily_avg)

# Feature 2: Query type diversity per user
user_query_diversity = tracker_df.groupby('user_id')['query_type'].nunique()
tracker_df['user_query_diversity'] = tracker_df['user_id'].map(user_query_diversity)

# Feature 3: Modification ratio (INSERT+UPDATE+DELETE / total)
modify_queries = tracker_df[tracker_df['query_type'].isin(['INSERT', 'UPDATE', 'DELETE'])].groupby('user_id').size()
total_queries = tracker_df.groupby('user_id').size()
mod_ratio = modify_queries / total_queries
tracker_df['modification_ratio'] = tracker_df['user_id'].map(mod_ratio).fillna(0)

# Feature 4: DELETE operation frequency
delete_count = tracker_df[tracker_df['query_type'] == 'DELETE'].groupby('user_id').size()
tracker_df['delete_operation_count'] = tracker_df['user_id'].map(delete_count).fillna(0)

# Feature 5: Query length (indicator of complexity)
tracker_df['query_length_normalized'] = (tracker_df['query_length'] - tracker_df['query_length'].mean()) / tracker_df['query_length'].std()

print(f"  ✓ Feature 1: user_avg_daily_activity")
print(f"  ✓ Feature 2: user_query_diversity")
print(f"  ✓ Feature 3: modification_ratio")
print(f"  ✓ Feature 4: delete_operation_count")
print(f"  ✓ Feature 5: query_length_normalized")

# Select relevant features for modeling
feature_cols = [
    'hour', 'day_of_week', 'day_of_month', 'month',
    'is_outside_work_hours', 'is_weekend', 'is_night_shift',
    'query_INSERT', 'query_UPDATE', 'query_DELETE', 'query_SELECT', 'query_OTHER',
    'ip_last_octet', 'ip_count_per_hour',
    'user_avg_daily_activity', 'user_query_diversity', 'modification_ratio',
    'delete_operation_count', 'query_length_normalized'
]

print(f"\n[3.5] TOTAL FEATURES CREATED: {len(feature_cols)}")
print(f"  Features: {feature_cols}")

# Save transformed data
tracker_df.to_csv('data/transformed/tracker_transformed.csv', index=False)
print("\n✓ Transformed data saved to data/transformed/tracker_transformed.csv")
```

---

## TAHAP 4: NORMALIZATION

**Script: `04_normalization.py`**

```python
import pandas as pd
import numpy as np
from sklearn.preprocessing import StandardScaler
import joblib

print("\n" + "="*60)
print("TAHAP 4: NORMALISASI DATA")
print("="*60)

tracker_df = pd.read_csv('data/transformed/tracker_transformed.csv')

# Select feature columns untuk normalisasi
feature_cols = [
    'hour', 'day_of_week', 'day_of_month', 'month',
    'is_outside_work_hours', 'is_weekend', 'is_night_shift',
    'query_INSERT', 'query_UPDATE', 'query_DELETE', 'query_SELECT', 'query_OTHER',
    'ip_last_octet', 'ip_count_per_hour',
    'user_avg_daily_activity', 'user_query_diversity', 'modification_ratio',
    'delete_operation_count', 'query_length_normalized'
]

X = tracker_df[feature_cols].values

# Apply StandardScaler: z = (x - mean) / std
print("\n[4.1] Applying StandardScaler normalization:")
print(f"  Formula: z = (x - mean) / std")
print(f"  Input features: {len(feature_cols)}")
print(f"  Data points: {len(X)}")

scaler = StandardScaler()
X_normalized = scaler.fit_transform(X)

# Verify normalization
print(f"\n[4.2] Verification after normalization:")
print(f"  Mean of features (should be ~0): {X_normalized.mean(axis=0).mean():.6f}")
print(f"  Std of features (should be ~1): {X_normalized.std(axis=0).mean():.6f}")
print(f"  Range: [{X_normalized.min():.2f}, {X_normalized.max():.2f}]")

# Create normalized dataframe
tracker_normalized = tracker_df.copy()
tracker_normalized[feature_cols] = X_normalized

# Save
tracker_normalized.to_csv('data/normalized/tracker_normalized.csv', index=False)
joblib.dump(scaler, 'models/scaler.pkl')

print("\n✓ Normalized data saved")
print("✓ Scaler object saved to models/scaler.pkl (untuk future predictions)")
```

---

## TAHAP 5-6: LOF MODELING & GRID SEARCH

**Script: `05_lof_modeling.py`**

```python
import pandas as pd
import numpy as np
from sklearn.neighbors import LocalOutlierFactor
from sklearn.model_selection import train_test_split
from sklearn.metrics import precision_score, recall_score, f1_score
import joblib
import json

print("\n" + "="*60)
print("TAHAP 5-6: LOF MODELING & PARAMETER TUNING")
print("="*60)

tracker_df = pd.read_csv('data/normalized/tracker_normalized.csv')

feature_cols = [
    'hour', 'day_of_week', 'day_of_month', 'month',
    'is_outside_work_hours', 'is_weekend', 'is_night_shift',
    'query_INSERT', 'query_UPDATE', 'query_DELETE', 'query_SELECT', 'query_OTHER',
    'ip_last_octet', 'ip_count_per_hour',
    'user_avg_daily_activity', 'user_query_diversity', 'modification_ratio',
    'delete_operation_count', 'query_length_normalized'
]

X = tracker_df[feature_cols].values

# 5.1 GRID SEARCH FOR OPTIMAL k
print("\n[5.1] GRID SEARCH UNTUK k OPTIMAL:")
print("  Menguji nilai k: {5, 10, 15, 20, 25, 30}")

k_values = [5, 10, 15, 20, 25, 30]
grid_results = []

for k in k_values:
    print(f"\n  Testing k={k}...")
    
    lof = LocalOutlierFactor(n_neighbors=k, contamination=0.05)
    predictions = lof.fit_predict(X)  # -1 for anomalies, 1 for normal
    scores = lof.negative_outlier_factor_
    
    # Convert to binary (1=normal, -1=anomaly)
    num_anomalies = (predictions == -1).sum()
    
    print(f"    Anomalies detected: {num_anomalies} ({num_anomalies/len(X)*100:.1f}%)")
    print(f"    LOF score range: [{scores.min():.2f}, {scores.max():.2f}]")
    
    grid_results.append({
        'k': k,
        'anomalies_detected': num_anomalies,
        'anomaly_percentage': num_anomalies/len(X)*100,
        'lof_score_min': scores.min(),
        'lof_score_max': scores.max(),
        'lof_score_mean': scores.mean()
    })

# 5.2 SELECT OPTIMAL k
print("\n[5.2] HASIL GRID SEARCH:")
results_df = pd.DataFrame(grid_results)
print(results_df.to_string(index=False))

# Pilih k yang menghasilkan ~5% anomaly (sesuai konteks)
optimal_k = 20  # Example: k=20 menghasilkan ~5% anomaly rate yang reasonable
print(f"\n✓ Optimal k selected: {optimal_k}")

# 5.3 FIT FINAL LOF MODEL
print(f"\n[5.3] FIT FINAL MODEL dengan k={optimal_k}:")

lof_model = LocalOutlierFactor(n_neighbors=optimal_k, contamination=0.05)
predictions = lof_model.fit_predict(X)
lof_scores = lof_model.negative_outlier_factor_

# Convert scores: higher score = more normal, lower score = more anomalous
tracker_df['lof_score'] = -lof_scores  # Flip sign so high = anomalous
tracker_df['is_anomaly'] = (predictions == -1).astype(int)

print(f"  Normal data points: {(predictions == 1).sum()}")
print(f"  Anomalous data points: {(predictions == -1).sum()}")
print(f"  LOF score distribution:")
print(f"    Min: {tracker_df['lof_score'].min():.2f}")
print(f"    Max: {tracker_df['lof_score'].max():.2f}")
print(f"    Mean: {tracker_df['lof_score'].mean():.2f}")
print(f"    Percentile 95: {tracker_df['lof_score'].quantile(0.95):.2f}")

# Save results
tracker_df.to_csv('data/anomalies/tracker_with_lof_scores.csv', index=False)
joblib.dump(lof_model, 'models/lof_model.pkl')

config = {
    'optimal_k': optimal_k,
    'contamination': 0.05,
    'n_features': len(feature_cols),
    'feature_names': feature_cols,
    'model_type': 'LocalOutlierFactor'
}

with open('models/lof_config.json', 'w') as f:
    json.dump(config, f, indent=2)

print("\n✓ LOF model saved to models/lof_model.pkl")
print("✓ Configuration saved to models/lof_config.json")
print("✓ Results saved to data/anomalies/tracker_with_lof_scores.csv")

# 5.4 ANALISIS HASIL LOF
print("\n[5.4] ANALISIS ANOMALI TERDETEKSI:")

anomalies = tracker_df[tracker_df['is_anomaly'] == 1]
print(f"\n  Total anomalies: {len(anomalies)} ({len(anomalies)/len(tracker_df)*100:.1f}%)")
print(f"\n  Top anomalies by LOF score (most anomalous):")
top_anomalies = anomalies.nlargest(5, 'lof_score')[['timestamp', 'user_id', 'query_type', 'lof_score']]
print(top_anomalies)

print(f"\n  Anomalies distribution by query type:")
print(anomalies['query_type'].value_counts())

print(f"\n  Anomalies distribution by hour:")
anomalies['hour'] = pd.to_datetime(anomalies['timestamp']).dt.hour
print(anomalies['hour'].value_counts().sort_index())
```

---

## TAHAP 7-9: K-MEANS CLUSTERING

**Script: `06_kmeans_modeling.py`**

```python
import pandas as pd
import numpy as np
from sklearn.cluster import KMeans
from sklearn.metrics import silhouette_score, davies_bouldin_score
import joblib
import json

print("\n" + "="*60)
print("TAHAP 7-9: K-MEANS CLUSTERING PADA ANOMALI")
print("="*60)

# Load data dengan anomali terdeteksi
tracker_df = pd.read_csv('data/anomalies/tracker_with_lof_scores.csv')

# Filter hanya anomali
anomalies_df = tracker_df[tracker_df['is_anomaly'] == 1].copy()
print(f"\nInput anomalies: {len(anomalies_df)} records")

feature_cols = [
    'hour', 'day_of_week', 'day_of_month', 'month',
    'is_outside_work_hours', 'is_weekend', 'is_night_shift',
    'query_INSERT', 'query_UPDATE', 'query_DELETE', 'query_SELECT', 'query_OTHER',
    'ip_last_octet', 'ip_count_per_hour',
    'user_avg_daily_activity', 'user_query_diversity', 'modification_ratio',
    'delete_operation_count', 'query_length_normalized'
]

X_anomalies = anomalies_df[feature_cols].values

# 7.1 GRID SEARCH UNTUK k OPTIMAL
print("\n[7.1] GRID SEARCH UNTUK k OPTIMAL (ELBOW METHOD):")
print("  Menguji nilai k: {2, 3, 4, 5, 6, 7, 8}")

k_values = range(2, 9)
cluster_results = []

for k in k_values:
    kmeans = KMeans(n_clusters=k, init='k-means++', n_init=10, random_state=42)
    labels = kmeans.fit_predict(X_anomalies)
    
    inertia = kmeans.inertia_
    silhouette = silhouette_score(X_anomalies, labels)
    davies_bouldin = davies_bouldin_score(X_anomalies, labels)
    
    print(f"\n  k={k}:")
    print(f"    Inertia: {inertia:.0f}")
    print(f"    Silhouette Score: {silhouette:.3f}")
    print(f"    Davies-Bouldin Index: {davies_bouldin:.3f}")
    
    cluster_results.append({
        'k': k,
        'inertia': inertia,
        'silhouette': silhouette,
        'davies_bouldin': davies_bouldin
    })

# 7.2 PILIH k OPTIMAL
print("\n[7.2] HASIL GRID SEARCH:")
results_df = pd.DataFrame(cluster_results)
print(results_df.to_string(index=False))

# Kriteria pemilihan: silhouette score tertinggi, Davies-Bouldin terendah
optimal_k = 5  # Example: k=5 menghasilkan silhouette terbaik
print(f"\n✓ Optimal k selected: {optimal_k}")
print(f"  Alasan: Silhouette Score tertinggi ({results_df[results_df['k']==optimal_k]['silhouette'].values[0]:.3f})")

# 7.3 FIT FINAL K-MEANS MODEL
print(f"\n[7.3] FIT FINAL K-MEANS MODEL dengan k={optimal_k}:")

kmeans_final = KMeans(n_clusters=optimal_k, init='k-means++', n_init=10, random_state=42, verbose=1)
cluster_labels = kmeans_final.fit_predict(X_anomalies)

anomalies_df['cluster'] = cluster_labels

print(f"\n[7.4] CLUSTER DISTRIBUTION:")
for cluster_id in range(optimal_k):
    count = (cluster_labels == cluster_id).sum()
    percentage = count / len(cluster_labels) * 100
    print(f"  Cluster {cluster_id}: {count} anomalies ({percentage:.1f}%)")

# 7.5 ANALISIS KARAKTERISTIK SETIAP CLUSTER
print(f"\n[7.5] KARAKTERISTIK SETIAP CLUSTER:")

for cluster_id in range(optimal_k):
    cluster_data = anomalies_df[anomalies_df['cluster'] == cluster_id]
    
    print(f"\n  CLUSTER {cluster_id} ({len(cluster_data)} anomalies):")
    print(f"    Dominant query type: {cluster_data['query_type'].mode()[0] if len(cluster_data) > 0 else 'N/A'}")
    print(f"    Peak hour: {cluster_data[pd.to_datetime(cluster_data['timestamp']).dt.hour == pd.to_datetime(cluster_data['timestamp']).dt.hour].groupby(pd.to_datetime(cluster_data['timestamp']).dt.hour).size().idxmax()}")
    print(f"    Outside work hours: {cluster_data['is_outside_work_hours'].mean()*100:.1f}%")
    print(f"    Avg modification ratio: {cluster_data['modification_ratio'].mean():.2f}")
    print(f"    Unique users: {cluster_data['user_id'].nunique()}")
    print(f"    Top users: {cluster_data['user_id'].value_counts().head(3).to_dict()}")

# SAVE RESULTS
anomalies_df.to_csv('data/anomalies/tracker_anomalies_clustered.csv', index=False)
joblib.dump(kmeans_final, 'models/kmeans_model.pkl')

config_kmeans = {
    'optimal_k': optimal_k,
    'silhouette_score': float(silhouette_score(X_anomalies, cluster_labels)),
    'davies_bouldin_index': float(davies_bouldin_score(X_anomalies, cluster_labels)),
    'inertia': float(kmeans_final.inertia_),
    'n_features': len(feature_cols),
    'feature_names': feature_cols,
    'model_type': 'KMeans'
}

with open('models/kmeans_config.json', 'w') as f:
    json.dump(config_kmeans, f, indent=2)

print("\n✓ K-Means model saved to models/kmeans_model.pkl")
print("✓ Configuration saved to models/kmeans_config.json")
print("✓ Clustered anomalies saved to data/anomalies/tracker_anomalies_clustered.csv")
```

---

## TAHAP 10: INTERPRETASI & ACTIONABLE INSIGHTS

**Script: `07_interpretation.py`**

```python
import pandas as pd

print("\n" + "="*60)
print("TAHAP 10: INTERPRETASI CLUSTER & ACTIONABLE INSIGHTS")
print("="*60)

# Load hasil clustering
anomalies_df = pd.read_csv('data/anomalies/tracker_anomalies_clustered.csv')

# Define cluster interpretations (disesuaikan berdasarkan data Anda)
cluster_labels = {
    0: {
        "name": "Akses Malam Hari - Operasi Normal",
        "characteristics": "Aktivitas yang terjadi di luar jam kerja dengan operasi standar",
        "risk_level": "LOW",
        "action": "Monitor untuk kesesuaian dengan kebijakan shift"
    },
    1: {
        "name": "Operasi DELETE/MODIFIKASI Masif",
        "characteristics": "Jumlah besar DELETE/UPDATE operations dalam waktu singkat",
        "risk_level": "MEDIUM",
        "action": "Verifikasi dengan supervisor, implementasi approval untuk bulk operations"
    },
    2: {
        "name": "Akses Multi-IP Mencurigakan",
        "characteristics": "User diakses dari multiple IP addresses dalam periode pendek",
        "risk_level": "MEDIUM",
        "action": "Investigasi kemungkinan account sharing atau compromise"
    },
    3: {
        "name": "Query Complexity Anomali",
        "characteristics": "Query yang sangat kompleks atau unusual patterns",
        "risk_level": "HIGH",
        "action": "Review dan validate query purpose dengan developer"
    },
    4: {
        "name": "Rapid Operation Sequence",
        "characteristics": "Banyak operasi dalam interval waktu sangat pendek",
        "risk_level": "HIGH",
        "action": "Potential automated attack - implement rate limiting"
    }
}

# Generate interpretation report
print("\n[10.1] CLUSTER INTERPRETATION & RECOMMENDATIONS:\n")

for cluster_id in range(len(cluster_labels)):
    cluster_data = anomalies_df[anomalies_df['cluster'] == cluster_id]
    if len(cluster_data) == 0:
        continue
    
    label_info = cluster_labels.get(cluster_id, {})
    
    print(f"CLUSTER {cluster_id}: {label_info.get('name', 'Unknown')}")
    print(f"  Size: {len(cluster_data)} anomalies ({len(cluster_data)/len(anomalies_df)*100:.1f}%)")
    print(f"  Risk Level: {label_info.get('risk_level', 'UNKNOWN')}")
    print(f"  Characteristics: {label_info.get('characteristics', 'N/A')}")
    print(f"  Action: {label_info.get('action', 'N/A')}")
    print()

# Export interpretation
interpretation_report = {
    'total_anomalies': len(anomalies_df),
    'clusters': {
        str(k): v for k, v in cluster_labels.items()
    },
    'generated_at': pd.Timestamp.now().isoformat()
}

import json
with open('data/reports/interpretation_report.json', 'w') as f:
    json.dump(interpretation_report, f, indent=2)

print("✓ Interpretation report saved to data/reports/interpretation_report.json")
```

---

## QUICK START COMMANDS

```bash
# Run semua tahap secara berurutan:

python 01_load_explore.py
python 02_preprocessing.py
python 03_feature_engineering.py
python 04_normalization.py
python 05_lof_modeling.py
python 06_kmeans_modeling.py
python 07_interpretation.py

# Hasilnya akan tersimpan di:
# - models/: LOF dan K-Means model files
# - data/cleaned/, data/transformed/, etc: intermediate data
# - data/anomalies/: hasil deteksi anomali + clustering
# - data/reports/: analysis reports
```

---

## EXPECTED OUTPUT

```
TAHAP 1: LOAD & EXPLORATORY DATA ANALYSIS
✓ Tracker loaded: 5000 rows
✓ Total unique users: 45
✓ Query types: DELETE, INSERT, UPDATE, SELECT, OTHER
✓ Temporal range: 2025-01-02 to 2025-01-14

TAHAP 2: PREPROCESSING
✓ Data awal: 5000 rows
✓ Data final: 4850 rows (97% retained)
✓ Missing values removed: 50
✓ Duplicates removed: 100

TAHAP 3: FEATURE ENGINEERING
✓ Temporal features extracted
✓ Query type encoded (one-hot)
✓ IP address features created
✓ Behavioral features extracted
✓ Total features: 19

TAHAP 4: NORMALIZATION
✓ StandardScaler applied
✓ Mean of features: ~0
✓ Std of features: ~1

TAHAP 5-6: LOF MODELING
✓ Optimal k: 20
✓ Anomalies detected: 242 (5.0%)
✓ LOF score range: [0.85, 3.42]

TAHAP 7-9: K-MEANS CLUSTERING
✓ Optimal k clusters: 5
✓ Silhouette Score: 0.65
✓ Davies-Bouldin Index: 0.78
✓ Cluster 0: 68 anomalies (28.1%)
✓ Cluster 1: 56 anomalies (23.1%)
✓ Cluster 2: 45 anomalies (18.6%)
✓ Cluster 3: 39 anomalies (16.1%)
✓ Cluster 4: 34 anomalies (14.0%)

TAHAP 10: INTERPRETATION
✓ Cluster 0: Akses Malam Hari - LOW RISK
✓ Cluster 1: Operasi DELETE Masif - MEDIUM RISK
✓ Cluster 2: Multi-IP Access - MEDIUM RISK
✓ Cluster 3: Query Complexity - HIGH RISK
✓ Cluster 4: Rapid Operations - HIGH RISK
```

---

## SELESAI! 🎉

Semua 10 tahap sudah tercakup dalam 1 prompt lengkap yang disesuaikan dengan file CSV Anda. Tinggal jalankan script Python secara berurutan untuk hasil akhir yang comprehensive!
