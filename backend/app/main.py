from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from . import store
from .mcp_server import mcp


@asynccontextmanager
async def lifespan(app: FastAPI):
    async with mcp.session_manager.run():
        yield


app = FastAPI(title="NexusCart AI // Core Hub", lifespan=lifespan)
app.add_middleware(CORSMiddleware, allow_origins=["http://localhost:5173"],
                   allow_methods=["*"], allow_headers=["*"])


@app.get("/api/state")
def get_state():
    return store.snapshot()


@app.post("/api/reset")
def reset_state():
    store.reset()
    return {"ok": True}


app.mount("/mcp", mcp.streamable_http_app())