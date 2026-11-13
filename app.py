import os
import re
import base64
import streamlit as st
import streamlit.components.v1 as components
import pandas as pd
import numpy as np
import joblib
import database as db

# Khởi tạo Database
db.init_db()

# Cấu hình trang
st.set_page_config(
    page_title="Hệ thống Phân loại Học lực Sinh viên - ICTU",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Quản lý trạng thái phiên đăng nhập
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "user_info" not in st.session_state:
    st.session_state.user_info = None
if "auth_mode" not in st.session_state:
    st.session_state.auth_mode = "login"

# Hàm chuyển ảnh nội bộ sang Base64
def get_base64_image(image_path):
    if os.path.exists(image_path):
        with open(image_path, "rb") as img_file:
            return base64.b64encode(img_file.read()).decode()
    return None

# CSS tùy chỉnh giao diện Card trắng tinh 100%
def inject_auth_css():
    img_base64 = get_base64_image("ictu_bg.jpg")
    
    if img_base64:
        bg_css = f"""
            background-image: linear-gradient(135deg, rgba(226, 236, 252, 0.45) 0%, rgba(190, 212, 245, 0.55) 100%),
                              url("data:image/jpeg;base64,{img_base64}");
        """
    else:
        bg_css = """
            background: linear-gradient(135deg, #dce7f9 0%, #c4d8f5 100%);
        """

    st.markdown(f"""
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Dancing+Script:wght@700&family=Plus+Jakarta+Sans:wght@400;500;600;700;800&display=swap');

        header[data-testid="stHeader"] {{
            display: none !important;
        }}
        
        .stApp {{
            {bg_css}
            background-size: cover;
            background-position: center;
            background-attachment: fixed;
            font-family: 'Plus Jakarta Sans', sans-serif;
        }}

        .stApp::before {{
            content: "";
            position: fixed;
            inset: 0;
            backdrop-filter: blur(6px);
            -webkit-backdrop-filter: blur(6px);
            z-index: 0;
            pointer-events: none;
        }}

        .block-container {{
            position: relative;
            z-index: 1;
            padding-top: 2rem !important;
            padding-bottom: 4.5rem !important;
        }}

        div[data-testid="stVerticalBlockBorderWrapper"],
        div[data-testid="stColumn"]:nth-of-type(2) > div[data-testid="stVerticalBlock"] > div[data-testid="stVerticalBlockBorderWrapper"],
        div[data-testid="stColumn"]:nth-of-type(2) div[style*="border"],
        .st-key-auth_card {{
            background-color: #ffffff !important;
            background: #ffffff !important;
            border-radius: 20px !important;
            padding: 36px 38px !important;
            box-shadow: 0 20px 50px rgba(18, 36, 78, 0.25) !important;
            border: 1px solid #e2e8f4 !important;
        }}

        .auth-title {{
            text-align: center;
            color: #1e2959;
            font-size: 24px;
            font-weight: 800;
            line-height: 1.3;
            margin-top: 8px;
            margin-bottom: 4px;
            letter-spacing: -0.3px;
        }}
        .auth-subtitle {{
            text-align: center;
            color: #526082;
            font-size: 14px;
            font-weight: 500;
            margin-bottom: 16px;
        }}
        .auth-divider {{
            height: 1px;
            background-color: #e6ebf5;
            margin: 0 0 20px 0;
        }}
        .form-heading {{
            color: #1e2959;
            font-size: 19px;
            font-weight: 700;
            margin-bottom: 14px;
            display: flex;
            align-items: center;
            gap: 8px;
        }}

        div[data-baseweb="input"], div[data-baseweb="select"] > div {{
            background-color: #f8fafd !important;
            border-radius: 10px !important;
            border: 1.5px solid #d5dfef !important;
            min-height: 44px !important;
            transition: all 0.2s ease;
        }}
        div[data-baseweb="input"]:focus-within, div[data-baseweb="select"] > div:focus-within {{
            border-color: #364fc7 !important;
            background-color: #ffffff !important;
            box-shadow: 0 0 0 3px rgba(54, 79, 199, 0.12) !important;
        }}
        input {{
            color: #1e2959 !important;
            font-size: 14.5px !important;
            font-weight: 500 !important;
        }}
        input::placeholder {{
            color: #7b88a8 !important;
            font-weight: 400 !important;
        }}

        div.stButton > button[kind="primary"] {{
            background-color: #3447b8 !important;
            color: #ffffff !important;
            border-radius: 10px !important;
            font-weight: 600 !important;
            font-size: 15px !important;
            border: none !important;
            padding: 11px 0 !important;
            box-shadow: 0 4px 14px rgba(52, 71, 184, 0.28) !important;
            transition: all 0.2s ease !important;
        }}
        div.stButton > button[kind="primary"]:hover {{
            background-color: #273696 !important;
            transform: translateY(-1px);
        }}

        div.stButton > button[kind="secondary"] {{
            background-color: #ffffff !important;
            border-radius: 10px !important;
            color: #1e2959 !important;
            border: 1.5px solid #cfd8ea !important;
            font-weight: 600 !important;
            font-size: 14.5px !important;
            padding: 10px 0 !important;
        }}
        div.stButton > button[kind="secondary"]:hover {{
            background-color: #f6f8fd !important;
            border-color: #3447b8 !important;
            color: #3447b8 !important;
        }}

        label[data-baseweb="checkbox"] span {{
            color: #3a476a !important;
            font-size: 13.5px !important;
            font-weight: 500 !important;
        }}

        .slogan-box {{
            padding-top: 50px;
            padding-left: 20px;
            color: #1e2959;
            text-shadow: 0 2px 12px rgba(255, 255, 255, 0.9);
        }}
        .slogan-script {{
            font-family: 'Dancing Script', cursive;
            font-size: 46px;
            line-height: 1.25;
            color: #182554;
            margin-bottom: 14px;
        }}
        .slogan-desc {{
            font-size: 15px;
            color: #2c3a63;
            font-weight: 600;
            line-height: 1.6;
            max-width: 340px;
        }}

        .custom-footer {{
            position: fixed;
            bottom: 0;
            left: 0;
            width: 100%;
            background: rgba(24, 39, 89, 0.94);
            backdrop-filter: blur(8px);
            color: #eef3fc;
            padding: 10px 40px;
            display: flex;
            justify-content: space-between;
            align-items: center;
            font-size: 13px;
            z-index: 999;
        }}
        </style>
    """, unsafe_allow_html=True)

LOGO_SVG = """
<div style="display: flex; justify-content: center; align-items: center; margin-bottom: 4px;">
    <svg width="84" height="72" viewBox="0 0 100 85" fill="none" xmlns="http://www.w3.org/2000/svg">
        <path d="M50 10L12 27L50 44L88 27L50 10Z" fill="#2B3990"/>
        <path d="M26 34V49C26 49 36 56 50 56C64 56 74 49 74 49V34L50 45L26 34Z" fill="#3B4CCA"/>
        <path d="M84 29V47" stroke="#2B3990" stroke-width="3" stroke-linecap="round"/>
        <circle cx="84" cy="49" r="3" fill="#2B3990"/>
        <path d="M21 67C13 59 10 47 14 36" stroke="#2B3990" stroke-width="3.5" stroke-linecap="round"/>
        <path d="M79 67C87 59 90 47 86 36" stroke="#2B3990" stroke-width="3.5" stroke-linecap="round"/>
        <path d="M27 74C34 78 42 80 50 80C58 80 66 78 73 74" stroke="#2B3990" stroke-width="3.2" stroke-linecap="round"/>
        <path d="M32 62C38 60 46 61 50 64C54 61 62 60 68 62V72C62 70 54 71 50 74C46 71 38 70 32 72V62Z" fill="#4C63E6"/>
    </svg>
</div>
"""

# ==========================================
# MÀN HÌNH 1: ĐĂNG NHẬP & ĐĂNG KÝ
# ==========================================
def show_auth_page():
    inject_auth_css()
    
    left_col, center_col, right_col = st.columns([1.05, 1.2, 0.85])
    
    with left_col:
        st.markdown("""
            <div class="slogan-box">
                <div class="slogan-script">Học tập tốt<br>– Tương lai sáng</div>
                <div class="slogan-desc">
                    Hệ thống phân tích, đánh giá và dự đoán xếp loại học lực sinh viên chuẩn quy chế ICTU.
                </div>
            </div>
        """, unsafe_allow_html=True)
    
    with center_col:
        with st.container(border=True, key="auth_card"):
            st.markdown(LOGO_SVG, unsafe_allow_html=True)
            st.markdown("<div class='auth-title'>Phân loại xếp loại học lực<br>của sinh viên</div>", unsafe_allow_html=True)
            st.markdown("<div class='auth-subtitle'>Dựa trên dữ liệu học tập</div>", unsafe_allow_html=True)
            st.markdown("<div class='auth-divider'></div>", unsafe_allow_html=True)

            # --- FORM ĐĂNG NHẬP ---
            if st.session_state.auth_mode == "login":
                st.markdown("<div class='form-heading'>⇥ Đăng nhập</div>", unsafe_allow_html=True)
                
                username = st.text_input("Tên đăng nhập", placeholder="👤  Tên đăng nhập (MSSV hoặc Email)", label_visibility="collapsed")
                password = st.text_input("Mật khẩu", type="password", placeholder="🔒  Mật khẩu", label_visibility="collapsed")
                
                c1, c2 = st.columns([1.1, 1])
                with c1:
                    st.checkbox("Ghi nhớ đăng nhập", value=False)
                with c2:
                    st.markdown("<div style='text-align: right; font-size: 13.5px; padding-top: 8px;'><a href='#' style='color: #3447b8; font-weight: 600; text-decoration: none;'>Quên mật khẩu?</a></div>", unsafe_allow_html=True)

                st.write("")
                if st.button("⇥  Đăng nhập", type="primary", use_container_width=True):
                    if not username or not password:
                        st.warning("Vui lòng nhập đầy đủ Tên đăng nhập và Mật khẩu!")
                    else:
                        user = db.login_user(username, password)
                        if user:
                            st.session_state.logged_in = True
                            st.session_state.user_info = {
                                "full_name": user[0],
                                "mssv": user[1],
                                "email": user[2],
                                "faculty": user[3]
                            }
                            st.rerun()
                        else:
                            st.error("Sai tên đăng nhập hoặc mật khẩu!")

                st.markdown("""
                    <div style='display: flex; align-items: center; margin: 16px 0; color: #7b88a8; font-size: 13.5px; font-weight: 500;'>
                        <div style='flex: 1; height: 1px; background: #e6ebf5;'></div>
                        <span style='padding: 0 14px;'>Hoặc</span>
                        <div style='flex: 1; height: 1px; background: #e6ebf5;'></div>
                    </div>
                """, unsafe_allow_html=True)
                
                if st.button("👤+  Đăng ký tài khoản", type="secondary", use_container_width=True):
                    st.session_state.auth_mode = "register"
                    st.rerun()

            # --- FORM ĐĂNG KÝ TÀI KHOẢN ---
            elif st.session_state.auth_mode == "register":
                st.markdown("<div class='form-heading'>👤+ Đăng ký tài khoản</div>", unsafe_allow_html=True)
                
                full_name = st.text_input("Họ và tên", placeholder="👤  Họ và tên", label_visibility="collapsed")
                mssv = st.text_input("Mã sinh viên (MSSV)", placeholder="🪪  Mã sinh viên (VD: DTC215480101)", label_visibility="collapsed")
                email = st.text_input("Email", placeholder="✉️  Email", label_visibility="collapsed")
                password = st.text_input("Mật khẩu", type="password", placeholder="🔒  Mật khẩu", label_visibility="collapsed")
                
                faculties = [
                    "🎓  Chọn khoa",
                    "Khoa Công nghệ thông tin",
                    "Khoa Kỹ thuật và Công nghệ",
                    "Khoa Kinh tế và Quản trị",
                    "Khoa Nghệ thuật và Truyền thông",
                    "Khoa Khoa học liên ngành"
                ]
                faculty = st.selectbox("Khoa", faculties, label_visibility="collapsed")

                st.write("")
                if st.button("👤+  Đăng ký", type="primary", use_container_width=True):
                    mssv_clean = mssv.strip().upper()
                    email_clean = email.strip()
                    
                    if not all([full_name.strip(), mssv_clean, email_clean, password]):
                        st.warning("Vui lòng điền đầy đủ tất cả các thông tin!")
                    elif not re.match(r"^DTC\d{9}$", mssv_clean):
                        st.error("⚠️ Mã sinh viên không hợp lệ! Phải bắt đầu bằng 'DTC' và theo sau là đúng 9 chữ số (VD: DTC215480101).")
                    elif not re.match(r"^[\w\.-]+@[\w\.-]+\.\w+$", email_clean):
                        st.error("⚠️ Địa chỉ Email không đúng định dạng!")
                    elif len(password) < 6:
                        st.warning("⚠️ Mật khẩu phải có ít nhất 6 ký tự!")
                    elif faculty == "🎓  Chọn khoa":
                        st.warning("⚠️ Vui lòng chọn Khoa của bạn!")
                    else:
                        success, msg = db.register_user(full_name, mssv_clean, email_clean, password, faculty)
                        if success:
                            st.success(msg)
                        else:
                            st.error(msg)

                st.write("")
                if st.button("←  Quay lại đăng nhập", type="secondary", use_container_width=True):
                    st.session_state.auth_mode = "login"
                    st.rerun()

    st.markdown("""
        <div class="custom-footer">
            <div>📊 Ứng dụng hỗ trợ phân tích và đánh giá học lực sinh viên một cách chính xác, hiệu quả</div>
            <div>🎓 Vì một môi trường giáo dục thông minh</div>
        </div>
    """, unsafe_allow_html=True)

# ==========================================
# MÀN HÌNH 2: HỆ THỐNG QUẢN LÝ & PHÂN TÍCH HỌC LỰC ICTU
# ==========================================
@st.cache_resource
def load_assets():
    model = joblib.load('models/best_model.pkl')
    scaler = joblib.load('models/scaler.pkl')
    return model, scaler

def calculate_ictu_grades(tdl, tbtn1, tbkt, thi):
    diem_10 = round(tdl * 0.05 + tbtn1 * 0.15 + tbkt * 0.30 + thi * 0.50, 2)
    if diem_10 >= 8.5:
        diem_4, diem_chu = 4.0, 'A'
    elif diem_10 >= 7.0:
        diem_4, diem_chu = 3.0, 'B'
    elif diem_10 >= 5.5:
        diem_4, diem_chu = 2.0, 'C'
    elif diem_10 >= 4.0:
        diem_4, diem_chu = 1.0, 'D'
    else:
        diem_4, diem_chu = 0.0, 'F'
    return diem_10, diem_4, diem_chu

def classify_gpa_ictu(gpa):
    if gpa >= 3.60:
        return "Xuất sắc"
    elif gpa >= 3.20:
        return "Giỏi"
    elif gpa >= 2.50:
        return "Khá"
    elif gpa >= 2.00:
        return "Trung bình"
    else:
        return "Yếu"

def show_main_dashboard():
    user = st.session_state.user_info
    
    # Thanh tiêu đề & Đăng xuất
    head_col1, head_col2 = st.columns([4.2, 1])
    with head_col1:
        st.title("🎓 Hệ Thống Quản Lý & Dự Đoán Học Lực Sinh Viên (ICTU)")
        st.caption(f"Sinh viên: **{user['full_name']}** | MSSV: **{user['mssv']}** | **{user['faculty']}**")
    with head_col2:
        st.write("")
        if st.button("🚪 Đăng xuất", use_container_width=True):
            st.session_state.logged_in = False
            st.session_state.user_info = None
            st.rerun()

    # Tải dữ liệu lịch sử của sinh viên để hiển thị Cảnh báo học vụ sớm
    records = db.get_records_by_mssv(user['mssv'])
    if records:
        f_subjects = [r[1] for r in records if r[8] == 0.0]
        d_subjects = [r[1] for r in records if r[8] == 1.0]
        if f_subjects:
            st.error(f"🚨 **Cảnh báo học vụ:** Bạn đang có **{len(f_subjects)} học phần điểm F** chưa đạt ({', '.join(f_subjects)}). Hãy ưu tiên đăng ký học lại!")
        elif d_subjects:
            st.warning(f"⚠️ **Lưu ý cải thiện GPA:** Bạn có **{len(d_subjects)} học phần điểm D** ({', '.join(d_subjects)}). Bạn có thể thử tính toán nâng hạng GPA ở Tab **Lịch Sử & GPA Tích Lũy**.")

    st.markdown("---")

    try:
        model, scaler = load_assets()
        tab1, tab2, tab3, tab4, tab5 = st.tabs([
            "📝 Dự đoán & Phân tích Môn học",
            "🎯 Mô phỏng Điểm thi Mục tiêu",
            "📁 Phân loại Hàng loạt (Lớp học)",
            "🗂️ Lịch Sử & Nâng hạng GPA",
            "💬 Trợ Lý Sinh Viên ICTU"
        ])

        # ==============================================================
        # TAB 1: DỰ ĐOÁN & BIỂU ĐỒ SO SÁNH ĐIỂM THÀNH PHẦN
        # ==============================================================
        with tab1:
            st.subheader("Bảng nhập thông tin & điểm thành phần môn học")
            
            info_c1, info_c2 = st.columns([3, 1])
            with info_c1:
                subject_name = st.text_input("Tên học phần", placeholder="Ví dụ: Khai phá dữ liệu, Lập trình Python...")
            with info_c2:
                credits = st.number_input("Số tín chỉ", min_value=1, max_value=10, value=3, step=1)

            col1, col2 = st.columns(2)
            with col1:
                tdl = st.number_input("Điểm TDL (Ý thức / Chuyên cần - 5%)", 0.0, 10.0, 8.5, step=0.5)
                tbtn1 = st.number_input("Điểm TBTN1 (KT Thường xuyên - 15%)", 0.0, 10.0, 7.5, step=0.5)
            with col2:
                tbkt = st.number_input("Điểm TBKT (KT Kỹ năng - 30%)", 0.0, 10.0, 8.0, step=0.5)
                thi = st.number_input("Điểm THI (Thi Kết thúc HP - 50%)", 0.0, 10.0, 7.0, step=0.5)

            save_to_db = st.checkbox("💾 Tự động lưu kết quả này vào cơ sở dữ liệu cá nhân", value=True)

            if st.button("🔍 Dự đoán & Phân tích Học lực", type="primary", use_container_width=True):
                diem_10, diem_4, diem_chu = calculate_ictu_grades(tdl, tbtn1, tbkt, thi)
                input_data = np.array([[tdl, tbtn1, tbkt, thi]])
                input_scaled = scaler.transform(input_data)
                pred_idx = model.predict(input_scaled)[0]
                
                class_names = ['Yếu', 'Trung bình', 'Khá', 'Giỏi', 'Xuất sắc']
                prediction = class_names[pred_idx]
                icons = {'Xuất sắc': '🌟', 'Giỏi': '🟢', 'Khá': '🔵', 'Trung bình': '🟡', 'Yếu': '🔴'}

                if save_to_db:
                    subj_to_save = subject_name if subject_name.strip() else "Học phần chưa đặt tên"
                    db.save_academic_record(
                        user['mssv'], subj_to_save, credits, tdl, tbtn1, tbkt, thi,
                        diem_10, diem_4, diem_chu, prediction
                    )

                st.markdown("---")
                m1, m2, m3 = st.columns(3)
                m1.metric("Điểm Học Phần (Hệ 10)", f"{diem_10}")
                m2.metric("Điểm Chữ", diem_chu)
                m3.metric("Điểm Quy Đổi (Hệ 4)", f"{diem_4}")

                st.success(f"### Kết quả Xếp loại: {icons.get(prediction, '')} **{prediction}**")

                # Biểu đồ trực quan so sánh điểm thành phần với chuẩn Giỏi (8.0)
                st.markdown("#### 📊 Biểu đồ phân tích cấu trúc điểm thành phần")
                chart_df = pd.DataFrame({
                    "Điểm của bạn": [tdl, tbtn1, tbkt, thi],
                    "Mức chuẩn Giỏi (8.0)": [8.0, 8.0, 8.0, 8.0]
                }, index=["1. TDL (5%)", "2. TBTN1 (15%)", "3. TBKT (30%)", "4. THI (50%)"])
                st.bar_chart(chart_df)

                # Nhận xét điểm yếu cần khắc phục
                scores_map = {"TDL (Chuyên cần)": tdl, "TBTN1 (Thường xuyên)": tbtn1, "TBKT (Kỹ năng)": tbkt, "THI (Cuối kỳ)": thi}
                lowest_comp = min(scores_map, key=scores_map.get)
                if scores_map[lowest_comp] < 7.0:
                    st.info(f"💡 **Gợi ý cải thiện:** Thành phần thấp nhất của bạn ở môn này là **{lowest_comp}** ({scores_map[lowest_comp]} điểm). Cải thiện cột điểm này ở các môn sau sẽ giúp nâng rõ rệt điểm tổng kết.")

        # ==============================================================
        # TAB 2: CÔNG CỤ MÔ PHỎNG ĐIỂM THI MỤC TIÊU ("WHAT-IF")
        # ==============================================================
        with tab2:
            st.subheader("🎯 Tính điểm thi kết thúc học phần cần đạt")
            st.caption("Nhập 3 cột điểm quá trình bạn đã có để biết kỳ thi cuối kỳ cần đạt tối thiểu bao nhiêu điểm.")

            sim_c1, sim_c2, sim_c3 = st.columns(3)
            with sim_c1:
                sim_tdl = st.number_input("Điểm TDL hiện có (5%)", 0.0, 10.0, 9.0, step=0.5, key="sim_tdl")
            with sim_c2:
                sim_tbtn1 = st.number_input("Điểm TBTN1 hiện có (15%)", 0.0, 10.0, 8.0, step=0.5, key="sim_tbtn1")
            with sim_c3:
                sim_tbkt = st.number_input("Điểm TBKT hiện có (30%)", 0.0, 10.0, 7.5, step=0.5, key="sim_tbkt")

            diem_qt = round(sim_tdl * 0.05 + sim_tbtn1 * 0.15 + sim_tbkt * 0.30, 2)
            st.info(f"📌 Điểm tích lũy quá trình (50% trọng số) hiện tại của bạn là: **{diem_qt} / 5.00 điểm**")

            targets = [
                ("Qua môn (Điểm D - 4.0)", 4.0),
                ("Mức Trung bình (Điểm C - 5.5)", 5.5),
                ("Mức Khá (Điểm B - 7.0)", 7.0),
                ("Mức Giỏi (Điểm A - 8.5)", 8.5)
            ]

            t_cols = st.columns(4)
            for idx, (label, target_score) in enumerate(targets):
                needed_thi = round((target_score - diem_qt) / 0.5, 2)
                with t_cols[idx]:
                    if needed_thi <= 0:
                        st.metric(label, "0.0 điểm", "Đã chắc chắn đạt")
                    elif needed_thi <= 10.0:
                        st.metric(label, f"{needed_thi} điểm", f"Cần tối thiểu {needed_thi}")
                    else:
                        st.metric(label, "Không khả thi", f"Vượt thang 10 ({needed_thi})", delta_color="inverse")

        # ==============================================================
        # TAB 3: PHÂN LOẠI HÀNG LOẠT & THỐNG KÊ KPI LỚP HỌC
        # ==============================================================
        with tab3:
            st.subheader("Tải lên danh sách điểm lớp học (Excel / CSV)")
            uploaded_file = st.file_uploader("Chọn file chứa các cột: TDL, TBTN1, TBKT, THI", type=["csv", "xlsx"])

            if uploaded_file is not None:
                try:
                    if uploaded_file.name.endswith('.csv'):
                        input_df = pd.read_csv(uploaded_file)
                    else:
                        input_df = pd.read_excel(uploaded_file)

                    req_cols = ['TDL', 'TBTN1', 'TBKT', 'THI']
                    if all(col in input_df.columns for col in req_cols):
                        X_batch = input_df[req_cols]
                        X_batch_scaled = scaler.transform(X_batch)
                        preds = model.predict(X_batch_scaled)

                        class_names = ['Yếu', 'Trung bình', 'Khá', 'Giỏi', 'Xuất sắc']
                        input_df['DiemTongKet_10'] = (
                            input_df['TDL'] * 0.05 + input_df['TBTN1'] * 0.15 +
                            input_df['TBKT'] * 0.30 + input_df['THI'] * 0.50
                        ).round(2)
                        input_df['XepLoai'] = [class_names[i] for i in preds]

                        # 4 Thẻ KPI Tổng quan lớp học
                        total_sv = len(input_df)
                        avg_class = round(input_df['DiemTongKet_10'].mean(), 2)
                        passed_sv = len(input_df[input_df['DiemTongKet_10'] >= 4.0])
                        pass_rate = round((passed_sv / total_sv) * 100, 1) if total_sv > 0 else 0
                        weak_sv = len(input_df[input_df['XepLoai'] == 'Yếu'])

                        k1, k2, k3, k4 = st.columns(4)
                        k1.metric("Sĩ số lớp học", f"{total_sv} SV")
                        k2.metric("Điểm TB Cả lớp", f"{avg_class} / 10")
                        k3.metric("Tỷ lệ Đạt (>= 4.0)", f"{pass_rate}%")
                        k4.metric("Nhóm nguy cơ (Yếu)", f"{weak_sv} SV", delta_color="inverse")

                        st.markdown("---")
                        c_chart, c_table = st.columns([1.2, 2])
                        with c_chart:
                            st.write("**Phân bố xếp loại cả lớp:**")
                            dist_counts = input_df['XepLoai'].value_counts().reindex(class_names, fill_value=0)
                            st.bar_chart(dist_counts)
                        with c_table:
                            st.write("**Chi tiết kết quả từng sinh viên:**")
                            st.dataframe(input_df, use_container_width=True, height=320)

                        csv = input_df.to_csv(index=False).encode('utf-8-sig')
                        st.download_button("📥 Tải về file kết quả lớp học (CSV)", data=csv, file_name="Ket_Qua_Xep_Loai_Lop_ICTU.csv", mime="text/csv")
                    else:
                        st.error("⚠️ File tải lên thiếu các cột bắt buộc: TDL, TBTN1, TBKT, THI")
                except Exception as ex:
                    st.error(f"⚠️ Lỗi đọc file: {ex}")

        # ==============================================================
        # TAB 4: LỊCH SỬ, BIỂU ĐỒ GPA & MÔ PHỎNG HỌC CẢI THIỆN
        # ==============================================================
        with tab4:
            st.subheader(f"Hồ sơ học tập tích lũy của {user['full_name']} ({user['mssv']})")
            records = db.get_records_by_mssv(user['mssv'])

            if records:
                columns = [
                    "ID", "Tên học phần", "Số TC", "TDL", "TBTN1", "TBKT", "THI",
                    "Điểm Hệ 10", "Điểm Hệ 4", "Điểm Chữ", "Xếp Loại", "Thời gian lưu"
                ]
                df_records = pd.DataFrame(records, columns=columns)

                passed_df = df_records[df_records["Điểm Hệ 4"] > 0]
                total_credits = int(passed_df["Số TC"].sum())
                total_points = (passed_df["Điểm Hệ 4"] * passed_df["Số TC"]).sum()
                gpa_tich_luy = round(total_points / total_credits, 2) if total_credits > 0 else 0.0
                xep_loai_toan_khoa = classify_gpa_ictu(gpa_tich_luy)

                g1, g2, g3 = st.columns(3)
                g1.metric("Tổng tín chỉ tích lũy (Đạt)", f"{total_credits} TC")
                g2.metric("Điểm Trung Bình Tích Lũy (GPA)", f"{gpa_tich_luy:.2f} / 4.00")
                g3.metric("Xếp Loại Học Lực Tích Lũy", xep_loai_toan_khoa)

                # Biểu đồ phổ điểm chữ và xu hướng điểm số
                st.markdown("---")
                ch1, ch2 = st.columns(2)
                with ch1:
                    st.write("**Phổ điểm chữ (A, B, C, D, F):**")
                    grade_counts = df_records["Điểm Chữ"].value_counts().reindex(['A', 'B', 'C', 'D', 'F'], fill_value=0)
                    st.bar_chart(grade_counts)
                with ch2:
                    st.write("**Biểu đồ biến động điểm Hệ 10 qua các môn:**")
                    trend_df = df_records.iloc[::-1].set_index("Tên học phần")[["Điểm Hệ 10"]]
                    st.line_chart(trend_df)

                # Bộ mô phỏng nâng hạng GPA khi học cải thiện
                with st.expander("🚀 Mô phỏng nâng hạng GPA nếu đăng ký học cải thiện"):
                    improvable = [r for r in records if r[8] < 4.0]
                    if improvable:
                        imp_options = {f"{r[1]} ({r[2]} TC - Hiện tại: {r[9]} / {r[8]})": r for r in improvable}
                        sel_imp_label = st.selectbox("Chọn học phần muốn học cải thiện:", list(imp_options.keys()))
                        sel_subj = imp_options[sel_imp_label]
                        
                        new_grade_map = {"B (3.0)": 3.0, "A (4.0)": 4.0}
                        target_new_label = st.radio("Mục tiêu điểm mới sau khi học cải thiện:", list(new_grade_map.keys()), horizontal=True)
                        new_score_4 = new_grade_map[target_new_label]
                        
                        if new_score_4 > sel_subj[8]:
                            # Nếu môn cũ bị F (0.0) thì được cộng thêm cả tín chỉ và điểm; nếu D/C/B thì thay thế điểm cũ
                            if sel_subj[8] == 0.0:
                                sim_credits = total_credits + sel_subj[2]
                                sim_points = total_points + (new_score_4 * sel_subj[2])
                            else:
                                sim_credits = total_credits
                                sim_points = total_points - (sel_subj[8] * sel_subj[2]) + (new_score_4 * sel_subj[2])
                            
                            new_gpa = round(sim_points / sim_credits, 2)
                            diff_gpa = round(new_gpa - gpa_tich_luy, 2)
                            st.success(f"📈 GPA tích lũy dự kiến sẽ tăng từ **{gpa_tich_luy:.2f}** lên **{new_gpa:.2f}** (+{diff_gpa:.2f}) — Xếp loại mới: **{classify_gpa_ictu(new_gpa)}**")
                        else:
                            st.warning("Vui lòng chọn mức điểm mục tiêu cao hơn điểm hiện tại của học phần.")
                    else:
                        st.success("Tất cả các học phần của bạn đều đã đạt điểm A tối đa!")

                st.markdown("---")
                st.write("**Danh sách chi tiết các học phần đã lưu:**")
                st.dataframe(df_records.drop(columns=["ID"]), use_container_width=True)

                act_c1, act_c2 = st.columns([2, 2])
                with act_c1:
                    export_csv = df_records.drop(columns=["ID"]).to_csv(index=False).encode('utf-8-sig')
                    st.download_button(
                        "📥 Xuất Bảng Điểm Cá Nhân (CSV)",
                        data=export_csv,
                        file_name=f"Bang_Diem_{user['mssv']}.csv",
                        mime="text/csv",
                        use_container_width=True
                    )
                with act_c2:
                    record_options = {f"#{r[0]} - {r[1]} ({r[7]} điểm)": r[0] for r in records}
                    selected_to_del = st.selectbox("Chọn bản ghi muốn xóa", list(record_options.keys()), label_visibility="collapsed")
                    if st.button("🗑️ Xóa bản ghi đã chọn", use_container_width=True):
                        db.delete_record(record_options[selected_to_del])
                        st.rerun()
            else:
                st.info("Chưa có dữ liệu điểm nào được lưu cho tài khoản này. Hãy thực hiện dự đoán ở tab đầu tiên để lưu lịch sử!")

        # ==============================================================
        # TAB 5: CỔNG TRỢ LÝ SINH VIÊN ICTU (iBot)
        # ==============================================================
        with tab5:
            head_bot1, head_bot2 = st.columns([3.5, 1.5])
            with head_bot1:
                st.subheader("💬 Cổng Tư Vấn & Hỗ Trợ Sinh Viên ICTU")
                st.caption("Kết nối trực tiếp với hệ thống hỗ trợ thông tin đào tạo của Nhà trường.")
            with head_bot2:
                st.write("")
                st.link_button(
                    "↗️ BOT CHAT",
                    url="https://ibot.ictu.edu.vn/",
                    use_container_width=True
                )

            components.iframe(
                "https://ibot.ictu.edu.vn/",
                height=650,
                scrolling=True
            )

    except Exception as e:
        st.error("⚠️ Chưa tìm thấy file mô hình! Vui lòng chạy lệnh 'python main.py' trong Terminal trước.")

# ==========================================
# ĐIỀU HƯỚNG HIỂN THỊ CHÍNH
# ==========================================
if st.session_state.logged_in:
    show_main_dashboard()
else:
    show_auth_page()