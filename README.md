# 🚀 Secure Azure AI Agent

Azure App Serviceで動作する統合AIエージェントアプリケーション。FastAPIバックエンドとChainlitフロントエンドを単一のApp Serviceで動作させる設計です。チャットモードとAI Foundryエージェントモードの切り替えが可能で、エージェントのトレース機能も備えています。

![Azure](https://img.shields.io/badge/azure-%230072C6.svg?style=for-the-badge&logo=microsoftazure&logoColor=white)
![Python](https://img.shields.io/badge/python-3.12%2B-blue?style=for-the-badge&logo=python&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-005571?style=for-the-badge&logo=fastapi)
![Chainlit](https://img.shields.io/badge/Chainlit-000000?style=for-the-badge&logo=chainlit&logoColor=white)

## ✨ 主要機能

### 🤖 デュアルモードAI システム
- **📝 チャットモード**: シンプルな会話型AIとして動作
- **🚀 エージェントモード**: AI Foundryの高度なエージェント機能を活用
- **⚙️ 簡単切り替え**: UIから即座にモード変更可能

### 🔍 エージェント動作トレース
- **ツール呼び出し**: エージェントが使用するツールの詳細表示
- **思考プロセス**: AIの意思決定プロセスを可視化
- **リアルタイム表示**: ストリーミング中のトレース情報配信

### 🏗️ 統合アーキテクチャ

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
├── eval/                 # RAG評価・テストシステム
│   ├── README_RAG_EVALUATION.md # RAG評価システムの詳細ガイド
│   ├── rag_evaluation.py       # RAGAS評価フレームワーク
│   ├── azure_rag.py           # Azure AI Search RAGシステム
│   ├── config.py              # 設定管理
│   └── sample_data.py         # サンプルデータ生成
├── ContosoTelecom社内資料.pdf  # RAGデモ用サンプルデータ
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

## 🧪 RAG評価システムとデモデータ

このプロジェクトには、RAG（Retrieval Augmented Generation）システムの性能を評価するための包括的な評価システムが含まれています。

### サンプルデータ

- **`ContosoTelecom社内資料.pdf`**: RAGデモンストレーション用の架空の社内資料
  - ContosoTelecom社の製品・サービス情報
  - 技術サポート手順とトラブルシューティング
  - 社内ポリシーと手順書
  - RAG検索とQAのテスト用コンテンツ

### RAG評価機能

- **RAGAS評価フレームワーク**: Faithfulness, Answer Relevancy, Context Precisionなどの包括的メトリクス
- **Azure AI Search統合**: ハイブリッド検索（セマンティック + キーワード）対応
- **バッチ評価**: 複数クエリの並列処理
- **結果エクスポート**: JSON/CSV形式での評価結果出力

詳細については[eval/README_RAG_EVALUATION.md](eval/README_RAG_EVALUATION.md)を参照してください。

## � 使い方

### モード切り替え方法
1. **設定ボタン**（⚙️）をクリック
2. **実行モード**で「チャットモード」または「エージェントモード」を選択
3. **トレース表示**を有効にしてエージェントの動作を詳細表示（エージェントモード時のみ）

### チャットモードの特徴
- 💬 シンプルで高速な会話型AI
- 🎯 Azure関連の質問に特化
- ⚡ 軽量で迅速な応答

### エージェントモードの特徴  
- 🤖 AI Foundryの高度なエージェント機能
- 🔧 専門ツールを活用した詳細分析
- 🔍 トレース機能でプロセス可視化
- 📊 複雑な問題への対応

### トレース機能の活用
- **ツール呼び出し**: どのツールが使われたかを確認
- **思考プロセス**: AIの判断理由を理解
- **デバッグ**: 問題発生時の詳細調査

## �🔧 設定

### 環境変数

#### 基本設定
| 変数名 | 説明 | デフォルト値 |
|--------|------|-------------|
| `PORT` | メインアプリケーションのポート | `8000` |
| `CHAINLIT_PORT` | Chainlit のポート | `8501` |
| `ENVIRONMENT` | 環境タイプ | `development` |
| `PYTHONPATH` | Python パス | `/home/site/wwwroot/backend/src` |

#### Azure OpenAI設定
| 変数名 | 説明 | 必須 |
|--------|------|------|
| `AZURE_OPENAI_API_KEY` | Azure OpenAI APIキー | ✅ |
| `AZURE_OPENAI_ENDPOINT` | Azure OpenAI エンドポイント | ✅ |
| `AZURE_OPENAI_DEPLOYMENT_NAME` | デプロイメント名 | No (default: `gpt-4`) |

#### AI Foundry エージェント設定
| 変数名 | 説明 | 必須 |
|--------|------|------|
| `PROJECT_ENDPOINT` | AI Foundry プロジェクトエンドポイント | エージェントモード使用時 |
| `FOUNDARY_TECHNICAL_SUPPORT_AGENT_ID` | Foundry技術サポートエージェントID | エージェントモード使用時 |

#### モード制御
| 変数名 | 説明 | デフォルト値 |
|--------|------|-------------|
| `USE_AZURE_AI_AGENT` | エージェントモードの有効化 | `false` |

#### トレース・デバッグ設定
| 変数名 | 説明 | デフォルト値 |
|--------|------|-------------|
| `SEMANTICKERNEL_EXPERIMENTAL_GENAI_ENABLE_OTEL_DIAGNOSTICS_SENSITIVE` | Semantic Kernelの詳細トレース | `false` |
| `AZURE_TRACING_GEN_AI_CONTENT_RECORDING_ENABLED` | AIコンテンツ記録 | `false` |

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