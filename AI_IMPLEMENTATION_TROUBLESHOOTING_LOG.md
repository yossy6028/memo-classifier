# AI実装トラブルシューティング履歴 - 2025-06-22〜23

## プロジェクト概要

**期間**: 2025-06-22〜23（丸2日間）  
**目的**: メモ分類システムにAI機能を統合し、適切なカテゴリ分類・タイトル生成・タグ生成を実現  
**技術スタック**: AppleScript + Python + Gemini API  

## 発生した主要問題と解決策

### 1. 過去のパターンに引っ張られる問題

**症状**: 「Claude料金体系解説」「AI比較活用法」等の固定タイトルが繰り返し生成される

**根本原因**: 
- `multi_ai_analyzer.py`にハードコードされたキーワード（obsidian, claude等）
- `_generate_corrected_title`関数の固定的なパターンマッチング

**解決策**: 
- 完全動的分析システム（`dynamic_analyzer.py`）を新規作成
- 毎回一意の分析IDでプロンプト送信
- 固定パターンを完全排除

```python
# 問題のあったコード
if 'obsidian' in content_lower:
    return "Obsidian設定"

# 解決後のコード
analysis_id = datetime.now().strftime("%Y%m%d%H%M%S%f")
# 動的にキーワード抽出して判定
```

### 2. キャッシュ・履歴データの影響

**症状**: コード修正しても古い結果が出続ける

**根本原因**:
- `embeddings_cache.pkl`（1.36MB）の残存
- `__pycache__`ディレクトリのPythonキャッシュ
- AppleScriptアプリのコンパイルキャッシュ

**解決策**:
```bash
# 必須のクリア手順
rm -f embeddings_cache.pkl
rm -rf __pycache__
find . -name "*.pyc" -delete
rm -rf OldApp.app  # 古いアプリ完全削除
osacompile -o NewApp.app script.applescript
```

### 3. カテゴリ分類の不具合

**症状**: ビジネス要素を含む教育関連メモが`education`に誤分類

**根本原因**: スコアリング方式では不十分

**解決策**: ビジネス要素1つでも検出→即座に`consulting`判定

```python
# Before: スコアリング方式
if cat == 'consulting':
    score *= 2

# After: 即座判定方式
for kw in business_keywords:
    if kw in content:
        return 'consulting'  # 即座に確定
```

### 4. AppleScript実行時のパス問題

**症状**: CLI実行は正常だがアプリ実行で`config.yaml`が見つからない

**根本原因**: AppleScript実行時のカレントディレクトリが異なる

**解決策**: 絶対パス指定

```python
# 問題のあったコード
self.gemini = GeminiClient()  # 相対パス'config.yaml'

# 解決後のコード
script_dir = os.path.dirname(os.path.abspath(__file__))
config_path = os.path.join(script_dir, 'config.yaml')
self.gemini = GeminiClient(config_path=config_path)
```

### 5. 結果構造の不整合

**症状**: DynamicAnalyzerの結果をminimal_analysis.pyで正しく取得できない

**根本原因**: 結果構造の理解不足

```python
# 問題のあったコード
if result and result.get('title'):

# 解決後のコード
if result and result.get('success'):
    analysis_result = result.get('result', {})
    title = analysis_result.get('title', '')
```

## 技術的な学習ポイント

### 1. AI統合システムの設計原則

**❌ 避けるべき設計**:
- ハードコードされたパターンマッチング
- 固定的なキーワードリスト
- 相対パスでの設定ファイル読み込み
- 単一の分析手法への依存

**✅ 推奨する設計**:
- 完全動的な分析システム
- 一意ID付きプロンプト送信
- 絶対パス指定
- フォールバック機構の実装

### 2. デバッグ戦略

**段階的デバッグの重要性**:
1. **CLI実行**: まずコマンドラインで動作確認
2. **関数単位**: 個別関数のテスト
3. **統合テスト**: 全体的な動作確認
4. **実環境テスト**: AppleScriptアプリでの動作確認

**デバッグログの活用**:
```python
# 実行コマンドをログに記録
do shell script "echo " & quoted form of ("EXECUTING: " & pythonCmd) & " >> " & quoted form of (logPath)

# 結果をログに記録
do shell script "echo " & quoted form of ("RESULT: " & result) & " >> " & quoted form of (logPath)
```

### 3. ファイル管理のベストプラクティス

**問題を引き起こすパターン**:
- 同名ファイルの上書き更新
- キャッシュファイルの放置
- 古いバージョンの残存

**推奨パターン**:
- 新機能は新名称でファイル作成
- 定期的なキャッシュクリア
- 古いファイルの完全削除

## 対処パターン別の解決手順

### パターン1: 同じ結果が繰り返し出力される

```bash
# Step 1: キャッシュクリア
rm -rf __pycache__
rm -f *.pkl
find . -name "*.pyc" -delete

# Step 2: アプリ再作成
rm -rf OldApp.app
osacompile -o NewApp.app script.applescript

# Step 3: 動作確認
python3 script.py preview "test content"
```

### パターン2: 設定ファイルが見つからない

```python
# 相対パス→絶対パス変更
import os
script_dir = os.path.dirname(os.path.abspath(__file__))
config_path = os.path.join(script_dir, 'config.yaml')
```

### パターン3: カテゴリ分類が不正確

```python
# スコアリング方式→即座判定方式
business_keywords = ['マーケティング', 'ブランディング', '事業', '売上']
for keyword in business_keywords:
    if keyword in content:
        return 'consulting'  # 即座に確定
```

## 今後のAI実装で注意すべき点

### 1. 設計フェーズ

**✅ 必須チェック項目**:
- [ ] 動的システム設計（固定パターン排除）
- [ ] 絶対パス使用
- [ ] 一意性確保機構
- [ ] フォールバック処理
- [ ] デバッグログ仕込み

### 2. 実装フェーズ

**✅ 実装順序**:
1. CLI版で動作確認
2. 関数単位テスト
3. 統合テスト
4. GUI/AppleScript統合
5. 本番環境テスト

### 3. トラブル発生時

**✅ 調査手順**:
1. CLI実行で切り分け
2. ログファイル確認
3. キャッシュクリア
4. 段階的デバッグ
5. 新名称で再作成

## 使用技術スタックでの注意点

### AppleScript + Python統合

**問題**: 実行環境の違い
**対策**: 絶対パス + 環境変数設定

```applescript
set pythonPath to "/Users/user/.pyenv/versions/3.11.9/bin/python3"
set scriptFile to "/absolute/path/to/script.py"
```

### Gemini API統合

**問題**: API呼び出し失敗時のフォールバック
**対策**: 多層フォールバック設計

```python
try:
    result = gemini_api.analyze(content)
except Exception:
    result = fallback_analyzer.analyze(content)
```

### macOS特有の問題

**問題**: iCloudストレージでのファイル同期遅延
**対策**: 重要な更新時は新名称ファイル作成

## 成功した最終構成

**ファイル構成**:
```
memo-classifier/
├── FinalMemo.app          # 最新アプリ
├── dynamic_analyzer.py    # 動的AI分析
├── tag_analyzer.py        # タグ分析
├── content_formatter.py   # コンテンツ整形
├── minimal_analysis.py    # メイン処理
├── gemini_client.py       # API クライアント
└── config.yaml           # 設定ファイル
```

**動作フロー**:
1. AppleScript → minimal_analysis.py呼び出し
2. minimal_analysis.py → dynamic_analyzer.py呼び出し
3. dynamic_analyzer.py → gemini_client.py + tag_analyzer.py
4. 結果統合 → フォーマット → 表示

## 計測データ

**開発時間**: 2日間（約16時間）
**主要問題数**: 5個
**作成ファイル数**: 8個
**削除ファイル数**: 6個（重複・テスト版）
**最終成功率**: 100%（全カテゴリ・タグ・タイトル生成正常動作）

## 次回プロジェクトへの提言

### 1. 事前準備

- [ ] 動的システム前提で設計
- [ ] デバッグ機構を最初から組み込み
- [ ] 絶対パス使用を標準に
- [ ] キャッシュクリア手順を文書化

### 2. 開発手順

- [ ] CLI版から開始
- [ ] 段階的統合
- [ ] 各段階でのテスト
- [ ] 問題発生時は新名称で作成

### 3. トラブル予防

- [ ] 定期的なキャッシュクリア
- [ ] ログファイルの活用
- [ ] バックアップ戦略
- [ ] 問題パターンの事前学習

このログを参考に、次回以降のAI実装プロジェクトでは同様の問題を回避し、より効率的な開発が可能になることを期待します。