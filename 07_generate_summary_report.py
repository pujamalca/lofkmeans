import pandas as pd
import json
from datetime import datetime
from pathlib import Path
import sys

# Set UTF-8 encoding for Windows console
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')

print("\n" + "="*80)
print("GENERATE SUMMARY REPORT - LOF + K-MEANS ANOMALY DETECTION")
print("="*80)

# Load all necessary data
print("\n[1] Memuat data...")
merged_df = pd.read_csv('data/anomalies/merged_anomalies_clustered.csv')
anomalies_df = merged_df[merged_df['is_anomaly'] == 1]

with open('models/lof_config_merged.json', 'r') as f:
    lof_config = json.load(f)

with open('models/kmeans_config_merged.json', 'r') as f:
    kmeans_config = json.load(f)

with open('models/feature_info_merged.json', 'r') as f:
    feature_info = json.load(f)

print(f"  ✓ Data dimuat")
print(f"  Total records: {len(merged_df):,}")
print(f"  Total anomalies: {len(anomalies_df):,}")

# Generate HTML Report
report_html = f"""
<!DOCTYPE html>
<html lang="id">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Laporan Deteksi Anomali - LOF + K-Means</title>
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            line-height: 1.6;
            color: #333;
            background: #f5f5f5;
            padding: 20px;
        }}
        .container {{
            max-width: 1200px;
            margin: 0 auto;
            background: white;
            padding: 40px;
            box-shadow: 0 0 20px rgba(0,0,0,0.1);
        }}
        h1 {{
            color: #2c3e50;
            border-bottom: 4px solid #3498db;
            padding-bottom: 10px;
            margin-bottom: 30px;
        }}
        h2 {{
            color: #34495e;
            margin-top: 40px;
            margin-bottom: 20px;
            border-left: 5px solid #3498db;
            padding-left: 15px;
        }}
        h3 {{
            color: #7f8c8d;
            margin-top: 25px;
            margin-bottom: 15px;
        }}
        .metadata {{
            background: #ecf0f1;
            padding: 20px;
            border-radius: 8px;
            margin-bottom: 30px;
        }}
        .metadata p {{
            margin: 5px 0;
        }}
        .stats-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 20px;
            margin: 20px 0;
        }}
        .stat-card {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 20px;
            border-radius: 8px;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        }}
        .stat-card h4 {{
            font-size: 14px;
            opacity: 0.9;
            margin-bottom: 10px;
        }}
        .stat-card .value {{
            font-size: 32px;
            font-weight: bold;
        }}
        .stat-card.green {{ background: linear-gradient(135deg, #11998e 0%, #38ef7d 100%); }}
        .stat-card.orange {{ background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%); }}
        .stat-card.blue {{ background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%); }}
        table {{
            width: 100%;
            border-collapse: collapse;
            margin: 20px 0;
            background: white;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }}
        th {{
            background: #34495e;
            color: white;
            padding: 12px;
            text-align: left;
        }}
        td {{
            padding: 12px;
            border-bottom: 1px solid #ecf0f1;
        }}
        tr:hover {{
            background: #f8f9fa;
        }}
        .cluster-section {{
            background: #f8f9fa;
            padding: 20px;
            margin: 20px 0;
            border-radius: 8px;
            border-left: 4px solid #3498db;
        }}
        .alert {{
            padding: 15px;
            margin: 20px 0;
            border-radius: 5px;
            border-left: 4px solid;
        }}
        .alert.info {{
            background: #d1ecf1;
            border-color: #0c5460;
            color: #0c5460;
        }}
        .alert.warning {{
            background: #fff3cd;
            border-color: #856404;
            color: #856404;
        }}
        .alert.danger {{
            background: #f8d7da;
            border-color: #721c24;
            color: #721c24;
        }}
        .footer {{
            margin-top: 50px;
            padding-top: 20px;
            border-top: 2px solid #ecf0f1;
            text-align: center;
            color: #7f8c8d;
        }}
        ul {{
            margin: 10px 0 10px 30px;
        }}
        li {{
            margin: 8px 0;
        }}
    </style>
</head>
<body>
    <div class="container">
        <h1>🔍 Laporan Deteksi Anomali</h1>
        <p style="font-size: 18px; color: #7f8c8d; margin-bottom: 30px;">
            LOF (Local Outlier Factor) + K-Means Clustering Analysis
        </p>

        <div class="metadata">
            <p><strong>Dataset:</strong> Merged Dataset (Tracker + Staff)</p>
            <p><strong>Tanggal Generate:</strong> {datetime.now().strftime('%d %B %Y, %H:%M:%S')}</p>
            <p><strong>Total Records:</strong> {len(merged_df):,} baris</p>
            <p><strong>Periode Data:</strong> Januari 2025</p>
        </div>

        <h2>📊 Executive Summary</h2>

        <div class="stats-grid">
            <div class="stat-card blue">
                <h4>Total Records</h4>
                <div class="value">{len(merged_df):,}</div>
            </div>
            <div class="stat-card orange">
                <h4>Anomalies Detected</h4>
                <div class="value">{len(anomalies_df)}</div>
                <p style="font-size: 14px; margin-top: 5px;">({len(anomalies_df)/len(merged_df)*100:.2f}%)</p>
            </div>
            <div class="stat-card green">
                <h4>Normal Data</h4>
                <div class="value">{len(merged_df) - len(anomalies_df):,}</div>
                <p style="font-size: 14px; margin-top: 5px;">({(len(merged_df)-len(anomalies_df))/len(merged_df)*100:.2f}%)</p>
            </div>
            <div class="stat-card">
                <h4>Clusters Identified</h4>
                <div class="value">{kmeans_config['optimal_k']}</div>
            </div>
        </div>

        <div class="alert info">
            <strong>ℹ️ Key Finding:</strong> Dari {len(merged_df):,} record yang dianalisis, terdeteksi {len(anomalies_df)} anomali ({len(anomalies_df)/len(merged_df)*100:.2f}%) yang dikategorikan ke dalam {kmeans_config['optimal_k']} cluster berbeda berdasarkan pola perilaku mereka.
        </div>

        <h2>🔬 Metodologi</h2>

        <h3>1. Local Outlier Factor (LOF)</h3>
        <ul>
            <li><strong>Optimal k-neighbors:</strong> {lof_config['optimal_k']}</li>
            <li><strong>Contamination rate:</strong> {lof_config['contamination']*100}%</li>
            <li><strong>Features used:</strong> {lof_config['n_features']} fitur</li>
            <li><strong>Anomalies detected:</strong> {lof_config['final_anomalies_count']} ({lof_config['final_anomaly_percentage']:.2f}%)</li>
        </ul>

        <h3>2. K-Means Clustering</h3>
        <ul>
            <li><strong>Optimal clusters:</strong> {kmeans_config['optimal_k']} (berdasarkan Silhouette Score)</li>
            <li><strong>Silhouette Score:</strong> {kmeans_config['silhouette_score']:.4f} (excellent clustering)</li>
            <li><strong>Inertia:</strong> {kmeans_config['inertia']:.2f}</li>
            <li><strong>Method:</strong> Elbow Method + Silhouette Analysis</li>
        </ul>

        <h3>3. Features Engineered ({feature_info['n_features']} total)</h3>
        <table>
            <tr>
                <th>Category</th>
                <th>Features</th>
                <th>Description</th>
            </tr>
            <tr>
                <td><strong>Temporal (7)</strong></td>
                <td>hour, day_of_week, month, day_of_month, IsOutsideWorkHours, IsWeekend, NightShift</td>
                <td>Pola waktu akses</td>
            </tr>
            <tr>
                <td><strong>Categorical (2)</strong></td>
                <td>source_tracker, source_staff</td>
                <td>Asal dataset</td>
            </tr>
            <tr>
                <td><strong>Behavioral (5)</strong></td>
                <td>frekuensi_aktivitas_per_user, frekuensi_per_user_per_source, pola_waktu_akses, rasio_weekend_per_user, rasio_outside_hours_per_user</td>
                <td>Pola perilaku user</td>
            </tr>
        </table>

        <h2>📈 Hasil Clustering Anomali</h2>

        <table>
            <tr>
                <th>Cluster</th>
                <th>Label</th>
                <th>Jumlah</th>
                <th>Persentase</th>
                <th>Top User</th>
            </tr>
"""

# Add cluster details
for cluster_id in range(kmeans_config['optimal_k']):
    cluster_info = kmeans_config['cluster_interpretations'][str(cluster_id)]
    top_users = list(cluster_info['top_users'].keys())[:3]
    top_users_str = ", ".join([f"User {u}" for u in top_users])

    report_html += f"""
            <tr>
                <td><strong>Cluster {cluster_id}</strong></td>
                <td>{cluster_info['label']}</td>
                <td>{cluster_info['count']}</td>
                <td>{cluster_info['percentage']:.1f}%</td>
                <td>{top_users_str}</td>
            </tr>
"""

report_html += """
        </table>

        <h2>🎯 Analisis Per Cluster</h2>
"""

# Detailed cluster analysis
for cluster_id in range(kmeans_config['optimal_k']):
    cluster_info = kmeans_config['cluster_interpretations'][str(cluster_id)]
    cluster_data = anomalies_df[anomalies_df['cluster'] == cluster_id]

    report_html += f"""
        <div class="cluster-section">
            <h3>Cluster {cluster_id}: {cluster_info['label']}</h3>
            <p><strong>Jumlah Anomali:</strong> {cluster_info['count']} ({cluster_info['percentage']:.1f}%)</p>

            <h4>Karakteristik:</h4>
            <ul>
                <li><strong>Rata-rata jam akses:</strong> {cluster_info['avg_hour']:.1f}</li>
                <li><strong>Aktivitas weekend:</strong> {cluster_info['weekend_pct']:.1f}%</li>
                <li><strong>Di luar jam kerja:</strong> {cluster_info['outside_hours_pct']:.1f}%</li>
                <li><strong>Frekuensi aktivitas (normalized):</strong> {cluster_info['avg_frequency']:.2f}</li>
                <li><strong>LOF Score rata-rata:</strong> {cluster_info['avg_lof_score']:.2e}</li>
            </ul>

            <h4>Top Users:</h4>
            <ul>
"""
    for user_id, count in cluster_info['top_users'].items():
        report_html += f"                <li>User {user_id}: {count} anomali</li>\n"

    # Top 3 anomalies in this cluster
    top_3 = cluster_data.nlargest(3, 'lof_score')
    report_html += """
            </ul>

            <h4>Top 3 Anomali (LOF Score):</h4>
            <table>
                <tr>
                    <th>User</th>
                    <th>Timestamp</th>
                    <th>LOF Score</th>
                </tr>
"""
    for idx, row in top_3.iterrows():
        report_html += f"""
                <tr>
                    <td>User {row['user_id']}</td>
                    <td>{row['timestamp'][:19]}</td>
                    <td>{row['lof_score']:.2e}</td>
                </tr>
"""

    report_html += """
            </table>
        </div>
"""

# Top anomalies overall
top_anomalies = anomalies_df.nlargest(20, 'lof_score')

report_html += """
        <h2>🚨 Top 20 Anomali dengan LOF Score Tertinggi</h2>

        <div class="alert warning">
            <strong>⚠️ Perhatian:</strong> Anomali dengan LOF score tinggi menunjukkan pola perilaku yang sangat berbeda dari mayoritas user dan memerlukan investigasi lebih lanjut.
        </div>

        <table>
            <tr>
                <th>#</th>
                <th>User ID</th>
                <th>Timestamp</th>
                <th>LOF Score</th>
                <th>Cluster</th>
                <th>Source</th>
            </tr>
"""

for i, (idx, row) in enumerate(top_anomalies.iterrows(), 1):
    cluster_label = kmeans_config['cluster_interpretations'][str(int(row['cluster']))]['label']
    report_html += f"""
            <tr>
                <td>{i}</td>
                <td>User {row['user_id']}</td>
                <td>{row['timestamp'][:19]}</td>
                <td>{row['lof_score']:.2e}</td>
                <td>C{int(row['cluster'])}: {cluster_label[:30]}...</td>
                <td>{row['dataset_source']}</td>
            </tr>
"""

# User-wise summary
user_anomaly_counts = anomalies_df['user_id'].value_counts().head(10)

report_html += f"""
        </table>

        <h2>👤 Top 10 Users dengan Anomali Terbanyak</h2>

        <table>
            <tr>
                <th>Rank</th>
                <th>User ID</th>
                <th>Total Anomali</th>
                <th>Persentase dari Total Anomali</th>
                <th>Primary Clusters</th>
            </tr>
"""

for rank, (user_id, count) in enumerate(user_anomaly_counts.items(), 1):
    pct = (count / len(anomalies_df)) * 100
    user_clusters = anomalies_df[anomalies_df['user_id'] == user_id]['cluster'].value_counts().head(3)
    clusters_str = ", ".join([f"C{int(c)}" for c in user_clusters.index])

    report_html += f"""
            <tr>
                <td>{rank}</td>
                <td><strong>User {user_id}</strong></td>
                <td>{count}</td>
                <td>{pct:.1f}%</td>
                <td>{clusters_str}</td>
            </tr>
"""

report_html += f"""
        </table>

        <h2>💡 Rekomendasi & Action Items</h2>

        <div class="alert danger">
            <h4>🔴 High Priority (Immediate Action Required)</h4>
            <ul>
                <li><strong>User {user_anomaly_counts.index[0]}</strong>: {user_anomaly_counts.iloc[0]} anomali terdeteksi ({user_anomaly_counts.iloc[0]/len(anomalies_df)*100:.1f}% dari total). Investigasi mendalam diperlukan.</li>
                <li><strong>Cluster 7</strong>: Aktivitas weekend dengan frekuensi tinggi - verifikasi apakah legitimate atau unauthorized access.</li>
                <li>Review semua anomali dengan LOF score > 1e+09 (20 teratas)</li>
            </ul>
        </div>

        <div class="alert warning">
            <h4>🟡 Medium Priority (Action Within 7 Days)</h4>
            <ul>
                <li>Setup monitoring untuk Users: {', '.join([str(int(u)) for u in user_anomaly_counts.index[:5]])}</li>
                <li>Review access patterns di Cluster 0, 5, dan 6</li>
                <li>Implement alerting system untuk anomali real-time</li>
            </ul>
        </div>

        <div class="alert info">
            <h4>🔵 Low Priority (Continuous Monitoring)</h4>
            <ul>
                <li>Monitor trend anomali bulanan</li>
                <li>Update model dengan data baru setiap bulan</li>
                <li>Review false positives dan adjust contamination rate jika diperlukan</li>
            </ul>
        </div>

        <h2>📋 Kesimpulan</h2>

        <p>Analisis LOF + K-Means berhasil mengidentifikasi <strong>{len(anomalies_df)} anomali</strong> dari {len(merged_df):,} records ({len(anomalies_df)/len(merged_df)*100:.2f}%) yang dikelompokkan ke dalam <strong>{kmeans_config['optimal_k']} cluster</strong> dengan karakteristik yang berbeda.</p>

        <p><strong>Key Findings:</strong></p>
        <ul>
            <li>Silhouette Score {kmeans_config['silhouette_score']:.4f} menunjukkan clustering quality yang excellent</li>
            <li>User {user_anomaly_counts.index[0]} memiliki anomali terbanyak ({user_anomaly_counts.iloc[0]} kasus)</li>
            <li>{len(anomalies_df[anomalies_df['IsWeekend']==1])} anomali terjadi di weekend</li>
            <li>Cluster terbesar: Cluster {max(kmeans_config['cluster_distribution'], key=kmeans_config['cluster_distribution'].get)} dengan {max(kmeans_config['cluster_distribution'].values())} anomali</li>
        </ul>

        <p><strong>Next Steps:</strong></p>
        <ol>
            <li>Investigasi immediate untuk high-priority anomalies</li>
            <li>Setup automated monitoring dan alerting</li>
            <li>Regular review (weekly) untuk trend analysis</li>
            <li>Update model dengan data baru secara periodik</li>
        </ol>

        <div class="footer">
            <p>Generated by LOF + K-Means Anomaly Detection System</p>
            <p>Report Date: {datetime.now().strftime('%d %B %Y, %H:%M:%S')}</p>
            <p>© 2025 Anomaly Detection Pipeline</p>
        </div>
    </div>
</body>
</html>
"""

# Save HTML report
output_path = Path('reports')
output_path.mkdir(exist_ok=True)

html_file = output_path / f'anomaly_detection_report_{datetime.now().strftime("%Y%m%d_%H%M%S")}.html'
with open(html_file, 'w', encoding='utf-8') as f:
    f.write(report_html)

print(f"\n[2] HTML Report generated:")
print(f"  ✓ {html_file}")

# Also generate Markdown version for easy reading
md_content = f"""# 🔍 Laporan Deteksi Anomali
## LOF + K-Means Clustering Analysis

**Dataset:** Merged Dataset (Tracker + Staff)
**Tanggal:** {datetime.now().strftime('%d %B %Y, %H:%M:%S')}
**Total Records:** {len(merged_df):,}

---

## 📊 Executive Summary

- **Total Records:** {len(merged_df):,}
- **Anomalies Detected:** {len(anomalies_df)} ({len(anomalies_df)/len(merged_df)*100:.2f}%)
- **Normal Data:** {len(merged_df) - len(anomalies_df):,} ({(len(merged_df)-len(anomalies_df))/len(merged_df)*100:.2f}%)
- **Clusters:** {kmeans_config['optimal_k']}

---

## 🔬 Metodologi

### LOF (Local Outlier Factor)
- Optimal k-neighbors: {lof_config['optimal_k']}
- Contamination: {lof_config['contamination']*100}%
- Features: {lof_config['n_features']}
- Anomalies: {lof_config['final_anomalies_count']} ({lof_config['final_anomaly_percentage']:.2f}%)

### K-Means Clustering
- Optimal k: {kmeans_config['optimal_k']}
- Silhouette Score: {kmeans_config['silhouette_score']:.4f}
- Inertia: {kmeans_config['inertia']:.2f}

---

## 📈 Cluster Distribution

| Cluster | Label | Count | % |
|---------|-------|-------|---|
"""

for cluster_id in range(kmeans_config['optimal_k']):
    cluster_info = kmeans_config['cluster_interpretations'][str(cluster_id)]
    md_content += f"| {cluster_id} | {cluster_info['label']} | {cluster_info['count']} | {cluster_info['percentage']:.1f}% |\n"

md_content += f"""
---

## 👤 Top 10 Users dengan Anomali Terbanyak

| Rank | User | Anomali | % |
|------|------|---------|---|
"""

for rank, (user_id, count) in enumerate(user_anomaly_counts.items(), 1):
    pct = (count / len(anomalies_df)) * 100
    md_content += f"| {rank} | User {user_id} | {count} | {pct:.1f}% |\n"

md_content += f"""
---

## 💡 Rekomendasi

### 🔴 High Priority
- User {user_anomaly_counts.index[0]}: {user_anomaly_counts.iloc[0]} anomali - Investigasi segera
- Review anomali dengan LOF > 1e+09
- Verifikasi aktivitas weekend (Cluster 7)

### 🟡 Medium Priority
- Monitor Users: {', '.join([str(int(u)) for u in user_anomaly_counts.index[:5]])}
- Setup alerting system

### 🔵 Low Priority
- Monthly model update
- Trend monitoring

---

**Generated:** {datetime.now().strftime('%d %B %Y, %H:%M:%S')}
"""

md_file = output_path / f'anomaly_detection_report_{datetime.now().strftime("%Y%m%d_%H%M%S")}.md'
with open(md_file, 'w', encoding='utf-8') as f:
    f.write(md_content)

print(f"\n[3] Markdown Report generated:")
print(f"  ✓ {md_file}")

print("\n" + "="*80)
print("SUMMARY REPORT GENERATION COMPLETE")
print("="*80)
print(f"\nReports saved to:")
print(f"  - {html_file}")
print(f"  - {md_file}")
print(f"\nBuka HTML report di browser untuk visualisasi lengkap!")
print("="*80 + "\n")
