"""Job management API"""
from fastapi import APIRouter
from pydantic import BaseModel
from redis import Redis
from rq import Queue
from backend.config import settings
from backend.workers.dummy_worker import dummy_job

router = APIRouter()

# Redis接続
redis_conn = Redis(host=settings.REDIS_HOST, port=settings.REDIS_PORT)
queue = Queue(connection=redis_conn)

class JobRequest(BaseModel):
    symbol: str

@router.post("/start")
async def start_job(request: JobRequest):
    """ジョブ開始"""

    # Step 1: まずjob_idなしでエンキュー（job_idを取得するため）
    temp_job = queue.enqueue(
        dummy_job,
        args=(request.symbol,),
        kwargs={"job_id": None},
        job_timeout='10m'
    )

    # Step 2: 一旦キャンセル
    temp_job.cancel()

    # Step 3: 正しいjob_idを渡して再エンキュー
    job = queue.enqueue(
        dummy_job,
        args=(request.symbol,),
        kwargs={"job_id": temp_job.id},
        job_id=temp_job.id,  # ← 同じIDを使う
        job_timeout='10m'
    )

    return {
        "job_id": job.id,
        "symbol": request.symbol,
        "message": "Job started"
    }

@router.get("/status/{job_id}")
async def get_status(job_id: str):
    """ジョブステータス確認"""
    from rq.job import Job
    try:
        job = Job.fetch(job_id, connection=redis_conn)
        return {
            "job_id": job.id,
            "status": job.get_status(),
            "result": job.result if job.is_finished else None
        }
    except:
        return {
            "job_id": job_id,
            "status": "not_found",
            "result": None
        }

@router.get("/logs/{job_id}")
async def get_logs(job_id: str, offset: int = 0):
    """ジョブのログを取得（増分）"""

    # Redisからログを取得（offset以降）
    logs = redis_conn.lrange(f"logs:{job_id}", offset, -1)
    logs = [log.decode('utf-8') for log in logs]

    # ジョブステータスも一緒に返す
    from rq.job import Job
    try:
        job = Job.fetch(job_id, connection=redis_conn)
        status = job.get_status()
        result = job.result if job.is_finished else None
    except:
        status = "not_found"
        result = None

    return {
        "job_id": job_id,
        "status": status,
        "logs": logs,
        "total_logs": offset + len(logs),
        "has_more": status not in ["finished", "failed", "not_found"],
        "result": result
    }
