"""Job management API (Redis不要版 - BackgroundTasks使用)"""
from fastapi import APIRouter, BackgroundTasks
from pydantic import BaseModel
import uuid
from backend.api.job_manager import job_manager
from backend.workers.dummy_worker import dummy_job

router = APIRouter()

class JobRequest(BaseModel):
    symbol: str

@router.post("/start")
async def start_job(request: JobRequest, background_tasks: BackgroundTasks):
    """ジョブ開始（BackgroundTasks使用）"""

    # ジョブID生成
    job_id = str(uuid.uuid4())

    # ジョブ作成（SQLite）
    job_manager.create_job(job_id, request.symbol)

    # バックグラウンドタスク追加
    background_tasks.add_task(dummy_job, request.symbol, job_id)

    return {
        "job_id": job_id,
        "symbol": request.symbol,
        "message": "Job started"
    }

@router.get("/status/{job_id}")
async def get_status(job_id: str):
    """ジョブステータス確認"""
    job = job_manager.get_job(job_id)

    if not job:
        return {
            "job_id": job_id,
            "status": "not_found",
            "result": None
        }

    return {
        "job_id": job["job_id"],
        "status": job["status"],
        "result": job["result"]
    }

@router.get("/logs/{job_id}")
async def get_logs(job_id: str, offset: int = 0):
    """ジョブのログを取得（増分）"""

    # ジョブ情報取得
    job = job_manager.get_job(job_id)

    if not job:
        return {
            "job_id": job_id,
            "status": "not_found",
            "logs": [],
            "total_logs": 0,
            "has_more": False,
            "result": None
        }

    # ログ取得（offset以降）
    logs = job_manager.get_logs(job_id, offset)
    total_count = job_manager.get_log_count(job_id)

    return {
        "job_id": job_id,
        "status": job["status"],
        "logs": logs,
        "total_logs": total_count,
        "has_more": job["status"] not in ["finished", "failed"],
        "result": job["result"]
    }
