# 🚀 Quick Start Guide - LOF + K-Means Pipeline (New UI)

## ⚡ 3 Langkah Memulai

### 1️⃣ Install Dependencies

```bash
pip install -r requirements.txt
```

### 2️⃣ Jalankan Pipeline (jika belum)

```bash
python 01_load_explore.py
python 02_preprocessing.py
python 03_feature_engineering.py
python 04_normalization.py
python 05_lof_modeling.py
python 06_kmeans_modeling.py
python 07_interpretation.py
```

### 3️⃣ Jalankan Streamlit App

```bash
streamlit run app.py
```

Buka browser di: `http://localhost:8501`

---

## 🎯 Apa yang Baru?

### ✨ Tampilan Modern
- **Tailwind CSS** styling
- **Inter font** family
- **Gradient backgrounds**
- **Smooth animations**

### 📊 Progress Tracker
```
●━━━━●━━━━●━━━━●━━━━●━━━━●━━━━●
01   02   03   04   05   06   07
Load Prep Feat Norm LOF KMeans Result
```

### 🔄 Unified Interface
**Sebelumnya:** Tracker dan Staff terpisah
**Sekarang:** Digabung dalam 1 aplikasi, pilih dari dropdown!

### 🎨 Custom Components
- **Metric Cards** - Color-coded dengan gradient
- **Alert Boxes** - Info, success, warning, danger
- **Progress Stepper** - Visual timeline
- **Interactive Charts** - Plotly visualizations

---

## 📱 Navigation

### Main Navigation
- **Next Button (▶)** - Lanjut ke stage berikutnya
- **Back Button (◀)** - Kembali ke stage sebelumnya
- **Start Over (🔄)** - Mulai dari awal

### Sidebar Quick Jump
Klik stage manapun untuk langsung jump:
- ✅ Completed stages
- ▶ Current stage
- ⭕ Pending stages

---

## 🎨 Color Meanings

| Color | Meaning | Usage |
|-------|---------|-------|
| 🔵 Blue | Primary/Info | Main actions, general info |
| 🟢 Green | Success/Good | Completed, optimal values |
| 🟡 Yellow | Warning/Caution | Needs attention |
| 🔴 Red | Danger/Anomaly | Errors, anomalies detected |
| 🟣 Purple | Highlight | Special metrics |

---

## 💡 Tips

1. **Pilih dataset di Stage 01** - Tracker atau Staff
2. **Navigate sequentially** - Ikuti flow 01 → 07
3. **Use sidebar** - Untuk jump ke completed stages
4. **Export di Stage 07** - Download CSV/JSON/Report
5. **Check metrics** - Color-coded untuk quick insights

---

## 🔍 What to Look For

### Stage 05 - LOF Detection
**Target:** Anomaly rate ~5%
- 🟢 Green jika 4-6%
- 🟡 Yellow jika diluar range

### Stage 06 - K-Means Clustering
**Silhouette Score:**
- 🟢 Green jika > 0.3
- 🟡 Yellow jika < 0.3

**Davies-Bouldin Index:**
- 🟢 Green jika < 1.5
- 🟡 Yellow jika > 1.5

---

## 📥 Export Options (Stage 07)

1. **📥 Download CSV** - Full dataset dengan cluster assignments
2. **📥 Download JSON** - Structured data format
3. **📥 Download Report** - Summary report dengan config

---

## 🐛 Troubleshooting

**Q: Data tidak muncul?**
A: Pastikan pipeline scripts sudah dijalankan (step 2 di atas)

**Q: Error "Module not found"?**
A: Install dependencies: `pip install -r requirements.txt`

**Q: Tampilan tidak bagus?**
A: Clear browser cache atau gunakan Incognito mode

**Q: Stage tidak bisa di-click?**
A: Hanya completed stages yang bisa di-jump via sidebar

---

## 📚 Full Documentation

Lihat `README_NEW_UI.md` untuk dokumentasi lengkap:
- Detailed feature list
- Design system
- Customization guide
- Advanced usage

---

**Happy analyzing! 🎉**
