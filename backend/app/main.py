
from fastapi import FastAPI
from app.api.routes import router

app = FastAPI(
    title="AI Resume Screener",
    description="An AI-powered resume screening API with RAG",
    version="0.1.0",
)
app.include_router(router)

@app.get("/")
def root():
    return {"message": "AI Resume Screener API is running"}


@app.get("/health")
def health_check():
    return {"status": "healthy"}
