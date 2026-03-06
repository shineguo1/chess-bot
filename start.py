import sys
import os

os.chdir(r'f:\workspace\qq-bot')
sys.path.insert(0, r'f:\workspace\qq-bot')

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="127.0.0.1",
        port=8080,
        reload=False,
        log_level="info"
    )
