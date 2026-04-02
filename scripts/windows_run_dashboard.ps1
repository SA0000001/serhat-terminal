param(
    [int]$Port = 8501
)

$repoRoot = Split-Path -Parent $PSScriptRoot
Set-Location $repoRoot
python -m streamlit run app/dashboard/main.py --server.port $Port
