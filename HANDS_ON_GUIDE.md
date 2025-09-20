# 🚀 Azure継続的デプロイ ハンズオンガイド

Azure App ServiceでPythonアプリケーションを継続的デプロイ（CI/CD）で自動デプロイするハンズオンです。

## 📋 ハンズオンの流れ

1. **リポジトリをフォーク**
2. **Azure.yamlファイルを編集**
3. **Azure App Serviceを作成・設定**
4. **継続的デプロイを有効化**
5. **デプロイの確認**

---

## 🎯 前提条件

- **Azureサブスクリプション** （無料アカウントでも可能）
- **GitHubアカウント**
- **基本的なYAMLの知識** （このガイドで説明します）

---

## 📝 Step 1: リポジトリのフォーク

1. このリポジトリの **Fork** ボタンをクリック
2. 自分のGitHubアカウントにフォーク
3. フォークしたリポジトリをクローン（オプション）

---

## ⚙️ Step 2: azure.yaml ファイルの編集

### 2-1. ファイルの準備

1. **azure.yaml.template** ファイルを開く
2. ファイルの内容を **全て選択してコピー**
3. リポジトリのルートに **azure.yaml** という名前で新しいファイルを作成
4. コピーした内容を貼り付け

### 2-2. 必須編集項目

#### ✅ **アプリケーション名の変更**
```yaml
# 変更前
name: secure-azureai-agent-{your-name}

# 変更後（例）
name: secure-azureai-agent-tanaka
```

**⚠️ 注意点：**
- 英数字とハイフンのみ使用
- 世界で一意である必要があります
- 自分の名前を含めることを推奨

#### ✅ **Python バージョンの確認**
```yaml
config:
  pythonVersion: "3.12"  # 必要に応じて変更
```

### 2-3. オプション編集項目

#### 📊 **リソース設定**
```yaml
sku: B1    # Basic プラン（推奨）
# sku: F1  # Free プラン（制限あり）
# sku: S1  # Standard プラン（高性能）
```

#### 🔧 **環境変数の追加**
```yaml
appSettings:
  ENVIRONMENT: "production"
  # カスタム環境変数を追加可能
  MY_CUSTOM_SETTING: "my-value"
```

### 2-4. 編集完了チェックリスト

- [ ] `name` フィールドを自分の名前に変更
- [ ] `pythonVersion` が適切に設定されている
- [ ] YAML の文法エラーがない（インデント確認）
- [ ] 特殊文字を使用していない

---

## 🌟 Step 3: Azure App Service の作成

### 3-1. Azure Portal にログイン

1. [Azure Portal](https://portal.azure.com) にアクセス
2. Azureアカウントでログイン

### 3-2. App Service の作成

1. **「リソースの作成」** をクリック
2. **「Web App」** を検索して選択
3. 以下の設定で作成：

```
基本設定:
├── サブスクリプション: （あなたのサブスクリプション）
├── リソースグループ: rg-handson-[yourname] （新規作成）
├── 名前: （azure.yamlのnameと同じにする）
├── 公開: コード
├── ランタイムスタック: Python 3.12
├── オペレーティングシステム: Linux
└── 地域: Japan East

App Service プラン:
├── 名前: （自動生成のままでOK）
└── 価格レベル: Basic B1 （推奨）
```

4. **「確認および作成」** → **「作成」**

### 3-3. 作成の確認

- 作成完了まで **2-3分** 待機
- 「リソースに移動」をクリック

---

## 🔄 Step 4: 継続的デプロイの設定

### 4-1. デプロイセンターへ移動

1. Azure Portal で作成したApp Serviceを開く
2. 左側メニューから **「デプロイセンター」** をクリック

### 4-2. GitHub連携の設定

1. **「GitHub」** を選択
2. GitHubアカウントで認証
3. 以下を設定：
   ```
   組織: （あなたのGitHubユーザー名）
   リポジトリ: secure-azureai-agent
   ブランチ: feature/unified-app
   ```
4. **「保存」** をクリック

### 4-3. 自動生成の確認

設定後、以下が自動で生成されます：
- ✅ `.github/workflows/` フォルダ
- ✅ GitHub Actions ワークフロー
- ✅ `azure.yaml` ファイル（シンプル版）

---

## 🎨 Step 5: azure.yaml の詳細編集

### 5-1. 自動生成されたファイルの確認

GitHub上で自動生成された `azure.yaml` を確認：

```yaml
# 自動生成版（シンプル）
name: your-app-name
services:
  web:
    project: .
    host: appservice
    language: python
```

### 5-2. テンプレートを使用した詳細設定

1. 自動生成された `azure.yaml` をクリック
2. **「Edit」** ボタンをクリック
3. 内容を **azure.yaml.template** の内容で置き換え
4. Step 2 の編集を再度実行

### 5-3. 変更のコミット

```yaml
# 最終的な設定例
name: secure-azureai-agent-tanaka
metadata:
  template: secure-azureai-agent-unified@1.0.0

services:
  unified-app:
    project: .
    host: appservice
    language: python
    config:
      pythonVersion: "3.12"
      appSettings:
        ENVIRONMENT: "production"
        CHAINLIT_PORT: "8501"
        WEBSITES_PORT: "8000"
        PYTHONPATH: "/home/site/wwwroot/backend/src"
        SCM_DO_BUILD_DURING_DEPLOYMENT: "true"
        ENABLE_ORYX_BUILD: "true"
      startupCommand: "bash startup.sh"
      sku: B1
```

---

## ✅ Step 6: デプロイの確認

### 6-1. GitHub Actions の確認

1. GitHubリポジトリの **「Actions」** タブをクリック
2. 最新のワークフローの実行状況を確認
3. ✅ 緑色になるまで待機（通常 5-10分）

### 6-2. アプリケーションの確認

1. Azure Portal でApp Serviceの **「概要」** を表示
2. **「URL」** をクリックしてアプリにアクセス
3. AIエージェントアプリケーションが表示されることを確認

### 6-3. ログの確認

問題が発生した場合：
1. Azure Portal → **「ログストリーム」**
2. GitHub Actions → **「失敗したジョブの詳細」**

---

## 🎉 完了！

おめでとうございます！Azure App Serviceでの継続的デプロイが完了しました。

### 🔄 今後の変更方法

1. GitHubでコードを編集
2. 変更をコミット・プッシュ
3. GitHub Actions が自動実行
4. Azure App Service に自動デプロイ

---

## 🐛 トラブルシューティング

### よくあるエラー

#### ❌ **「App name already exists」**
```yaml
# 解決方法: アプリ名を変更
name: secure-azureai-agent-tanaka-2
```

#### ❌ **「YAML syntax error」**
```yaml
# 原因: インデントミス
# 解決: 2スペースでインデント統一
```

#### ❌ **「Build failed」**
- Azure Portal の「ログストリーム」を確認
- GitHub Actions のエラーメッセージを確認
- `requirements.txt` の依存関係を確認

### サポート

問題が解決しない場合：
1. **GitHub Issues** で質問を投稿
2. **Azure サポート** （有料プランの場合）
3. **Stack Overflow** で検索

---

## 📚 参考資料

- [Azure App Service ドキュメント](https://docs.microsoft.com/azure/app-service/)
- [GitHub Actions ドキュメント](https://docs.github.com/actions)
- [Azure Developer CLI ガイド](https://docs.microsoft.com/azure/developer/azure-developer-cli/)

---

**ハッピーデプロイ！** 🚀