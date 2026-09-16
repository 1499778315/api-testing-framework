# 📘 详细入门指南（适合所有水平）

本指南**一步步**讲解如何运行、理解并修改 **api-testing-framework** 项目，
从你的电脑到 GitHub 上 CI 执行时发生的一切。目标是让**初级开发者**也能
毫无障碍地完成。

> 建议阅读顺序：**1)** 这是什么？→ **2)** 术语表 → **3)** 框架 → **4)** 前置条件 →
> **5)** 克隆 → **6)** 本地运行 → **7)** 报告 → **8)** 如何修改 → **9)** CI 做了什么。

---

## 1. 这是什么项目？

这是一个用于**测试 REST API**（通过 HTTP 返回数据、通常是 JSON 的服务）的框架。
它校验 API 是否返回正确内容：正确的**状态码**（200、401、404、422…）、预期的
**响应体**、**安全**规则（认证）、**边界**（分页），以及**契约**（JSON 的形状）
是否未经通知就发生变化。

它自带**测试用 API**（一个自动在本地端口启动的 **FastAPI** 服务），因此
**运行不依赖任何外部服务**。使用 **pytest**，并通过 **Allure** 生成带每个测试
请求/响应细节的报告。

```
pytest ─► tests/*.py ─► utils/api_client (HTTP) ─► FastAPI 应用 (app/) ─► Allure
```

---

## 2. 术语表（关键概念）

| 术语 | 简单解释 |
|---------|--------------------------|
| **API REST** | 通过 HTTP 提供数据的服务（如 `GET /api/customers`）。 |
| **Endpoint（端点）** | API 的一条路由（如 `POST /api/auth/token`）。 |
| **状态码** | 表示结果的数字：`200` 成功、`401` 未授权、`404` 不存在、`422` 数据非法。 |
| **Payload / Body（请求体）** | 发送或接收的内容（JSON）。 |
| **Token / Bearer** | 放在请求头中用于认证的"凭据"。 |
| **契约测试** | 校验响应是否符合约定的**形状**（JSON Schema）。 |
| **JSON Schema** | 描述 JSON 应长什么样的文档（字段、类型、必填项）。 |
| **Happy path（正向路径）** | 正确/成功的路径。 |
| **Negative path（反向路径）** | 刻意构造的错误场景（错误 token、非法数据…）。 |
| **Boundary（边界）** | 极限场景（如请求第 0 页或超范围的大小）。 |
| **pytest** | Python 的测试框架。 |
| **Fixture** | 可复用的准备件（这里指：测试前启动 API）。 |
| **Parametrize（参数化）** | 用多组数据重复执行一个测试（数据驱动）。 |
| **SUT** | *System Under Test*，被测系统（这里指 `app/` 下的 FastAPI API）。 |
| **Allure** | 交互式报告，展示每个测试的详情（请求/响应）。 |
| **CI** | 每次变更时自动在 GitHub 上运行测试。 |
| **gh-pages** | 用于把 Allure 报告发布为网站的分支。 |

---

## 3. 框架与语言（各自的作用）

| 工具 | 语言 | 在本项目中**起什么作用** |
|-------------|----------|----------------------------------------|
| **Python** | — | 框架的基础语言。 |
| **pytest** | Python | 测试**执行器**。 |
| **requests** | Python | HTTP 客户端：发起对 API 的调用。 |
| **jsonschema** | Python | 校验响应是否符合**契约**（JSON Schema）。 |
| **allure-pytest** | Python | 生成 **Allure** 报告并附加请求/响应。 |
| **FastAPI** | Python | **被测系统（SUT）**：带端点的测试用 API。 |
| **Uvicorn** | Python | 在本地端口启动 FastAPI API 的**服务器**。 |
| **GitHub Actions** | YAML | **CI**：运行测试并发布报告。 |

---

## 4. 前置条件

1. **Python 3.10+** → https://www.python.org/downloads/ （`python --version` 验证）。
2. **Git** → https://git-scm.com/
3. *（可选，用于报告面板）* **Allure CLI** → `npm install -g allure-commandline`。

> 无需配置任何外部内容：测试用 API 会**自动**启动。

---

## 5. 克隆项目

```bash
git clone https://github.com/1499778315/api-testing-framework.git
cd api-testing-framework
```

---

## 6. 本地运行（分步）

### 第 1 步 — 虚拟环境与安装
```bash
python -m venv .venv
```
激活：
- **Windows（PowerShell）：** `.\.venv\Scripts\Activate.ps1`
- **Linux / macOS：** `source .venv/bin/activate`

安装依赖：
```bash
pip install -r requirements.txt
```

### 第 2 步 — 运行测试
```bash
pytest
```
测试用 API 会**自动启动**（无需手动启动）。你会看到类似 `39 passed in ~2s` 的结果。

### 第 3 步 — 带 Allure 报告面板（一条命令）
- **Windows（PowerShell）：** `.\scripts\run_demo.ps1`
- **Linux / macOS：** `./scripts/run_demo.sh`

或手动执行：
```bash
pytest --alluredir=allure-results
allure serve allure-results
```

### 手动体验 API（可选）
```bash
uvicorn app.main:app --reload
# 然后打开 http://127.0.0.1:8000/docs  （交互式 Swagger 文档）
```

---

## 7. 报告

- **Allure** 展示每个测试及其附带的**请求和响应**，任何结果都可追溯。
  用 `allure serve allure-results` 打开。

- **HTML 报告（不需要 Allure CLI，也不需要 Java）**：一条命令生成后，
  **双击** `reports/report.html` 就能看（单文件自包含，不用起本地服务）：

  ```bash
  pytest --alluredir=reports/allure-results --clean-alluredir --html=reports/report.html --self-contained-html
  ```

  产物统一放在 `reports/` 下（已在 `.gitignore` 中，不会提交）：

  ```
  reports/
  ├── report.html          # 自包含 HTML 报告，直接双击打开
  └── allure-results/      # Allure 原始 JSON（可 allure serve reports/allure-results）
  ```

  两个容易踩的坑：`report.html` **每次运行都会被覆盖**（同名文件，旧报告不留）；
  `allure-results/` 里的文件名是随机 UUID，**不加 `--clean-alluredir` 就会把多轮
  结果混在一起**（越跑文件越多），加上它则每次运行前自动清空。

---

## 8. 如何修改项目（初级配方）

### a) 新增一条测试
在 `tests/` 下创建或编辑文件（必须以 `test_` 开头）。示例：
```python
def test_health_ok(api_client):
    resp = api_client.get("/health")
    assert resp.status_code == 200
```
`pytest` 会自动发现它。

### b) 数据驱动测试（多组用例）
```python
import pytest

@pytest.mark.parametrize("page_size", [0, 999])
def test_pagination_out_of_range(api_client, page_size):
    resp = api_client.get(f"/api/customers?page_size={page_size}")
    assert resp.status_code == 422
```

### c) 新增/修改契约（JSON Schema）
契约文件位于 `tests/schemas/`。新建一个（如 `order.json`），并在测试中用
`utils/schema_validator.py` 校验它。

### d) 给测试用 API 新增端点
编辑 `app/main.py`（路由）和 `app/data.py`（内存数据）。

### e) 了解各部分的位置
- `tests/*.py` → 测试（**做什么**）。
- `utils/api_client.py` → 测试使用的 HTTP 客户端。
- `utils/schema_validator.py` → 按 JSON Schema 校验响应。
- `conftest.py` → 测试前**启动 API**、结束后关闭。
- `app/` → 被测的 FastAPI API。

---

## 9. GitHub 上的 CI 做了什么？（分步）

CI 位于 `.github/workflows/ci.yml`，在每次 `push`/`pull request` 时运行：

1. **Set up Python + install** — 安装 Python 与 `requirements.txt`。
2. **Run API test suite** — `pytest --alluredir=allure-results`（API 在测试内部
   自动启动）。
3. **Upload Allure results** — 把结果作为可下载的工件保存。
4. **Job `publish-report`（仅在 push 时）** — 生成 **Allure** 报告并
   **发布到 GitHub Pages**（`gh-pages` 分支）。

### 在哪里看结果？
- GitHub → **Actions** 标签页 → 对应 run（✅ / ❌）。
- 在线 Allure 报告：**https://1499778315.github.io/api-testing-framework/**
  （需在 *Settings → Pages → 分支 `gh-pages`* 中启用 GitHub Pages）。

---

## 10. 常见问题

| 问题 | 解决方法 |
|----------|----------|
| `pytest: command not found` | 激活 `.venv` 并 `pip install -r requirements.txt`。 |
| 测试找不到 API | `conftest.py` 会自动启动；若失败，检查端口是否被占用。 |
| `allure: command not found` | 安装 CLI：`npm install -g allure-commandline`。 |
| PowerShell 阻止脚本 | `Set-ExecutionPolicy -Scope Process -ExecutionPolicy RemoteSigned`。 |
| Allure 徽章返回 404 | 未启用 GitHub Pages（`gh-pages` 分支）。 |

---

## 11. 文件地图

```
tests/                 测试（test_auth、test_customers、test_balances、...）
  schemas/             响应的 JSON Schema 契约
utils/
  api_client.py        测试使用的 HTTP 客户端
  schema_validator.py  按 JSON Schema 校验响应
app/                   被测的 FastAPI API（main.py = 路由，data.py = 数据）
conftest.py            自动为测试启动/关闭 API
pytest.ini            pytest 配置
scripts/run_demo.*     运行测试套件并打开 Allure
.github/workflows/ci.yml  CI 流水线
```

---

有疑问？从**第 6 节**开始（安装并运行 `pytest`）：API 会自动启动，几秒钟内
就能看到结果。
