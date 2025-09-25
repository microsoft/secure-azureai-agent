# 🚀 Secure Azure AI Agent

Azure App Serviceで動作する統合AIエージェントアプリケーション。FastAPIバックエンドとChainlitフロントエンドを単一のApp Serviceで動作させる設計です。

![Azure](https://img.shields.io/badge/azure-%230072C6.svg?style=for-the-badge&logo=microsoftazure&logoColor=white)
![Python](https://img.shields.io/badge/python-3.12%2B-blue?style=for-the-badge&logo=python&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-005571?style=for-the-badge&logo=fastapi)
![Chainlit](https://img.shields.io/badge/Chainlit-000000?style=for-the-badge&logo=chainlit&logoColor=white)

## 🏗️ アーキテクチャ

```
統合アプリケーション (app.py)
├── FastAPI Backend (port 8000)
│   ├── /api/* - APIエンドポイント
│   ├── /health - ヘルスチェック
│   └── /docs - API ドキュメント
└── Chainlit Frontend (port 8501)
    └── Proxy による UI 提供
```

## 📁 プロジェクト構造

```
secure-azureai-agent/
├── app.py                  # 統合アプリケーション（メインエントリーポイント）
├── requirements.txt        # 統合された依存関係
├── startup.sh             # Azure App Service 起動スクリプト
├── azure.yaml.template    # Azure Developer CLI 設定テンプレート
├── backend/               # バックエンドコード
│   ├── src/
│   │   ├── main.py       # FastAPI アプリケーション
│   │   ├── agents/       # Azure Troubleshoot Agent
│   │   ├── telemetry/    # テレメトリ設定
│   │   └── utils/        # ユーティリティ
│   └── requirements.txt
├── frontend/              # フロントエンドコード
│   ├── app.py           # Chainlit アプリケーション
│   ├── chainlit.md      # UI 設定
│   └── requirements.txt
└── infra/                # Azure インフラストラクチャ
    ├── main.bicep       # メイン Bicep テンプレート
    ├── unified-resources.bicep  # リソース定義
    └── main.parameters.json     # パラメータファイル
```

## 🚀 デプロイメント

詳細な手順については [DEPLOYMENT.md](DEPLOYMENT.md) を参照してください。

### Azure Developer CLI を使用

```bash
# Azure にログイン
azd auth login

# プロビジョニングとデプロイ
azd up

# 既存リソースへのデプロイのみ
azd deploy
```

## 🛠️ ローカル開発

### 前提条件

- Python 3.12+
- Azure CLI
- Azure Developer CLI (azd)

### セットアップ

1. 依存関係のインストール:
   ```bash
   pip install -r requirements.txt
   ```

2. 環境変数の設定:
   ```bash
   # .env ファイルを作成
   ENVIRONMENT=development
   CHAINLIT_PORT=8501
   AZURE_KEY_VAULT_URL=your-key-vault-url
   AZURE_OPENAI_ENDPOINT=your-openai-endpoint
   ```

3. アプリケーションの起動:
   ```bash
   python app.py
   ```

アプリケーションは `http://localhost:8000` で起動し、UIは自動的にChainlitにプロキシされます。

## ⚙️ 技術スタック

| カテゴリ | 技術 | バージョン | 説明 |
|---------|------|-----------|------|
| **言語** | Python | 3.12+ | メイン開発言語 |
| **Web Framework** | FastAPI | 最新 | RESTful API |
| **UI Framework** | Chainlit | 最新 | チャットベースUI |
| **AI/ML** | Semantic Kernel | 最新 | AIエージェント |
| **クラウド** | Azure App Service | - | ホスティング |
| **インフラ** | Bicep | - | IaC |

## 🔧 設定

### 環境変数

| 変数名 | 説明 | デフォルト値 |
|--------|------|-------------|
| `PORT` | メインアプリケーションのポート | `8000` |
| `CHAINLIT_PORT` | Chainlit のポート | `8501` |
| `ENVIRONMENT` | 環境タイプ | `development` |
| `PYTHONPATH` | Python パス | `/home/site/wwwroot/backend/src` |

### Azure App Service 設定

- **Python バージョン**: 3.12
- **起動コマンド**: `bash startup.sh`
- **Always On**: 有効
- **HTTPS Only**: 有効

## 📊 監視とログ

- **Application Insights**: 自動的に設定されます
- **Log Analytics**: すべてのログが収集されます
- **ヘルスチェック**: `/health` エンドポイントで確認

## 🔒 セキュリティ

- **Managed Identity**: Azure リソースへの認証に使用
- **Key Vault**: シークレット管理
- **HTTPS**: 強制有効
- **RBAC**: Role-Based Access Control

## 📚 参考資料

- 📖 [ARCHITECTURE.md](ARCHITECTURE.md) - アーキテクチャ詳細
- 📖 [DEPLOYMENT.md](DEPLOYMENT.md) - デプロイメント完全ガイド
- 📖 [DEVELOPMENT.md](DEVELOPMENT.md) - 開発者向けガイド
- 📖 [API.md](API.md) - API ドキュメント
- 📖 [TESTING.md](TESTING.md) - テスト戦略とガイド

## 🤝 サポート

質問や問題がある場合：
1. **Issues** タブで既存の質問を検索
2. 新しい **Issue** を作成して質問
3. [SUPPORT.md](SUPPORT.md) を参照

## 📄 ライセンス

このプロジェクトは [MIT License](LICENSE) の下でライセンスされています。