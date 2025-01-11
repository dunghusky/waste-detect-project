import pandas as pd


def create_waste_classification_csv(
    output_csv="./train_data/garbage_classification/create_csv/waste_classification.csv",
):
    """
    Hàm tạo tập dữ liệu phân loại rác và lưu vào file CSV.

    Args:
    - output_csv (str): Tên file CSV đầu ra. Mặc định là "waste_classification.csv".

    Outputs:
    - Tạo file CSV chứa tập dữ liệu phân loại rác với các nhãn và loại rác tương ứng.
    """
    data = {
        'Object_Label': [
            'chai-lo-manh-vo-thuy-tinh', 'chai-nhua', 'lon-nuoc-giai-khat-bang-kim-loai',
            'hop-sua', 'khau-trang', 'ly-nhua', 'tui-nilon',
            'rac-huu-co'
        ],
        'Waste_Category': [
            'rac-tai-che', 'rac-tai-che', 'rac-tai-che',
            'rac-vo-co', 'rac-vo-co', 'rac-vo-co', 'rac-vo-co',
            'rac-huu-co'
        ],
        'Category_Label': [0, 0, 0, 1, 1, 1, 1, 2]  # 0: rac-tai-che, 1: rac-vo-co, 2: rac-huu-co
    }

    # Tạo DataFrame từ dữ liệu
    df = pd.DataFrame(data)

    # Lưu DataFrame vào file CSV
    df.to_csv(output_csv, index=False)

    print(f"Tập dữ liệu phân loại rác đã được tạo và lưu tại '{output_csv}'.")
