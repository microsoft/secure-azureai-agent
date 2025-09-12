# 🍴 Fork & Deploy Guide

このレポジトリをフォークして、あなた自身のAzure環境にデプロイするためのガイドです。

## 📋 前提条件

- Azure アカウント（アクティブなサブスクリプション）
- GitHub アカウント
- Azure CLI がインストール済み（推奨）

## 🔐 セキュリティ階層設計

このプロジェクトは **2層セキュリティ戦略** を採用しています：

### Layer 1: GitHub Secrets（CI/CDデプロイ用）
- Service Principal認証情報
- リソースのデプロイと更新のみに使用

### Layer 2: Azure App Service環境変数（実行時用）  
- アプリケーション実行時の設定
- Azure OpenAI、Key Vaultなどのサービス接続情報

## 🚀 セットアップ手順

### Step 1: リポジトリのフォーク

1. このリポジトリの右上の **Fork** ボタンをクリック
2. あなたのGitHubアカウントにフォーク
3. フォークしたリポジトリをローカルにクローン：
   ```bash
   git clone https://github.com/YOUR-USERNAME/secure-azureai-agent.git
   cd secure-azureai-agent
   ```

### Step 2: Azureリソースの準備

#### Option A: 既存リソースを使用する場合
```bash
# 既存のリソースを確認
az resource list --output table

# App Serviceの名前を確認
az webapp list --query "[].{Name:name, ResourceGroup:resourceGroup}" --output table
```

#### Option B: 新規リソースを作成する場合
```bash
# Azure Developer CLI を使用（推奨）
azd auth login
azd init
azd up
```

### Step 3: GitHub Secrets の設定

あなたのフォークリポジトリで：
1. **Settings** > **Secrets and variables** > **Actions**
2. 以下のSecretsを追加：

```bash
# Service Principal の作成
az ad sp create-for-rbac --name "github-actions-sp-$(date +%s)" \
  --role contributor \
  --scopes /subscriptions/{YOUR-SUBSCRIPTION-ID}/resourceGroups/{YOUR-RESOURCE-GROUP} \
  --sdk-auth
```

上記コマンドの出力から以下の値を設定：
- `AZURE_CLIENT_ID`
- `AZURE_CLIENT_SECRET`  
- `AZURE_TENANT_ID`
- `AZURE_SUBSCRIPTION_ID`

### Step 4: ワークフロー設定の更新

`.github/workflows/azure-webapp-deploy.yml` で以下を変更：

```yaml
env:
  AZURE_WEBAPP_BACKEND_NAME: 'YOUR-BACKEND-APP-NAME'     # 🔧 変更必要
  AZURE_WEBAPP_FRONTEND_NAME: 'YOUR-FRONTEND-APP-NAME'   # 🔧 変更必要  
  AZURE_RESOURCE_GROUP: 'YOUR-RESOURCE-GROUP-NAME'       # 🔧 変更必要
```

### Step 5: Azure App Service環境変数の設定

#### バックエンドApp Service
Azure Portal > App Service > 構成 > アプリケーション設定：

```bash
# 必須設定
AZURE_OPENAI_API_KEY=your-openai-api-key
AZURE_OPENAI_ENDPOINT=https://your-openai.openai.azure.com/
AZURE_OPENAI_DEPLOYMENT_NAME=gpt-4

# オプション設定（Azure AI Foundry使用時）
PROJECT_ENDPOINT=https://your-project.eastus.inference.ml.azure.com
FOUNDARY_TECHNICAL_SUPPORT_AGENT_ID=your-agent-id
USE_AZURE_AI_AGENT=true

# セキュリティ設定（推奨）
AZURE_KEYVAULT_URL=https://your-keyvault.vault.azure.net/
ENVIRONMENT=production
```

#### フロントエンドApp Service  
Azure Portal > App Service > 構成 > アプリケーション設定：

```bash
BACKEND_API_URL=https://YOUR-BACKEND-APP.azurewebsites.net
ENVIRONMENT=production
```

### Step 6: デプロイの実行

```bash
git add .
git commit -m "Configure for my Azure environment"
git push origin main
```

## 🔒 セキュリティベストプラクティス

### ✅ 推奨事項
- **Azure Managed Identity** の使用（可能な場合）
- **Azure Key Vault** での機密情報管理
- **定期的なSecret ローテーション**
- **最小権限の原則** に従った権限設定

### ❌ 避けるべきこと  
- コードへの直接的なクレデンシャル記述
- `.env` ファイルのコミット
- 過度なアクセス権限の付与
- パブリックなログへの機密情報出力

## 🛠️ トラブルシューティング

### デプロイエラー
```bash
# Service Principal の権限確認
az role assignment list --assignee YOUR-CLIENT-ID

# App Service の状態確認  
az webapp show --name YOUR-APP-NAME --resource-group YOUR-RG
```

### 実行時エラー
```bash
# App Service ログの確認
az webapp log tail --name YOUR-APP-NAME --resource-group YOUR-RG

# 環境変数の確認
az webapp config appsettings list --name YOUR-APP-NAME --resource-group YOUR-RG
```

## 🆘 サポート

問題が発生した場合：
1. [Issues](../../issues) でバグレポートを作成
2. [Discussions](../../discussions) で質問
3. ドキュメントの改善提案も歓迎

---

## 📚 関連ドキュメント

- [Azure App Service 構成リファレンス](https://docs.microsoft.com/azure/app-service/configure-common)
- [GitHub Actions for Azure](https://docs.microsoft.com/azure/developer/github/github-actions)
- [Azure Key Vault ベストプラクティス](https://docs.microsoft.com/azure/key-vault/general/best-practices)
