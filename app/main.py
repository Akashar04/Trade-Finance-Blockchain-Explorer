from fastapi import FastAPI
from .database import engine
from .models import Base
from .routers import auth_router, document_router, transaction_router, user_router, analytics_router, export_router, admin_router


from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(debug=True)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

Base.metadata.create_all(bind=engine)

app.include_router(auth_router.router)
app.include_router(document_router.router)
app.include_router(transaction_router.router)
app.include_router(user_router.router)
app.include_router(analytics_router.router)
app.include_router(analytics_router.router)
app.include_router(export_router.router)
app.include_router(admin_router.router)

@app.get("/")
def root():
    return {"message": "Trade Finance Explorer Running"}