from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from database.connect_db._database_mysql import Base


class VideoXuLy(Base):
    __tablename__ = "VideoXuLy"

    maVideo = Column(Integer, primary_key=True, autoincrement=True)
    tenVideo = Column(String(1000), nullable=False)
    thoiLuong = Column(String(1000), nullable=False)
    ngayBatDauQuay = Column(String(1000), nullable=False)
    ngayKetThuc = Column(String(1000), nullable=False)
    moTa = Column(String(1000), nullable=False)
    duongDan = Column(String(1000), nullable=False)
    maCamera = Column(Integer, ForeignKey("Camera.maCamera"))
    maMoHinh = Column(Integer, ForeignKey("DanhMucMoHinh.maMoHinh"))

    camera = relationship("Camera", back_populates="videos")
    danhmucmohinh = relationship("DanhMucMoHinh", back_populates="videos")
    ctxlyracs = relationship("ChiTietXuLyRac", back_populates="video")
