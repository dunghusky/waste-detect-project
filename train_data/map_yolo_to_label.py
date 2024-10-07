def map_yolo_to_label(yolo_label):
    """
    Hàm ánh xạ nhãn từ YOLO sang nhãn số (0, 1, 2).
    """
    yolo_to_category = {
        "chai-nhua": 0,
        "chai-lo-manh-vo-thuy-tinh": 0,
        "lon-nuoc-giai-khat-bang-kim-loai": 0,
        "hop-sua": 1,  # rac-vo-co
        "khau-trang": 1,
        "ly-nhua": 1,
        "tui-nilon": 1,
        "rac-huu-co": 2,  # rac-huu-co
    }
    return yolo_to_category.get(yolo_label, -1)
