#!/bin/bash

# ============================================
# 🔧 ハンズオン設定: 以下を個人の環境に合わせて変更してください
# ============================================

# 既存Azureリソースの設定 (az resource list で確認可能)
RESOURCE_GROUP="redteaming-demo-rg-swe-mkurahara"          # 🔧 変更必要: あなたのResource Group名
BACKEND_APP="redteaming-demo-back-swe-mkurahara"           # 🔧 変更必要: あなたのバックエンドApp Service名
FRONTEND_APP="redteaming-demo-front-swe-mkurahara"         # 🔧 変更必要: あなたのフロントエンドApp Service名

# Azure OpenAI/AI Foundryのエンドポイント (AI Foundryポータルで確認)
AZURE_OPENAI_ENDPOINT="https://redteaming-demo-aifoundry-swe-mkurahara.openai.azure.com/"  # 🔧 変更必要: あなたのAI Foundryエンドポイント

# ============================================

echo "🔧 既存App Serviceの設定を更新しています..."
echo "📋 使用するリソース:"
echo "   Resource Group: $RESOURCE_GROUP"
echo "   Backend App: $BACKEND_APP"
echo "   Frontend App: $FRONTEND_APP"
echo ""

# バックエンドApp Serviceの設定
echo "📱 バックエンドApp Service設定中..."
az webapp config set \
  --resource-group $RESOURCE_GROUP \
  --name $BACKEND_APP \
  --startup-file "gunicorn --bind 0.0.0.0:8000 src.main:app -k uvicorn.workers.UvicornWorker"

# バックエンドApp Serviceの環境変数設定
echo "⚙️ バックエンド環境変数設定中..."
az webapp config appsettings set \
  --resource-group $RESOURCE_GROUP \
  --name $BACKEND_APP \
  --settings \
    AZURE_OPENAI_ENDPOINT="$AZURE_OPENAI_ENDPOINT" \
    FRONTEND_URL="https://$FRONTEND_APP.azurewebsites.net" \
    ENVIRONMENT="production" \
    PYTHONPATH="/home/site/wwwroot" \
    PYTHONUNBUFFERED="1"

# フロントエンドApp Serviceの設定
echo "🎨 フロントエンドApp Service設定中..."
az webapp config set \
  --resource-group $RESOURCE_GROUP \
  --name $FRONTEND_APP \
  --startup-file "chainlit run app.py --host 0.0.0.0 --port 8000"

# フロントエンドApp Serviceの環境変数設定
echo "⚙️ フロントエンド環境変数設定中..."
az webapp config appsettings set \
  --resource-group $RESOURCE_GROUP \
  --name $FRONTEND_APP \
  --settings \
    BACKEND_API_URL="https://$BACKEND_APP.azurewebsites.net" \
    PYTHONUNBUFFERED="1"

# CORS設定の確認・更新
echo "🌐 CORS設定更新中..."
az webapp cors add \
  --resource-group $RESOURCE_GROUP \
  --name $BACKEND_APP \
  --allowed-origins "https://$FRONTEND_APP.azurewebsites.net" \
  --allowed-origins "https://localhost:8501" \
  --allowed-origins "https://127.0.0.1:8501"

echo "✅ 設定更新完了！"

# 設定確認
echo "📋 現在の設定を確認しています..."
echo "バックエンドApp Service URL: https://$BACKEND_APP.azurewebsites.net"
echo "フロントエンドApp Service URL: https://$FRONTEND_APP.azurewebsites.net"

# App Serviceの再起動
echo "🔄 App Serviceを再起動しています..."
az webapp restart --resource-group $RESOURCE_GROUP --name $BACKEND_APP
az webapp restart --resource-group $RESOURCE_GROUP --name $FRONTEND_APP

echo "🎉 すべての設定が完了しました！"
