from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from database.connect_db._database_mysql import Base


class ChiTietXuLyRac(Base):
    __tablename__ = "ChiTietXuLyRac"

    maVideo = Column(
        Integer,
        ForeignKey("VideoXuLy.maVideo", ondelete="CASCADE", onupdate="CASCADE"),
        primary_key=True,
    )
    maRacThai = Column(
        Integer,
        ForeignKey("RacThai.maRacThai", ondelete="CASCADE", onupdate="CASCADE"),
        primary_key=True,
    )
    SoLuongXuLy = Column(Integer, nullable=False)
    ghiChu = Column(String(1000))

    racthai = relationship("RacThai", back_populates="ctxlyracs")
    video = relationship("VideoXuLy", back_populates="ctxlyracs")
