from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from config._config import settings

# Chuỗi kết nối tới MySQL
SQLALCHEMY_DATABASE_URL = settings.database_url

# Thêm connect_timeout và các thông số kết nối khác
engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={
        "connect_timeout": 30000,  # Thời gian timeout khi kết nối (giây)
        "autocommit": True,  # Tùy chọn thêm nếu cần
    },
    pool_pre_ping=True,  # Tự động kiểm tra kết nối trước khi sử dụng
    pool_recycle=28000,  # Tái sử dụng kết nối sau thời gian nhất định
)

# Tạo session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Khởi tạo Base cho các model kế thừa
Base = declarative_base()
