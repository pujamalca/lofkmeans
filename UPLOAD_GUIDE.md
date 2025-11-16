# 📤 Data Upload Guide - LOF + K-Means Pipeline

## Overview
Aplikasi sekarang mendukung **4 cara** untuk memuat data:
1. ✅ **Load from file** - Load dari file CSV yang sudah ada
2. ✅ **Upload CSV** - Upload file CSV baru
3. ✅ **Upload SQL** - Upload file SQL dan execute ke database
4. ✅ **Connect to Database** - Koneksi langsung ke database

---

## 🎯 Cara Menggunakan

### 1. Load from File (Default)

**Kapan digunakan:**
- Data sudah ada di folder `data/raw/`
- Menggunakan data yang sudah pernah diupload sebelumnya

**Cara:**
1. Pilih dataset (Tracker/Staff)
2. Pilih "Load from file"
3. Data otomatis dimuat dari `data/raw/{dataset}_raw.csv`

**File Path:**
- Tracker: `data/raw/tracker_raw.csv`
- Staff: `data/raw/staff_raw.csv`

---

### 2. Upload CSV

**Kapan digunakan:**
- Punya file CSV baru
- Data dalam format comma (,), semicolon (;), atau tab-separated

**Cara:**
1. Pilih dataset (Tracker/Staff)
2. Pilih "Upload CSV"
3. Click "Browse files" atau drag & drop file CSV
4. Aplikasi otomatis:
   - Detect separator (,  ; atau tab)
   - Parse CSV
   - Validate data structure
   - Save ke `data/raw/{dataset}_raw.csv`

**Supported formats:**
- `.csv` - Comma Separated Values
- `.txt` - Text files dengan delimiter

**Example CSV structure for Tracker:**
```csv
timestamp,user_id,query_type,query_info,ip_address
2024-01-01 10:00:00,user001,SELECT,SELECT * FROM users,192.168.1.100
2024-01-01 10:05:00,user002,INSERT,INSERT INTO logs,192.168.1.101
```

**Example CSV structure for Staff:**
```csv
user_id,name,date,timestamp
staff001,John Doe,2024-01-01,2024-01-01 08:00:00
staff002,Jane Smith,2024-01-01,2024-01-01 08:15:00
```

**Validation:**
- ✅ Required columns checked
- ✅ Data type validation
- ⚠️ Missing values checked
- ⚠️ Empty dataset checked

---

### 3. Upload SQL File

**Kapan digunakan:**
- Punya file SQL dengan query
- Ingin execute query ke database
- Query sudah disiapkan dalam file .sql

**Cara:**
1. Pilih dataset (Tracker/Staff)
2. Pilih "Upload SQL"
3. **Upload SQL file** (.sql)
4. **Configure database:**
   - Pilih Database Type (MySQL, PostgreSQL, SQLite)
   - Isi connection details:
     - Host (e.g., localhost)
     - Port (3306 untuk MySQL, 5432 untuk PostgreSQL)
     - Username
     - Password
     - Database Name
5. Click "Execute SQL"
6. Data hasil query akan di-save ke `data/raw/{dataset}_raw.csv`

**Example SQL file (tracker_query.sql):**
```sql
-- Get tracker data
SELECT
    timestamp,
    user_id,
    operation AS query_type,
    query_string AS query_info,
    ip_address
FROM
    activity_log
WHERE
    timestamp >= '2024-01-01'
ORDER BY
    timestamp DESC
LIMIT 10000;
```

**Example SQL file (staff_query.sql):**
```sql
-- Get staff login data
SELECT
    staff_id AS user_id,
    staff_name AS name,
    login_date AS date,
    login_timestamp AS timestamp
FROM
    staff_login
WHERE
    login_date >= '2024-01-01'
ORDER BY
    login_timestamp DESC;
```

**Supported databases:**
- ✅ MySQL (via mysql-connector-python atau pymysql)
- ✅ PostgreSQL (via psycopg2)
- ✅ SQLite (via sqlite3)

**SQL file features:**
- Removes `--` comments
- Removes `#` comments
- Removes `/* */` multi-line comments
- Normalizes whitespace

---

### 4. Connect to Database (Direct)

**Kapan digunakan:**
- Ingin query langsung tanpa file SQL
- Testing query on-the-fly
- Database accessible dari aplikasi

**Cara:**
1. Pilih dataset (Tracker/Staff)
2. Pilih "Connect to Database"
3. **Configure connection** (left column):
   - Pilih Database Type
   - Isi connection details (sama seperti Upload SQL)
4. **Write query** (right column):
   - Tulis SQL query langsung di text area
   - Default: `SELECT * FROM table_name LIMIT 1000`
5. Click "Connect & Query"
6. Data hasil query akan di-save ke `data/raw/{dataset}_raw.csv`

**Example MySQL connection:**
```
Database Type: mysql
Host: localhost
Port: 3306
Username: root
Password: ********
Database Name: hospital_db

Query:
SELECT * FROM activity_tracker
WHERE date >= '2024-01-01'
LIMIT 5000
```

**Example PostgreSQL connection:**
```
Database Type: postgresql
Host: db.example.com
Port: 5432
Username: dbuser
Password: ********
Database Name: analytics_db

Query:
SELECT
    event_time as timestamp,
    user_id,
    event_type as query_type
FROM events
WHERE event_date >= '2024-01-01'
```

**Example SQLite connection:**
```
Database Type: sqlite
Database Path: ./hospital.db

Query:
SELECT * FROM tracker_logs
ORDER BY timestamp DESC
LIMIT 10000
```

---

## ✅ Data Validation

Setelah upload, aplikasi otomatis melakukan validasi:

### For Tracker Dataset

**Required columns:**
- `timestamp` - Waktu aktivitas
- `user_id` - ID user

**Recommended columns:**
- `query_info` - Informasi query
- `query_type` - Tipe query (SELECT, INSERT, UPDATE, DELETE)
- `ip_address` - IP address

**Validation checks:**
- ❌ Error jika missing required columns
- ⚠️ Warning jika missing recommended columns
- ⚠️ Warning jika >50% missing values
- ❌ Error jika dataset kosong (0 rows)

### For Staff Dataset

**Required columns:**
- `user_id` - ID staff
- `timestamp` - Waktu login

**Recommended columns:**
- `name` - Nama staff
- `date` - Tanggal login

**Validation checks:**
- ❌ Error jika missing required columns
- ⚠️ Warning jika missing recommended columns
- ⚠️ Warning jika >50% missing values
- ❌ Error jika dataset kosong (0 rows)

---

## 🔧 Installation Requirements

### For CSV Upload
```bash
# Core dependencies (already included)
pip install pandas streamlit
```

### For Database Features
```bash
# Install database drivers
pip install sqlalchemy>=2.0.0

# MySQL support
pip install mysql-connector-python>=8.0.33
pip install pymysql>=1.1.0

# PostgreSQL support
pip install psycopg2-binary>=2.9.6
```

Or simply:
```bash
pip install -r requirements.txt
```

---

## 📊 Data Flow

### Upload Flow
```
┌─────────────┐
│ Data Source │
└──────┬──────┘
       │
       ├─→ CSV File ──→ Parse CSV ──→ Validate
       │
       ├─→ SQL File ──→ Parse SQL ──→ Execute on DB ──→ Validate
       │
       └─→ Direct DB ──→ Execute Query ──→ Validate

       ↓

┌──────────────────┐
│ Save to CSV      │
│ data/raw/*.csv   │
└─────────┬────────┘
          │
          ↓
┌──────────────────┐
│ Display Preview  │
│ Show Metrics     │
└─────────┬────────┘
          │
          ↓
┌──────────────────┐
│ Continue to      │
│ Stage 02         │
└──────────────────┘
```

---

## 🐛 Troubleshooting

### CSV Upload Issues

**Problem:** "Error uploading CSV: codec can't decode"
**Solution:** Ensure file is UTF-8 encoded

**Problem:** "Delimiter detection failed"
**Solution:** Use standard delimiters (comma, semicolon, or tab)

**Problem:** "Missing required columns"
**Solution:** Check column names match requirements (timestamp, user_id)

---

### SQL Upload Issues

**Problem:** "Module not found: mysql.connector"
**Solution:** Install MySQL connector
```bash
pip install mysql-connector-python
```

**Problem:** "Module not found: psycopg2"
**Solution:** Install PostgreSQL connector
```bash
pip install psycopg2-binary
```

**Problem:** "Connection refused"
**Solution:**
- Check database is running
- Check host/port are correct
- Check firewall allows connection

**Problem:** "Access denied for user"
**Solution:**
- Check username/password
- Check user has SELECT permission on table

---

### Database Connection Issues

**Problem:** "Connection timeout"
**Solution:**
- Check network connectivity
- Check database server is accessible
- Use correct host (localhost vs IP address)

**Problem:** "Table doesn't exist"
**Solution:**
- Verify table name in query
- Check you're connecting to correct database

**Problem:** "SQL syntax error"
**Solution:**
- Test query in database client first
- Check SQL dialect matches database type

---

## 💡 Best Practices

### For CSV Upload

1. **Clean your data first:**
   - Remove extra spaces in column names
   - Use consistent date formats
   - Check for special characters

2. **Use standard column names:**
   - Tracker: timestamp, user_id, query_type, query_info
   - Staff: user_id, name, date, timestamp

3. **Check file encoding:**
   - Use UTF-8
   - Avoid special characters in column names

---

### For SQL Upload

1. **Test query first:**
   - Run query in database client (MySQL Workbench, pgAdmin, etc.)
   - Verify results before uploading

2. **Limit results:**
   - Use LIMIT clause to avoid loading too much data
   - Start with smaller datasets for testing

3. **Column aliases:**
   - Use AS to rename columns to standard names
   ```sql
   SELECT
       event_time AS timestamp,
       user AS user_id,
       type AS query_type
   FROM events
   ```

4. **Optimize queries:**
   - Add WHERE clause to filter data
   - Use indexes on filter columns
   - Avoid SELECT * if possible

---

### For Database Connection

1. **Security:**
   - Don't hardcode passwords
   - Use environment variables for credentials
   - Use read-only database users

2. **Performance:**
   - Limit number of rows (use LIMIT)
   - Filter old data (use WHERE timestamp > ...)
   - Create indexes on frequently queried columns

3. **Testing:**
   - Test connection with simple query first
   - Start with LIMIT 100 to verify structure
   - Increase limit after validation

---

## 📝 Example Workflows

### Workflow 1: Upload CSV from Excel

1. Export from Excel as CSV
2. Open in text editor to verify delimiter
3. Check column names
4. Upload via "Upload CSV"
5. Verify validation passed
6. Continue to Stage 02

---

### Workflow 2: Query from MySQL Database

1. Prepare SQL file:
   ```sql
   SELECT
       log_timestamp AS timestamp,
       user_id,
       operation_type AS query_type,
       sql_query AS query_info
   FROM activity_log
   WHERE log_timestamp >= '2024-01-01'
   LIMIT 10000;
   ```

2. Save as `tracker_query.sql`
3. Choose "Upload SQL"
4. Upload file
5. Configure MySQL connection
6. Click "Execute SQL"
7. Verify data loaded
8. Continue pipeline

---

### Workflow 3: Direct PostgreSQL Query

1. Choose "Connect to Database"
2. Fill connection details:
   - Type: postgresql
   - Host: localhost
   - Port: 5432
   - User: analyst
   - Password: ***
   - Database: analytics_db
3. Write query:
   ```sql
   SELECT * FROM user_events
   WHERE event_date >= CURRENT_DATE - INTERVAL '30 days'
   ORDER BY event_timestamp DESC
   ```
4. Click "Connect & Query"
5. Verify results
6. Proceed with analysis

---

## 🆕 What's New

**Version 2.0 Features:**
- ✅ Multi-source data loading
- ✅ CSV auto-detection (comma, semicolon, tab)
- ✅ SQL file parsing with comment removal
- ✅ MySQL, PostgreSQL, SQLite support
- ✅ Automatic data validation
- ✅ Clear error messages & warnings
- ✅ Data saved automatically to data/raw/

---

## 📞 Support

### If upload fails:

1. **Check file format:**
   - CSV must be valid format
   - SQL must be valid syntax
   - Check encoding (UTF-8)

2. **Check data structure:**
   - Required columns must exist
   - Column names must match (case-sensitive)

3. **Check database connection:**
   - Database must be accessible
   - Credentials must be correct
   - User must have permissions

4. **Check error messages:**
   - Red alerts (❌) = Critical errors - must fix
   - Yellow alerts (⚠️) = Warnings - can proceed but check data

---

## 🎓 For Thesis Documentation

### Screenshots to include:

1. **CSV Upload Interface**
2. **SQL File Upload with DB Config**
3. **Direct Database Connection**
4. **Validation Results (Success)**
5. **Validation Results (Warnings)**
6. **Data Preview After Upload**

### Key points for report:

- ✅ Multiple data source support
- ✅ Automatic format detection
- ✅ Database integration (MySQL, PostgreSQL, SQLite)
- ✅ Data validation on upload
- ✅ User-friendly error messages
- ✅ Secure password handling

---

**🎉 Happy uploading! Data Anda siap untuk dianalisis dengan LOF + K-Means Pipeline!**
