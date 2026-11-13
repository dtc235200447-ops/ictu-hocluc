import os
import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import classification_report, accuracy_score, f1_score
import joblib

# Các thuật toán Machine Learning
from sklearn.neighbors import KNeighborsClassifier
from sklearn.svm import SVC
from sklearn.tree import DecisionTreeClassifier
from sklearn.ensemble import RandomForestClassifier
from sklearn.naive_bayes import GaussianNB

# Tạo thư mục lưu trữ
os.makedirs('data', exist_ok=True)
os.makedirs('models', exist_ok=True)

print("[1/4] Khởi tạo bộ dữ liệu học tập chuẩn ICTU...")
np.random.seed(42)
n_samples = 1000

# Sinh dữ liệu ngẫu nhiên cho các cột điểm thành phần (Thang 10)
tdl = np.random.uniform(5.0, 10.0, n_samples).round(1)    # Ý thức/Thái độ (5%)
tbtn1 = np.random.uniform(2.0, 10.0, n_samples).round(1)  # Kiểm tra thường xuyên (15%)
tbkt = np.random.uniform(2.0, 10.0, n_samples).round(1)   # Kiểm tra kỹ năng (30%)
thi = np.random.uniform(1.0, 10.0, n_samples).round(1)    # Thi kết thúc học phần (50%)

df = pd.DataFrame({
    'TDL': tdl,
    'TBTN1': tbtn1,
    'TBKT': tbkt,
    'THI': thi
})

# 1. Tính Điểm Học phần (Thang 10) theo quy chế ICTU
df['DiemHP_10'] = (df['TDL'] * 0.05 + df['TBTN1'] * 0.15 + df['TBKT'] * 0.30 + df['THI'] * 0.50).round(2)

# 2. Quy đổi Thang 10 sang Thang 4
def quy_doi_thang_4(score):
    if score >= 8.5:
        return 4.0
    elif score >= 7.0:
        return 3.0
    elif score >= 5.5:
        return 2.0
    elif score >= 4.0:
        return 1.0
    else:
        return 0.0

df['DiemHP_4'] = df['DiemHP_10'].apply(quy_doi_thang_4)

# 3. Phân loại Học lực dựa trên điểm hệ 4
def xep_loai_ictu(gpa):
    if gpa >= 3.6:
        return 4  # Xuất sắc
    elif gpa >= 3.2:
        return 3  # Giỏi
    elif gpa >= 2.5:
        return 2  # Khá
    elif gpa >= 2.0:
        return 1  # Trung bình
    else:
        return 0  # Yếu

df['HocLuc'] = df['DiemHP_4'].apply(xep_loai_ictu)
df.to_csv('data/students.csv', index=False)
print("-> Đã lưu bộ dữ liệu chuẩn vào 'data/students.csv'")

print("\n[2/4] Tiền xử lý dữ liệu...")
X = df[['TDL', 'TBTN1', 'TBKT', 'THI']]
y = df['HocLuc']

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42, stratify=y)

scaler = StandardScaler()
X_train_scaled = scaler.fit_transform(X_train)
X_test_scaled = scaler.transform(X_test)

joblib.dump(scaler, 'models/scaler.pkl')

print("\n[3/4] Huấn luyện & So sánh 5 thuật toán Machine Learning...")
models = {
    'KNN': KNeighborsClassifier(),
    'SVM': SVC(),
    'Decision Tree': DecisionTreeClassifier(random_state=42),
    'Random Forest': RandomForestClassifier(random_state=42),
    'Naive Bayes': GaussianNB()
}

results = []
best_model = None
best_f1 = -1
best_model_name = ""

for name, model in models.items():
    model.fit(X_train_scaled, y_train)
    y_pred = model.predict(X_test_scaled)
    
    acc = accuracy_score(y_test, y_pred)
    f1 = f1_score(y_test, y_pred, average='macro')
    
    results.append({'Algorithm': name, 'Accuracy': round(acc, 4), 'F1-Macro': round(f1, 4)})
    
    if f1 > best_f1:
        best_f1 = f1
        best_model = model
        best_model_name = name

results_df = pd.DataFrame(results).sort_values(by='F1-Macro', ascending=False)
print("\n--- BẢNG SO SÁNH HIỆU NĂNG MÔ HÌNH ---")
print(results_df.to_string(index=False))

print(f"\n[4/4] Mô hình xuất sắc nhất: {best_model_name}")
joblib.dump(best_model, 'models/best_model.pkl')

y_pred_best = best_model.predict(X_test_scaled)
target_names = ['Yếu', 'Trung bình', 'Khá', 'Giỏi', 'Xuất sắc']
present_classes = np.unique(np.concatenate((y_test, y_pred_best)))
labels_to_show = [target_names[i] for i in present_classes]

print("\n--- BÁO CÁO CHI TIẾT (CLASSIFICATION REPORT) ---")
print(classification_report(y_test, y_pred_best, labels=present_classes, target_names=labels_to_show))