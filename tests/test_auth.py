"""认证测试：有效 token 与安全反向用例。"""
import allure
import pytest

from app import data


@allure.feature("认证")
class TestAuthentication:

    @allure.story("有效 token")
    @allure.title("正确凭据返回 Bearer token")
    @allure.severity(allure.severity_level.CRITICAL)
    def test_正确凭据返回BearerToken(self, unauth_client):
        response = unauth_client.post("/auth/token", json={
            "client_id": data.DEMO_CLIENT_ID,
            "client_secret": data.DEMO_CLIENT_SECRET,
        })
        assert response.status_code == 200
        body = response.json()
        assert body["token_type"] == "bearer"
        assert len(body["access_token"]) > 0
        assert body["expires_in"] > 0

    @allure.story("无效凭据")
    @allure.title("错误的凭据返回 401")
    @pytest.mark.parametrize("client_id,client_secret", [
        (data.DEMO_CLIENT_ID, "secreto-incorrecto"),
        ("cliente-inexistente", data.DEMO_CLIENT_SECRET),
        ("cliente-inexistente", "secreto-incorrecto"),
    ])
    def test_错误凭据返回401(self, unauth_client, client_id, client_secret):
        response = unauth_client.post("/auth/token", json={
            "client_id": client_id, "client_secret": client_secret,
        })
        assert response.status_code == 401

    @allure.story("非法请求体")
    @allure.title("请求体缺失或非法返回 422")
    @pytest.mark.parametrize("body", [
        {"client_id": "solo-id"},                       # 缺少 client_secret
        {"client_secret": "solo-secret"},               # 缺少 client_id
        {"client_id": "", "client_secret": ""},         # 空值（min_length=1）
        {},                                             # 空请求体
    ])
    def test_畸形请求体返回422(self, unauth_client, body):
        response = unauth_client.post("/auth/token", json=body)
        assert response.status_code == 422

    @allure.story("受保护资源")
    @allure.title("无 token 访问受保护资源返回 401")
    def test_无token访问受保护资源返回401(self, unauth_client):
        response = unauth_client.get("/api/v1/customers")
        assert response.status_code == 401

    @allure.story("受保护资源")
    @allure.title("使用无效 token 访问返回 401")
    def test_无效token访问受保护资源返回401(self, base_url):
        from utils.api_client import APIClient

        bogus = APIClient(base_url, token="token-falso-123")
        response = bogus.get("/api/v1/customers")
        assert response.status_code == 401
