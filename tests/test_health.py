"""被测服务健康检查的冒烟测试（无需认证）。"""
import allure


@allure.feature("服务")
@allure.story("健康检查")
@allure.title("GET /health 返回 200 且状态为 ok")
def test_健康检查返回200(unauth_client):
    response = unauth_client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}
