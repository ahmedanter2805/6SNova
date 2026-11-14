import os
import sys
import uvicorn
from dotenv import load_dotenv

# Load environment variables (.env)
load_dotenv()

# Ensure backend folder is in path
backend_path = os.path.join(os.path.dirname(__file__), "backend")
if backend_path not in sys.path:
    sys.path.insert(0, backend_path)

from server import app

if __name__ == "__main__":
    print("=" * 60)
    print("  TrendLens | NASA Earth System Trend Detective")
    print("  Server starting on: http://127.0.0.1:8000")
    print("=" * 60)
    uvicorn.run("server:app", host="127.0.0.1", port=8000, reload=True, reload_dirs=[backend_path], log_level="info")

