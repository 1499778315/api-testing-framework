"""余额资源测试，包括一条业务规则校验（份额占比合计 100%）。"""
import allure
import pytest


@allure.feature("余额")
class TestBalances:

    @allure.story("查询")
    @allure.title("获取已有客户的余额")
    def test_获取已有客户的余额(self, client):
        response = client.get("/api/v1/customers/1/balances")
        assert response.status_code == 200
        body = response.json()
        assert body["customer_id"] == 1
        assert isinstance(body["balances"], list)
        for b in body["balances"]:
            assert b["fund"] in {"A", "B", "C", "D", "E"}
            assert b["balance_clp"] >= 0

    @allure.story("业务规则")
    @allure.title("余额份额占比合计为 100%")
    @pytest.mark.parametrize("customer_id", [1, 5, 10, 15])
    def test_份额占比合计为100(self, client, customer_id):
        response = client.get(f"/api/v1/customers/{customer_id}/balances")
        assert response.status_code == 200
        balances = response.json()["balances"]
        if balances:  # 部分客户可能没有余额
            total_pct = sum(b["share_pct"] for b in balances)
            assert abs(total_pct - 100.0) <= 0.1, f"份额占比合计 {total_pct}%，而非 100%。"

    @allure.story("查询")
    @allure.title("获取不存在客户的余额返回 404")
    def test_不存在客户的余额返回404(self, client):
        response = client.get("/api/v1/customers/999999/balances")
        assert response.status_code == 404
