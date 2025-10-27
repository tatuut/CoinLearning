"""Phase 2: ダミーワーカー（Claude Code実行をシミュレート）"""
import time
from redis import Redis
from backend.config import settings

def dummy_job(symbol: str, job_id: str = None):
    """Claude Code実行をシミュレート（3ステップ、計5秒）"""

    # Redis接続
    redis_conn = Redis(host=settings.REDIS_HOST, port=settings.REDIS_PORT)

    def log(msg):
        """ログ出力＋Redis蓄積"""
        print(f"[DUMMY] {msg}")

        # Redisに追記
        if job_id:
            redis_conn.rpush(f"logs:{job_id}", msg)

    log(f"🚀 Job started for {symbol}")

    # Step 1: WebSearch シミュレート
    log("⏳ Step 1/3: Simulating WebSearch...")
    time.sleep(2)
    log("✅ Step 1 done: Found 5 articles")

    # Step 2: Analysis シミュレート
    log("⏳ Step 2/3: Simulating analysis...")
    time.sleep(2)
    log("✅ Step 2 done: Average sentiment +0.45")

    # Step 3: DB Save シミュレート
    log("⏳ Step 3/3: Simulating DB save...")
    time.sleep(1)
    log("✅ Step 3 done: Saved to database")

    log("🎉 Completed!")

    # ログの有効期限を設定（1時間）
    if job_id:
        redis_conn.expire(f"logs:{job_id}", 3600)

    return {
        "success": True,
        "symbol": symbol,
        "news_count": 5,
        "avg_sentiment": 0.45
    }
