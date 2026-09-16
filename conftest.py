"""
会话级 fixtures：在本地真实启动被测 API，并为用例提供 HTTP 客户端。

被测 API（``app.main``）通过 uvicorn 在空闲端口上的一个线程中运行。
测试通过 ``requests`` 走真实 HTTP 访问它（非进程内调用），与访问一个
已部署的服务行为完全一致。会话结束后，服务器自动关闭。
"""
from __future__ import annotations

import socket
import threading
import time

import pytest
import requests
import uvicorn

from app import data
from app.main import app


def _free_port() -> int:
    """获取一个系统空闲的本地端口。"""
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.bind(("127.0.0.1", 0))
    port = s.getsockname()[1]
    s.close()
    return port


@pytest.fixture(scope="session")
def base_url():
    """启动被测 API 并返回其基础 URL（整个会话只启动一次）。"""
    port = _free_port()
    config = uvicorn.Config(app, host="127.0.0.1", port=port, log_level="warning")
    server = uvicorn.Server(config)
    server.install_signal_handlers = lambda: None  # 非主线程中必须屏蔽信号处理器

    thread = threading.Thread(target=server.run, daemon=True)
    thread.start()

    url = f"http://127.0.0.1:{port}"
    deadline = time.time() + 15
    while time.time() < deadline:
        try:
            if requests.get(f"{url}/health", timeout=0.5).status_code == 200:
                break
        except requests.RequestException:
            time.sleep(0.1)
    else:
        raise RuntimeError("被测 API 未在限定时间内响应。")

    yield url

    server.should_exit = True
    thread.join(timeout=5)


@pytest.fixture(scope="session")
def auth_token(base_url):
    """从认证接口获取一个有效的 Bearer token（整个会话只取一次）。"""
    resp = requests.post(
        f"{base_url}/auth/token",
        json={"client_id": data.DEMO_CLIENT_ID, "client_secret": data.DEMO_CLIENT_SECRET},
        timeout=10,
    )
    assert resp.status_code == 200, f"获取 token 失败：{resp.text}"
    return resp.json()["access_token"]


@pytest.fixture
def client(base_url, auth_token):
    """已登录的 HTTP 客户端（自动注入 Bearer token）。"""
    from utils.api_client import APIClient

    return APIClient(base_url, token=auth_token)


@pytest.fixture
def unauth_client(base_url):
    """未登录的 HTTP 客户端（用于安全反向用例）。"""
    from utils.api_client import APIClient

    return APIClient(base_url)


@pytest.fixture(autouse=True)
def _reset_state():
    """每个用例执行前重置内存数据，保证用例相互独立。"""
    data.reset_state()
    yield
