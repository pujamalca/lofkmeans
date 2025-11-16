# 🔗 Dataset Merge Concept - Tracker + Staff

## Overview

Konsep merge Tracker + Staff menjadi satu dataset gabungan untuk diproses dalam satu pipeline.

---

## 🎯 Workflow Baru

### **Current Flow** (Terpisah):
```
Stage 01: Load Tracker  ──→  Process Tracker  ──→  Results Tracker
          Load Staff    ──→  Process Staff    ──→  Results Staff
```

### **New Flow** (Gabung):
```
Stage 01: Load Tracker + Load Staff
          ↓
Stage 02: Merge & Preprocessing
          ↓
Stage 03-07: Process Merged Dataset
          ↓
Results: Combined Analysis (dengan identifier dataset_source)
```

---

## 📦 Merge Function

### Function Definition

```python
def merge_datasets(df_tracker: pd.DataFrame, df_staff: pd.DataFrame) -> pd.DataFrame:
    """
    Merge tracker and staff datasets into one unified dataset

    Returns:
        Merged DataFrame dengan kolom 'dataset_source'
    """
```

### Merge Strategy

1. **Add Source Identifier**
   - Tracker data: `dataset_source = 'tracker'`
   - Staff data: `dataset_source = 'staff'`

2. **Find Common Columns**
   - Identify columns yang ada di KEDUA dataset
   - Required: `timestamp`, `user_id`
   - Optional: columns lain yang common

3. **Concatenate Data**
   - Keep only common columns
   - Add `dataset_source` column
   - Merge dengan `pd.concat()`

4. **Save Merged Data**
   - Output: `data/raw/merged_raw.csv`

---

## 📊 Example Data Structure

### Before Merge

**Tracker:**
```
| timestamp           | user_id | query_type | query_info    | ip_address     |
|---------------------|---------|------------|---------------|----------------|
| 2024-01-01 10:00:00 | user001 | SELECT     | SELECT * ...  | 192.168.1.100  |
| 2024-01-01 10:05:00 | user002 | INSERT     | INSERT INTO.. | 192.168.1.101  |
```

**Staff:**
```
| timestamp           | user_id | name      | date       |
|---------------------|---------|-----------|------------|
| 2024-01-01 08:00:00 | staff01 | John Doe  | 2024-01-01 |
| 2024-01-01 08:15:00 | staff02 | Jane Smith| 2024-01-01 |
```

### After Merge

**Merged:**
```
| timestamp           | user_id | dataset_source |
|---------------------|---------|----------------|
| 2024-01-01 10:00:00 | user001 | tracker        |
| 2024-01-01 10:05:00 | user002 | tracker        |
| 2024-01-01 08:00:00 | staff01 | staff          |
| 2024-01-01 08:15:00 | staff02 | staff          |
```

Note: Hanya common columns yang di-keep.

---

## 🔧 Implementation Steps

### Step 1: Load Both Datasets (Stage 01)

```python
# Load Tracker
df_tracker = load_data("data/raw/tracker_raw.csv")

# Load Staff
df_staff = load_data("data/raw/staff_raw.csv")

# Check both loaded
if df_tracker is not None and df_staff is not None:
    # Both ready for merge
    pass
```

### Step 2: Merge & Preprocess (Stage 02)

```python
# Merge datasets
df_merged = merge_datasets(df_tracker, df_staff)

# Preprocessing on merged data
df_cleaned = preprocess_data(df_merged)

# Save
df_cleaned.to_csv("data/cleaned/merged_cleaned.csv")
```

### Step 3: Feature Engineering (Stage 03)

```python
# Load merged cleaned data
df = load_data("data/cleaned/merged_cleaned.csv")

# Feature engineering untuk merged data
# Bisa tambah features berdasarkan dataset_source
df['is_tracker'] = (df['dataset_source'] == 'tracker').astype(int)
df['is_staff'] = (df['dataset_source'] == 'staff').astype(int)

# Continue dengan feature engineering normal
```

### Step 4: LOF & K-Means (Stage 05-06)

```python
# LOF pada merged data
lof = LocalOutlierFactor(...)
df['lof_score'] = lof.fit_predict(df_features)

# K-Means pada merged anomalies
# Dataset_source tetap di-keep untuk analysis
```

### Step 7: Results & Interpretation

```python
# Analysis berdasarkan dataset_source
tracker_anomalies = df[df['dataset_source'] == 'tracker']
staff_anomalies = df[df['dataset_source'] == 'staff']

# Comparison
print(f"Tracker anomalies: {len(tracker_anomalies)}")
print(f"Staff anomalies: {len(staff_anomalies)}")
```

---

## ✅ Advantages

### 1. **Unified Analysis**
- Satu model LOF untuk kedua dataset
- Satu model K-Means untuk semua anomalies
- Consistent parameters

### 2. **Cross-Dataset Patterns**
- Bisa detect pola yang melibatkan tracker DAN staff
- Correlation analysis antar dataset
- Comprehensive view

### 3. **Simplified Pipeline**
- Satu flow instead of dua
- Easier maintenance
- Consistent hasil

### 4. **Better Comparison**
- Easy compare tracker vs staff anomalies
- Same scale untuk LOF scores
- Unified clustering

---

## ⚠️ Considerations

### 1. **Column Compatibility**
- Kedua dataset HARUS punya `timestamp` dan `user_id`
- Columns lain bersifat optional
- Data types harus compatible

### 2. **Data Size**
- Merged dataset lebih besar
- Performance considerations
- Memory usage

### 3. **Feature Engineering**
- Different features untuk tracker vs staff
- Need conditional feature creation
- Or use only common features

### 4. **Interpretation**
- Harus selalu check `dataset_source`
- Anomalies bisa dari tracker atau staff
- Different meaning untuk masing-masing

---

## 🔄 Migration Path

### Option A: Full Refactor (Recommended)

**Pros:**
- Clean implementation
- Optimal performance
- Best user experience

**Cons:**
- Requires substantial code changes
- Need to refactor Stages 02-07
- Testing needed

**Steps:**
1. Update Stage 01: Load both datasets
2. Update Stage 02: Merge + preprocess
3. Update Stage 03: Unified feature engineering
4. Update Stage 04-07: Work with merged data
5. Add dataset_source filters in results

### Option B: Keep Separate + Add Comparison

**Pros:**
- Minimal code changes
- Current functionality preserved
- Easy rollback

**Cons:**
- Two separate pipelines
- Redundant processing
- Less integrated

**Steps:**
1. Keep current flow
2. Add comparison view in Stage 07
3. Run both pipelines
4. Compare results

---

## 📝 Code Changes Required

### Minimal Changes (Already Done):

```python
# ✅ merge_datasets() function added
def merge_datasets(df_tracker, df_staff):
    # Add dataset_source identifier
    # Find common columns
    # Concatenate
    # Save to merged_raw.csv
```

### Required Changes for Full Implementation:

**Stage 01:**
- Load BOTH datasets (tracker + staff)
- Show statistics for both
- Validate both before proceeding

**Stage 02:**
- Call merge_datasets()
- Preprocessing on merged data
- Save to `data/cleaned/merged_cleaned.csv`

**Stage 03:**
- Feature engineering dengan dataset_source consideration
- Or use only common features

**Stage 04:**
- Normalization pada merged data

**Stage 05:**
- LOF pada merged data
- Save with dataset_source preserved

**Stage 06:**
- K-Means pada merged anomalies
- Clusters across both datasets

**Stage 07:**
- Results dengan breakdown by dataset_source
- Comparison tracker vs staff
- Export dengan identifier

---

## 🎯 Recommended Approach

### For Now: **Hybrid Approach**

1. **Keep Current Implementation**
   - Tracker & Staff separate pipelines work
   - Upload features work

2. **Add Merge Option**
   - Checkbox di Stage 01: "Merge datasets?"
   - If checked: use merge flow
   - If not: use separate flow

3. **Gradual Migration**
   - Start with merge in Stage 02
   - Gradually update other stages
   - Test thoroughly

### Implementation:

```python
# Stage 01
merge_mode = st.checkbox("Merge Tracker + Staff datasets?", value=False)

if merge_mode:
    # Load both
    df_tracker = load_tracker()
    df_staff = load_staff()

    # Store in session state
    st.session_state.merge_mode = True
    st.session_state.df_tracker = df_tracker
    st.session_state.df_staff = df_staff
else:
    # Current single dataset flow
    dataset = st.selectbox(...)
    df = load_dataset(dataset)
```

```python
# Stage 02
if st.session_state.get('merge_mode', False):
    # Merge flow
    df_merged = merge_datasets(
        st.session_state.df_tracker,
        st.session_state.df_staff
    )
    # Process merged
else:
    # Current separate flow
    df = load_cleaned(dataset)
```

---

## 📊 Example Use Cases

### Use Case 1: Detect Cross-Dataset Anomalies

```python
# After K-Means clustering
# Find clusters with BOTH tracker and staff anomalies
for cluster_id in clusters:
    cluster_data = df[df['cluster'] == cluster_id]
    tracker_count = len(cluster_data[cluster_data['dataset_source'] == 'tracker'])
    staff_count = len(cluster_data[cluster_data['dataset_source'] == 'staff'])

    if tracker_count > 0 and staff_count > 0:
        print(f"Cluster {cluster_id} has BOTH tracker and staff anomalies!")
        # Investigate correlation
```

### Use Case 2: Compare Anomaly Rates

```python
# Anomaly rate comparison
tracker_total = len(df[df['dataset_source'] == 'tracker'])
staff_total = len(df[df['dataset_source'] == 'staff'])

tracker_anomalies = len(df[(df['dataset_source'] == 'tracker') & (df['is_anomaly'] == -1)])
staff_anomalies = len(df[(df['dataset_source'] == 'staff') & (df['is_anomaly'] == -1)])

print(f"Tracker anomaly rate: {tracker_anomalies/tracker_total*100:.2f}%")
print(f"Staff anomaly rate: {staff_anomalies/staff_total*100:.2f}%")
```

### Use Case 3: Temporal Correlation

```python
# Check if tracker and staff anomalies happen at same time
import pandas as pd

df['hour'] = pd.to_datetime(df['timestamp']).dt.hour
df['date'] = pd.to_datetime(df['timestamp']).dt.date

# Count anomalies by hour and source
pivot = df[df['is_anomaly'] == -1].pivot_table(
    values='user_id',
    index='hour',
    columns='dataset_source',
    aggfunc='count',
    fill_value=0
)

# Find hours with high activity in BOTH
high_both = pivot[(pivot['tracker'] > threshold) & (pivot['staff'] > threshold)]
```

---

## 🚀 Next Steps

### Immediate (Already Done):
- ✅ Created `merge_datasets()` function
- ✅ Document merge concept

### Short Term (Recommended):
1. Add checkbox "Merge mode?" di Stage 01
2. Update Stage 02 dengan merge logic
3. Test dengan sample data
4. Refine merge strategy based on results

### Long Term (Full Implementation):
1. Refactor all stages 03-07
2. Add dataset_source analytics
3. Enhanced comparison views
4. Documentation update

---

## 💡 Tips

1. **Always Preserve dataset_source**
   - Don't drop this column
   - Use it for filtering and analysis
   - Include in exports

2. **Handle Missing Columns**
   - Not all columns exist in both datasets
   - Use common columns only
   - Or fill NaN for missing

3. **Validate Merge**
   - Check row counts: merged = tracker + staff
   - Verify dataset_source distribution
   - Ensure no data loss

4. **Performance**
   - Merged dataset 2x size
   - May need sampling for large datasets
   - Consider memory usage

---

## 🎓 For Thesis

### Benefits to Highlight:

1. **Comprehensive Analysis**
   - Unified view of all anomalies
   - Cross-dataset patterns

2. **Methodology**
   - Advanced data integration
   - Multi-source analysis

3. **Insights**
   - Correlation between tracker & staff anomalies
   - Holistic security view

### Screenshots:

1. Merge configuration UI
2. Merged dataset statistics
3. Cross-dataset anomaly clusters
4. Comparison metrics (tracker vs staff)

---

**Status:**
- ✅ Concept documented
- ✅ Merge function created
- ⏳ Full implementation pending
- ⏳ Testing needed

**Next Action:** Decide on implementation approach (Hybrid recommended)
