import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

import uvicorn
from fastapi import FastAPI
from contextlib import asynccontextmanager

from app.database import init_db
from app.routers import auth, admin, workflow

@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    yield

app = FastAPI(title="ClinicVault Enterprise", lifespan=lifespan)

# Register Routers
app.include_router(auth.router)
app.include_router(admin.router)
app.include_router(workflow.router)

if __name__ == "__main__":
    uvicorn.run("app.main:app", host="127.0.0.1", port=8000, reload=True)