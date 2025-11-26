from fastapi import FastAPI, Request
from fastapi.responses import StreamingResponse, HTMLResponse
import base64
import asyncio

app = FastAPI()

# Store latest frame for each student
student_frames = {}


@app.post("/upload_frame")
async def upload_frame(request: Request):
    data = await request.json()
    student_id = data["student_id"]
    frame = base64.b64decode(data["frame"])

    student_frames[student_id] = frame
    return {"status": "ok"}


@app.get("/view/{student_id}")
async def view_stream(student_id: str):
    async def frame_generator():
        while True:
            if student_id in student_frames:
                frame = student_frames[student_id]
                yield (
                        b"--frame\r\n"
                        b"Content-Type: image/jpeg\r\n\r\n" + frame + b"\r\n"
                )
            await asyncio.sleep(0.05)

    return StreamingResponse(frame_generator(), media_type="multipart/x-mixed-replace; boundary=frame")


@app.get("/")
async def dashboard():
    html = """
    <html>
    <body>
        <h2>Available Students</h2>
        <ul>
    """
    for student in student_frames.keys():
        html += f'<li><a href="/view/{student}" target="_blank">{student}</a></li>'
    html += """
        </ul>
    </body>
    </html>
    """
    return HTMLResponse(html)
