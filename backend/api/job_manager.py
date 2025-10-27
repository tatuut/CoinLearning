"""Job management with SQLite (Redis不要版)"""
import sqlite3
import json
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Optional

class JobManager:
    """ジョブ管理（SQLiteベース）"""

    def __init__(self, db_path: str = "data/jobs.db"):
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._init_db()

    def _init_db(self):
        """データベース初期化"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        # ジョブテーブル
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS jobs (
                job_id TEXT PRIMARY KEY,
                symbol TEXT NOT NULL,
                status TEXT NOT NULL,
                result TEXT,
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL
            )
        """)

        # ログテーブル
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS job_logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                job_id TEXT NOT NULL,
                message TEXT NOT NULL,
                timestamp TEXT NOT NULL,
                FOREIGN KEY (job_id) REFERENCES jobs(job_id)
            )
        """)

        conn.commit()
        conn.close()

    def create_job(self, job_id: str, symbol: str) -> None:
        """ジョブ作成"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        now = datetime.now().isoformat()

        cursor.execute("""
            INSERT INTO jobs (job_id, symbol, status, created_at, updated_at)
            VALUES (?, ?, 'queued', ?, ?)
        """, (job_id, symbol, now, now))

        conn.commit()
        conn.close()

    def update_status(self, job_id: str, status: str, result: Optional[Dict] = None) -> None:
        """ステータス更新"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        now = datetime.now().isoformat()

        result_json = json.dumps(result) if result else None

        cursor.execute("""
            UPDATE jobs
            SET status = ?, result = ?, updated_at = ?
            WHERE job_id = ?
        """, (status, result_json, now, job_id))

        conn.commit()
        conn.close()

    def add_log(self, job_id: str, message: str) -> None:
        """ログ追加"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        now = datetime.now().isoformat()

        cursor.execute("""
            INSERT INTO job_logs (job_id, message, timestamp)
            VALUES (?, ?, ?)
        """, (job_id, message, now))

        conn.commit()
        conn.close()

    def get_job(self, job_id: str) -> Optional[Dict]:
        """ジョブ情報取得"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute("""
            SELECT job_id, symbol, status, result, created_at, updated_at
            FROM jobs
            WHERE job_id = ?
        """, (job_id,))

        row = cursor.fetchone()
        conn.close()

        if not row:
            return None

        result_dict = json.loads(row[3]) if row[3] else None

        return {
            "job_id": row[0],
            "symbol": row[1],
            "status": row[2],
            "result": result_dict,
            "created_at": row[4],
            "updated_at": row[5]
        }

    def get_logs(self, job_id: str, offset: int = 0) -> List[str]:
        """ログ取得（offset以降）"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute("""
            SELECT message
            FROM job_logs
            WHERE job_id = ?
            ORDER BY id
            LIMIT -1 OFFSET ?
        """, (job_id, offset))

        rows = cursor.fetchall()
        conn.close()

        return [row[0] for row in rows]

    def get_log_count(self, job_id: str) -> int:
        """ログ件数取得"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute("""
            SELECT COUNT(*)
            FROM job_logs
            WHERE job_id = ?
        """, (job_id,))

        count = cursor.fetchone()[0]
        conn.close()

        return count

# グローバルインスタンス
job_manager = JobManager()
