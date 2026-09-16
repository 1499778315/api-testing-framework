#!/usr/bin/env bash
# 运行完整测试套件并打开 Allure 报告面板（Linux / macOS）。
set -euo pipefail
cd "$(dirname "$0")/.."

echo "[1/2] 正在运行 API 测试套件..."
python -m pytest --alluredir=allure-results

echo "[2/2] 正在打开 Allure 报告面板..."
if command -v allure >/dev/null 2>&1; then
    allure serve allure-results
else
    echo "未找到 Allure CLI，请先安装：npm install -g allure-commandline"
fi
