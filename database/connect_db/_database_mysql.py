from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from _config import settings

# Chuỗi kết nối tới MySQL
SQLALCHEMY_DATABASE_URL = settings.database_url

# Tạo engine kết nối tới MySQL, không cần tham số encoding
engine = create_engine(SQLALCHEMY_DATABASE_URL)

# Tạo session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Khởi tạo Base cho các model kế thừa
Base = declarative_base()
