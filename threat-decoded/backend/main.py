from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import os

from database import init_db

from routes.inbound import router as inbound_router
from routes.review import router as review_router

app = FastAPI(title="Threat Decoded", version="0.3.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Email pipeline routes
app.include_router(inbound_router)
app.include_router(review_router)

# Admin page
_admin_dir = os.path.join(os.path.dirname(__file__), "..", "admin")
if os.path.isdir(_admin_dir):
    app.mount("/admin", StaticFiles(directory=_admin_dir, html=True), name="admin")


@app.on_event("startup")
def on_startup():
    init_db()


@app.get("/")
def health():
    return {"status": "ok", "service": "threat-decoded"}
