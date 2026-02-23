"""
FastAPI backend for expense_report.
All code and comments are in English.
"""
from typing import List, Optional, Dict, Any
import os
import asyncio
import random
import string
import smtplib
from email.mime.text import MIMEText
from datetime import date, datetime
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field, EmailStr
import asyncpg
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv('DATABASE_URL')
if not DATABASE_URL:
    raise RuntimeError('DATABASE_URL environment variable not set.')

# Email configuration
SMTP_HOST = os.getenv('SMTP_HOST', 'smtp.gmail.com')
SMTP_PORT = int(os.getenv('SMTP_PORT', 587))
SMTP_USER = os.getenv('SMTP_USER')
SMTP_PASSWORD = os.getenv('SMTP_PASSWORD')
FROM_EMAIL = os.getenv('FROM_EMAIL', 'zhangyangzuo@hotmail.com')

@asynccontextmanager
async def lifespan(app):
    """Initialize database connection pool on startup."""
    global db_pool
    max_attempts = 5
    delay = 1
    for attempt in range(1, max_attempts + 1):
        try:
            db_pool = await asyncpg.create_pool(DATABASE_URL)
            print(f"[lifespan] Database connected on attempt {attempt}")
            break
        except Exception as e:
            print(f"[lifespan] Attempt {attempt} failed: {e}")
            if attempt == max_attempts:
                raise
            await asyncio.sleep(delay)
            delay *= 2

    try:
        yield
    finally:
        if db_pool:
            await db_pool.close()

app = FastAPI(title='Expense Report API', lifespan=lifespan)

# CORS configuration - Added common frontend development ports
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",  # Vite default port
        "http://localhost:8080",  # Vue CLI default port
        "http://localhost:3000",  # React default port
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

from admin import router as admin_router
app.include_router(admin_router)

db_pool: Optional[asyncpg.pool.Pool] = None


class ExpenseReportIn(BaseModel):
    gpn: str = Field(..., pattern=r"^\d{7,8}$")
    report_title: Optional[str] = None
    invoice_number: str = Field(..., min_length=1)
    item: str
    details: Optional[str] = None
    amount: float = Field(..., ge=0)
    attachment: Optional[str] = None
    report_date: date
    user_email: Optional[EmailStr] = None  # Added email field


class ExpenseReportOut(ExpenseReportIn):
    id: int
    created_at: datetime


def generate_temp_password(length: int = 10) -> str:
    """Generate a random temporary password."""
    chars = string.ascii_letters + string.digits + "!@#$%^&*"
    return ''.join(random.choice(chars) for _ in range(length))


async def send_password_email(to_email: str, password: str, gpn: str):
    """Send temporary password email to user."""
    if not all([SMTP_USER, SMTP_PASSWORD]):
        print(f"[Email] SMTP not configured. Password for {gpn}: {password}")
        return
    
    try:
        msg = MIMEText(f"""
Hello,

Your expense report has been submitted successfully.

Login Credentials:
- GPN: {gpn}
- Temporary Password: {password}

Please use these credentials to review your requests at:
http://localhost:5173/login

For security reasons, please change your password after first login.

Best regards,
Expense Report System
        """)
        
        msg['Subject'] = 'Expense Report - Your Temporary Password'
        msg['From'] = FROM_EMAIL
        msg['To'] = to_email
        
        # Send email via SMTP
        loop = asyncio.get_event_loop()
        
        def send_sync():
            with smtplib.SMTP(SMTP_HOST, SMTP_PORT) as server:
                server.starttls()
                server.login(SMTP_USER, SMTP_PASSWORD)
                server.send_message(msg)
        
        await loop.run_in_executor(None, send_sync)
        print(f"[Email] Password sent to {to_email}")
        
    except Exception as e:
        print(f"[Email] Failed to send email: {e}")
        # Don't raise exception - allow report submission even if email fails


async def store_user_password(gpn: str, email: str, password: str):
    """Store or update users password in database."""
    import hashlib
    password_hash = hashlib.sha256(password.encode()).hexdigest()
    
    async with db_pool.acquire() as conn:
        # Check if users exists
        existing = await conn.fetchrow(
            'SELECT id FROM "users" WHERE gpn = $1',
            gpn
        )
        
        if existing:
            # Update existing user
            await conn.execute(
                '''
                UPDATE "users" 
                SET email = $1, 
                    password_hash = $2, 
                    updated_at = CURRENT_TIMESTAMP
                WHERE gpn = $3
                ''',
                email, password_hash, gpn
            )
        else:
            # Insert new users
            await conn.execute(
                '''
                INSERT INTO "users" (gpn, email, password_hash, created_at, updated_at)
                VALUES ($1, $2, $3, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP)
                ''',
                gpn, email, password_hash
            )



async def fetchrow(query: str, *args) -> asyncpg.Record:
    """Fetch a single row from database."""
    async with db_pool.acquire() as conn:
        return await conn.fetchrow(query, *args)


async def fetch(query: str, *args) -> List[asyncpg.Record]:
    """Fetch multiple rows from database."""
    async with db_pool.acquire() as conn:
        return await conn.fetch(query, *args)


async def execute(query: str, *args) -> str:
    """Execute a query (INSERT, UPDATE, DELETE) and return command status."""
    async with db_pool.acquire() as conn:
        return await conn.execute(query, *args)


@app.post('/reports/bulk', response_model=List[ExpenseReportOut])
async def bulk_insert(reports: List[ExpenseReportIn]):
    """
    Insert or update expense reports.
    UPSERT logic: if same gpn + invoice_number + item + report_date exists, update it.
    Also generates temp password and sends email if user_email provided.
    """
    if not reports:
        return []
    
    # Get user email from first report
    user_email = reports[0].user_email
    gpn = reports[0].gpn
    
    # Generate and store password if email provided
    temp_password = None
    if user_email:
        temp_password = generate_temp_password()
        await store_user_password(gpn, user_email, temp_password)
        # Send email asynchronously (don't block response)
        asyncio.create_task(send_password_email(user_email, temp_password, gpn))
    
    async with db_pool.acquire() as conn:
        async with conn.transaction():
            out = []
            for r in reports:
                existing = await conn.fetchrow(
                    '''
                    SELECT id FROM expense_report 
                    WHERE gpn = $1 AND invoice_number = $2 AND item = $3 AND report_date = $4
                    ''',
                    r.gpn, r.invoice_number, r.item, r.report_date
                )
                
                if existing:
                    row = await conn.fetchrow(
                        '''
                        UPDATE expense_report 
                        SET report_title = $1,
                            details = $2,
                            amount = $3,
                            attachment = $4,
                            created_at = CURRENT_TIMESTAMP
                        WHERE id = $5
                        RETURNING id, gpn, report_title, invoice_number, item, details, amount, 
                                  attachment, report_date, created_at
                        ''',
                        r.report_title, r.details, r.amount, r.attachment, existing['id']
                    )
                else:
                    row = await conn.fetchrow(
                        '''
                        INSERT INTO expense_report (gpn, report_title, invoice_number, item, details, amount, attachment, report_date)
                        VALUES ($1,$2,$3,$4,$5,$6,$7,$8)
                        RETURNING id, gpn, report_title, invoice_number, item, details, amount, 
                                  attachment, report_date, created_at
                        ''',
                        r.gpn, r.report_title, r.invoice_number, r.item, 
                        r.details, r.amount, r.attachment, r.report_date
                    )
                
                out.append(dict(row))
    
    return out


@app.get('/health')
async def health_check():
    """Health check endpoint to verify API and database status."""
    return {"status": "ok", "database": "connected" if db_pool else "disconnected"}
