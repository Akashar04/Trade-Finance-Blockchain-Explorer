from fastapi import FastAPI
from app.api.routes import auth

app = FastAPI(title="Trade Finance Blockchain Explorer")

app.include_router(auth.router)
