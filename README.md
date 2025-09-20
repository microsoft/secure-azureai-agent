# 🚀 Azure AI Agent - 統合アプリケーション

この統合アプリケーションは、Azure Troubleshoot AgentのFastAPIバックエンドとChainlitフロントエンドを単一のApp Serviceで動作させるために設計されています。

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

## 📁 ディレクトリ構造

```
unified-app/
├── app.py                  # 統合アプリケーション（メインエントリーポイント）
├── requirements.txt        # 統合された依存関係
├── startup.sh             # Azure App Service 起動スクリプト
├── azure.yaml             # Azure Developer CLI 設定
├── .deployment            # Azure デプロイメント設定
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

## 🚀 Azure デプロイメント

### Azure Developer CLI を使用

```bash
# Azure にログイン
azd auth login

# プロビジョニングとデプロイ
azd up

# 既存リソースへのデプロイのみ
azd deploy
```

### 手動デプロイ

1. Azure リソースのプロビジョニング:
   ```bash
   az deployment sub create \
     --location japaneast \
     --template-file infra/main.bicep \
     --parameters infra/main.parameters.json
   ```

2. アプリケーションのデプロイ:
   ```bash
   az webapp deployment source config-zip \
     --resource-group rg-your-env-unified \
     --name app-your-env-unified-xxxxx \
     --src unified-app.zip
   ```

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

## ⚡ パフォーマンス

- **App Service Plan**: B2 (Basic tier)
- **Auto Scale**: 必要に応じて設定可能
- **CDN**: 静的コンテンツ配信（オプション）

## 🐛 トラブルシューティング

### よくある問題

1. **Chainlit が起動しない**
   - ログを確認: `az webapp log tail`
   - ポート競合の確認
   - Python 依存関係の確認

2. **プロキシエラー**
   - 内部通信の確認
   - ファイアウォール設定

3. **メモリ不足**
   - App Service Plan のスケールアップ
   - 不要なプロセスの停止

### ログの確認

```bash
# リアルタイムログ
az webapp log tail --resource-group rg-your-env-unified --name app-your-env-unified-xxxxx

# Application Insights でのログ分析
az monitor app-insights query --app your-app-insights --analytics-query "traces | limit 100"
```

## 🔄 従来構成からの移行

### 移行手順

1. **統合アプリのテスト**: ローカルで動作確認
2. **Azure リソース作成**: 新しいリソースグループに作成
3. **データ移行**: 必要に応じてKey Vaultシークレットをコピー
4. **DNS更新**: 新しいエンドポイントに更新
5. **旧リソース削除**: 確認後に削除

### 利点

- **コスト削減**: 1つのApp Serviceで運用
- **管理簡素化**: 単一のデプロイメント
- **パフォーマンス向上**: 内部通信の高速化

## 📝 ライセンス

MIT License - 詳細は [LICENSE](../LICENSE) ファイルを参照してください。