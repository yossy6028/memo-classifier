# Memo Classifier

AI（Gemini 2.5 Flash）を使用したメモの自動分析・分類システム

## 機能

- メモ内容の自動タイトル生成
- カテゴリ自動分類（consulting, tech, education, kindle, music, media, others）
- タグ自動生成
- Obsidianファイル自動作成
- 関連ファイル検索

## セットアップ

### 1. API key設定

```bash
# テンプレートをコピー
cp api_config.py.template api_config.py

# エディタでapi_config.pyを開いてAPI keyを設定
# YOUR_GEMINI_API_KEY_HERE を実際のGemini API keyに置き換え
```

### 2. 依存関係インストール

```bash
pip install -r requirements.txt
```

### 3. 使用方法

#### コマンドライン
```bash
# プレビュー
python universal_analysis.py preview "メモ内容"

# 保存
python universal_analysis.py save "メモ内容"
```

#### AppleScript（macOS）
`SafeMinimalMemo.applescript`を実行してGUIから使用

## ファイル構成

- `universal_analysis.py` - メインエントリーポイント
- `universal_analyzer.py` - 分析エンジン
- `gemini_client.py` - AI通信（Gemini 2.5 Flash）
- `api_config.py` - API key設定（gitignore対象）
- `tag_analyzer.py` - タグ生成
- `content_formatter.py` - コンテンツフォーマット
- `SafeMinimalMemo.applescript` - macOS GUI

## セキュリティ

- `api_config.py`は`.gitignore`により除外済み
- API keyはリポジトリにコミットされません
- 本番環境では環境変数の使用を推奨

## 対応カテゴリ

- **consulting**: ビジネス戦略、コンサルティング
- **tech**: プログラミング、技術解説
- **education**: 教育手法、学習方法
- **kindle**: 書籍内容、読書記録
- **music**: 音楽理論、演奏技術
- **media**: SNS、YouTube、外部発信
- **others**: その他