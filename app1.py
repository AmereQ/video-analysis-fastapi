from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from starlette.requests import Request
import cv2  # OpenCV for video processing
import asyncio
import threading
import queue
import uvicorn

app = FastAPI()
templates = Jinja2Templates(directory="templates")

video_queue = queue.Queue()

class WebSocketManager:
    def __init__(self):
        self.websocket = None
        self.video_thread = threading.Thread(target=self.process_video)
        self.video_thread.start()

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.websocket = websocket
        try:
            while True:
                data = await websocket.receive_bytes()
                video_queue.put(data)
                print("Received video frame and added to queue")
        except WebSocketDisconnect:
            print("Client disconnected")
        except Exception as e:
            print(f"Unexpected error: {e}")

    def process_video(self):
        while True:
            frame_data = video_queue.get()
            if frame_data is None:
                break

            try:
                print("Processing video frame from queue")
                frame_array = np.frombuffer(frame_data, np.uint8)
                frame = cv2.imdecode(frame_array, cv2.IMREAD_COLOR)

                # Placeholder for Florence-2 model processing
                # Replace with actual Florence-2 processing code
                # Example: result = florence_model.process_frame(frame)

                result_text = "Detected object: Placeholder"  # Replace with actual result

                if self.websocket:
                    asyncio.run(self.websocket.send_text(result_text))
            except Exception as e:
                print(f"Error processing video frame: {e}")

websocket_manager = WebSocketManager()

@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    return templates.TemplateResponse("florecne2.html", {"request": request})

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket_manager.connect(websocket)

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)
