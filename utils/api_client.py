"""
基于 ``requests`` 的轻量 HTTP 客户端，供接口测试使用。

集中管理基础 URL、Bearer token 注入，并把每次请求/响应作为证据记录到
Allure 报告。将这些逻辑放在测试之外，可以让用例保持声明式、易读。
"""
from __future__ import annotations

import json
from typing import Any, Optional

import allure
import requests


class APIClient:
    def __init__(self, base_url: str, token: Optional[str] = None, timeout: int = 10):
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout
        self.session = requests.Session()
        if token:
            self.session.headers.update({"Authorization": f"Bearer {token}"})

    def _request(self, method: str, path: str, **kwargs) -> requests.Response:
        url = f"{self.base_url}{path}"
        with allure.step(f"{method} {path}"):
            response = self.session.request(method, url, timeout=self.timeout, **kwargs)
            _attach("请求", _format_request(method, url, kwargs))
            _attach("响应", _format_response(response))
            return response

    def get(self, path: str, **kwargs) -> requests.Response:
        return self._request("GET", path, **kwargs)

    def post(self, path: str, **kwargs) -> requests.Response:
        return self._request("POST", path, **kwargs)

    def put(self, path: str, **kwargs) -> requests.Response:
        return self._request("PUT", path, **kwargs)

    def delete(self, path: str, **kwargs) -> requests.Response:
        return self._request("DELETE", path, **kwargs)


def _attach(name: str, body: str) -> None:
    allure.attach(body, name=name, attachment_type=allure.attachment_type.TEXT)


def _format_request(method: str, url: str, kwargs: dict) -> str:
    lines = [f"{method} {url}"]
    if "params" in kwargs and kwargs["params"]:
        lines.append(f"查询参数: {kwargs['params']}")
    if "json" in kwargs and kwargs["json"] is not None:
        lines.append("请求体:\n" + json.dumps(kwargs["json"], indent=2, ensure_ascii=False))
    return "\n".join(lines)


def _format_response(response: requests.Response) -> str:
    lines = [f"HTTP {response.status_code} ({response.elapsed.total_seconds() * 1000:.0f} ms)"]
    try:
        lines.append(json.dumps(response.json(), indent=2, ensure_ascii=False))
    except ValueError:
        lines.append(response.text)
    return "\n".join(lines)
