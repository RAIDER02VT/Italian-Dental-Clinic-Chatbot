import os
from fastapi import FastAPI, Request
from fastapi.responses import FileResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from app.routes.chat import router as chat_route

app = FastAPI(
    title="Chat Assistente Edile",
    description="API per assistente virtuale Marinetti Edilizia",
    version="1.0.0"
)

@app.middleware("http")
async def add_private_network_header(request: Request, call_next):
    response = await call_next(request)
    response.headers["Access-Control-Allow-Private-Network"] = "true"
    return response

app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://probable-meme-wr9wr7p75w5wcwj4-5173.app.github.dev"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(chat_route, prefix="/api")

# ✅ Solo se esiste la cartella build/static, monta React
static_dir = "frontend/build/static"
if os.path.isdir(static_dir):
    app.mount("/static", StaticFiles(directory=static_dir), name="static")

# 🏠 Serve index.html solo se esiste
@app.get("/{full_path:path}")
async def serve_react_app():
    index_path = os.path.join("frontend", "build", "index.html")
    if os.path.exists(index_path):
        return FileResponse(index_path)
    return JSONResponse(
        status_code=404,
        content={"message": "⚠️ Frontend non buildato. Esegui `npm run build` prima di mettere online."}
    )
