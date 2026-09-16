# 架构说明

## 设计目标

1. **自包含。** 被测系统（一个 FastAPI 应用）随测试一起分发并在本地运行，
   因此测试套件无需任何外部服务，完全可复现——克隆、安装、`pytest`。
2. **真实 HTTP。** 测试通过 `requests` 访问 localhost 上的 API，与访问已部署
   服务的方式完全一致（不使用进程内捷径）。
3. **分层覆盖。** 功能（正向/反向/边界）、安全（认证）与契约（JSON Schema）
   检查，全部汇总到 Allure 报告中。

## 组件

```
                    pytest  （测试运行器）
                      │
        ┌─────────────┼─────────────────────────┐
        │             │                          │
   conftest.py    tests/*.py                utils/
   (fixtures)    (测试用例)        ┌───────────┴───────────┐
        │                            │                       │
        │                       api_client.py        schema_validator.py
        │                       (requests 封装)     (JSON Schema 契约)
        │
        ▼  在线程中启动（uvicorn，空闲端口）
   app/main.py  ── FastAPI "Veridian 投资平台 API"（被测系统）
   app/data.py  ── 确定性的内存合成数据
```

## fixture 生命周期（`conftest.py`）

- `base_url` *（session）* — 选取空闲端口，用 uvicorn 在守护线程中启动 API，
  轮询 `/health` 直到就绪，yield URL，测试结束关闭服务器。
- `auth_token` *（session）* — 执行一次 OAuth 风格的 token 换取。
- `client` / `unauth_client` *（function）* — 已登录与匿名的 `APIClient` 实例。
- `_reset_state` *（autouse）* — 每个测试前恢复内存数据集，保证用例相互独立
  （例如：创建客户不会影响其他用例的计数）。

## 测试分类

| 文件 | 类别 | 示例 |
|---|---|---|
| `test_health.py` | 冒烟 | 服务存活 |
| `test_auth.py` | 安全 / 反向 | 有效 token、错误凭据 401、无/无效 token 401、畸形请求体 422 |
| `test_customers.py` | 功能 / 边界 | 列表、分页上限、segment 筛选、404、201 创建、422 校验 |
| `test_balances.py` | 功能 / 业务规则 | 余额查询、份额占比合计 100% |
| `test_contracts.py` | 契约 | 响应按 JSON Schema 校验 |

## 为什么用模拟 API 而不是公共 API

访问公共 API（如 JSONPlaceholder）会让测试套件偶发失败且不确定：网络故障、
限流、未通知的变更都会在与代码无关的情况下破坏 CI。自带被测系统可以保证
套件确定性，并完整演示测试生命周期，包括公共 API 很少允许按需触发的可控
错误条件（401/404/422）。

## 配套项目

这是 [`data-quality-framework`](https://github.com/d4tr3s14/data-quality-framework)
在 **API 层** 的对应部分，后者在 **数据/数仓层** 校验同一个虚构的 "Veridian"
平台。两者共同展示端到端的质量覆盖：落入数仓的数据与对外暴露这些数据的 API。
