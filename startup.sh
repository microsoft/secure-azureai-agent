#!/bin/bash

# Azure App Service 用起動スクリプト
# 統合アプリケーションの起動設定

echo "🚀 Starting Azure Troubleshoot Agent Unified App"

# 環境変数の設定
export PYTHONPATH="/home/site/wwwroot/backend/src:$PYTHONPATH"
export BACKEND_API_URL="http://localhost:$PORT"
export CHAINLIT_PORT="8501"
export ENVIRONMENT="production"

# ログ出力先の設定
export PYTHONUNBUFFERED=1

# 作業ディレクトリの設定
cd /home/site/wwwroot

echo "📦 Installing dependencies..."
# 依存関係のインストール（Azure App Service では自動で実行される）
# pip install -r requirements.txt

echo "🔧 Environment setup:"
echo "PORT: $PORT"
echo "CHAINLIT_PORT: $CHAINLIT_PORT"
echo "PYTHONPATH: $PYTHONPATH"
echo "Working directory: $(pwd)"

# ディレクトリ構造の確認
echo "📂 Directory structure:"
ls -la

# Gunicorn を使用してアプリケーションを起動
echo "🎯 Starting application with Gunicorn and UvicornWorker..."

# UvicornWorkerが利用できない場合の fallback
if python -c "import uvicorn.workers" 2>/dev/null; then
    echo "✅ UvicornWorker is available"
    exec gunicorn app:app \
        --bind 0.0.0.0:$PORT \
        --workers 1 \
        --worker-class uvicorn.workers.UvicornWorker \
        --timeout 120 \
        --keepalive 5 \
        --max-requests 1000 \
        --max-requests-jitter 100 \
        --access-logfile - \
        --error-logfile - \
        --log-level info \
        --capture-output
else
    echo "⚠️  UvicornWorker not available, using uvicorn directly"
    exec uvicorn app:app \
        --host 0.0.0.0 \
        --port $PORT \
        --workers 1 \
        --timeout-keep-alive 5 \
        --access-log \
        --log-level info
fi