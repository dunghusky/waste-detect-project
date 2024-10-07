import pandas as pd

data = {
    'Object_Label':[
        'chai-lo-manh-vo-thuy-tinh', 'chai-nhua', 'lon-nuoc-giai-khat-bang-kim-loai',
        'hop-sua', 'khau-trang', 'ly-nhua', 'tui-nilon',
        'rac-huu-co'
    ],
    'Waste_Category':[
        'rac-tai-che', 'rac-tai-che', 'rac-tai-che',
        'rac-vo-co', 'rac-vo-co', 'rac-vo-co', 'rac-vo-co',
        'rac-huu-co'
    ]
}

df = pd.DataFrame(data)

df.to_csv("waste_classification.csv", index=False)

print("Tập dữ liệu phân loại rác đã được tạo.")