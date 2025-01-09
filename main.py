from fastapi import FastAPI
from database.connect_db._database_mysql import engine, Base
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
from database.router import _user, _rac_thai, _danh_muc_plr, _camera, _ctxl_rac, _danh_muc_mh, _video_xu_ly
from yolo_model.router import _detect_object, _detect_img


app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "*", "https://waste-detect.vercel.app"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(_user.router)
app.include_router(_detect_object.router)
app.include_router(_rac_thai.router)
app.include_router(_danh_muc_plr.router)
app.include_router(_camera.router)
app.include_router(_ctxl_rac.router)
app.include_router(_danh_muc_mh.router)
app.include_router(_video_xu_ly.router)
app.include_router(_detect_img.router)

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
