from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import os

from config import FRONTEND_ORIGIN
from db import init_db
from database import init_db as init_db_v2

from routes import analyze, reports, campaigns, profile, chat, training, dashboard
from routes.inbound import router as inbound_router
from routes.review import router as review_router

app = FastAPI(title="Threat Decoded", version="0.2.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Original routes
app.include_router(analyze.router, prefix="/api")
app.include_router(reports.router, prefix="/api")
app.include_router(campaigns.router, prefix="/api")
app.include_router(profile.router, prefix="/api")
app.include_router(chat.router, prefix="/api")
app.include_router(training.router, prefix="/api")
app.include_router(dashboard.router, prefix="/api")

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
    init_db_v2()


@app.get("/")
def health():
    return {"status": "ok", "service": "threat-decoded"}
