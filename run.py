import os
import sys
import subprocess

os.chdir(os.path.join(os.path.dirname(__file__), "backend"))
sys.path.insert(0, os.getcwd())

port = os.environ.get("PORT", "8000")
cmd = [
    "uvicorn",
    "app.main:app",
    "--host", "0.0.0.0",
    "--port", port,
    "--workers", "4",
    "--proxy-headers",
    "--forwarded-allow-ips", "*",
]
sys.exit(subprocess.call(cmd))
