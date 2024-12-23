from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship
from database.connect_db._database_mysql import Base

class DanhMucMoHinh(Base):
    __tablename__ = "DanhMucMoHinh"

    maMoHinh = Column(Integer, primary_key=True, autoincrement=True)
    tenMoHinh = Column(String(1000), nullable=False, unique=True)
    duongDan = Column(String(1000))
    ghiChu = Column(String(1000))

    videos = relationship("VideoXuLy", back_populates="danhmucmohinh")
