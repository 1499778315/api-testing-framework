"""
基于 JSON Schema 的响应契约校验。

契约测试验证的是响应的"形状"（字段、类型、必填项）是否保持稳定，
与具体的数值无关。这是发现 API 不兼容变更（字段改名/删除、类型改变）
的关键手段。
"""
from __future__ import annotations

import json
import os

import allure
from jsonschema import Draft202012Validator

_SCHEMA_DIR = os.path.join(os.path.dirname(__file__), "..", "tests", "schemas")


def load_schema(name: str) -> dict:
    path = os.path.join(_SCHEMA_DIR, name)
    with open(path, encoding="utf-8") as fh:
        return json.load(fh)


def assert_matches_schema(instance, schema_name: str) -> None:
    """若响应不符合契约，则聚合全部违规项并抛出可读的断言错误。"""
    schema = load_schema(schema_name)
    validator = Draft202012Validator(schema)
    errors = sorted(validator.iter_errors(instance), key=lambda e: list(e.path))

    if errors:
        detail = "\n".join(
            f"- {'/'.join(map(str, e.path)) or '(根)'}: {e.message}" for e in errors
        )
        allure.attach(detail, name=f"契约违规（{schema_name}）",
                      attachment_type=allure.attachment_type.TEXT)
        raise AssertionError(
            f"响应不符合契约 '{schema_name}':\n{detail}"
        )
