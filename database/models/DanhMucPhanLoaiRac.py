from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship
from database.connect_db._database_mysql import Base


class DanhMucPhanLoaiRac(Base):
    __tablename__ = "DanhMucPhanLoaiRac"

    maDanhMuc = Column(Integer, primary_key=True, autoincrement=True)
    tenDanhMuc = Column(String(1000), nullable=False)

    racthais = relationship("RacThai", back_populates="danhmucphanloai")
