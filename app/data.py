"""
被测 API 的内存合成数据。

模拟虚构的多基金投资平台 "Veridian" 的客户及其在各基金（A-E）上的余额。
所有数据均为虚构且确定性生成，不包含任何真实客户数据。

它是 data-quality-framework 项目在 API 层的对应部分，后者在数据库层
验证同一套业务概念。
"""
from __future__ import annotations

import random

SEGMENTS = ["RETAIL", "PREMIUM", "PRIVATE"]
FUNDS = ["A", "B", "C", "D", "E"]

# 演示 API 的账号凭据（虚构，仅用于本地 mock）。
DEMO_CLIENT_ID = "veridian-demo"
DEMO_CLIENT_SECRET = "demo-secret"


def _seed_customers():
    rng = random.Random(42)
    customers = {}
    balances = {}
    first = ["Ana", "Bruno", "Carla", "Diego", "Elena", "Felipe", "Gloria",
             "Hugo", "Ines", "Javier", "Karen", "Luis", "Marta", "Nestor", "Olga"]
    last = ["Rojas", "Soto", "Vega", "Munoz", "Castro", "Pinto", "Araya",
            "Bravo", "Cortes", "Diaz", "Fuentes", "Gomez", "Herrera"]

    for cid in range(1, 16):
        name = f"{rng.choice(first)} {rng.choice(last)}"
        email = f"cliente{cid}@veridian.example"
        segment = rng.choice(SEGMENTS)
        customers[cid] = {
            "id": cid,
            "full_name": name,
            "email": email,
            "segment": segment,
            "status": "ACTIVE",
        }

        # 每个客户的基金持仓（随机选取基金子集），并计算份额占比。
        client_funds = rng.sample(FUNDS, rng.randint(1, 4))
        raw = {f: round(rng.uniform(1_000_000, 90_000_000), 0) for f in client_funds}
        total = sum(raw.values())
        balances[cid] = [
            {"fund": f, "balance_clp": amount,
             "share_pct": round(amount / total * 100, 2)}
            for f, amount in sorted(raw.items())
        ]

    return customers, balances


CUSTOMERS, BALANCES = _seed_customers()
_NEXT_ID = max(CUSTOMERS) + 1


def reset_state():
    """重置内存状态（用于测试之间隔离）。"""
    global CUSTOMERS, BALANCES, _NEXT_ID
    CUSTOMERS, BALANCES = _seed_customers()
    _NEXT_ID = max(CUSTOMERS) + 1


def add_customer(full_name: str, email: str, segment: str) -> dict:
    global _NEXT_ID
    new = {
        "id": _NEXT_ID,
        "full_name": full_name,
        "email": email,
        "segment": segment,
        "status": "ACTIVE",
    }
    CUSTOMERS[_NEXT_ID] = new
    BALANCES[_NEXT_ID] = []
    _NEXT_ID += 1
    return new
