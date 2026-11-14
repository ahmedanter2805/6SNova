import sys
import os

root_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
if root_dir not in sys.path:
    sys.path.insert(0, root_dir)

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from backend.server import api_telegram_subscribers

app = FastAPI()
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_credentials=True, allow_methods=["*"], allow_headers=["*"])

app.get("/")(api_telegram_subscribers)
app.get("/subscribers")(api_telegram_subscribers)
app.get("/api/telegram/subscribers")(api_telegram_subscribers)
