# setup_env.ps1
# Use this script to create a virtual environment with a Python version compatible with scikit-learn 1.4.2.
# You need Python 3.11 or 3.12 installed on Windows.

Write-Host "Checking for Python 3.12..."
$pythonPath = & py -3.12 -c "import sys; print(sys.executable)" 2>$null
if (-not $?) {
    Write-Host "Python 3.12 not found. Install it from https://www.python.org/downloads/windows/ or use winget."
    Write-Host "Example: winget install --id Python.Python.312"
    exit 1
}

Write-Host "Using Python: $pythonPath"
$venvPath = Join-Path $PSScriptRoot "venv312"
if (-Not (Test-Path $venvPath)) {
    Write-Host "Creating virtual environment at $venvPath..."
    & py -3.12 -m venv $venvPath
} else {
    Write-Host "Virtual environment already exists at $venvPath"
}

Write-Host "Activating virtual environment..."
& "$venvPath\Scripts\Activate.ps1"
Write-Host "Upgrading pip..."
python -m pip install --upgrade pip
Write-Host "Installing requirements..."
pip install -r requirements.txt
Write-Host "Setup complete. Use 'streamlit run app.py' while the virtual environment is activated."