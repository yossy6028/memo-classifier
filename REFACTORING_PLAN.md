# メモ分類システム リファクタリング計画

## 現状分析

### ファイル構成（5つのPythonファイル）
1. **universal_analysis.py** - メインエントリーポイント
2. **universal_analyzer.py** - 分析ロジック
3. **gemini_client.py** - AI API連携
4. **tag_analyzer.py** - タグ生成
5. **content_formatter.py** - コンテンツ整形

### 問題点
1. **責任の重複**: 分析ロジックが複数ファイルに分散
2. **設定の分散**: ハードコードされたパスや設定が各所に
3. **エラーハンドリングの不統一**: 各ファイルで異なる方式
4. **テスタビリティ**: 結合度が高く単体テストが困難
5. **保守性**: ビジネスロジックとインフラ層が混在

## リファクタリング方針

### 1. アーキテクチャの整理
```
memo_classifier/
├── core/              # コアビジネスロジック
│   ├── __init__.py
│   ├── analyzer.py    # 統合分析エンジン
│   ├── models.py      # データモデル定義
│   └── config.py      # 設定管理
├── services/          # 外部サービス連携
│   ├── __init__.py
│   ├── gemini.py      # Gemini API
│   └── obsidian.py    # Obsidian連携
├── utils/             # ユーティリティ
│   ├── __init__.py
│   ├── text_processor.py  # テキスト処理
│   ├── file_manager.py    # ファイル操作
│   └── logger.py      # ログ管理
├── main.py            # エントリーポイント
└── config.yaml        # 設定ファイル
```

### 2. 責任の明確化
- **Analyzer**: タイトル・カテゴリ・タグの分析統合
- **Gemini Service**: AI API通信のみ
- **Obsidian Service**: ファイル操作・検索のみ
- **Text Processor**: テキスト処理・フォーマット
- **File Manager**: ファイルI/O・パス管理

### 3. 設定の統一
```yaml
# config.yaml
obsidian:
  base_path: "/Users/yoshiikatsuhiko/Library/Mobile Documents/iCloud~md~obsidian/Documents"
  inbox_path: "02_Inbox"

gemini:
  model: "gemini-2.0-flash-thinking-exp"

categories:
  consulting: "Consulting"
  tech: "Tech"
  education: "Education"
  kindle: "kindle"
  music: "Music"
  media: "Media"
  others: "Others"
```

### 4. エラーハンドリングの統一
- カスタム例外クラスの定義
- 一元的なエラーログ管理
- 適切なフォールバック処理

## 実装順序

### Phase 1: コア構造の整理
1. models.py でデータ構造定義
2. config.py で設定管理統一
3. logger.py でログ管理統一

### Phase 2: サービス層の分離
1. gemini.py にAPI通信を集約
2. obsidian.py にファイル操作を集約
3. text_processor.py にテキスト処理を集約

### Phase 3: ビジネスロジックの統合
1. analyzer.py に分析ロジックを統合
2. 既存ファイルから機能を移行
3. main.py でエントリーポイント統一

### Phase 4: 最適化とクリーンアップ
1. 不要ファイルの削除
2. テストケースの追加
3. パフォーマンス最適化

## 期待効果

### 保守性向上
- 単一責任原則による明確な役割分担
- 設定変更の影響範囲限定
- 新機能追加時の影響範囲予測可能

### 可読性向上
- 機能ごとの明確な境界
- 統一されたコーディング規約
- 適切な抽象化レベル

### テスタビリティ向上
- 依存性注入による結合度低減
- モック化しやすい構造
- 単体テスト実行可能

### パフォーマンス向上
- 不要な処理の削除
- キャッシュ機能の統一
- 効率的なファイルアクセス