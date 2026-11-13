import sqlite3
import hashlib
from datetime import datetime

DB_NAME = "ictu_system.db"

def init_db():
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    
    # 1. Bảng lưu thông tin tài khoản sinh viên
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
    
    # 2. Bảng lưu lịch sử kết quả tính điểm & xếp loại học lực
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
            score_10 REAL NOT NULL,
            score_4 REAL NOT NULL,
            letter_grade TEXT NOT NULL,
            classification TEXT NOT NULL,
            created_at TEXT NOT NULL
        )
    ''')
    
    conn.commit()
    conn.close()

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def register_user(full_name, mssv, email, password, faculty):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    try:
        c.execute('''
            INSERT INTO users (full_name, mssv, email, password, faculty, created_at)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (full_name.strip(), mssv.strip().upper(), email.strip().lower(), hash_password(password), faculty, now))
        conn.commit()
        return True, "Đăng ký tài khoản thành công! Vui lòng đăng nhập."
    except sqlite3.IntegrityError:
        return False, "Mã sinh viên (MSSV) hoặc Email này đã được đăng ký!"
    finally:
        conn.close()

def login_user(username_or_email, password):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    user_input = username_or_email.strip()
    hashed_pw = hash_password(password)
    
    c.execute('''
        SELECT full_name, mssv, email, faculty FROM users
        WHERE (UPPER(mssv) = UPPER(?) OR LOWER(email) = LOWER(?)) AND password = ?
    ''', (user_input, user_input, hashed_pw))
    
    user = c.fetchone()
    conn.close()
    return user

# --- CÁC HÀM QUẢN LÝ DỮ LIỆU ĐIỂM HỌC PHẦN ---

def save_academic_record(mssv, subject_name, credits, tdl, tbtn1, tbkt, thi, score_10, score_4, letter_grade, classification):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    now = datetime.now().strftime("%d/%m/%Y %H:%M")
    c.execute('''
        INSERT INTO academic_records 
        (mssv, subject_name, credits, tdl, tbtn1, tbkt, thi, score_10, score_4, letter_grade, classification, created_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (mssv, subject_name.strip(), credits, tdl, tbtn1, tbkt, thi, score_10, score_4, letter_grade, classification, now))
    conn.commit()
    conn.close()

def get_records_by_mssv(mssv):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute('''
        SELECT id, subject_name, credits, tdl, tbtn1, tbkt, thi, score_10, score_4, letter_grade, classification, created_at
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