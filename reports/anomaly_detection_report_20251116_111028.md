# 🔍 Laporan Deteksi Anomali
## LOF + K-Means Clustering Analysis

**Dataset:** Merged Dataset (Tracker + Staff)
**Tanggal:** 16 November 2025, 11:10:28
**Total Records:** 2,662

---

## 📊 Executive Summary

- **Total Records:** 2,662
- **Anomalies Detected:** 133 (5.00%)
- **Normal Data:** 2,529 (95.00%)
- **Clusters:** 10

---

## 🔬 Metodologi

### LOF (Local Outlier Factor)
- Optimal k-neighbors: 25
- Contamination: 5.0%
- Features: 14
- Anomalies: 133 (5.00%)

### K-Means Clustering
- Optimal k: 10
- Silhouette Score: 0.8385
- Inertia: 16.94

---

## 📈 Cluster Distribution

| Cluster | Label | Count | % |
|---------|-------|-------|---|
| 0 | Aktivitas Weekend - Frekuensi Rendah | 12 | 9.0% |
| 1 | Frekuensi Rendah - Anomali Kuat | 19 | 14.3% |
| 2 | Frekuensi Tinggi - Anomali Kuat | 12 | 9.0% |
| 3 | Frekuensi Rendah | 16 | 12.0% |
| 4 | Frekuensi Rendah | 13 | 9.8% |
| 5 | Frekuensi Rendah - Anomali Kuat | 22 | 16.5% |
| 6 | Frekuensi Tinggi - Anomali Kuat | 11 | 8.3% |
| 7 | Aktivitas Weekend - Frekuensi Tinggi - Anomali Kuat | 5 | 3.8% |
| 8 | Frekuensi Rendah | 12 | 9.0% |
| 9 | Frekuensi Rendah | 11 | 8.3% |

---

## 👤 Top 10 Users dengan Anomali Terbanyak

| Rank | User | Anomali | % |
|------|------|---------|---|
| 1 | User 1 | 51 | 38.3% |
| 2 | User 7 | 28 | 21.1% |
| 3 | User 8 | 20 | 15.0% |
| 4 | User 10 | 16 | 12.0% |
| 5 | User 5 | 11 | 8.3% |
| 6 | User 9 | 7 | 5.3% |

---

## 💡 Rekomendasi

### 🔴 High Priority
- User 1: 51 anomali - Investigasi segera
- Review anomali dengan LOF > 1e+09
- Verifikasi aktivitas weekend (Cluster 7)

### 🟡 Medium Priority
- Monitor Users: 1, 7, 8, 10, 5
- Setup alerting system

### 🔵 Low Priority
- Monthly model update
- Trend monitoring

---

**Generated:** 16 November 2025, 11:10:28
