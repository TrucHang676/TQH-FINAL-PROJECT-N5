@echo off
echo ==============================================
echo Khởi động Hệ thống Dashboard IT Việt Nam
echo ==============================================

echo [1/2] Dang khoi dong Backend (FastAPI) tren cong 8000...
start "Backend API Server" cmd /k "cd dashboard && py -m uvicorn backend.main:app --reload"

echo [2/2] Dang khoi dong Frontend (React/Vite) tren cong 5173...
start "Frontend React Server" cmd /k "cd dashboard/frontend && npm run dev"

echo Da kich hoat ca hai server! Hai cua so terminal moi da duoc mo.
echo Hay doi vai giay roi truy cap http://localhost:5173 tren trinh duyet.
pause
