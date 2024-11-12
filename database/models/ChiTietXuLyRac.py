from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from database.connect_db._database_mysql import Base


class ChiTietXuLyRac(Base):
    __tablename__ = "ChiTietXuLyRac"

    maVideo = Column(Integer, ForeignKey("VideoXuLy.maVideo"), primary_key=True)
    maRacThai = Column(Integer, ForeignKey("RacThai.maRacThai"), primary_key=True)
    SoLuongXuLy = Column(String(1000), nullable=False)
    ghiChu = Column(String(1000), nullable=False)

    racthai = relationship("RacThai", back_populates="ctxlyracs")
    video = relationship("VideoXuLy", back_populates="ctxlyracs")
