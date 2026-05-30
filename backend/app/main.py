from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/api/analyze")
async def analyze(image: UploadFile = File(...)):
    contents = await image.read()
    return {
        "filename": image.filename,
        "size_bytes": len(contents),
        "message": "受け取り成功。分析はcoming soon"
    }