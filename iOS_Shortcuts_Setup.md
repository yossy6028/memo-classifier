# 📱 memo-classifier iOS Shortcuts セットアップガイド

## 🚀 **完全セットアップ手順**

### **Step 1: Mac側APIサーバー起動**

1. **依存関係のインストール**
```bash
cd /path/to/memo-classifier
pip install -r requirements_api.txt
```

2. **APIサーバー起動**
```bash
python3 api_server.py
```

3. **MacのIPアドレス確認**
```bash
ifconfig | grep "inet " | grep -v 127.0.0.1
```
例: `192.168.1.100` をメモしておく

### **Step 2: iPhone Shortcuts作成**

#### **🎯 Shortcut 1: メモ分析（プレビュー版）**

1. **Shortcuts.app**を開く
2. **「+」**で新しいショートカット作成
3. **名前**: `メモ分析`
4. **アクション追加順序**:

```
1. 📝 Ask for Input
   - Input Type: Text
   - Prompt: "分析したいメモを入力してください"
   - Allow Multiline: ON

2. 🌐 Get Contents of URL
   - URL: http://[MacのIPアドレス]:8080/quick-analyze
   - Method: POST
   - Headers:
     Content-Type: application/json
   - Request Body (JSON):
     {
       "content": [Ask for Input の結果],
       "action": "preview"
     }

3. 📊 Get Value from Input
   - Input: [Get Contents of URL の結果]
   - Get Value for: title

4. 📊 Get Value from Input
   - Input: [Get Contents of URL の結果] 
   - Get Value for: category

5. 📊 Get Value from Input
   - Input: [Get Contents of URL の結果]
   - Get Value for: tags

6. 📊 Get Value from Input
   - Input: [Get Contents of URL の結果]
   - Get Value for: confidence

7. 💬 Show Notification
   - Title: "分析完了"
   - Body: "📋 タイトル: [title]
📂 カテゴリ: [category] ([confidence])
🏷️ タグ: [tags]"
```

#### **💾 Shortcut 2: メモ保存版**

1. **新しいショートカット作成**
2. **名前**: `メモ保存`
3. **アクション追加順序**:

```
1. 📝 Ask for Input
   - Input Type: Text
   - Prompt: "保存するメモを入力してください"
   - Allow Multiline: ON

2. 🌐 Get Contents of URL
   - URL: http://[MacのIPアドレス]:8080/analyze
   - Method: POST
   - Headers:
     Content-Type: application/json
   - Request Body (JSON):
     {
       "content": [Ask for Input の結果],
       "action": "save"
     }

3. 📊 Get Value from Input
   - Input: [Get Contents of URL の結果]
   - Get Value for: message

4. 💬 Show Notification
   - Title: "保存完了"
   - Body: [message]
```

#### **⚡ Shortcut 3: クイック分析（共有シート版）**

1. **新しいショートカット作成**
2. **名前**: `クイック分析`
3. **Receive**: Text from Share Sheet
4. **アクション追加順序**:

```
1. 🌐 Get Contents of URL
   - URL: http://[MacのIPアドレス]:8080/quick-analyze
   - Method: POST
   - Headers:
     Content-Type: application/json
   - Request Body (JSON):
     {
       "content": [Shortcut Input],
       "action": "preview"
     }

2. 📊 Get Value from Input
   - Input: [Get Contents of URL の結果]
   - Get Value for: title

3. 📊 Get Value from Input  
   - Input: [Get Contents of URL の結果]
   - Get Value for: category

4. 💬 Show Result
   - Text: "📋 [title]
📂 [category]
🏷️ [tags]"
```

### **Step 3: 動作テスト**

1. **APIサーバーが起動していることを確認**
   ```bash
   curl http://localhost:8080/health
   ```

2. **iPhone Shortcutsを実行**
   - Shortcuts.appから「メモ分析」を実行
   - テストメモを入力: "Claude CodeとGitHubの技術メモです"

3. **期待される結果**:
   ```
   📋 タイトル: プログラミングとGitの開発
   📂 カテゴリ: tech (100%)
   🏷️ タグ: #Claude, #GitHub, #記録
   ```

### **🔧 トラブルシューティング**

#### **よくある問題と解決法**

1. **「接続できません」エラー**
   - MacとiPhoneが同じWi-Fiネットワークに接続されているか確認
   - Macのファイアウォール設定を確認
   - IPアドレスが正しいか確認

2. **「不正なJSON」エラー**
   - Shortcuts内のRequest BodyでText形式ではなくJSON形式を選択
   - 変数の埋め込み方法を確認

3. **「タイムアウト」エラー**
   - APIサーバーが起動しているか確認
   - Macがスリープモードになっていないか確認

### **🎨 カスタマイズ例**

#### **Siri対応版**
1. Shortcutsの設定で「Add to Siri」
2. フレーズ設定: "メモを分析して"
3. 音声でメモ入力→自動分析

#### **ウィジェット版**
1. Shortcutsをホーム画面ウィジェットに追加
2. ワンタップでメモ分析開始

#### **オートメーション版**
1. 特定のアプリ（メモ、Notes等）で共有時に自動実行
2. 時間指定での定期実行

### **📊 API エンドポイント一覧**

| エンドポイント | 説明 | 用途 |
|---------------|------|------|
| `/health` | サーバー状態確認 | 接続テスト |
| `/analyze` | 完全分析・保存 | メイン機能 |
| `/quick-analyze` | 簡易分析 | 高速プレビュー |

これで、iPhone上でmemo-classifierの全機能が利用できるようになります！