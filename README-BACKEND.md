# Backend-Only Branch

このブランチはバックエンド（FastAPI）専用です。

## 構成
- `backend/` - FastAPI アプリケーション
- `azure.yaml` - バックエンド用設定

## デプロイ用環境変数
```bash
# Core (必須)
AZURE_OPENAI_ENDPOINT=https://your-openai-resource.openai.azure.com/
AZURE_OPENAI_API_KEY=your-openai-api-key
AZURE_OPENAI_DEPLOYMENT_NAME=gpt-4

# Runtime
ENVIRONMENT=production
PORT=8000

# Security
FRONTEND_URL=https://your-frontend-appservice.azurewebsites.net
ALLOWED_HOST=your-backend-appservice.azurewebsites.net
```

## 起動方法
```bash
cd backend
python src/main.py
```

## Azure App Service設定
- **スタートアップコマンド**: `cd backend && python src/main.py`
- **ポート**: 8000
- **ヘルスチェック**: `/health`
