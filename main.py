from fastapi import FastAPI, Path

from src.contacts.routers import router as contacts_router

app = FastAPI()

app.include_router(router=contacts_router, prefix="/contacts", tags=["contacts"])

@app.get("/ping")
async def ping():
    return {"message": "pong"}





