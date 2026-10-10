"""Start the chatbot:   python run.py   then open http://127.0.0.1:8000"""
import uvicorn

import config

if __name__ == "__main__":
    print(f"\n  AI Scooty chatbot is starting...\n  Open this in your browser:  http://{config.HOST}:{config.PORT}\n")
    uvicorn.run("app.main:app", host=config.HOST, port=config.PORT, reload=False)
