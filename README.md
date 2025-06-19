# Cursor Memo Classifier v1.0

カーソルメモ分類・Obsidian投入システム

## 概要

このシステムは、カーソルのテキストウィンドウに入力されたメモを自動的に分析・分類し、適切なタグとリレーションを付けてObsidianの「02_Inbox」フォルダに保存します。

## 主な機能

- 🎯 **AI による自動分類**: Claude 3.5 Sonnet を使用したメモの自動分類
- 📝 **タイトル自動生成**: 25文字以内の最適化されたタイトル生成
- 🏷️ **タグ自動付与**: 既存タグ体系との統合による適切なタグ生成
- 🔗 **関連性分析**: 高度な文脈理解による既存メモとのリレーション設定
- 💾 **Obsidian連携**: Markdownファイルとして適切なフォルダに自動保存

## システム要件

- Python 3.11+
- macOS (現在の実装)
- Obsidian with 02_Inbox フォルダ構造

## セットアップ

### 1. 仮想環境作成

```bash
python3 -m venv venv
source venv/bin/activate
```

### 2. 依存関係インストール

```bash
pip install -r requirements.txt
```

### 3. 環境変数設定

```bash
export ANTHROPIC_API_KEY="your-api-key-here"
```

### 4. 設定ファイル編集

`config.yaml` を編集してObsidianのパスを設定:

```yaml
obsidian_vault_path: "/path/to/your/obsidian/vault"
```

## 使用方法

### 対話モード

```bash
python main.py --interactive
```

### 単一メモ処理

```bash
python main.py --memo "あなたのメモテキスト"
```

### バッチ処理

```bash
python main.py --batch memos.txt
```

## フォルダ構造

```
02_Inbox/
├── education/      # 教育・学習関連
├── tech/          # 技術・プログラミング
├── business/      # ビジネス・マーケティング
├── ideas/         # アイデア・創作
├── general/       # 一般・日常
├── kindle/        # 読書メモ (既存)
└── Readwise/      # Web記事 (既存)
```

## 開発状況

### Phase 1: 基盤構築 ✅
- [x] プロジェクト環境設定
- [x] 基本的なファイル構造作成
- [x] 設定ファイル作成
- [x] 主要モジュール作成

### Phase 2: AI分析基盤開発 🚧
- [ ] Claude API連携実装
- [ ] タイトル自動生成機能
- [ ] 基本的な内容分析機能
- [ ] 文脈分析エンジンの実装

## ライセンス

MIT License

## 開発者

Cursor Memo Classifier Project 