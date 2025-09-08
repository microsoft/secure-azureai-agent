# Configuration & Environment Variables

本プロジェクトで利用する環境変数を一元管理します。`README.md` / `DEVELOPMENT.md` / `DEPLOYMENT.md` / `SECURITY_DEPLOYMENT_GUIDE.md` / `frontend/INTEGRATION.md` に分散していた説明を統合し、重複を削減しました。

## 📌 使い方概要

1. ルートにある `.env.sample` をコピーして `.env` を作成
2. ローカル開発では `source .env` してから backend / frontend を起動
3. Azure 環境 (App Service など) では必要な値のみアプリ設定 (App Settings) / Key Vault に設定

## 🔑 分類ルール

| 区分 | 説明 |
|------|------|
| Required | 最低限必須 (起動時バリデーションあり) |
| Optional | 利用シナリオに応じて設定 |
| Secret | 秘匿情報 (Key Vault 推奨) |
| Backend | Backend のみ参照 |
| Frontend | Frontend のみ参照 |
| Both | 両方で使用 (将来的な統合考慮) |

## 🧩 変数一覧

### Core (必須)

| 変数 | 説明 | 必須 | デフォルト | Secret | Scope |
|------|------|------|------------|--------|-------|
| AZURE_OPENAI_ENDPOINT | Azure OpenAI エンドポイント URL | Yes | - | Yes (機微 URL として扱う場合) | Backend |
| AZURE_OPENAI_API_KEY | Azure OpenAI API Key | Yes | - | Yes | Backend |

### Azure OpenAI / 推論設定

| 変数 | 説明 | 必須 | デフォルト | Secret | Scope |
|------|------|------|------------|--------|-------|
| AZURE_OPENAI_DEPLOYMENT_NAME | モデルデプロイ名 | No | gpt-4 | No | Backend |
| USE_AZURE_AI_AGENT | Azure AI Foundry エージェントモード有効化 (`true/false`) | No | false | No | Backend |
| PROJECT_ENDPOINT | Azure AI Foundry Project Endpoint | 条件付き (USE_AZURE_AI_AGENT=true の場合) | - | No | Backend / Frontend(評価) |
| FOUNDARY_TECHNICAL_SUPPORT_AGENT_ID | Foundry 上の技術サポートエージェントID | 条件付き | - | Yes | Backend |

### Telemetry / Logging

| 変数 | 説明 | 必須 | デフォルト | Secret | Scope |
|------|------|------|------------|--------|-------|
| APPLICATIONINSIGHTS_CONNECTION_STRING | App Insights 接続文字列 | 推奨 | - | Yes | Backend |
| SEMANTICKERNEL_EXPERIMENTAL_GENAI_ENABLE_OTEL_DIAGNOSTICS_SENSITIVE | センシティブなトレース出力許可 (本番は false 推奨) | No | true(サンプル) | No | Backend |
| AZURE_TRACING_GEN_AI_CONTENT_RECORDING_ENABLED | モデル入力/出力記録 (本番は false 推奨) | No | true(サンプル) | No | Backend |
| LOG_LEVEL | フロントエンドログレベル | No | INFO | No | Frontend |

### ランタイム / ネットワーク / セキュリティ

| 変数 | 説明 | 必須 | デフォルト | Secret | Scope |
|------|------|------|------------|--------|-------|
| ENVIRONMENT | `development` / `production` | No | development | No | Backend |
| FRONTEND_URL | 許可するフロントエンド Origin | No | http://localhost:8501 | No | Backend |
| ALLOWED_HOST | TrustedHostMiddleware 用 ホスト | 本番推奨 | localhost | No | Backend |
| BACKEND_API_URL | フロントエンドが呼び出すBackend URL | Frontend 必須 | http://localhost:8000 | No | Frontend |
| PORT | Backend ポート | No | 8000 | No | Backend |
| KEY_VAULT_URL | Key Vault URL (本番推奨) | No | - | No | Backend |

### Azure Dev / Meta

| 変数 | 説明 | 必須 | デフォルト | Secret | Scope |
|------|------|------|------------|--------|-------|
| AZURE_ENV_NAME | azd 環境名 | No | dev | No | Backend |
| AZURE_LOCATION | リージョン | No | eastus | No | Backend |

### 認証 (オプション – DefaultAzureCredential で不要な場合は未設定)

| 変数 | 説明 | 必須 | Secret | Scope |
|------|------|------|--------|-------|
| AZURE_CLIENT_ID | サービスプリンシパル / マネージドID クライアントID | No | Yes | Both |
| AZURE_CLIENT_SECRET | サービスプリンシパル シークレット | No | Yes | Both |
| AZURE_TENANT_ID | テナントID | No | Yes | Both |

## ✅ パターン別最小セット

### 1. ローカル開発 (Agentless / 最小)
```
AZURE_OPENAI_ENDPOINT=...
AZURE_OPENAI_API_KEY=...
AZURE_OPENAI_DEPLOYMENT_NAME=gpt-4
BACKEND_API_URL=http://localhost:8000
```

### 2. Azure AI Foundry エージェントモード
```
USE_AZURE_AI_AGENT=true
PROJECT_ENDPOINT=... # https://{project}.services.ai.azure.com/api/projects/{name}
FOUNDARY_TECHNICAL_SUPPORT_AGENT_ID=...  # Key Vault 推奨
```

### 3. 本番 (推奨追加)
```
ENVIRONMENT=production
APPLICATIONINSIGHTS_CONNECTION_STRING=... # Key Vault
FRONTEND_URL=https://your-frontend.example.com
ALLOWED_HOST=your-backend.azurewebsites.net
SEMANTICKERNEL_EXPERIMENTAL_GENAI_ENABLE_OTEL_DIAGNOSTICS_SENSITIVE=false
AZURE_TRACING_GEN_AI_CONTENT_RECORDING_ENABLED=false
KEY_VAULT_URL=https://your-keyvault.vault.azure.net/
```

## 🔐 Secret 取り扱い指針

| 種別 | 保管場所 | 備考 |
|------|----------|------|
| API Key / Connection String | Azure Key Vault | App Service の Key Vault 参照を利用 |
| Foundry Agent ID | Key Vault (任意) | 頻繁に変わらない識別子 |
| 認証資格情報 | 可能な限り Managed Identity | 代替: Federated Credential + OIDC |

## 🧪 確認コマンド例 (ローカル)
```bash
grep -E 'AZURE_OPENAI_ENDPOINT|AZURE_OPENAI_API_KEY' .env || echo "Missing core OpenAI vars"
```

## ♻️ 重複整理方針

| 以前 | 状態 |
|------|------|
| `frontend/.env.sample` | 削除（統合） |
| `frontend/.env.example` | 削除（統合） |
| 各ドキュメント内バラバラの表 | 本ファイルへ集約 |

## 🗺 今後の改善候補

- 変数スキーマを JSON Schema 化し起動前検証
- `scripts/validate_env.py` の追加で CI 失敗条件化
- Azure App Configuration への段階的移行

---
このファイルを更新した場合は、関連する `README.md` のリンク切れチェックも合わせて行ってください。
