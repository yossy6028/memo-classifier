#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
動的タグ分析システム - 個別具体的な単語を優先
"""

import os
import re
import glob
from collections import Counter
from typing import List, Set, Dict, Tuple
import logging

class TagAnalyzer:
    """既存ファイルのタグ頻度を分析し、ユニークなタグを優先"""
    
    def __init__(self, vault_path: str = None):
        self.logger = logging.getLogger(__name__)
        
        # Obsidianの保管場所
        if vault_path:
            self.vault_path = vault_path
        else:
            self.vault_path = "/Users/yoshiikatsuhiko/Library/Mobile Documents/iCloud~md~obsidian/Documents"
        
        # 一般的すぎる単語のブラックリスト
        self.common_words = {
            # 一般的な名詞
            '方法', '問題', '解決', '対策', '情報', '内容', 'データ', 'システム',
            '機能', '設定', '管理', '利用', '使用', '実装', '処理', '結果',
            '料金', '価格', '費用', 'コスト', '時間', '期間', '場所', '理由',
            'もの', 'こと', 'とき', 'ため', 'ところ', 'わけ', 'はず',
            # 一般的な動詞の名詞形
            '作成', '削除', '追加', '変更', '更新', '確認', '検討', '調査',
            '分析', '評価', '比較', '選択', '決定', '実行', '開始', '終了',
            # 抽象的な概念
            '概要', '詳細', '全体', '部分', '基本', '応用', '理論', '実践',
            '原因', '結果', '効果', '影響', '関係', '連携', '統合', '分離',
            # 英語の一般語
            'the', 'and', 'or', 'in', 'on', 'at', 'to', 'for', 'of', 'with',
            'data', 'info', 'system', 'method', 'problem', 'solution'
        }
        
        # 既存タグの使用頻度を計算（初回のみ）
        self._existing_tag_frequency = None
    
    def get_existing_tag_frequency(self) -> Counter:
        """既存ファイルのタグ使用頻度を取得（キャッシュ付き）"""
        if self._existing_tag_frequency is None:
            self._existing_tag_frequency = self._analyze_vault_tags()
        return self._existing_tag_frequency
    
    def _analyze_vault_tags(self) -> Counter:
        """Vaultの既存ファイルからタグ使用頻度を分析"""
        tag_counter = Counter()
        
        try:
            # マークダウンファイルを検索
            md_files = glob.glob(os.path.join(self.vault_path, "**/*.md"), recursive=True)
            
            for file_path in md_files[:100]:  # パフォーマンスのため最大100ファイル
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                        
                    # YAMLフロントマターからタグを抽出
                    if content.startswith('---'):
                        yaml_match = re.search(r'^---\s*\n(.*?)\n---', content, re.DOTALL)
                        if yaml_match:
                            yaml_content = yaml_match.group(1)
                            # tags: の行を探す
                            tags_match = re.search(r'tags:\s*\[(.*?)\]', yaml_content)
                            if tags_match:
                                tags_str = tags_match.group(1)
                                tags = [tag.strip().strip('"').strip("'") for tag in tags_str.split(',')]
                                tag_counter.update(tags)
                                
                except Exception as e:
                    continue
                    
        except Exception as e:
            self.logger.warning(f"Vault分析エラー: {e}")
            
        return tag_counter
    
    def generate_unique_tags(self, content: str, max_tags: int = 5) -> List[str]:
        """個別具体的でユニークなタグを生成"""
        
        # 既存タグの頻度を取得
        existing_frequency = self.get_existing_tag_frequency()
        
        # 候補となる単語を抽出
        candidates = self._extract_tag_candidates(content)
        
        # スコアリング（低頻度・具体的な単語を優先）
        scored_tags = []
        for word in candidates:
            score = self._calculate_tag_score(word, existing_frequency, content)
            if score > 0:
                scored_tags.append((word, score))
        
        # スコア順でソート
        scored_tags.sort(key=lambda x: x[1], reverse=True)
        
        # 上位のタグを返す
        return [tag for tag, _ in scored_tags[:max_tags]]
    
    def _extract_tag_candidates(self, content: str) -> List[str]:
        """タグ候補となる単語を抽出"""
        candidates = []
        
        # 固有名詞パターン
        patterns = [
            # 英語の固有名詞（大文字始まり、単語単位）
            r'\b[A-Z][a-zA-Z]+\b',
            # カタカナ語（3文字以上）
            r'[\u30a1-\u30f6\u30fc]{3,}',
            # 漢字熟語（2-6文字）
            r'[\u4e00-\u9fa5]{2,6}',
            # カタカナ+漢字の複合語
            r'[\u30a1-\u30f6\u30fc]+[\u4e00-\u9fa5]+',
            # 漢字+カタカナの複合語
            r'[\u4e00-\u9fa5]+[\u30a1-\u30f6\u30fc]+',
            # 数字を含む語（バージョンなど）
            r'\b[A-Za-z]+\d+\b',
            # ハイフン・アンダースコア含む複合語
            r'\b\w+[-_]\w+\b',
            # 英数字混合（GPT-4など）
            r'\b[A-Z]{2,}-\d+\b'
        ]
        
        for pattern in patterns:
            matches = re.findall(pattern, content)
            candidates.extend(matches)
        
        # 重複除去と正規化
        seen = set()
        unique_candidates = []
        for word in candidates:
            normalized = word.strip()
            if normalized and normalized not in seen:
                seen.add(normalized)
                unique_candidates.append(normalized)
        
        return unique_candidates
    
    def _calculate_tag_score(self, word: str, existing_frequency: Counter, content: str) -> float:
        """タグのスコアを計算（低頻度・具体的を高評価）"""
        
        word_lower = word.lower()
        
        # 一般的な単語は除外
        if word_lower in self.common_words:
            return 0
        
        # 短すぎる・長すぎる単語は除外
        if len(word) < 2 or len(word) > 20:
            return 0
        
        # 基本スコア
        score = 1.0
        
        # 文字数による具体性評価（3-15文字が最適）
        if 3 <= len(word) <= 15:
            score += 0.5
        elif len(word) > 15:
            score -= 0.3
        
        # 既存使用頻度による評価（使用頻度が低いほど高スコア）
        existing_count = existing_frequency.get(word, 0)
        if existing_count == 0:
            score += 2.0  # 未使用タグは高評価
        elif existing_count <= 2:
            score += 1.0  # 低頻度タグも評価
        elif existing_count >= 10:
            score -= 1.0  # 高頻度タグは低評価
        
        # 固有名詞判定（大文字始まりやカタカナ）
        if re.match(r'^[A-Z]', word) or re.match(r'^[\u30a1-\u30f6\u30fc]+$', word):
            score += 1.5
        
        # 複合語・専門用語判定
        if '-' in word or '_' in word or re.search(r'\d', word):
            score += 1.0
        
        # コンテンツ内での重要度（出現回数）
        occurrences = content.count(word)
        if occurrences >= 3:
            score += 0.5
        elif occurrences == 1:
            score -= 0.2
        
        # 文脈での役割判定
        # タイトルっぽい位置（最初の方）に出現
        if content[:100].find(word) >= 0:
            score += 0.5
        
        return max(0, score)
    
    def get_tag_suggestions(self, content: str, current_tags: List[str] = None) -> Dict[str, float]:
        """タグ候補とそのスコアを返す（デバッグ用）"""
        
        existing_frequency = self.get_existing_tag_frequency()
        candidates = self._extract_tag_candidates(content)
        
        suggestions = {}
        for word in candidates:
            score = self._calculate_tag_score(word, existing_frequency, content)
            if score > 0:
                suggestions[word] = score
        
        # 現在のタグがある場合は、それらのスコアも表示
        if current_tags:
            for tag in current_tags:
                if tag not in suggestions:
                    suggestions[tag] = self._calculate_tag_score(tag, existing_frequency, content)
        
        return dict(sorted(suggestions.items(), key=lambda x: x[1], reverse=True))


# テスト
if __name__ == "__main__":
    analyzer = TagAnalyzer()
    
    test_content = """
    Obsidian Zettelkasten方式でのナレッジ管理について。
    Claude APIとGPT-4の料金比較も実施。
    バックリンク機能の活用方法を解説。
    """
    
    tags = analyzer.generate_unique_tags(test_content)
    print("生成タグ:", tags)
    
    suggestions = analyzer.get_tag_suggestions(test_content)
    print("\nタグ候補とスコア:")
    for tag, score in list(suggestions.items())[:10]:
        print(f"  {tag}: {score:.2f}")