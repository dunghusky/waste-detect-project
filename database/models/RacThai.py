from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from database.connect_db._database_mysql import Base


class RacThai(Base):
    __tablename__ = "RacThai"

    maRacThai = Column(Integer, primary_key=True, autoincrement=True)
    tenRacThai = Column(String(1000), nullable=False)
    ghiChu = Column(String(1000))
    hinhAnh = Column(String(1000))
    maRacThaiQuyChieu = Column(String(1000), nullable=False)
    maDanhMuc = Column(
        Integer,
        ForeignKey(
            "DanhMucPhanLoaiRac.maDanhMuc", ondelete="CASCADE", onupdate="CASCADE"
        ),
    )

    danhmucphanloai = relationship(
        "DanhMucPhanLoaiRac", back_populates="racthais", lazy="joined"
    )
    ctxlyracs = relationship("ChiTietXuLyRac", back_populates="racthai")
