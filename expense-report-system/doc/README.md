启动步骤
1. 后端启动
bash
cd backend
# 创建虚拟环境（如果还没有）
python -m venv .venv

# 激活虚拟环境
.venv\Scripts\activate  # Windows
# source .venv/bin/activate  # Mac/Linux

# 安装依赖
pip install fastapi uvicorn asyncpg pydantic python-dotenv pyjwt bcrypt

# 启动服务
uvicorn main:app --reload

2. 前端启动
bash
cd frontend
# 安装依赖（如果还没有）
npm install

# 启动开发服务器
npm run dev

3. 访问地址

用户报销表单
http://localhost:5173/
普通用户提交费用
管理员登录
http://localhost:5173/admin
账号: admin / 密码: admin123
管理仪表盘
http://localhost:5173/admin/dashboard
登录后自动跳转
数据库表结构（PostgreSQL）
sql
CREATE TABLE expense_report (
    id SERIAL PRIMARY KEY,
    gpn VARCHAR(8) NOT NULL CHECK (gpn ~ '^\d{7,8}$'),
    report_title VARCHAR(200),
    invoice_number VARCHAR(100),
    item VARCHAR(200) NOT NULL,
    details TEXT,
    amount DECIMAL(10,2) NOT NULL DEFAULT 0,
    attachment VARCHAR(500),
    report_date DATE NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
