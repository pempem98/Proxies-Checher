@echo off
REM Check if Python is installed
where python >nul 2>nul
if %errorlevel% neq 0 (
    echo Python not found. Installing...
    REM Install the latest version of Python 3
    powershell.exe -Command "iex (new-object net.webclient).downloadstring('https://www.python.org/ftp/python/3.10.1/python-3.10.1-amd64.exe')"
    python-3.10.1-amd64.exe /quiet InstallAllUsers=1 PrependPath=1 Include_test=0
)

REM Check if the required Python packages are installed
python -c "import asyncio, configparser, csv, playwright" >nul 2>nul
if %errorlevel% neq 0 (
    echo Required Python packages not found. Installing...
    REM Install the required Python packages
    pip install asyncio configparser playwright[async]
)

REM Check if the Playwright browser drivers are installed
if not exist "%USERPROFILE%\\AppData\\Local\\ms-playwright\\" (
    echo Playwright browser drivers not found. Installing...
    REM Install the Playwright browser drivers
    python -m playwright install
)

REM Check if the proxies.csv and config.ini files exist
if not exist proxies.csv (
    echo Error: proxies.csv file not found.
    exit /b 1
)
if not exist config.ini (
    echo Error: config.ini file not found.
    exit /b 1
)

REM Check if the proxies_checker.py script is downloaded and download it from GitHub if necessary
if not exist proxies_checker.py (
    echo proxies_checker.py script not found. Downloading from GitHub...
    curl -LJO https://raw.githubusercontent.com/pempem98/Proxies-Checher/main/proxies_checker.py
)

echo All dependencies are installed.
echo Running the Python script...

REM Run the Python script
python proxies_checker.py
del proxies_checker.py

pause
