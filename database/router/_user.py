from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from database.models.User import User
from database.schemas._user import Login
from database.connect_db._database_mysql import SessionLocal
from database.dependencies.dependencies import get_db
from fastapi.responses import JSONResponse


router = APIRouter(
    prefix="/api/v1/user",
    tags=["user"],
)
@router.post("/login")
@router.post("/login/")
async def login(user: Login, db: Session = Depends(get_db)):
    try:
        # Kiểm tra nếu email tồn tại trong cơ sở dữ liệu
        user_in_db = (
            db.query(User)
            .filter(User.userName == user.user_name, User.password == user.password)
            .first()
        )
        print(user_in_db)
        # Kiểm tra nếu không tìm thấy user
        if user_in_db is None:
            # Trả về lỗi nếu username hoặc password sai
            return JSONResponse({"status": 400, "message": "Tên đăng nhập hoặc mật khẩu không đúng!"})

        response = JSONResponse({"status": 200, "message": "Đăng nhập thành công!"})

        return response
    except Exception as e:
        # Trả về lỗi hệ thống
        return JSONResponse({"status": 500, "message": "Lỗi hệ thống!"})
