from graphviz import Digraph

# Tạo đối tượng Digraph
dot = Digraph("Business_Process_Diagram_Admin", format="png")

# Thêm các node cho quy trình nghiệp vụ
dot.node("Start", "Bắt đầu", shape="circle")
dot.node("Login", "Đăng nhập", shape="box")
dot.node("Check_Credentials", "Kiểm tra thông tin đăng nhập", shape="diamond")
dot.node("Success_Login", "Đăng nhập thành công", shape="box")
dot.node("Failure_Login", "Đăng nhập thất bại", shape="box")
dot.node("Access_Dashboard", "Truy cập Dashboard", shape="box")
dot.node("View_Models", "Xem mô hình nhận diện", shape="box")
dot.node("Manage_Models", "Quản lý mô hình nhận diện\n(Tạo, Sửa, Xóa)", shape="box")
dot.node("View_Data", "Xem dữ liệu rác thải", shape="box")
dot.node("CRUD_Data", "CRUD dữ liệu rác thải", shape="box")
dot.node("View_Reports", "Xem báo cáo", shape="box")
dot.node("Filter_Products", "Lọc sản phẩm", shape="box")
dot.node("View_Video", "Xem lại video đã phân loại", shape="box")
dot.node("Live_Tracking", "Xem livestream", shape="box")
dot.node("End", "Kết thúc", shape="circle")

# Kết nối các bước
dot.edge("Start", "Login")
dot.edge("Login", "Check_Credentials")
dot.edge("Check_Credentials", "Success_Login", label="Đúng")
dot.edge("Check_Credentials", "Failure_Login", label="Sai")
dot.edge("Success_Login", "Access_Dashboard")
dot.edge("Access_Dashboard", "View_Models")
dot.edge("Access_Dashboard", "View_Data")
dot.edge("Access_Dashboard", "View_Reports")
dot.edge("Access_Dashboard", "Filter_Products")
dot.edge("Access_Dashboard", "View_Video")
dot.edge("Access_Dashboard", "Live_Tracking")
dot.edge("View_Models", "Manage_Models")
dot.edge("View_Data", "CRUD_Data")
dot.edge("Manage_Models", "End")
dot.edge("CRUD_Data", "End")
dot.edge("View_Reports", "End")
dot.edge("Filter_Products", "End")
dot.edge("View_Video", "End")
dot.edge("Live_Tracking", "End")
dot.edge("Failure_Login", "End")

# Xuất sơ đồ
output_path = "./Admin_Business_Process_Diagram.png"
dot.render(output_path, format="png")
