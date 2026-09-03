from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.routes import router
from app.api.routes_chat import router as chat_router
from app.api.routes_approval import router as approval_router
app = FastAPI(title="Enterprise AI Ops Assistant")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:8501"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.include_router(router)
app.include_router(chat_router)
app.include_router(approval_router)

@app.get("/")
def root():
    return {"message": "Enterprise AI Ops Assistant API is running"}


@app.get("/health")
def health():
    return {"status": "healthy"}