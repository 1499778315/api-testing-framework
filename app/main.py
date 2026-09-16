"""
演示用 REST API：虚构的多基金投资平台 "Veridian"。

它是本框架的*被测系统*（SUT）。完全在本地运行，因此测试套件不依赖任何
外部服务，结果可完全复现（与 data-quality-framework 项目在数据库层的
验证形成呼应）。

提供 Bearer token 认证、分页资源、请求体校验（422）以及可控错误
（401/404），用于覆盖正向、反向、边界和契约测试场景。
"""
from __future__ import annotations

import uuid
from enum import Enum
from typing import Optional

from fastapi import Depends, FastAPI, HTTPException, Query, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from pydantic import BaseModel, Field

from app import data

app = FastAPI(title="Veridian 投资平台 API（测试演示）", version="1.0.0")

# 本次运行中已签发的 token（mock 的内存存储）。
_ISSUED_TOKENS: set[str] = set()


# --------------------------- 数据模型 ---------------------------------------
class Segment(str, Enum):
    RETAIL = "RETAIL"
    PREMIUM = "PREMIUM"
    PRIVATE = "PRIVATE"


class TokenRequest(BaseModel):
    client_id: str = Field(..., min_length=1)
    client_secret: str = Field(..., min_length=1)


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    expires_in: int = 3600


class Customer(BaseModel):
    id: int
    full_name: str
    email: str
    segment: Segment
    status: str


class CustomerCreate(BaseModel):
    full_name: str = Field(..., min_length=2, max_length=80)
    email: str = Field(..., pattern=r"^[^@\s]+@[^@\s]+\.[^@\s]+$")
    segment: Segment


class Balance(BaseModel):
    fund: str
    balance_clp: float
    share_pct: float


class CustomerBalances(BaseModel):
    customer_id: int
    balances: list[Balance]


class CustomerList(BaseModel):
    items: list[Customer]
    total: int
    limit: int
    offset: int


# --------------------------- 安全方案 ---------------------------------------
# 在 OpenAPI 中声明该安全方案后，Swagger UI 会显示 "Authorize" 按钮
# （所有受保护资源共用一次授权），而不是在每个端点上重复填写请求头。
# auto_error=False 让 401 由本依赖统一抛出（自定义错误消息），
# 而不是使用 FastAPI 默认返回的 403。
_bearer_scheme = HTTPBearer(
    auto_error=False,
    description="通过 POST /auth/token 获取的 Bearer token（Swagger 会自动补上 'Bearer ' 前缀）。",
)


def require_auth(credentials: Optional[HTTPAuthorizationCredentials] = Depends(_bearer_scheme)):
    """校验 Bearer token，缺失或无效时返回 401。"""
    if credentials is None or credentials.scheme.lower() != "bearer":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="缺少认证 token。",
            headers={"WWW-Authenticate": "Bearer"},
        )
    if credentials.credentials not in _ISSUED_TOKENS:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="token 无效或已过期。",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return credentials.credentials


# --------------------------- 接口端点 ---------------------------------------
@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/auth/token", response_model=TokenResponse)
def issue_token(body: TokenRequest):
    if body.client_id != data.DEMO_CLIENT_ID or body.client_secret != data.DEMO_CLIENT_SECRET:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="凭据无效。",
        )
    token = uuid.uuid4().hex
    _ISSUED_TOKENS.add(token)
    return TokenResponse(access_token=token)


@app.get("/api/v1/customers", response_model=CustomerList)
def list_customers(
    segment: Optional[Segment] = None,
    limit: int = Query(default=10, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
    _: str = Depends(require_auth),
):
    items = list(data.CUSTOMERS.values())
    if segment:
        items = [c for c in items if c["segment"] == segment.value]
    total = len(items)
    page = items[offset: offset + limit]
    return {"items": page, "total": total, "limit": limit, "offset": offset}


@app.get("/api/v1/customers/{customer_id}", response_model=Customer)
def get_customer(customer_id: int, _: str = Depends(require_auth)):
    customer = data.CUSTOMERS.get(customer_id)
    if not customer:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"客户 {customer_id} 不存在。")
    return customer


@app.post("/api/v1/customers", response_model=Customer, status_code=status.HTTP_201_CREATED)
def create_customer(body: CustomerCreate, _: str = Depends(require_auth)):
    return data.add_customer(body.full_name, body.email, body.segment.value)


@app.get("/api/v1/customers/{customer_id}/balances", response_model=CustomerBalances)
def get_balances(customer_id: int, _: str = Depends(require_auth)):
    if customer_id not in data.CUSTOMERS:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"客户 {customer_id} 不存在。")
    return {"customer_id": customer_id, "balances": data.BALANCES.get(customer_id, [])}
