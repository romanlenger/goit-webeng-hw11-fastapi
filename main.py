from fastapi import FastAPI, Path

from src.contacts.routers import router as contacts_router
from src.auth.routers import router as auth_routers

app = FastAPI()

app.include_router(router=contacts_router, prefix="/contacts", tags=["contacts"])
app.include_router(router=auth_routers, prefix="/auth", tags=["auth"])

@app.get("/ping")
async def ping():
    return {"message": "pong"}







