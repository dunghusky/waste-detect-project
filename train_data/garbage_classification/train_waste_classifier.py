import pandas as pd
from sklearn.metrics import accuracy_score
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder
from sklearn.linear_model import LogisticRegression
import pickle

def train_waste_classifier(csv_file, model_path = 'waste_classifier_model.pkl'):
    """
    Hàm huấn luyện mô hình Logistic Regression cho phân loại rác thải.

    Args:
    - csv_file (str): Đường dẫn đến file CSV chứa dữ liệu huấn luyện.
    - model_path (str): Đường dẫn lưu mô hình và các bộ mã hóa (dạng .pkl).

    Outputs:
    - In ra độ chính xác của mô hình.
    - Lưu mô hình và các bộ mã hóa thành các file .pkl.
    """
    # 1. Đọc dữ liệu từ file CSV
    df = pd.read_csv(csv_file)

    # 2. Mã hóa các nhãn thành các số (Label Encoding)
    label_encoder_object = LabelEncoder()
    label_encoder_category = LabelEncoder()

    # Biến đổi Object_Label và Waste_Category thành các số để huấn luyện
    df['Object_Label_Encoded'] = label_encoder_object.fit_transform(df['Object_Label'])
    df['Category_Label_Encoded'] = label_encoder_category.fit_transform(df['Waste_Category'])

    # 3. Chia dữ liệu thành train và test
    X = df[['Object_Label_Encoded']]
    y = df['Category_Label_Encoded']

    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

    # 4. Huấn luyện mô hình Logistic Regression
    clf = LogisticRegression(random_state=42, max_iter=200) # max_iter=200 để đảm bảo hội tụ
    clf.fit(X_train, y_train)

    # 5. Đánh giá mô hình trên tập test
    y_pred = clf.predict(X_test)
    accuracy = accuracy_score(y_test, y_pred)*100
    print(f"Độ chính xác của mô hình phân loại: {accuracy: .2f}%")

    # 6. Lưu các bộ mã hóa và mô hình để sử dụng sau này
    pickle.dump(clf, open(model_path, "wb"))
    pickle.dump(label_encoder_object, open("lable_encoder_object.pkl", "wb"))
    pickle.dump(label_encoder_category, open("lable_encoder_Category.pkl", "wb"))

    print(f"Mô hình đã được lưu tại '{model_path}', 'label_encoder_object.pkl', và 'label_encoder_category.pkl'")


# train_waste_classifier("waste_classification.csv", "waste_classifier_model.pkl")
