#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
普遍的メモ分析システム - キーワードに依存しない動的タイトル生成
どんなジャンルのメモでも適切なタイトルを生成する普遍的アルゴリズム
"""

import os
import re
import json
from typing import Dict, List, Optional
from datetime import datetime
import logging

from gemini_client import GeminiClient
from tag_analyzer import TagAnalyzer

class UniversalAnalyzer:
    """普遍的メモ分析システム - ジャンルに依存しない分析"""
    
    def __init__(self):
        script_dir = os.path.dirname(os.path.abspath(__file__))
        config_path = os.path.join(script_dir, 'config.yaml')
        
        self.gemini = GeminiClient(config_path=config_path)
        self.tag_analyzer = TagAnalyzer()
        self.logger = logging.getLogger(__name__)
        
    def analyze(self, content: str, categories: List[str]) -> Dict:
        """コンテンツを普遍的に分析してタイトル・カテゴリ・タグを生成"""
        
        analysis_id = datetime.now().strftime("%Y%m%d%H%M%S%f")
        
        prompt = f"""
あなたは文書分析の専門家です。以下のメモを分析し、普遍的な手法でタイトル・カテゴリ・タグを生成してください。

分析ID: {analysis_id}
現在時刻: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}

【重要な分析原則】
1. 特定のキーワードに依存せず、文書の本質を理解する
2. 文書の種類（戦略書、手順書、分析レポート等）を判定する
3. 主要な動作・目的（分析、提案、説明、計画等）を特定する
4. 対象領域（教育、ビジネス、技術等）を抽出する

【タイトル生成の普遍的ルール】
- 文書種別 + 対象 + 動作の組み合わせで生成
- 例：「教育システム分析」「マーケティング戦略提案」「開発手順説明」
- 体言止めで簡潔に（10-20文字）
- 内容の本質を一目で理解できるように

【カテゴリ判定の普遍的ルール】
- ビジネス・経営・戦略・コンサル要素 → consulting
- 技術・開発・システム・プログラミング → tech  
- 純粋な教育手法・学習方法（ビジネス要素なし） → education
- 書籍・読書・出版 → kindle
- 音楽・演奏・楽器 → music
- SNS・YouTube・note等外部発信全般、コンテンツ制作、映像、デザイン → media
- その他 → others

重要：SNS(X/Twitter/Instagram/TikTok等)、YouTube、note、ブログ等の外部発信プラットフォーム関連は必ずmediaに分類

メモ内容:
{content}

カテゴリ選択肢: {', '.join(categories)}

以下の形式で出力してください（JSON形式）：
{{
    "document_type": "文書の種類（戦略書/手順書/分析レポート/会議記録/提案書など）",
    "main_action": "主要な動作（分析/提案/説明/計画/検討など）",
    "target_domain": "対象領域（教育/マーケティング/技術/経営など）",
    "title": "普遍的手法で生成した体言止めタイトル",
    "category": "最も適切なカテゴリ",
    "tags": ["関連タグ1", "関連タグ2", "関連タグ3"],
    "confidence": "タイトル生成の信頼度（0.0-1.0）"
}}
"""
        
        try:
            response = self.gemini.model.generate_content(prompt).text
            
            # JSON部分を抽出
            json_match = re.search(r'\{[^{}]*?\}', response, re.DOTALL)
            if json_match:
                result = json.loads(json_match.group())
                
                # 結果の検証と補完
                result = self._validate_and_enhance(result, content)
                
                return {
                    'success': True,
                    'result': {
                        'title': result.get('title', '分析メモ'),
                        'category': result.get('category', 'others'),
                        'tags': result.get('tags', ['メモ']),
                        'meta': {
                            'document_type': result.get('document_type', '不明'),
                            'main_action': result.get('main_action', '記録'),
                            'target_domain': result.get('target_domain', '一般'),
                            'confidence': result.get('confidence', 0.7)
                        }
                    },
                    'confidence': result.get('confidence', 0.7),
                    'model': 'universal-analyzer'
                }
                
        except Exception as e:
            self.logger.error(f"普遍的分析エラー: {e}")
            
        # フォールバック：基本的な構造分析
        return self._structural_fallback(content, categories)
    
    def _validate_and_enhance(self, result: Dict, content: str) -> Dict:
        """結果の検証と普遍的強化"""
        
        # タイトルの検証
        title = result.get('title', '')
        if not title or len(title) < 3 or len(title) > 30:
            # 構造的にタイトルを再生成
            title = self._generate_structural_title(
                result.get('document_type', ''), 
                result.get('target_domain', ''), 
                result.get('main_action', ''),
                content
            )
            result['title'] = title
        
        # カテゴリの検証
        if result.get('category') not in ['consulting', 'tech', 'education', 'kindle', 'music', 'media', 'others']:
            result['category'] = self._classify_by_content_structure(content)
        
        # タグの強化
        if not result.get('tags') or len(result['tags']) < 2:
            result['tags'] = self.tag_analyzer.generate_unique_tags(content)[:5]
        
        return result
    
    def _generate_structural_title(self, doc_type: str, domain: str, action: str, content: str) -> str:
        """構造的タイトル生成 - キーワードに依存しない"""
        
        # 内容の長さと複雑さを判定
        word_count = len(content)
        has_structure = any(marker in content for marker in ['##', '**', '■', '◆', '①', '1.', '・'])
        
        # 文書種別の判定
        if not doc_type or doc_type == '不明':
            if '戦略' in content or '計画' in content:
                doc_type = '戦略'
            elif '手順' in content or 'ステップ' in content or '方法' in content:
                doc_type = '手順'
            elif '分析' in content or '検証' in content or '評価' in content:
                doc_type = '分析'
            elif '提案' in content or '案' in content:
                doc_type = '提案'
            elif word_count > 1000 and has_structure:
                doc_type = 'レポート'
            else:
                doc_type = 'メモ'
        
        # 対象領域の判定
        if not domain or domain == '一般':
            if any(word in content for word in ['教育', '学習', '授業', '生徒', '指導']):
                domain = '教育'
            elif any(word in content for word in ['マーケティング', 'ブランディング', '集客', '営業']):
                domain = 'マーケティング'
            elif any(word in content for word in ['コード', 'プログラミング', 'システム', 'AI', 'DX']):
                domain = '技術'
            elif any(word in content for word in ['経営', 'ビジネス', '事業', '戦略']):
                domain = 'ビジネス'
            else:
                # 内容から最頻出の名詞を抽出
                domain = self._extract_main_topic(content)
        
        # 動作の判定
        if not action or action == '記録':
            if '提案' in content or '案' in content:
                action = '提案'
            elif '分析' in content or '検証' in content:
                action = '分析'
            elif '計画' in content or '戦略' in content:
                action = '計画'
            elif '説明' in content or '解説' in content:
                action = '説明'
            elif '手順' in content or '方法' in content:
                action = '手順'
            else:
                action = '検討'
        
        # タイトル組み立て
        if domain and action:
            return f"{domain}{action}"
        elif domain:
            return f"{domain}{doc_type}"
        else:
            return f"{doc_type}メモ"
    
    def _extract_main_topic(self, content: str) -> str:
        """内容から主要トピックを抽出"""
        
        # 頻出する意味のある単語を抽出
        import re
        from collections import Counter
        
        # 名詞的な単語を抽出（カタカナ、漢字）
        words = re.findall(r'[\u30a1-\u30f6\u30fc]{3,}|[\u4e00-\u9fa5]{2,}', content)
        
        # 一般的すぎる単語を除外
        exclude_words = {
            '内容', '情報', 'データ', 'システム', '方法', '問題', '結果', '場合', '状況',
            '今回', '最初', '最後', '時間', '場所', '必要', '重要', '可能', '確認'
        }
        
        meaningful_words = [w for w in words if w not in exclude_words and len(w) > 1]
        
        if meaningful_words:
            # 最頻出の単語を返す
            counter = Counter(meaningful_words)
            return counter.most_common(1)[0][0]
        
        return '一般'
    
    def _classify_by_content_structure(self, content: str) -> str:
        """内容の構造からカテゴリを分類"""
        
        content_lower = content.lower()
        
        # ビジネス・コンサル要素（最優先）
        business_keywords = [
            '戦略', '計画', '提案', 'コンサル', '営業', '売上', '収益', '事業', '経営',
            'マーケティング', 'ブランディング', '集客', '顧客', 'クライアント',
            '打ち合わせ', '会議', 'ミーティング', '検討', '分析', '企画'
        ]
        
        # ビジネス要素がある場合は他の要素より優先してconsulting
        if any(keyword in content for keyword in business_keywords):
            return 'consulting'
        
        # 技術要素
        tech_keywords = [
            'プログラミング', 'コード', 'システム', 'アプリ', 'API', 'AI', 'DX',
            'バイブコーディング', 'リファクタリング', '開発', '実装', 'ファイル'
        ]
        
        if any(keyword in content for keyword in tech_keywords):
            return 'tech'
        
        # 教育要素（ビジネス要素がない場合のみ）
        education_keywords = ['教育', '学習', '授業', '指導', '生徒', '学校', '塾']
        
        if any(keyword in content for keyword in education_keywords):
            return 'education'
        
        # その他の判定
        if any(keyword in content for keyword in ['本', '書籍', '読書', 'Kindle']):
            return 'kindle'
        
        if any(keyword in content for keyword in ['音楽', '楽器', '演奏', 'ライブ']):
            return 'music'
        
        # メディア・外部発信要素（ビジネス要素がない場合のみ）
        media_keywords = [
            'SNS', 'YouTube', 'note', 'ブログ', 'Instagram', 'Twitter', 'TikTok',
            'コンテンツ制作', '外部発信', 'ニュース', '記事', 'メディア'
        ]
        
        if any(keyword in content for keyword in media_keywords):
            return 'media'
        
        return 'others'
    
    def _structural_fallback(self, content: str, categories: List[str]) -> Dict:
        """構造的フォールバック処理"""
        
        # 基本的な構造分析
        title = self._generate_structural_title('', '', '', content)
        category = self._classify_by_content_structure(content)
        tags = self.tag_analyzer.generate_unique_tags(content)
        
        return {
            'success': True,
            'result': {
                'title': title,
                'category': category if category in categories else 'others',
                'tags': tags[:5] if tags else ['メモ'],
                'meta': {
                    'document_type': '構造分析',
                    'main_action': '記録',
                    'target_domain': '一般',
                    'confidence': 0.6
                }
            },
            'confidence': 0.6,
            'model': 'structural-fallback'
        }


if __name__ == "__main__":
    # テスト実行
    analyzer = UniversalAnalyzer()
    
    test_content = """
    バイブコーディングするときAIに、
    「いいですね。ここでいったんファイルとコードを俯瞰して、リファクタリングしましょう。無駄なコードや非合理なストラクチャを整理し、適切な粒度でファイルを整理し、メンテナンス性をあげてください」
    って、定期的に命令する
    """
    
    result = analyzer.analyze(test_content, ['tech', 'education', 'others'])
    print(json.dumps(result, ensure_ascii=False, indent=2))