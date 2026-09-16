"""客户资源测试：列表、分页、筛选、详情与创建。"""
import allure
import pytest

TOTAL_CUSTOMERS = 15  # 确定性种子的客户总数


@allure.feature("客户")
class TestListCustomers:

    @allure.story("列表")
    @allure.title("默认列表返回第一页")
    def test_默认列表返回第一页(self, client):
        response = client.get("/api/v1/customers")
        assert response.status_code == 200
        body = response.json()
        assert body["total"] == TOTAL_CUSTOMERS
        assert body["limit"] == 10
        assert body["offset"] == 0
        assert len(body["items"]) == 10

    @allure.story("分页")
    @allure.title("分页遵循 limit 和 offset")
    @pytest.mark.parametrize("limit,offset,expected_len", [
        (5, 0, 5),
        (10, 10, 5),
        (5, 13, 2),
        (100, 0, TOTAL_CUSTOMERS),
    ])
    def test_分页遵循limit和offset(self, client, limit, offset, expected_len):
        response = client.get("/api/v1/customers", params={"limit": limit, "offset": offset})
        assert response.status_code == 200
        assert len(response.json()["items"]) == expected_len

    @allure.story("分页")
    @allure.title("分页参数越界返回 422")
    @pytest.mark.parametrize("params", [
        {"limit": 0},      # ge=1
        {"limit": 101},    # le=100
        {"offset": -1},    # ge=0
    ])
    def test_分页参数越界返回422(self, client, params):
        response = client.get("/api/v1/customers", params=params)
        assert response.status_code == 422

    @allure.story("筛选")
    @allure.title("按 segment 筛选只返回该 segment")
    @pytest.mark.parametrize("segment", ["RETAIL", "PREMIUM", "PRIVATE"])
    def test_按segment筛选只返回该segment(self, client, segment):
        response = client.get("/api/v1/customers", params={"segment": segment, "limit": 100})
        assert response.status_code == 200
        items = response.json()["items"]
        assert all(c["segment"] == segment for c in items)


@allure.feature("客户")
class TestGetCustomer:

    @allure.story("详情")
    @allure.title("获取存在的客户返回其数据")
    def test_获取存在的客户详情(self, client):
        response = client.get("/api/v1/customers/1")
        assert response.status_code == 200
        assert response.json()["id"] == 1

    @allure.story("详情")
    @allure.title("获取不存在的客户返回 404")
    def test_获取不存在的客户返回404(self, client):
        response = client.get("/api/v1/customers/999999")
        assert response.status_code == 404


@allure.feature("客户")
class TestCreateCustomer:

    @allure.story("创建")
    @allure.title("创建有效客户返回 201 及创建的资源")
    @allure.severity(allure.severity_level.CRITICAL)
    def test_创建有效客户返回201(self, client):
        payload = {"full_name": "Patricia Núñez", "email": "patricia@veridian.example",
                   "segment": "PREMIUM"}
        response = client.post("/api/v1/customers", json=payload)
        assert response.status_code == 201
        body = response.json()
        assert body["id"] > TOTAL_CUSTOMERS
        assert body["full_name"] == payload["full_name"]
        assert body["segment"] == "PREMIUM"
        assert body["status"] == "ACTIVE"

    @allure.story("创建")
    @allure.title("创建无效客户返回 422")
    @pytest.mark.parametrize("payload", [
        {"full_name": "A", "email": "a@b.com", "segment": "RETAIL"},          # 姓名过短
        {"full_name": "Nombre Valido", "email": "no-es-email", "segment": "RETAIL"},  # 邮箱非法
        {"full_name": "Nombre Valido", "email": "a@b.com", "segment": "GOLD"},  # 不存在的 segment
        {"email": "a@b.com", "segment": "RETAIL"},                            # 缺少 full_name
    ])
    def test_创建无效客户返回422(self, client, payload):
        response = client.post("/api/v1/customers", json=payload)
        assert response.status_code == 422
