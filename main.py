from fastapi import FastAPI
from database.connect_db._database_mysql import engine, Base
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
from database.router import _user
from model.router import _detect_object
from database.models import (
    Camera,
    ChiTietXuLyRac,
    DanhMucMoHinh,
    DanhMucPhanLoaiRac,
    RacThai,
    User,
    VideoXuLy,
)

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "*",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(_user.router)
app.include_router(_detect_object.router)

Base.metadata.create_all(bind=engine)  # Tạo lại các bảng mới nhất


# Khởi tạo các router cho API
# app.include_router(...)
if __name__ == "__main__":
    uvicorn.run(
        app,
        host="127.0.0.1",
        port=8000,
        limit_concurrency=1000,
        timeout_keep_alive=3600,  # Tăng thời gian chờ kết nối lên 1 giờ (3600 giây)
    )
