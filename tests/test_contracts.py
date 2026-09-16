"""
契约测试：用 JSON Schema 校验响应的"形状"。

用于发现不兼容变更（字段改名/删除、类型改变），与具体的数据取值无关。
"""
import allure

from app import data
from utils.schema_validator import assert_matches_schema


@allure.feature("契约（JSON Schema）")
class TestContracts:

    @allure.title("token 响应符合契约")
    def test_token响应符合契约(self, unauth_client):
        response = unauth_client.post("/auth/token", json={
            "client_id": data.DEMO_CLIENT_ID, "client_secret": data.DEMO_CLIENT_SECRET,
        })
        assert_matches_schema(response.json(), "token.json")

    @allure.title("客户详情响应符合契约")
    def test_客户详情响应符合契约(self, client):
        response = client.get("/api/v1/customers/1")
        assert_matches_schema(response.json(), "customer.json")

    @allure.title("客户列表响应符合契约")
    def test_客户列表响应符合契约(self, client):
        response = client.get("/api/v1/customers")
        assert_matches_schema(response.json(), "customer_list.json")

    @allure.title("余额响应符合契约")
    def test_余额响应符合契约(self, client):
        response = client.get("/api/v1/customers/1/balances")
        assert_matches_schema(response.json(), "balances.json")
