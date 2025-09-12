# 🎓 ハンズオン: 既存リソース用CI/CDパイプライン設定ガイド

このガイドでは、既存のAzureリソースを使用してCI/CDパイプラインを設定する方法を説明します。

## � 事前準備: 既存リソースの確認

まず、あなたの環境にある既存のAzureリソースを確認してください：

```bash
# 利用可能なリソースを確認
az resource list --query "[].{Name:name, Type:type, ResourceGroup:resourceGroup}" --output table
```

## 🔍 手順1: リソース情報の特定

以下の情報を確認・メモしてください：

### 必須リソース
- **Resource Group名**: `<your-resource-group-name>`
- **フロントエンド App Service名**: `<your-frontend-app-service>`
- **バックエンド App Service名**: `<your-backend-app-service>`
- **AI Foundry/Azure OpenAI名**: `<your-ai-foundry-name>`

### リソース確認コマンド例
```bash
# Resource Groupを確認
az group list --query "[].name" --output table

# App Serviceを確認
az webapp list --query "[].{Name:name, ResourceGroup:resourceGroup}" --output table

# AI Foundry/Azure OpenAIを確認
az cognitiveservices account list --query "[].{Name:name, Kind:kind, ResourceGroup:resourceGroup}" --output table
```

## 🔧 手順2: 設定ファイルの更新

### GitHub Actions設定

`.github/workflows/azure-webapp-deploy.yml` ファイルの以下の箇所を更新：

```yaml
env:
  # 🔧 ここを変更してください
  AZURE_WEBAPP_BACKEND_NAME: 'your-backend-app-service-name'   # あなたのバックエンドApp Service名
  AZURE_WEBAPP_FRONTEND_NAME: 'your-frontend-app-service-name' # あなたのフロントエンドApp Service名
  AZURE_RESOURCE_GROUP: 'your-resource-group-name'             # あなたのResource Group名
```

### App Service設定スクリプト

`scripts/configure-existing-resources.sh` ファイルの以下の箇所を更新：

```bash
# 🔧 ここを変更してください
RESOURCE_GROUP="your-resource-group-name"
BACKEND_APP="your-backend-app-service-name"
FRONTEND_APP="your-frontend-app-service-name"
AZURE_OPENAI_ENDPOINT="https://your-ai-foundry-name.openai.azure.com/"
```

## ⚙️ 1. App Service設定の更新

既存のApp Serviceを適切に設定するため、以下のスクリプトを実行してください：

```bash
# 設定スクリプトを実行
./scripts/configure-existing-resources.sh
```

または手動で設定：

```bash
# バックエンドの起動コマンド設定
az webapp config set \
  --resource-group redteaming-demo-rg-swe-mkurahara \
  --name redteaming-demo-back-swe-mkurahara \
  --startup-file "gunicorn --bind 0.0.0.0:8000 src.main:app -k uvicorn.workers.UvicornWorker"

# フロントエンドの起動コマンド設定
az webapp config set \
  --resource-group redteaming-demo-rg-swe-mkurahara \
  --name redteaming-demo-front-swe-mkurahara \
  --startup-file "chainlit run app.py --host 0.0.0.0 --port 8000"

# バックエンドの環境変数設定
az webapp config appsettings set \
  --resource-group redteaming-demo-rg-swe-mkurahara \
  --name redteaming-demo-back-swe-mkurahara \
  --settings \
    AZURE_OPENAI_ENDPOINT="https://redteaming-demo-aifoundry-swe-mkurahara.openai.azure.com/" \
    FRONTEND_URL="https://redteaming-demo-front-swe-mkurahara.azurewebsites.net" \
    ENVIRONMENT="production"

# フロントエンドの環境変数設定
az webapp config appsettings set \
  --resource-group redteaming-demo-rg-swe-mkurahara \
  --name redteaming-demo-front-swe-mkurahara \
  --settings \
    BACKEND_API_URL="https://redteaming-demo-back-swe-mkurahara.azurewebsites.net"
```

## 🚀 2. Azure DevOps Pipeline設定

### Variables設定

Azure DevOpsのProject Settings > Pipelines > Library で以下の変数を設定：

```yaml
# Variable Group: 'existing-resources-config'
resourceGroupName: 'redteaming-demo-rg-swe-mkurahara'
backendAppName: 'redteaming-demo-back-swe-mkurahara'
frontendAppName: 'redteaming-demo-front-swe-mkurahara'
azureLocation: 'swedencentral'
```

### Service Connection設定

1. Project Settings > Service connections
2. "New service connection" > "Azure Resource Manager"
3. 接続名: `azure-service-connection`
4. サブスクリプションを選択してauthorize

## 🔧 3. GitHub Actions設定

### Repository Variables設定

GitHub リポジトリ Settings > Secrets and variables > Actions で設定：

**Variables**:
- `AZURE_WEBAPP_BACKEND_NAME`: `redteaming-demo-back-swe-mkurahara`
- `AZURE_WEBAPP_FRONTEND_NAME`: `redteaming-demo-front-swe-mkurahara`
- `AZURE_RESOURCE_GROUP`: `redteaming-demo-rg-swe-mkurahara`

**Secrets**:
- `AZURE_CREDENTIALS`: Service Principal認証情報JSON
- `AZURE_SUBSCRIPTION_ID`: サブスクリプションID

### Service Principal作成

```bash
# Service Principal作成（Azure CLI）
az ad sp create-for-rbac --name "secure-azureai-agent-sp" \
  --role Contributor \
  --scopes /subscriptions/<YOUR_SUBSCRIPTION_ID>/resourceGroups/redteaming-demo-rg-swe-mkurahara \
  --sdk-auth
```

## 📝 4. 変更済みファイル

以下のファイルが既存リソース用に更新されました：

- ✅ `.github/workflows/azure-webapp-deploy.yml` - GitHub Actions設定
- ✅ `scripts/configure-existing-resources.sh` - App Service設定スクリプト

## 🎯 5. デプロイメント手順

### 準備
1. ☑️ App Service設定を更新（上記スクリプト実行）
2. ☑️ GitHub Secretsを設定

### 実行
**GitHub Actions**: mainブランチにpushまたは手動実行

パイプラインは以下を実行します：
- ✅ ビルドとテスト
- ✅ バックエンドApp Serviceへのデプロイ
- ✅ フロントエンドApp Serviceへのデプロイ

## 🔗 6. アクセスURL

デプロイ後のアクセス先：

- **フロントエンド**: https://redteaming-demo-front-swe-mkurahara.azurewebsites.net
- **バックエンドAPI**: https://redteaming-demo-back-swe-mkurahara.azurewebsites.net
- **APIドキュメント**: https://redteaming-demo-back-swe-mkurahara.azurewebsites.net/docs

## 🔍 7. トラブルシューティング

### ログ確認
```bash
# バックエンドログ
az webapp log tail --name redteaming-demo-back-swe-mkurahara --resource-group redteaming-demo-rg-swe-mkurahara

# フロントエンドログ
az webapp log tail --name redteaming-demo-front-swe-mkurahara --resource-group redteaming-demo-rg-swe-mkurahara
```

### よくある問題
1. **起動コマンド未設定**: 上記の`az webapp config set`コマンドを実行
2. **環境変数不足**: App Serviceの環境変数を確認
3. **CORS エラー**: バックエンドのCORS設定を確認

これで既存リソースを使用したCI/CDパイプラインの設定が完了です！
