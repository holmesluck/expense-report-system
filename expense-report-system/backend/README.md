# Backend (FastAPI)

说明（中文）:

- 该后端使用 FastAPI + asyncpg 连接到 PostgreSQL。请在根目录 `backend` 下创建一个 `.env` 文件并设置 `DATABASE_URL`，格式例如：

  `DATABASE_URL=postgresql://user:password@localhost:5432/yourdb`

- 你也可以配置 Redis 用于缓存与并发锁，提高并发查询/修改的吞吐与一致性：

  `REDIS_URL=redis://localhost:6379/0`

- 安装依赖并启动开发服务器的步骤：

```bash
cd backend
python -m venv .venv
source .venv/Scripts/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

If you use Redis, ensure the service is running and set `REDIS_URL` in `.env`. Example to install Redis on Ubuntu:

```bash
# install redis on Ubuntu
sudo apt update && sudo apt install redis-server
sudo systemctl enable --now redis
```

- 提供的 6 个接口：
  - `POST /reports` — insert a single report
  - `POST /reports/bulk` — insert multiple reports in a transaction
  - `GET /reports` — query list with optional `gpn` and `item` filters
  - `GET /reports/{report_id}` — get single by `id`
  - `PUT /reports/{report_id}` — update fields of a report
  - `DELETE /reports/{report_id}` — delete by `id`

代码与注释为英文；此 README 及运行说明为中文。
