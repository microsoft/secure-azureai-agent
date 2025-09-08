# Azure Pipelines デプロイメント - セットアップ完了

Azure Pipelinesを使用したセキュアなAzure AI エージェントアプリケーションのデプロイメント設定が完了しました。

## 作成された設定ファイル

### Infrastructure as Code (Bicep)
- `infra/main.bicep` - メインのBicepテンプレート（サブスクリプションスコープ）
- `infra/resources.bicep` - Azure リソース定義
- `infra/main.parameters.json` - パラメーター設定

### CI/CD パイプライン
- `azure-pipelines.yml` - Azure DevOps Pipelines設定
- `.github/workflows/azure-webapp-deploy.yml` - GitHub Actions設定

### アプリケーション設定
- `azure.yaml` - Azure Developer CLI設定
- `backend/Dockerfile` - バックエンドコンテナ設定
- `frontend/Dockerfile` - フロントエンドコンテナ設定
- `.env.template` - 環境変数テンプレート

### ドキュメント
- `DEPLOYMENT-AZURE-PIPELINES.md` - 詳細なデプロイメントガイド

## アーキテクチャ

```
┌─────────────────┐    ┌─────────────────┐
│   Frontend      │    │   Backend       │
│   (Chainlit)    │────│   (FastAPI)     │
│   App Service   │    │   App Service   │
└─────────────────┘    └─────────────────┘
         │                       │
         └───────────────────────┼─────────┐
                                 │         │
                    ┌─────────────────┐   │
                    │  Azure OpenAI   │   │
                    └─────────────────┘   │
                                          │
                    ┌─────────────────┐   │
                    │  Key Vault      │───┘
                    └─────────────────┘
                                │
                    ┌─────────────────┐
                    │ App Insights &  │
                    │ Log Analytics   │
                    └─────────────────┘
```

## 次のステップ

1. **Azure DevOps または GitHub でパイプラインを設定**:
   - Azure DevOps: `azure-pipelines.yml` をインポート
   - GitHub: Actions が自動で `.github/workflows/azure-webapp-deploy.yml` を検出

2. **必要なシークレット/変数を設定**:
   - Azure Service Principal の認証情報
   - サブスクリプション ID
   - その他の環境固有の設定

3. **パイプラインを実行**:
   - インフラストラクチャが自動プロビジョニングされます
   - アプリケーションが自動デプロイされます

4. **監視とログの確認**:
   - Application Insights でパフォーマンスを監視
   - Log Analytics でログを確認

詳細なセットアップ手順については、`DEPLOYMENT-AZURE-PIPELINES.md` を参照してください。
