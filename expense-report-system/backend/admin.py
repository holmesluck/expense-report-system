"""
Admin backend for expense report management with JWT authentication.
All code and comments are in English.
"""
from typing import List, Optional, Dict, Any
from datetime import date, datetime, timedelta
from fastapi import APIRouter, HTTPException, Depends, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel
import jwt
import bcrypt

router = APIRouter(prefix="/admin", tags=["Admin"])

# Security configuration (should be environment variables in production)
SECRET_KEY = "your-secret-key-change-this-in-production"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 480  # 8 hours

# Admin credentials (should be in database in production)
ADMIN_USERNAME = "admin"
ADMIN_PASSWORD_HASH = bcrypt.hashpw("admin123".encode(), bcrypt.gensalt()).decode()

security = HTTPBearer()


class LoginRequest(BaseModel):
    username: str
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str


class ReportOut(BaseModel):
    id: int
    gpn: str
    report_title: Optional[str]
    invoice_number: Optional[str]
    item: str
    details: Optional[str]
    amount: float
    attachment: Optional[str]
    report_date: date
    created_at: datetime


class StatsOut(BaseModel):
    total_count: int
    total_amount: float
    avg_amount: float
    item_breakdown: Dict[str, Dict[str, Any]]


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a plain password against a hashed password."""
    return bcrypt.checkpw(plain_password.encode(), hashed_password.encode())


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    """Create a JWT access token with expiration time."""
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=15))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


async def verify_token(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Verify JWT token from Authorization header."""
    token = credentials.credentials
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None or username != ADMIN_USERNAME:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid authentication credentials",
                headers={"WWW-Authenticate": "Bearer"},
            )
        return username
    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token expired",
            headers={"WWW-Authenticate": "Bearer"},
        )
    except jwt.JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token",
            headers={"WWW-Authenticate": "Bearer"},
        )


def get_db_helpers():
    """Import db helpers lazily to avoid circular import."""
    from main import db_pool, fetch, fetchrow, execute
    return db_pool, fetch, fetchrow, execute


@router.post("/login", response_model=TokenResponse)
async def login(credentials: LoginRequest):
    """
    Admin login endpoint.
    Validates credentials and returns JWT access token.
    """
    # Validate username
    if credentials.username != ADMIN_USERNAME:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password"
        )
    
    # Validate password
    if not verify_password(credentials.password, ADMIN_PASSWORD_HASH):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password"
        )
    
    # Create access token
    access_token = create_access_token(
        data={"sub": ADMIN_USERNAME},
        expires_delta=timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    )
    
    return {
        "access_token": access_token,
        "token_type": "bearer"
    }


@router.get("/verify")
async def verify_admin(current_user: str = Depends(verify_token)):
    """Verify if the provided token is valid."""
    return {"message": "Token valid", "user": current_user}


@router.get("/reports", response_model=List[ReportOut])
async def get_all_reports(
    gpn: Optional[str] = None,
    item: Optional[str] = None,
    start_date: Optional[date] = None,
    end_date: Optional[date] = None,
    min_amount: Optional[float] = None,
    max_amount: Optional[float] = None,
    sort_by: str = "created_at",
    sort_order: str = "desc",
    limit: int = 1000,
    offset: int = 0,
    current_user: str = Depends(verify_token)
):
    """Get all expense reports with flexible filtering and sorting."""
    from main import db_pool, fetch
    
    clauses = []
    args: List[Any] = []
    idx = 1
    
    if gpn:
        clauses.append(f"gpn = ${idx}")
        args.append(gpn)
        idx += 1
    
    if item:
        clauses.append(f"item ILIKE ${idx}")
        args.append(f"%{item}%")
        idx += 1
    
    if start_date:
        clauses.append(f"report_date >= ${idx}")
        args.append(start_date)
        idx += 1
    
    if end_date:
        clauses.append(f"report_date <= ${idx}")
        args.append(end_date)
        idx += 1
    
    if min_amount is not None:
        clauses.append(f"amount >= ${idx}")
        args.append(min_amount)
        idx += 1
    
    if max_amount is not None:
        clauses.append(f"amount <= ${idx}")
        args.append(max_amount)
        idx += 1
    
    where = ('WHERE ' + ' AND '.join(clauses)) if clauses else ''
    
    allowed_sort_fields = ['id', 'gpn', 'item', 'amount', 'report_date', 'created_at']
    if sort_by not in allowed_sort_fields:
        sort_by = 'created_at'
    
    sort_order = 'ASC' if sort_order.lower() == 'asc' else 'DESC'
    
    query = f"""
        SELECT id, gpn, report_title, invoice_number, item, details, amount, 
               attachment, report_date, created_at 
        FROM expense_report 
        {where} 
        ORDER BY {sort_by} {sort_order} 
        LIMIT ${idx} OFFSET ${idx+1}
    """
    args.extend([limit, offset])
    
    rows = await fetch(query, *args)
    return [dict(r) for r in rows]


@router.get("/reports/{report_id}", response_model=ReportOut)
async def get_report_detail(
    report_id: int,
    current_user: str = Depends(verify_token)
):
    """Get single report details by ID."""
    from main import fetchrow
    
    row = await fetchrow(
        '''SELECT id, gpn, report_title, invoice_number, item, details, amount, 
                  attachment, report_date, created_at 
           FROM expense_report WHERE id = $1''', 
        report_id
    )
    if not row:
        raise HTTPException(status_code=404, detail="Report not found")
    return dict(row)


@router.delete("/reports/{report_id}")
async def delete_report(
    report_id: int,
    current_user: str = Depends(verify_token)
):
    """Delete a report by ID."""
    from main import execute
    
    result = await execute('DELETE FROM expense_report WHERE id = $1', report_id)
    if result == "DELETE 0":
        raise HTTPException(status_code=404, detail="Report not found")
    return {"message": "Report deleted successfully", "id": report_id}


@router.get("/stats", response_model=StatsOut)
async def get_statistics(
    start_date: Optional[date] = None,
    end_date: Optional[date] = None,
    current_user: str = Depends(verify_token)
):
    """Get real-time statistics for admin dashboard."""
    from main import fetch, fetchrow
    
    date_clause = ""
    args: List[Any] = []
    idx = 1
    
    if start_date and end_date:
        date_clause = f"WHERE report_date >= ${idx} AND report_date <= ${idx+1}"
        args.extend([start_date, end_date])
        idx += 2
    elif start_date:
        date_clause = f"WHERE report_date >= ${idx}"
        args.append(start_date)
        idx += 1
    elif end_date:
        date_clause = f"WHERE report_date <= ${idx}"
        args.append(end_date)
        idx += 1
    
    stats_query = f"""
        SELECT 
            COUNT(*) as total_count,
            COALESCE(SUM(amount), 0) as total_amount,
            COALESCE(AVG(amount), 0) as avg_amount
        FROM expense_report
        {date_clause}
    """
    stats_row = await fetchrow(stats_query, *args)
    
    breakdown_query = f"""
        SELECT 
            item,
            COUNT(*) as count,
            SUM(amount) as total,
            AVG(amount) as average
        FROM expense_report
        {date_clause}
        GROUP BY item
        ORDER BY total DESC
    """
    breakdown_rows = await fetch(breakdown_query, *args)
    
    item_breakdown = {}
    for row in breakdown_rows:
        item_breakdown[row['item']] = {
            "count": row['count'],
            "total": float(row['total']),
            "average": float(row['average'])
        }
    
    return {
        "total_count": stats_row['total_count'],
        "total_amount": float(stats_row['total_amount']),
        "avg_amount": float(stats_row['avg_amount']),
        "item_breakdown": item_breakdown
    }


@router.get("/gpns")
async def get_all_gpns(current_user: str = Depends(verify_token)):
    """Get list of all unique GPNs for filter dropdown."""
    from main import fetch
    
    rows = await fetch("SELECT DISTINCT gpn FROM expense_report ORDER BY gpn")
    return [r['gpn'] for r in rows]


@router.get("/items")
async def get_all_items(current_user: str = Depends(verify_token)):
    """Get list of all unique items/categories for filter dropdown."""
    from main import fetch
    
    rows = await fetch("SELECT DISTINCT item FROM expense_report ORDER BY item")
    return [r['item'] for r in rows]
