# 🎓 Azure CI/CD Pipeline ハンズオンガイド

このハンズオンでは、既存のAzureリソースを使用してCI/CDパイプラインを構築し、PythonアプリケーションをAzure App Serviceにデプロイします。

## 📋 ハンズオンの概要

### 🎯 目標
- 既存のAzure App Serviceリソースを活用
- Azure DevOps または GitHub Actions でCI/CDパイプラインを構築
- Python Webアプリケーション（フロントエンド・バックエンド）の自動デプロイ

### 🏗️ アーキテクチャ
```
Developer
    ↓ (git push)
GitHub/Azure DevOps
    ↓ (CI/CD Pipeline)
Azure App Service (Frontend + Backend)
    ↓ (AI機能)
Azure AI Foundry/OpenAI
```

## 🛠️ 事前準備

### 1. 必要なツール
- [Azure CLI](https://docs.microsoft.com/cli/azure/install-azure-cli)
- Git
- Visual Studio Code (推奨)

### 2. Azureアカウント
- Azure サブスクリプション
- 以下のリソースが既に作成済み:
  - Resource Group
  - 2つのApp Service (フロントエンド・バックエンド用)
  - AI Foundry または Azure OpenAI Service

## 📝 Step 1: 既存リソースの確認

### 1.1 Azure CLIでログイン
```bash
az login
az account show  # 現在のサブスクリプションを確認
```

### 1.2 既存リソースの一覧取得
```bash
# すべてのリソースを確認
az resource list --query "[].{Name:name, Type:type, ResourceGroup:resourceGroup}" --output table

# App Serviceのみを確認
az webapp list --query "[].{Name:name, ResourceGroup:resourceGroup, DefaultHostName:defaultHostName}" --output table
```

### 1.3 リソース情報をメモ
以下の情報を控えてください：
- **Resource Group名**: `_________________________`
- **バックエンドApp Service名**: `_________________________`
- **フロントエンドApp Service名**: `_________________________`
- **AI Foundry/OpenAI名**: `_________________________`

## 🔧 Step 2: プロジェクトファイルの設定

### 2.1 環境変数ファイルの準備

まず、ハンズオン用の環境変数テンプレートを使用して`.env`ファイルを作成します：

```bash
# ハンズオン用テンプレートをコピー
cp .env.template .env

# .envファイルを編集（🔧マークの箇所を変更）
code .env  # VS Codeで編集
# または
nano .env  # ターミナルで編集
```

### 2.2 設定ファイルの更新

以下のファイルで `🔧 変更必要` とマークされた箇所を更新してください：

#### A. Azure DevOps Pipeline (`azure-pipelines.yml`)
```yaml
variables:
  azureServiceConnection: 'azure-service-connection'  # 🔧 Service Connection名
  resourceGroupName: 'your-resource-group-name'       # 🔧 あなたのRG名
  backendAppName: 'your-backend-app-name'             # 🔧 バックエンドApp Service名
  frontendAppName: 'your-frontend-app-name'           # 🔧 フロントエンドApp Service名
```

#### B. GitHub Actions (`.github/workflows/azure-webapp-deploy.yml`)
```yaml
env:
  AZURE_WEBAPP_BACKEND_NAME: 'your-backend-app-name'   # 🔧 バックエンドApp Service名
  AZURE_WEBAPP_FRONTEND_NAME: 'your-frontend-app-name' # 🔧 フロントエンドApp Service名
  AZURE_RESOURCE_GROUP: 'your-resource-group-name'     # 🔧 あなたのRG名
```

#### C. App Service設定スクリプト (`scripts/configure-existing-resources.sh`)
```bash
RESOURCE_GROUP="your-resource-group-name"              # 🔧 あなたのRG名
BACKEND_APP="your-backend-app-name"                    # 🔧 バックエンドApp Service名
FRONTEND_APP="your-frontend-app-name"                  # 🔧 フロントエンドApp Service名
AZURE_OPENAI_ENDPOINT="https://your-ai-foundry.openai.azure.com/"  # 🔧 AI FoundryエンドポイントURL
```

#### D. 環境変数設定ファイル (`.env`)
```bash
# ハンズオン用テンプレートを使用
cp .env.template .env

# 🔧マークの箇所を編集して以下を設定:
AZURE_OPENAI_ENDPOINT=<your-azure-openai-endpoint>     # 🔧 AI FoundryのEndpoint URL
AZURE_OPENAI_API_KEY=<your-azure-openai-api-key>       # 🔧 AI FoundryのAPIキー
AZURE_RESOURCE_GROUP=<your-resource-group-name>        # 🔧 あなたのResource Group名
```

## 🚀 Step 3: App Serviceの設定

### 3.1 設定スクリプトの実行
```bash
# スクリプトを実行可能にする
chmod +x scripts/configure-existing-resources.sh

# App Serviceの設定を更新
./scripts/configure-existing-resources.sh
```

### 3.2 設定確認
```bash
# バックエンドApp Serviceの設定確認
az webapp config show --name <your-backend-app-name> --resource-group <your-rg-name>

# フロントエンドApp Serviceの設定確認
az webapp config show --name <your-frontend-app-name> --resource-group <your-rg-name>
```

## 🔐 Step 4: CI/CDパイプラインの設定

### Option A: Azure DevOps を使用する場合

#### 4.1 Service Principalの作成
```bash
az ad sp create-for-rbac --name "your-app-sp" \
  --role Contributor \
  --scopes /subscriptions/<your-subscription-id>/resourceGroups/<your-rg-name> \
  --sdk-auth
```

#### 4.2 Azure DevOpsでService Connection作成
1. Azure DevOps Project → Project Settings
2. Service connections → New service connection
3. Azure Resource Manager → Service principal (manual)
4. 上記で作成したService Principalの情報を入力
5. Connection name: `azure-service-connection` (または更新した名前)

#### 4.3 Pipeline作成
1. Azure DevOps → Pipelines → New pipeline
2. GitHub/Azure Repos を選択
3. `azure-pipelines.yml` を選択
4. Save and run

### Option B: GitHub Actions を使用する場合

#### 4.1 GitHub Secretsの設定
Repository → Settings → Secrets and variables → Actions

**Secrets:**
- `AZURE_CREDENTIALS`: Service Principalの認証情報JSON
- `AZURE_SUBSCRIPTION_ID`: サブスクリプションID

**Variables:**
- `AZURE_WEBAPP_BACKEND_NAME`: バックエンドApp Service名
- `AZURE_WEBAPP_FRONTEND_NAME`: フロントエンドApp Service名  
- `AZURE_RESOURCE_GROUP`: Resource Group名

#### 4.2 Workflow実行
- mainブランチにpushすると自動実行
- または Actions タブから手動実行

## 🧪 Step 5: デプロイメントのテスト

### 5.1 パイプライン実行
- コードを変更してmainブランチにpush
- パイプラインが自動実行されることを確認

### 5.2 デプロイメント確認
```bash
# アプリケーションログの確認
az webapp log tail --name <your-backend-app-name> --resource-group <your-rg-name>
az webapp log tail --name <your-frontend-app-name> --resource-group <your-rg-name>

# アプリケーションの動作確認
curl https://<your-backend-app-name>.azurewebsites.net/health
```

### 5.3 Webアプリケーションへのアクセス
- **フロントエンド**: `https://<your-frontend-app-name>.azurewebsites.net`
- **バックエンドAPI**: `https://<your-backend-app-name>.azurewebsites.net`
- **API ドキュメント**: `https://<your-backend-app-name>.azurewebsites.net/docs`

## 🎉 Step 6: 完了確認

### ✅ チェックリスト
- [ ] 既存Azureリソースの確認完了
- [ ] 設定ファイルの更新完了
- [ ] App Serviceの設定完了
- [ ] CI/CDパイプラインの設定完了
- [ ] デプロイメントの成功確認
- [ ] Webアプリケーションの動作確認

## 🔧 トラブルシューティング

### よくある問題と解決方法

#### 1. App Serviceの起動エラー
```bash
# ログを確認
az webapp log tail --name <app-name> --resource-group <rg-name>

# 起動コマンドを確認・修正
az webapp config set --name <app-name> --resource-group <rg-name> --startup-file "your-startup-command"
```

#### 2. 環境変数の不足
```bash
# 環境変数を確認
az webapp config appsettings list --name <app-name> --resource-group <rg-name>

# 環境変数を追加
az webapp config appsettings set --name <app-name> --resource-group <rg-name> --settings KEY=VALUE
```

#### 3. CORS エラー
```bash
# CORS設定を確認
az webapp cors show --name <backend-app-name> --resource-group <rg-name>

# CORS設定を追加
az webapp cors add --name <backend-app-name> --resource-group <rg-name> --allowed-origins <frontend-url>
```

## 📚 参考リンク

- [Azure App Service Documentation](https://docs.microsoft.com/azure/app-service/)
- [Azure DevOps Pipelines](https://docs.microsoft.com/azure/devops/pipelines/)
- [GitHub Actions for Azure](https://docs.microsoft.com/azure/developer/github/github-actions)

## 🏆 次のステップ

ハンズオン完了後、以下の拡張にチャレンジしてみてください：

1. **ステージング環境の追加**: 本番環境とは別のステージング環境を作成
2. **監視の強化**: Application Insights でより詳細な監視を設定
3. **セキュリティの強化**: Key Vault や Managed Identity を活用
4. **パフォーマンス最適化**: Auto Scaling や CDN の設定

おつかれさまでした！🎊
