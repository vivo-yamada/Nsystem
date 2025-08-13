@echo off
cd /d "%~dp0"

echo WSL内でDjangoサーバーを起動します...
echo 仮想環境をアクティベートしてサーバーを起動中...

REM WSL内で仮想環境をアクティベートしてサーバー起動
wsl bash -c "cd /mnt/c/ClaudeCode/APPS/Nsystem && source venv/bin/activate && python manage.py migrate && python manage.py runserver 0.0.0.0:8080"

pause