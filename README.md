# 接口自动化测试框架（API Testing Framework）

[![CI](https://github.com/1499778315/api-testing-framework/actions/workflows/ci.yml/badge.svg)](https://github.com/1499778315/api-testing-framework/actions/workflows/ci.yml)
![Python](https://img.shields.io/badge/python-3.10%2B-blue.svg)
![pytest](https://img.shields.io/badge/tested%20with-pytest-0a9edc.svg)
![Contract testing](https://img.shields.io/badge/contracts-JSON%20Schema-6f42c1.svg)
![Reporting](https://img.shields.io/badge/reporting-Allure-orange.svg)
[![Allure Report](https://img.shields.io/badge/Allure-live%20report-fa4d56?logo=allure)](https://1499778315.github.io/api-testing-framework/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

> 📘 第一次接触或初级水平？先读 **[详细入门指南](docs/GUIA.md)**
> （含术语表、每个工具的作用、本地运行与 CI 说明）。

一个专业的 **REST API 接口自动化测试框架**，基于 `pytest` + `requests` 构建，
覆盖功能、安全、边界和**契约（JSON Schema）**测试，集成 **Allure** 报告与 CI。

> **开箱即用。** 框架自带被测系统——一个小巧但真实的 FastAPI 服务，会在
> 空闲本地端口上自动启动。克隆、安装、运行 `pytest` 即可。无需外部 API、
> 无需凭据、不会偶发失败。

```
39 passed in ~2s
```

## 为什么做这个项目

接口质量问题很隐蔽：一个返回错误响应体的 `200`、一个缺失的 `401`、一份
悄悄漂移的契约。本框架用资深 QA 工程师的方式对 API 进行测试：

- **正向**用例（happy path：正确的状态码与响应体）
- **反向**用例（`401` 认证失败、`404` 不存在、`422` 校验失败）
- **边界**条件（分页上限、字段约束）
- **契约**测试（响应按 JSON Schema 校验）
- **业务规则**（如余额份额占比合计必须为 100%）

它是 [`data-quality-framework`](https://github.com/d4tr3s14/data-quality-framework)
在 **API 层的配套项目**：两者测试同一个虚构的多基金投资平台 **"Veridian"**
——一个在数据/数仓层，一个在 API 层。所有数据均为虚构和合成数据。

## 测试了哪些内容

| 测试套件 | 类别 | 要点 |
|---|---|---|
| `test_health.py` | 冒烟 | 服务存活，无需认证 |
| `test_auth.py` | 安全 / 反向 | Bearer token 签发、错误/缺失/无效 token 返回 `401`、畸形请求体返回 `422` |
| `test_customers.py` | 功能 / 边界 | 列表、分页（含越界 → `422`）、segment 筛选、`404`、`201` 创建、`422` 校验 |
| `test_balances.py` | 功能 / 业务规则 | 余额查询、**份额占比合计为 100%** |
| `test_contracts.py` | 契约 | 每个响应按 JSON Schema 校验 |

**39 个测试**，通过 `pytest.mark.parametrize` 数据驱动，完全隔离
（每个测试前重置内存状态）。

## 架构

```
pytest ──▶ tests/*.py ──▶ utils/api_client.py ──(HTTP, requests)──▶ FastAPI 应用
                      └──▶ utils/schema_validator.py (JSON Schema)        (app/)
conftest.py 用 uvicorn 在空闲端口启动应用，测试结束后关闭。
```

测试通过 **localhost 上的真实 HTTP** 访问 API（非进程内调用），因此行为与
访问已部署的服务完全一致。详见 [docs/architecture.md](docs/architecture.md)。

## 快速开始

### 前置条件

- Python 3.10+
- （可选，查看报告面板）[Allure CLI](https://allurereport.org/docs/install/) —
  例如 `npm install -g allure-commandline`

### 1. 搭建环境

```bash
python -m venv .venv
# Windows（PowerShell）：
.venv\Scripts\Activate.ps1
# Linux / macOS：
source .venv/bin/activate

pip install -r requirements.txt
```

### 2. 运行测试

```bash
pytest
```

### 3. 一条命令运行并打开 Allure 报告

**Windows（PowerShell）：**

```powershell
.\scripts\run_demo.ps1
```

> 若遇到执行策略错误，先为当前会话放开脚本权限：
> `Set-ExecutionPolicy -Scope Process -ExecutionPolicy RemoteSigned`

**Linux / macOS：**

```bash
./scripts/run_demo.sh
```

每个测试都会把**请求和响应**附加到 Allure 报告中，任何结果都可完整追溯。

## 手动体验 API（可选）

被测系统是一个真实的 FastAPI 应用，带交互式 Swagger 文档：

```bash
uvicorn app.main:app --reload
# 然后打开 http://127.0.0.1:8000/docs
```

`POST /auth/token` 的演示账号：`client_id=veridian-demo`、
`client_secret=demo-secret`。

受保护接口需要 Bearer token：先调用 `POST /auth/token` 拿到 `access_token`，
再点 Swagger 右上角的 **Authorize** 按钮粘贴该 token
（**不要**自己加 `Bearer ` 前缀，Swagger 会自动补上），之后所有受保护接口
都会自动携带这个凭证，无需逐端点填写请求头。

## 项目结构

```
api-testing-framework/
├── app/                      # 被测系统（本地 FastAPI 模拟 API）
│   ├── main.py               # 接口端点：认证、客户、余额
│   └── data.py               # 确定性的内存合成数据
├── tests/
│   ├── test_health.py
│   ├── test_auth.py
│   ├── test_customers.py
│   ├── test_balances.py
│   ├── test_contracts.py
│   └── schemas/              # JSON Schema 契约文件
├── utils/
│   ├── api_client.py         # requests 封装 + Allure 请求/响应日志
│   └── schema_validator.py   # JSON Schema 契约校验
├── conftest.py               # fixtures：启动/关闭 API、认证 token、客户端
├── scripts/                  # 一键运行脚本
├── .github/workflows/ci.yml  # CI：安装依赖 + 跑测试 + 上传 Allure 结果
├── pytest.ini
└── requirements.txt
```

## 技术栈

- **Python 3.10+**、**pytest**（通过 parametrize 数据驱动）
- **requests**（HTTP）、**jsonschema**（契约测试）
- **FastAPI** + **uvicorn**（自包含的被测系统）
- **Allure**（报告）、**GitHub Actions**（CI）

## 配套项目

本框架在 **API 层** 校验虚构的 **"Veridian"** 平台。它的配套项目
[**data-quality-framework**](https://github.com/d4tr3s14/data-quality-framework)
在 **数据/数仓层** 校验同一平台（基于 behave + BigQuery/DuckDB 的 BDD 数据质量
与本地到云迁移测试）。两者共同展示端到端的质量覆盖。

## 说明

- 所有数据与实体均为**虚构和合成**——不包含任何真实或专有数据。
- 模拟 API 的存在是为了让测试套件可复现，并支持按需触发可控错误条件
  （`401`/`404`/`422`）。

## 许可证

[MIT](LICENSE)

## 致谢

本项目基于 [d4tr3s14/api-testing-framework](https://github.com/d4tr3s14/api-testing-framework)
（MIT License, Copyright (c) 2025 David Leiva）改造而来，原作者提供了完整的框架设计：
自包含的 FastAPI 被测系统、fixtures 的组织方式，以及功能 / 安全 / 边界 / 契约
四类测试的划分。

本仓库在此基础上完成的工作：

- **中文本地化** —— 文档、代码注释、接口文案、JSON Schema 描述与测试用例名
- **鉴权方案改进** —— 安全方案在 OpenAPI 中声明为 `HTTPBearer(auto_error=False)`：
  Swagger UI 出现 `Authorize` 按钮，可全局一次授权，不必逐端点填写请求头；
  同时保留原有 `401` 语义（自定义文案 + `WWW-Authenticate: Bearer`）
  与 `422` 请求体校验行为
- **验证** —— `pytest`：39 passed；并手工回归了 6 种鉴权边界场景
  （无 token / 错误 token / `Bearer` 大小写 / `Basic` 方案 / 裸 token / 正确 token）

感谢原作者的框架设计。

