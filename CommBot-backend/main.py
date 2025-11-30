from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routers import qa, auth, chats
from db import init_db

app = FastAPI(title="LLM Agent Backend")
init_db()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/debug")
def debug():
    import os
    return {
        "cwd": os.getcwd(),
        "files_in_dir": os.listdir(),
        "router_loaded": [route.path for route in app.routes],
    }


app.include_router(qa.router)
app.include_router(auth.router)
app.include_router(chats.router)

@app.get("/")
def root():
    return {"status": "ok"}
