# Azure Troubleshoot Agent - 統合アプリケーション

このブランチは、Azure App Serviceでの自動デプロイに最適化された統合アプリケーションです。

## 🏗️ アーキテクチャ

```
統合アプリケーション (単一のApp Service)
├── FastAPI (メインアプリ) - ポート 8000
│   ├── /api/* - バックエンドAPIエンドポイント
│   ├── /health - ヘルスチェック
│   └── /* - Chainlitへのプロキシ
└── Chainlit (サブプロセス) - ポート 8501
    └── WebSocketとUI処理
```

## 📁 プロジェクト構造

```
.
├── app.py                 # 統合メインアプリケーション
├── requirements.txt       # 統合依存関係
├── startup.sh            # Azure起動スクリプト
├── azure.yaml            # Azure Developer CLI設定
├── .deployment           # Azure デプロイ設定
├── backend/              # バックエンドコード
│   ├── src/
│   │   ├── main.py
│   │   ├── agents/
│   │   ├── telemetry/
│   │   └── utils/
│   └── requirements.txt
├── frontend/             # フロントエンドコード
│   ├── app.py
│   ├── chainlit.md
│   └── requirements.txt
└── infra/               # Bicepインフラストラクチャ
    ├── main.bicep
    ├── unified-resources.bicep
    └── main.parameters.json
```

## 🚀 デプロイ手順

### Azure Developer CLI を使用

```bash
# Azure CLI でログイン
az login

# 環境を初期化
azd init

# デプロイ
azd up
```

### GitHub Actions を使用

1. リポジトリのSecrets設定：
   - `AZURE_CREDENTIALS`
   - `AZURE_SUBSCRIPTION_ID`
   - `AZURE_CLIENT_ID`
   - `AZURE_TENANT_ID`

2. プッシュすると自動でデプロイされます

## 🔧 ローカル開発

```bash
# 依存関係をインストール
pip install -r requirements.txt

# 統合アプリを起動
python app.py
```

アプリケーションは http://localhost:8000 でアクセス可能です。

## 📊 主要な利点

### 🎯 シンプルな構成
- **単一App Service**: 1つのサービスで全機能を提供
- **統合ログ**: 一箇所で全てのログを管理
- **簡単なモニタリング**: 単一のエンドポイントでヘルスチェック

### 💰 コスト最適化
- **リソース効率**: 単一インスタンスで両方のアプリケーションを実行
- **低い運用コスト**: App Serviceプランを1つだけ使用
- **効率的なスケーリング**: 必要に応じて縦横スケーリング

### 🛠️ 運用の簡素化
- **単一デプロイ**: 1回のデプロイで全機能をリリース
- **統一設定管理**: 環境変数とシークレットの一元管理
- **簡単なCI/CD**: 単一パイプラインでデプロイ

## 🔒 セキュリティ機能

- **Managed Identity**: Azure リソースへの安全な認証
- **Key Vault統合**: シークレットの安全な管理
- **HTTPS強制**: すべての通信を暗号化
- **RBAC**: Role-Based Access Control

## 📈 モニタリング & ログ

- **Application Insights**: パフォーマンスと可用性の監視
- **Log Analytics**: 構造化ログの分析
- **ヘルスチェック**: `/health` エンドポイントで状態確認

## 🔧 設定可能な環境変数

| 変数名 | デフォルト値 | 説明 |
|--------|-------------|------|
| `PORT` | `8000` | メインアプリケーションのポート |
| `CHAINLIT_PORT` | `8501` | Chainlitのポート |
| `ENVIRONMENT` | `development` | 実行環境 |
| `AZURE_KEY_VAULT_URL` | - | Key Vault URL |
| `AZURE_OPENAI_ENDPOINT` | - | Azure OpenAI エンドポイント |

## 🐛 トラブルシューティング

### アプリケーションが起動しない場合

1. **ログを確認**:
   ```bash
   az webapp log tail --name <app-name> --resource-group <rg-name>
   ```

2. **依存関係を確認**:
   - `requirements.txt` が正しく設定されているか
   - Python バージョンが 3.12 に設定されているか

3. **環境変数を確認**:
   - 必要な環境変数が設定されているか
   - Key Vault への権限があるか

### Chainlit が起動しない場合

1. **プロセス確認**:
   - Chainlit プロセスが正常に起動しているか
   - ポート競合がないか

2. **ログ確認**:
   - Chainlit 起動時のエラーメッセージを確認

## 📝 開発者向け情報

### アプリケーション起動フロー

1. `app.py` が起動
2. FastAPI アプリケーション初期化
3. Chainlit をサブプロセスで起動
4. プロキシミドルウェアが `/api/*` 以外を Chainlit に転送
5. ヘルスチェックエンドポイントが利用可能

### カスタマイズ可能な部分

- **プロキシルール**: `ProxyMiddleware` クラス
- **起動設定**: `startup.sh` スクリプト
- **リソース設定**: `infra/unified-resources.bicep`

## 📞 サポート

問題が発生した場合は、以下を確認してください：

1. [Azure App Service ドキュメント](https://docs.microsoft.com/azure/app-service/)
2. [FastAPI ドキュメント](https://fastapi.tiangolo.com/)
3. [Chainlit ドキュメント](https://docs.chainlit.io/)

---

**注意**: このブランチは統合アプリケーション専用です。分離されたバックエンド/フロントエンドの実装については、`main` ブランチを参照してください。