# Frontend-Only Branch

このブランチはフロントエンド（Chainlit WebUI）専用です。

## 構成
- `frontend/` - Chainlit アプリケーション
- `eval/` - 評価モジュール（オプション）
- `azure.yaml` - フロントエンド用設定

## デプロイ用環境変数
```bash
# Backend API接続（必須）
BACKEND_API_URL=https://your-backend-appservice.azurewebsites.net

# Optional: AI Foundry評価機能
PROJECT_ENDPOINT=https://your-project.services.ai.azure.com/api/projects/firstProject

# Runtime
LOG_LEVEL=INFO
```

## 起動方法
```bash
cd frontend
chainlit run app.py --port 8000
```

## Azure App Service設定
- **スタートアップコマンド**: `cd frontend && chainlit run app.py --port 8000`
- **ポート**: 8000
- **依存サービス**: バックエンドAPI
