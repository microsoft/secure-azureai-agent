# Azure Pipelines デプロイメントガイド

このガイドでは、Azure Pipelinesを使用してセキュアなAzure AI エージェントアプリケーションをAzure App Serviceにデプロイする方法を説明します。

## アーキテクチャ概要

このソリューションは以下のコンポーネントで構成されています：

- **フロントエンド**: Chainlitベースのウェブインターフェース (Python)
- **バックエンド**: FastAPI RESTAPIサーバー (Python)
- **Azure OpenAI**: AI機能を提供
- **Azure Key Vault**: シークレット管理
- **Application Insights**: 監視とテレメトリ
- **Log Analytics Workspace**: ログ収集と分析

## 前提条件

1. Azure サブスクリプション
2. Azure DevOps または GitHub アカウント
3. Azure CLI または Azure Developer CLI (azd)
4. 適切な権限 (Contributor以上)

## セットアップ手順

### 1. Azure サービス プリンシパルの作成

Azure Pipelinesがリソースにアクセスできるよう、サービス プリンシパルを作成します：

```bash
# サービス プリンシパルを作成
az ad sp create-for-rbac --name "secure-azureai-agent-sp" \
  --role Contributor \
  --scopes /subscriptions/<YOUR_SUBSCRIPTION_ID> \
  --sdk-auth
```

### 2. GitHub Secrets (GitHub Actions使用時)

GitHub リポジトリで以下のSecretsを設定：

- `AZURE_CREDENTIALS`: サービス プリンシパルのJSON
- `AZURE_CLIENT_ID`: サービス プリンシパルのクライアントID
- `AZURE_CLIENT_SECRET`: サービス プリンシパルのシークレット
- `AZURE_TENANT_ID`: テナントID
- `AZURE_SUBSCRIPTION_ID`: サブスクリプションID

### 3. Azure DevOps Service Connection (Azure DevOps使用時)

Azure DevOpsで新しいサービス接続を作成：

1. Project Settings → Service connections
2. "New service connection" → "Azure Resource Manager"
3. "Service principal (automatic)" を選択
4. 接続名を "azure-service-connection" として設定

### 4. 環境設定

`.env.template`ファイルをコピーして`.env`を作成し、必要な値を設定：

```bash
cp .env.template .env
# .envファイルを編集して適切な値を設定
```

### 5. インフラストラクチャのデプロイ

Azure Developer CLIを使用してインフラストラクチャをデプロイ：

```bash
# Azure Developer CLIにログイン
azd auth login

# 新しい環境を作成
azd env new production

# インフラストラクチャをプロビジョン
azd provision

# アプリケーションをデプロイ
azd deploy
```

または、手動でBicepテンプレートをデプロイ：

```bash
# リソースグループを作成
az group create --name rg-secure-azureai-agent --location eastus

# Bicepテンプレートをデプロイ
az deployment group create \
  --resource-group rg-secure-azureai-agent \
  --template-file infra/main.bicep \
  --parameters infra/main.parameters.json
```

## CI/CDパイプライン

### GitHub Actions

`.github/workflows/azure-webapp-deploy.yml` ファイルが設定されており、以下の機能を提供：

1. **Build and Test**: 依存関係のインストールとテスト実行
2. **Deploy Infrastructure**: Bicepテンプレートを使用したインフラデプロイ
3. **Deploy Backend**: バックエンドAPIのデプロイ
4. **Deploy Frontend**: フロントエンドアプリのデプロイ

### Azure DevOps Pipelines

`azure-pipelines.yml` ファイルが設定されており、同様のCI/CD機能を提供します。

## 設定詳細

### App Service 設定

両方のApp Serviceは以下のように設定されます：

- **ランタイム**: Python 3.11
- **OS**: Linux
- **Pricing Tier**: Basic B1 (本番環境では適切にスケール)
- **HTTPS**: 必須
- **Managed Identity**: ユーザー割り当て管理ID

### セキュリティ設定

- **CORS**: フロントエンドドメインのみ許可
- **Key Vault**: RBAC有効化でシークレット管理
- **Managed Identity**: Azure サービス間の認証
- **HTTPS Only**: すべての通信を暗号化

### 監視とログ

- **Application Insights**: パフォーマンス監視
- **Log Analytics**: ログ集約と分析
- **Diagnostic Settings**: App Serviceログの自動収集

## トラブルシューティング

### よくある問題

1. **デプロイメント失敗**
   - Azure CLI/azd のバージョンを確認
   - サービス プリンシパルの権限を確認
   - リソース名の一意性を確認

2. **アプリケーション起動失敗**
   - App Serviceのログを確認 (`az webapp log tail`)
   - 環境変数の設定を確認
   - startup-commandの設定を確認

3. **認証エラー**
   - Managed Identityの設定を確認
   - Key Vaultのアクセス権限を確認
   - Azure OpenAIのエンドポイント設定を確認

### ログの確認

```bash
# バックエンドアプリのログを表示
az webapp log tail --name app-backend-production-<resource-token> --resource-group rg-production

# フロントエンドアプリのログを表示
az webapp log tail --name app-frontend-production-<resource-token> --resource-group rg-production
```

## 本番環境への考慮事項

1. **スケーリング**: App Service Planのスケールアップ/アウト設定
2. **バックアップ**: 定期的なバックアップの設定
3. **セキュリティ**: ネットワークアクセス制御の強化
4. **監視**: カスタムアラートとダッシュボードの設定
5. **更新戦略**: ブルー/グリーンデプロイまたはスロットデプロイの検討

## サポート

追加のサポートが必要な場合は、プロジェクトのIssueを作成するか、Azureサポートにお問い合わせください。
