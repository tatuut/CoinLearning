"""FastAPI main application"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from backend.config import settings
from backend.api.jobs import router as jobs_router
import uvicorn

app = FastAPI(title="Grass Coin Trader API", version="1.0.0")

# CORS設定
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 全てのドメインを許可（開発用）
    allow_credentials=True,
    allow_methods=["*"],  # 全てのHTTPメソッドを許可
    allow_headers=["*"],  # 全てのヘッダーを許可
)

# ジョブAPIを登録
app.include_router(jobs_router, prefix="/api/jobs", tags=["jobs"])

@app.get("/")
async def root():
    return {"message": "Grass Coin Trader API", "version": "1.0.0"}

if __name__ == "__main__":
    uvicorn.run("backend.main:app", host=settings.FASTAPI_HOST, port=settings.FASTAPI_PORT, reload=True)
