from fastapi import FastAPI, Query, WebSocket
from fastapi.responses import JSONResponse
import uvicorn

# from train_data.connect_webcam import connect_camera
from connect_webcam import connect_camera

app = FastAPI()


@app.post("/detect-stream")
def detect_stream(stream_url: str = Query(..., description="URL của luồng video HTTP")):
    try:
        # Gọi hàm `run_detection` với URL luồng video
        waste_label = connect_camera.run_detection(stream_url)
        if waste_label != -1:
            return waste_label
        else:
            return JSONResponse({"status": "error", "message": "Không nhận diện được rác"})
    except Exception as e:
        return JSONResponse({"status": "error", "message": str(e)})


@app.websocket("/detect-stream")
async def detect_stream(websocket: WebSocket, stream_url: str = Query(...)):
    """
    WebSocket API cho frontend hoặc phần cứng:
    - Gửi luồng video đã xử lý tới frontend.
    - Trả nhãn nhận diện tới phần cứng (qua JSON).
    """
    await websocket.accept()
    try:
        # Gọi hàm `run_detection` với WebSocket
        await connect_camera.run_detection(stream_url, websocket=websocket)
    except Exception as e:
        await websocket.send_json({"status": "error", "message": str(e)})
    finally:
        await websocket.close()


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
