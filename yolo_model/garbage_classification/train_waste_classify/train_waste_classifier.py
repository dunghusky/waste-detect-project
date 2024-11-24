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

    # 2. Mã hóa nhãn Object_Label thành số (Label Encoding cho các nhãn YOLO)
    label_encoder_object = LabelEncoder()
    df["Object_Label_Encoded"] = label_encoder_object.fit_transform(df["Object_Label"])

    # Không cần mã hóa lại Waste_Category vì đã có nhãn `Category_Label` (0, 1, 2)
    X = df[["Object_Label_Encoded"]]
    y = df["Category_Label"]  # Sử dụng trực tiếp cột Category_Label từ CSV

    # 3. Chia dữ liệu thành train và test
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42
    )

    # 4. Huấn luyện mô hình Logistic Regression
    clf = LogisticRegression(random_state=42, max_iter=200)
    clf.fit(X_train, y_train)

    # 5. Đánh giá mô hình trên tập test
    y_pred = clf.predict(X_test)
    accuracy = accuracy_score(y_test, y_pred) * 100
    print(f"Độ chính xác của mô hình phân loại: {accuracy: .2f}%")

    # 6. Lưu các bộ mã hóa và mô hình để sử dụng sau này
    pickle.dump(clf, open(model_path, "wb"))
    pickle.dump(label_encoder_object, open("label_encoder_object.pkl", "wb"))

    print(f"Mô hình đã được lưu tại '{model_path}' và 'label_encoder_object.pkl'")


train_waste_classifier(
    "./create_csv/waste_classification.csv", "./train_waste_classify/waste_classifier_model.pkl"
)
