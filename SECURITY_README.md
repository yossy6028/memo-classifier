# セキュリティ設定ガイド

## APIキーの安全な設定

### 1. 環境変数での設定（推奨）

#### macOS/Linux
```bash
# ~/.bashrc または ~/.zshrc に追加
export GEMINI_API_KEY="your_actual_api_key_here"

# または一時的に設定
export GEMINI_API_KEY="your_actual_api_key_here"
```

#### Windows
```cmd
# コマンドプロンプト
set GEMINI_API_KEY=your_actual_api_key_here

# PowerShell
$env:GEMINI_API_KEY="your_actual_api_key_here"
```

### 2. .envファイルでの設定

プロジェクトルートに `.env` ファイルを作成：
```
GEMINI_API_KEY=your_actual_api_key_here
DEBUG=false
LOG_LEVEL=INFO
```

**注意**: `.env` ファイルは `.gitignore` で除外されており、Gitにコミットされません。

### 3. 新しいAPIキーの取得

**重要**: 既存のAPIキーが漏洩した場合は、以下の手順で新しいキーを取得してください：

1. [Google AI Studio](https://aistudio.google.com/app/apikey) にアクセス
2. 既存のAPIキーを無効化（Revoke）
3. 新しいAPIキーを生成
4. 新しいキーを環境変数に設定

### 4. セキュリティのベストプラクティス

- ✅ 環境変数またはローカル.envファイルでAPIキーを管理
- ✅ `.gitignore` でシークレット情報を除外
- ✅ 定期的なAPIキーの更新
- ❌ コードやconfig.yamlに直接APIキーを記述
- ❌ 公開リポジトリにAPIキーをコミット

## 緊急対応

APIキーが漏洩した場合：
1. 🚨 **即座にAPIキーを無効化**
2. 🔑 **新しいAPIキーを生成**
3. 🗑️ **Git履歴からも削除**（git filter-branch等）
4. 📊 **使用量を監視**して不正利用をチェック