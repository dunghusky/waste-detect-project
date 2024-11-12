from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship
from database.connect_db._database_mysql import Base


class Camera(Base):
    __tablename__ = "Camera"

    maCamera = Column(Integer, primary_key=True, autoincrement=True)
    tenCamera = Column(String(1000), nullable=False)
    diaDiem = Column(String(1000), nullable=False)
    trangThaiHoatDong = Column(Integer, nullable=False, default=1)
    moTa =  Column(String(1000), nullable=False)

    videos = relationship("VideoXuLy", back_populates="camera")
