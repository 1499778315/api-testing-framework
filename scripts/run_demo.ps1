# 运行完整测试套件并打开 Allure 报告面板（Windows / PowerShell）。
$ErrorActionPreference = "Stop"
Set-Location (Join-Path $PSScriptRoot "..")

Write-Host "`n[1/2] 正在运行 API 测试套件..." -ForegroundColor Cyan
python -m pytest --alluredir=allure-results

Write-Host "`n[2/2] 正在打开 Allure 报告面板..." -ForegroundColor Cyan
$allureCmd = $null
foreach ($c in @(
    "$env:APPDATA\npm\allure.cmd",
    "$env:ProgramData\chocolatey\bin\allure.cmd",
    "$env:USERPROFILE\scoop\shims\allure.cmd"
)) {
    if (Test-Path $c) { $allureCmd = $c; break }
}

if ($allureCmd) {
    # 通过 cmd.exe 调用：避免 PowerShell 对 .cmd 文件使用 & 运算符时的
    # 配置问题，并正确处理带空格的路径。
    & cmd.exe /d /s /c """$allureCmd"" serve allure-results"
} else {
    Write-Host "`n未找到 Allure CLI，请先安装：" -ForegroundColor Yellow
    Write-Host "  npm install -g allure-commandline" -ForegroundColor White
}
