from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from database.models.User import User
from database.schemas._user import Login
from database.connect_db._database_mysql import SessionLocal
from database.dependencies.dependencies import get_db
from datetime import datetime, timedelta
from fastapi.responses import JSONResponse

from datetime import datetime

router = APIRouter(
    prefix="/api/v1/user",
    tags=["user"],
)


@router.post("/login")
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
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Tên đăng nhập hoặc mật khẩu không đúng",
            )

        response = JSONResponse({"status": 200, "message": "Đăng nhập thành công"})

        return response
    except Exception as e:
        # Trả về lỗi hệ thống
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Lỗi hệ thống: {e}",
        )
