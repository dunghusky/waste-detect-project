from fastapi import FastAPI, Query
import uvicorn

from train_data.connect_webcam import connect_camera

app = FastAPI()


@app.get("/detect-stream")
def detect_stream(stream_url: str = Query(..., description="URL của luồng video HTTP")):
    try:
        # Gọi hàm `run_detection` với URL luồng video
        waste_label = connect_camera.run_detection(stream_url)
        if waste_label != -1:
            return {"status": "success", "waste_label": waste_label}
        else:
            return {"status": "error", "message": "Không nhận diện được rác"}
    except Exception as e:
        return {"status": "error", "message": str(e)}


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
