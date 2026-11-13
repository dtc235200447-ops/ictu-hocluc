import os
import sqlite3
import hashlib
import tempfile
from datetime import datetime

# Lưu database vào thư mục tạm có quyền ghi trên Streamlit Cloud
DB_NAME = os.path.join(tempfile.gettempdir(), "ictu_system.db")

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def init_db():
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            full_name TEXT NOT NULL,
            mssv TEXT UNIQUE NOT NULL,
            email TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            faculty TEXT NOT NULL,
            created_at TEXT
        )
    ''')
    c.execute('''
        CREATE TABLE IF NOT EXISTS academic_records (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            mssv TEXT NOT NULL,
            subject_name TEXT NOT NULL,
            credits INTEGER NOT NULL,
            tdl REAL NOT NULL,
            tbtn1 REAL NOT NULL,
            tbkt REAL NOT NULL,
            thi REAL NOT NULL,
            diem_10 REAL NOT NULL,
            diem_4 REAL NOT NULL,
            diem_chu TEXT NOT NULL,
            xep_loai TEXT NOT NULL,
            created_at TEXT
        )
    ''')
    conn.commit()
    conn.close()

def register_user(full_name, mssv, email, password, faculty):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    try:
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        c.execute('''
            INSERT INTO users (full_name, mssv, email, password, faculty, created_at)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (full_name.strip(), mssv.strip().upper(), email.strip().lower(), hash_password(password), faculty, now))
        conn.commit()
        return True, "Đăng ký tài khoản thành công! Vui lòng quay lại màn hình đăng nhập."
    except sqlite3.IntegrityError:
        return False, "Mã sinh viên (MSSV) hoặc Email này đã được đăng ký!"
    finally:
        conn.close()

def login_user(username, password):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    user_input = username.strip()
    hashed_pw = hash_password(password)
    c.execute('''
        SELECT full_name, mssv, email, faculty FROM users
        WHERE (UPPER(mssv) = UPPER(?) OR LOWER(email) = LOWER(?)) AND password = ?
    ''', (user_input, user_input, hashed_pw))
    user = c.fetchone()
    conn.close()
    return user

def save_academic_record(mssv, subject_name, credits, tdl, tbtn1, tbkt, thi, diem_10, diem_4, diem_chu, xep_loai):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    c.execute('''
        INSERT INTO academic_records (
            mssv, subject_name, credits, tdl, tbtn1, tbkt, thi,
            diem_10, diem_4, diem_chu, xep_loai, created_at
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (mssv, subject_name, credits, tdl, tbtn1, tbkt, thi, diem_10, diem_4, diem_chu, xep_loai, now))
    conn.commit()
    conn.close()

def get_records_by_mssv(mssv):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute('''
        SELECT id, subject_name, credits, tdl, tbtn1, tbkt, thi,
               diem_10, diem_4, diem_chu, xep_loai, created_at
        FROM academic_records
        WHERE mssv = ?
        ORDER BY id DESC
    ''', (mssv,))
    rows = c.fetchall()
    conn.close()
    return rows

def delete_record(record_id):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute('DELETE FROM academic_records WHERE id = ?', (record_id,))
    conn.commit()
    conn.close()