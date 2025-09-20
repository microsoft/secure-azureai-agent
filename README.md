# 🤖 Azure AI エージェント - ハンズオンリポジトリ# 🚀 Azure AI Agent - 統合アプリケーション



Azure App Serviceでの継続的デプロイ（CI/CD）を学ぶハンズオン用リポジトリです。この統合アプリケーションは、Azure Troubleshoot AgentのFastAPIバックエンドとChainlitフロントエンドを単一のApp Serviceで動作させるために設計されています。



![Azure](https://img.shields.io/badge/azure-%230072C6.svg?style=for-the-badge&logo=microsoftazure&logoColor=white)## 🏗️ アーキテクチャ

![Python](https://img.shields.io/badge/python-3.12%2B-blue?style=for-the-badge&logo=python&logoColor=white)

![FastAPI](https://img.shields.io/badge/FastAPI-005571?style=for-the-badge&logo=fastapi)```

![Chainlit](https://img.shields.io/badge/Chainlit-000000?style=for-the-badge&logo=chainlit&logoColor=white)統合アプリケーション (app.py)

├── FastAPI Backend (port 8000)

## 🎯 このハンズオンで学べること│   ├── /api/* - APIエンドポイント

│   ├── /health - ヘルスチェック

- ✅ Azure App Service での Python アプリケーションデプロイ│   └── /docs - API ドキュメント

- ✅ GitHub Actions による継続的デプロイ（CI/CD）└── Chainlit Frontend (port 8501)

- ✅ Azure.yaml ファイルによる設定管理    └── Proxy による UI 提供

- ✅ FastAPI + Chainlit 統合アプリケーションの動作確認```



## 🚀 クイックスタート## 📁 ディレクトリ構造



### 1️⃣ このリポジトリをフォーク```

unified-app/

右上の「Fork」ボタンをクリックして、自分のGitHubアカウントにフォークしてください。├── app.py                  # 統合アプリケーション（メインエントリーポイント）

├── requirements.txt        # 統合された依存関係

### 2️⃣ ハンズオンガイドを確認├── startup.sh             # Azure App Service 起動スクリプト

├── azure.yaml             # Azure Developer CLI 設定

詳細な手順は以下のガイドを参照してください：├── .deployment            # Azure デプロイメント設定

├── backend/               # バックエンドコード

**📋 [HANDS_ON_GUIDE.md](HANDS_ON_GUIDE.md) - 完全ガイド**│   ├── src/

│   │   ├── main.py       # FastAPI アプリケーション

### 3️⃣ azure.yaml を編集│   │   ├── agents/       # Azure Troubleshoot Agent

│   │   ├── telemetry/    # テレメトリ設定

1. `azure.yaml.template` をコピーして `azure.yaml` を作成│   │   └── utils/        # ユーティリティ

2. アプリケーション名を自分の名前に変更│   └── requirements.txt

3. 必要に応じて設定をカスタマイズ├── frontend/              # フロントエンドコード

│   ├── app.py           # Chainlit アプリケーション

### 4️⃣ Azure にデプロイ│   ├── chainlit.md      # UI 設定

│   └── requirements.txt

Azure Portal でApp Serviceを作成し、GitHubと連携して自動デプロイを開始。└── infra/                # Azure インフラストラクチャ

    ├── main.bicep       # メイン Bicep テンプレート

## 📁 リポジトリ構成    ├── unified-resources.bicep  # リソース定義

    └── main.parameters.json     # パラメータファイル

``````

secure-azureai-agent/

├── 📋 HANDS_ON_GUIDE.md          # ハンズオン詳細ガイド## 🛠️ ローカル開発

├── 📄 azure.yaml.template        # 編集用テンプレート

├── 📄 azure.yaml.example         # 完全設定例### 前提条件

├── 🐍 app.py                     # 統合メインアプリケーション

├── 📦 requirements.txt           # 統合依存関係- Python 3.12+

├── 🔧 startup.sh                 # Azure起動スクリプト- Azure CLI

├── 📁 backend/                   # バックエンド（FastAPI）- Azure Developer CLI (azd)

│   └── src/

│       ├── main.py              # FastAPI アプリケーション### セットアップ

│       ├── agents/              # AIエージェント

│       ├── telemetry/           # テレメトリ設定1. 依存関係のインストール:

│       └── utils/               # ユーティリティ   ```bash

├── 📁 frontend/                  # フロントエンド（Chainlit）   pip install -r requirements.txt

│   ├── app.py                   # Chainlit UI   ```

│   └── chainlit.md              # UI設定

└── 📁 infra/                     # インフラ（Bicep）2. 環境変数の設定:

    ├── main.bicep               # メインテンプレート   ```bash

    └── unified-resources.bicep   # リソース定義   # .env ファイルを作成

```   ENVIRONMENT=development

   CHAINLIT_PORT=8501

## 🏗️ アーキテクチャ   AZURE_KEY_VAULT_URL=your-key-vault-url

   AZURE_OPENAI_ENDPOINT=your-openai-endpoint

```mermaid   ```

graph TB

    A[GitHub Repository] --> B[GitHub Actions]3. アプリケーションの起動:

    B --> C[Azure App Service]   ```bash

    C --> D[FastAPI Backend]   python app.py

    C --> E[Chainlit Frontend]   ```

    D --> F[Azure OpenAI]

    D --> G[Azure Key Vault]アプリケーションは `http://localhost:8000` で起動し、UIは自動的にChainlitにプロキシされます。

    C --> H[Application Insights]

```## 🚀 Azure デプロイメント



### 統合アプリケーション構成### Azure Developer CLI を使用

- **メインプロセス**: FastAPI (ポート 8000)

- **サブプロセス**: Chainlit (ポート 8501) ```bash

- **プロキシ**: `/api/*` → FastAPI、その他 → Chainlit# Azure にログイン

- **監視**: Application Insights で統合監視azd auth login



## ⚙️ 技術スタック# プロビジョニングとデプロイ

azd up

| カテゴリ | 技術 | バージョン | 説明 |

|---------|------|-----------|------|# 既存リソースへのデプロイのみ

| **言語** | Python | 3.12+ | メイン開発言語 |azd deploy

| **Web Framework** | FastAPI | 最新 | RESTful API |```

| **UI Framework** | Chainlit | 最新 | チャットベースUI |

| **AI/ML** | Semantic Kernel | 最新 | AIエージェント |### 手動デプロイ

| **クラウド** | Azure App Service | - | ホスティング |

| **CI/CD** | GitHub Actions | - | 自動デプロイ |1. Azure リソースのプロビジョニング:

| **インフラ** | Bicep | - | IaC |   ```bash

   az deployment sub create \

## 🎓 ハンズオン参加者向け情報     --location japaneast \

     --template-file infra/main.bicep \

### 📋 必要な準備     --parameters infra/main.parameters.json

   ```

- **Azureアカウント** (無料アカウントでも可能)

- **GitHubアカウント**2. アプリケーションのデプロイ:

- **基本的なYAML知識** (ガイドで説明)   ```bash

   az webapp deployment source config-zip \

### ⏱️ 想定時間     --resource-group rg-your-env-unified \

     --name app-your-env-unified-xxxxx \

- **準備**: 10分     --src unified-app.zip

- **設定・デプロイ**: 20分   ```

- **動作確認**: 10分

- **合計**: 約40分## 🔧 設定



### 🎯 学習目標### 環境変数



1. Azure App Service の基本操作| 変数名 | 説明 | デフォルト値 |

2. 継続的デプロイの仕組み理解|--------|------|-------------|

3. YAML設定ファイルの編集| `PORT` | メインアプリケーションのポート | `8000` |

4. GitHub Actions の動作確認| `CHAINLIT_PORT` | Chainlit のポート | `8501` |

5. Azure リソースの監視方法| `ENVIRONMENT` | 環境タイプ | `development` |

| `PYTHONPATH` | Python パス | `/home/site/wwwroot/backend/src` |

## 🔧 ローカル開発（オプション）

### Azure App Service 設定

ローカルで動作確認したい場合：

- **Python バージョン**: 3.12

```bash- **起動コマンド**: `bash startup.sh`

# 依存関係のインストール- **Always On**: 有効

pip install -r requirements.txt- **HTTPS Only**: 有効



# 統合アプリケーションの起動## 📊 監視とログ

python app.py

- **Application Insights**: 自動的に設定されます

# ブラウザでアクセス- **Log Analytics**: すべてのログが収集されます

# http://localhost:8000- **ヘルスチェック**: `/health` エンドポイントで確認

```

## 🔒 セキュリティ

## 🐛 トラブルシューティング

- **Managed Identity**: Azure リソースへの認証に使用

よくある問題と解決方法：- **Key Vault**: シークレット管理

- **HTTPS**: 強制有効

### ❌ 「App name already exists」- **RBAC**: Role-Based Access Control

```yaml

# 解決: アプリ名にユニークな接尾辞を追加## ⚡ パフォーマンス

name: secure-azureai-agent-tanaka-2024

```- **App Service Plan**: B2 (Basic tier)

- **Auto Scale**: 必要に応じて設定可能

### ❌ 「YAML syntax error」- **CDN**: 静的コンテンツ配信（オプション）

- インデントを2スペースで統一

- タブ文字を使用しない## 🐛 トラブルシューティング

- 文字列にクォートが必要な場合がある

### よくある問題

### ❌ 「Build failed」

- Azure Portal の「ログストリーム」を確認1. **Chainlit が起動しない**

- GitHub Actions のエラーログを確認   - ログを確認: `az webapp log tail`

   - ポート競合の確認

詳細は [HANDS_ON_GUIDE.md](HANDS_ON_GUIDE.md) のトラブルシューティングセクションを参照。   - Python 依存関係の確認



## 📚 参考資料2. **プロキシエラー**

   - 内部通信の確認

- 📖 [Azure App Service ドキュメント](https://docs.microsoft.com/azure/app-service/)   - ファイアウォール設定

- 📖 [GitHub Actions ドキュメント](https://docs.github.com/actions)

- 📖 [FastAPI ドキュメント](https://fastapi.tiangolo.com/)3. **メモリ不足**

- 📖 [Chainlit ドキュメント](https://docs.chainlit.io/)   - App Service Plan のスケールアップ

   - 不要なプロセスの停止

## 🤝 サポート

### ログの確認

質問や問題がある場合：

```bash

1. **Issues** タブで既存の質問を検索# リアルタイムログ

2. 新しい **Issue** を作成して質問az webapp log tail --resource-group rg-your-env-unified --name app-your-env-unified-xxxxx

3. ハンズオンメンター/講師に相談

# Application Insights でのログ分析

## 📄 ライセンスaz monitor app-insights query --app your-app-insights --analytics-query "traces | limit 100"

```

このプロジェクトは [MIT License](LICENSE) の下でライセンスされています。

## 🔄 従来構成からの移行

---

### 移行手順

**ハッピーラーニング & ハッピーデプロイ！** 🚀🎉
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