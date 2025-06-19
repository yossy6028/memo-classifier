#!/usr/bin/env python3
"""
統合プレビュー機能付き強化メモ処理システム
AppleScript確認画面用の完全な事前分析
"""

import sys
import os
import re
import json
from pathlib import Path
from datetime import datetime
from collections import Counter, defaultdict


class IntegratedMemoProcessor:
    """統合メモプロセッサー（プレビュー対応）"""
    
    def __init__(self):
        # 基本設定
        self.obsidian_path = "/Users/yoshiikatsuhiko/Library/Mobile Documents/iCloud~md~obsidian/Documents"
        self.inbox_path = "02_Inbox"
        
        # カテゴリマッピング
        self.category_folders = {
            'education': '0_Education_国語教育_AI',
            'tech': '1_Tech_MCP_API', 
            'business': '2_Business_集客_アイデア',
            'ideas': '3_Ideas_プロジェクト',
            'general': '4_General',
            'kindle': '5_Kindle',
            'readwise': '6_Readwise'
        }
        
        # 強化されたカテゴリ判定キーワード
        self.category_keywords = {
            'education': [
                # 基本教育用語
                '教育', '指導', '授業', '学習', '国語', '読解', '表現', '生徒', '先生', '教師',
                # 文学・国語技法
                '対句法', 'リズム', '音数', '韻律', '修辞', '技法', '文体', '表現法',
                # 授業場面の語彙
                'シーン', '考えて', '選びなさい', '思い出す', '思い浮かべ', 'わかる', 'ひっかけ',
                '問題', '答え', '正解', '不正解', '例えば', '仮に', '場面', '状況', '状態',
                # 評価・指導語
                'そうですね', '素晴らしい', '残念', '惜しい', 'くん', 'さん', 'ちゃん',
                # 五感・感覚
                '聴覚', '視覚', '触覚', '嗅覚', '味覚', '五感', '感覚', '体の部分', 'メロディー'
            ],
            'tech': [
                'プログラミング', 'API', 'システム', 'アプリ', 'python', 'javascript', 
                'tech', '技術', '開発', 'コード', 'データ', 'AI', '機械学習'
            ],
            'business': [
                'ビジネス', 'マーケティング', '戦略', '営業', '集客', 'SEO', 'SNS', 
                '広告', '売上', '収益', '顧客', '市場'
            ],
            'ideas': [
                'アイデア', '企画', '提案', '案', 'プロジェクト', '創作', '発想', 
                'ブレスト', 'コンセプト', 'プラン'
            ]
        }
    
    def preview_analysis(self, content: str) -> dict:
        """プレビュー用の完全分析"""
        try:
            print("🔄 統合分析開始...")
            
            # 1. カテゴリ分析（強化版）
            category_result = self._enhanced_category_analysis(content)
            print(f"📂 カテゴリ分析: {category_result}")
            
            # 2. タイトル生成（主題把握）
            title_result = self._intelligent_title_generation(content, category_result)
            print(f"📋 タイトル生成: {title_result}")
            
            # 3. タグ生成（多層分析）
            tags_result = self._comprehensive_tag_generation(content, category_result)
            print(f"🏷️ タグ生成: {tags_result}")
            
            # 4. 関連ファイル検索
            relations_result = self._find_related_files(content, title_result['title'])
            print(f"🔗 関連分析: {relations_result}")
            
            # 5. 統合結果構築
            result = {
                'success': True,
                'category': category_result,
                'title': title_result,
                'tags': tags_result,
                'relations': relations_result,
                'preview_info': self._build_preview_info(category_result, title_result, tags_result, relations_result),
                'timestamp': datetime.now().isoformat()
            }
            
            print("✅ 統合分析完了!")
            return result
            
        except Exception as e:
            print(f"❌ 統合分析エラー: {e}")
            return {
                'success': False,
                'error': str(e),
                'category': {'name': 'general', 'confidence': 0.0},
                'title': {'title': 'エラー', 'method': 'error'},
                'tags': {'tags': ['#エラー'], 'count': 1},
                'relations': {'relations': [], 'count': 0}
            }
    
    def _enhanced_category_analysis(self, content: str) -> dict:
        """強化されたカテゴリ分析"""
        
        content_lower = content.lower()
        
        # 教育パターンマッチング（特別強化）
        education_patterns = [
            r'[ぁ-んー]+くん|[ぁ-んー]+さん|[ぁ-んー]+ちゃん',  # 生徒名
            r'わかる？|わかりますか？|理解できた？',  # 教師の確認
            r'そうですね|素晴らしい|残念|惜しい|正解|不正解',  # 評価
            r'考えて|思い出す|思い浮かべ|選びなさい|答えなさい',  # 指示
            r'例えば|仮に|場合|シーン|状況|場面',  # 設定
            r'ひっかけ|問題|テスト|授業|指導',  # 教育文脈
            r'聴覚|視覚|五感|体の部分|感覚',  # 感覚教育
        ]
        
        # パターンマッチングスコア
        pattern_scores = defaultdict(int)
        
        for pattern in education_patterns:
            if re.search(pattern, content):
                pattern_scores['education'] += 3  # 高スコア
        
        # キーワードマッチングスコア
        keyword_scores = defaultdict(int)
        
        for category, keywords in self.category_keywords.items():
            for keyword in keywords:
                if keyword in content_lower:
                    keyword_scores[category] += 1
        
        # 総合スコア計算
        total_scores = defaultdict(float)
        
        for category in self.category_keywords.keys():
            pattern_score = pattern_scores.get(category, 0)
            keyword_score = keyword_scores.get(category, 0)
            
            # 教育カテゴリは特別扱い
            if category == 'education':
                total_scores[category] = pattern_score * 2 + keyword_score
            else:
                total_scores[category] = pattern_score + keyword_score
        
        # 最高スコアのカテゴリを選択
        if total_scores:
            best_category = max(total_scores, key=total_scores.get)
            confidence = total_scores[best_category] / max(1, len(content.split()) * 0.1)
            confidence = min(1.0, confidence)  # 1.0を上限とする
        else:
            best_category = 'general'
            confidence = 0.1
        
        return {
            'name': best_category,
            'confidence': confidence,
            'scores': dict(total_scores),
            'pattern_matches': dict(pattern_scores),
            'keyword_matches': dict(keyword_scores)
        }
    
    def _intelligent_title_generation(self, content: str, category_result: dict) -> dict:
        """知的タイトル生成"""
        
        # 複数の手法を試行
        methods = []
        
        # 1. 主題パターン検出
        theme_title = self._extract_theme_title(content)
        if theme_title:
            methods.append({'method': 'theme_pattern', 'title': theme_title, 'score': 3.0})
        
        # 2. カテゴリ特化タイトル
        category_title = self._generate_category_specific_title(content, category_result['name'])
        if category_title:
            methods.append({'method': 'category_specific', 'title': category_title, 'score': 2.5})
        
        # 3. 重要語クラスタリング
        cluster_title = self._generate_cluster_title(content)
        if cluster_title:
            methods.append({'method': 'word_clustering', 'title': cluster_title, 'score': 2.0})
        
        # 4. 核心内容抽出
        core_title = self._extract_core_content_title(content)
        if core_title:
            methods.append({'method': 'core_content', 'title': core_title, 'score': 1.5})
        
        # 最高スコアの手法を選択
        if methods:
            best_method = max(methods, key=lambda x: x['score'])
            return {
                'title': best_method['title'],
                'method': best_method['method'],
                'alternatives': [m for m in methods if m != best_method],
                'confidence': best_method['score'] / 3.0
            }
        else:
            # フォールバック
            fallback_title = f"メモ_{datetime.now().strftime('%m%d_%H%M')}"
            return {
                'title': fallback_title,
                'method': 'fallback',
                'alternatives': [],
                'confidence': 0.1
            }
    
    def _extract_theme_title(self, content: str) -> str:
        """主題パターンからタイトル抽出"""
        
        patterns = [
            # 特定パターンを最優先
            r'(.{5,30})では「(.{5,25})」と「(.{5,25})」',  # 「〜では「A」と「B」」
            r'(.{5,30})では「(.{5,25})」',  # 「〜では「A」」
            r'(.{5,30})では『(.{5,25})』',  # 「〜では『A』」
            r'「(.{5,30})の(.{5,25})」',  # 「AのB」
            r'『(.{5,30})の(.{5,25})』',  # 『AのB』
            # 一般的なパターン
            r'(.{5,25})について[は話し説明考え解説]',
            r'(.{5,25})とは[^ぁ-ん]{0,10}',
            r'(.{5,25})を[考え説明解説検討分析]',
            r'(.{5,25})に関して',
            r'(.{5,25})における',
            r'重要なのは(.{5,25})',
            r'ポイントは(.{5,25})',
            r'「(.{5,30})」[とという]',
            r'『(.{5,30})』[とという]',
            # 最後に緩いパターン
            r'(.{5,25})の[問題課題効果方法手順解説説明]',
        ]
        
        for pattern in patterns:
            match = re.search(pattern, content)
            if match:
                # 複数のグループがある場合は最も意味のあるものを選択
                groups = match.groups()
                theme = None
                
                # 複数グループの処理
                if len(groups) == 3 and all(g for g in groups):
                    # 「AではBとC」パターン
                    first, second, third = groups[0].strip(), groups[1].strip(), groups[2].strip()
                    theme = f"{first}の{second}と{third}"
                    if len(theme) > 30:
                        theme = f"{first}の{second}"
                elif len(groups) == 2 and all(g for g in groups):
                    # 「AではB」または「AのB」パターン
                    first, second = groups[0].strip(), groups[1].strip()
                    if len(first) > 3 and len(second) > 3:
                        theme = f"{first}の{second}"
                        if len(theme) > 30:
                            theme = second if len(second) < len(first) else first
                    else:
                        theme = first if len(first) > len(second) else second
                else:
                    # 単一グループまたは他のパターン
                    for group in groups:
                        if group and len(group.strip()) > 2 and not self._is_meaningless_phrase(group.strip()):
                            theme = group.strip()
                            break
                
                if theme:
                    return self._clean_title_text(theme)
        
        return ""
    
    def _generate_category_specific_title(self, content: str, category: str) -> str:
        """カテゴリ特化タイトル生成"""
        
        if category == 'education':
            # 教育カテゴリの特殊処理
            if '対句法' in content and 'リズム' in content:
                return "対句法とリズム分析"
            elif '聴覚' in content and '五感' in content:
                return "聴覚と五感の学習"
            elif 'ひっかけ' in content and '問題' in content:
                return "ひっかけ問題の指導"
            elif re.search(r'[ぁ-んー]+くん', content):
                return "授業記録と生徒指導"
            elif '指導' in content:
                return "教育指導メモ"
            else:
                return "教育関連記録"
        
        elif category == 'tech':
            # 固有名詞（カタカナ・英語）を優先的に抽出
            katakana_entities = re.findall(r'[ア-ヶー]{3,10}', content)
            english_entities = re.findall(r'[A-Z][a-z]+|ChatGPT|Python|API|JavaScript|React|Vue|Node|Git|GitHub|Docker|AWS|Azure|GCP|Obsidian', content)
            tech_terms = re.findall(r'API|プログラミング|システム|アプリ|開発|技術', content, re.IGNORECASE)
            
            # 固有名詞を含むタイトルを生成
            entities = []
            if katakana_entities:
                # 一般語を除外
                common_katakana = {'アイデア', 'メモ', 'ファイル', 'フォルダ', 'ページ', 'サイト', 'システム', 'データ', 'ユーザー', 'サービス'}
                entities.extend([e for e in katakana_entities if e not in common_katakana])
            if english_entities:
                entities.extend(english_entities)
            
            if len(entities) >= 2:
                return f"{entities[0]}と{entities[1]}の開発"
            elif len(entities) == 1:
                if tech_terms:
                    return f"{entities[0]}{tech_terms[0]}"
                else:
                    return f"{entities[0]}開発メモ"
            elif tech_terms:
                return f"{tech_terms[0]}に関する技術メモ"
            else:
                return "技術関連メモ"
        
        elif category == 'business':
            # ビジネス固有名詞を抽出
            katakana_entities = re.findall(r'[ア-ヶー]{3,10}', content)
            english_entities = re.findall(r'[A-Z][a-z]+|Instagram|Twitter|Facebook|LinkedIn|YouTube|TikTok|Google|Amazon|Apple', content)
            biz_terms = re.findall(r'マーケティング|戦略|営業|集客|SEO|ビジネス', content, re.IGNORECASE)
            
            entities = []
            if katakana_entities:
                common_katakana = {'マーケティング', 'ビジネス', 'サービス', 'ユーザー', 'データ'}
                entities.extend([e for e in katakana_entities if e not in common_katakana])
            if english_entities:
                entities.extend(english_entities)
                
            if len(entities) >= 1:
                if biz_terms:
                    return f"{entities[0]}{biz_terms[0]}"
                else:
                    return f"{entities[0]}ビジネス戦略"
            elif biz_terms:
                return f"{biz_terms[0]}戦略メモ"
            else:
                return "ビジネス関連メモ"
        
        elif category == 'ideas':
            # アイデア系も固有名詞を含める
            katakana_entities = re.findall(r'[ア-ヶー]{3,10}', content)
            english_entities = re.findall(r'[A-Z][a-z]+', content)
            
            entities = []
            if katakana_entities:
                entities.extend([e for e in katakana_entities[:2]])
            if english_entities:
                entities.extend([e for e in english_entities[:2]])
                
            if entities:
                return f"{entities[0]}アイデア"
            else:
                return "アイデア・企画メモ"
        
        return ""
    
    def _generate_cluster_title(self, content: str) -> str:
        """重要語クラスタリングによるタイトル生成（固有名詞優先）"""
        
        # 固有名詞を最優先で抽出
        entities = []
        
        # カタカナ固有名詞
        katakana_entities = re.findall(r'[ア-ヶー]{3,10}', content)
        common_katakana = {'アイデア', 'メモ', 'ファイル', 'フォルダ', 'ページ', 'サイト', 'システム', 'データ', 'ユーザー', 'サービス', 'マーケティング', 'ビジネス'}
        entities.extend([e for e in katakana_entities if e not in common_katakana])
        
        # 英語固有名詞
        english_entities = re.findall(r'[A-Z][a-z]+|ChatGPT|Python|API|JavaScript|Obsidian|GitHub|Instagram|Twitter|Facebook|Google|Amazon|Apple', content)
        entities.extend(english_entities)
        
        # 重要な日本語語彙
        important_words = re.findall(r'[ぁ-んァ-ヶー一-龯]{2,8}', content)
        word_freq = Counter(important_words)
        
        # 代表的な語彙（頻出・専門用語・動作語）
        representative_words = []
        for word, freq in word_freq.items():
            if (freq >= 2 and len(word) > 2 and not self._is_common_word(word)) or \
               word in ['開発', '設計', '実装', '分析', '検討', '構築', '作成', '生成', '連携', '活用', '解釈', '理解', '指導', '学習', '授業', '記録']:
                representative_words.append(word)
        
        # タイトル構築の優先順位
        if len(entities) >= 2:
            return f"{entities[0]}と{entities[1]}"
        elif len(entities) == 1 and len(representative_words) >= 1:
            return f"{entities[0]}{representative_words[0]}"
        elif len(entities) == 1:
            return f"{entities[0]}について"
        elif len(representative_words) >= 2:
            return f"{representative_words[0]}と{representative_words[1]}"
        elif len(representative_words) == 1:
            return f"{representative_words[0]}に関して"
        
        return ""
    
    def _extract_core_content_title(self, content: str) -> str:
        """核心内容からタイトル抽出"""
        
        sentences = re.split(r'[。．！？\n]', content)
        
        # 導入文をスキップして核心部分を見つける
        for i, sentence in enumerate(sentences):
            sentence = sentence.strip()
            
            # 質問文や挨拶をスキップ
            if (len(sentence) > 15 and 
                not sentence.endswith('ですか？') and
                not sentence.endswith('だろうか？') and
                not sentence.startswith('このシーン') and
                not sentence.startswith('そうですね')):
                
                # 文の主要部分を抽出
                core_part = self._extract_sentence_core(sentence)
                if core_part:
                    return core_part
        
        return ""
    
    def _extract_sentence_core(self, sentence: str) -> str:
        """文の核心部分を抽出"""
        
        # 「〜は〜です」「〜が〜する」等のパターンから主語・述語を抽出
        patterns = [
            r'([ぁ-んァ-ヶー一-龯]{2,8})[はが]([^。]{5,20})',
            r'([ぁ-んァ-ヶー一-龯]{2,8})を([ぁ-んァ-ヶー一-龯]{2,8})',
            r'([ぁ-んァ-ヶー一-龯]{2,8})という([ぁ-んァ-ヶー一-龯]{2,8})'
        ]
        
        for pattern in patterns:
            match = re.search(pattern, sentence)
            if match:
                subject = match.group(1)
                predicate = match.group(2)
                if len(subject) > 2 and len(predicate) > 2:
                    return f"{subject}の{predicate[:6]}"
        
        # フォールバック：文の最初の重要語句
        words = re.findall(r'[ぁ-んァ-ヶー一-龯]{3,8}', sentence)
        important_words = [w for w in words if not self._is_common_word(w)]
        
        if important_words:
            return important_words[0]
        
        return ""
    
    def _comprehensive_tag_generation(self, content: str, category_result: dict) -> dict:
        """file-organizer式6層タグ生成システム"""
        try:
            category = category_result['name']
            tags = set()
            
            # Layer 1: 最優先 - 固有名詞・専門用語（重み: 3倍）
            try:
                priority_tags = self._extract_priority_entities(content, category)
                for tag in priority_tags:
                    tags.add(f"PRIORITY:{tag}")
            except:
                pass
            
            # Layer 2: カテゴリベースタグ（重み: 2倍）
            try:
                category_tags = self._get_category_base_tags(category)
                for tag in category_tags:
                    keywords = self._get_category_keywords(category, tag)
                    if any(keyword in content for keyword in keywords):
                        tags.add(f"CATEGORY:{tag}")
            except:
                pass
            
            # Layer 3: アクション・動作タグ
            try:
                action_tags = self._extract_action_tags_enhanced(content)
                tags.update(action_tags)
            except:
                pass
            
            # Layer 4: 感情・トーンタグ
            try:
                emotion_tags = self._extract_emotion_tags_enhanced(content)
                tags.update(emotion_tags)
            except:
                pass
            
            # Layer 5: コンテンツタイプタグ
            try:
                content_type_tags = self._extract_content_type_tags_enhanced(content)
                tags.update(content_type_tags)
            except:
                pass
            
            # Layer 6: 頻出語タグ（2回以上出現）
            try:
                frequent_tags = self._extract_frequent_terms_enhanced(content)
                tags.update(frequent_tags)
            except:
                pass
            
            # 優先度に基づいてタグをソート・選択
            final_tags = self._prioritize_and_select_tags(tags, content)
            
            # 空の場合は従来方式にフォールバック
            if not final_tags:
                fallback_tags = self._extract_priority_terms(content, category)
                final_tags = [f"#{tag}" for tag in fallback_tags]
            
            prioritized_tags = final_tags[:12]  # 最大12個
            
            return {
                'tags': prioritized_tags,
                'count': len(prioritized_tags),
                'layer_info': '6-layer hierarchical system',
                'method': 'file-organizer_enhanced'
            }
            
        except Exception as e:
            print(f"⚠️ タグ生成エラー、従来方式を使用: {e}")
            # エラー時は従来の方式にフォールバック
            fallback_tags = self._extract_priority_terms(content, category)
            return {
                'tags': [f"#{tag}" for tag in fallback_tags],
                'count': len(fallback_tags),
                'method': 'fallback'
            }
    
    def _extract_priority_entities(self, content: str, category: str) -> set:
        """Layer 1: 最優先固有名詞・専門用語抽出"""
        entities = set()
        
        if category == 'education':
            # 学校名（最優先）
            school_patterns = {
                '開成': ['開成中学', '開成'],
                '麻布': ['麻布中学', '麻布'],
                '駒東': ['駒場東邦', '駒東'],
                '桜蔭': ['桜蔭中学', '桜蔭'],
                '女子学院': ['女子学院', 'JG'],
                '雙葉': ['雙葉中学', '雙葉'],
                '筑駒': ['筑波大駒場', '筑駒'],
                '渋幕': ['渋谷幕張', '渋幕'],
                '武蔵': ['武蔵中学', '武蔵'],
                'SAPIX': ['サピックス', 'SAPIX', 'サピ']
            }
            for school, patterns in school_patterns.items():
                if any(pattern in content for pattern in patterns):
                    entities.add(school)
                    
        elif category == 'tech':
            # 技術固有名詞（最優先）
            tech_entities = {
                'Claude': ['Claude', 'claude'],
                'ChatGPT': ['ChatGPT', 'chatgpt', 'Chat GPT'],
                'GitHub': ['GitHub', 'github', 'Github'],
                'Python': ['Python', 'python'],
                'JavaScript': ['JavaScript', 'javascript', 'JS'],
                'Cursor': ['Cursor', 'cursor'],
                'Obsidian': ['Obsidian', 'obsidian'],
                'MCP': ['MCP', 'mcp'],
                'Supabase': ['Supabase', 'supabase']
            }
            for entity, patterns in tech_entities.items():
                if any(pattern in content for pattern in patterns):
                    entities.add(entity)
                    
        elif category == 'media':
            # メディア・SNS固有名詞（最優先）
            media_entities = {
                '西村創一朗': ['西村創一朗', '西村'],
                '西川将史': ['西川将史', '西川'],
                '梶谷健人': ['梶谷健人', '梶谷'],
                'X分析': ['X分析', 'Ｘ分析'],
                'SNS分析': ['SNS分析', 'ポスト分析', 'アカウント分析'],
                'エンゲージメント': ['エンゲージメント', 'いいね', 'リポスト']
            }
            for entity, patterns in media_entities.items():
                if any(pattern in content for pattern in patterns):
                    entities.add(entity)
        
        # 一般的な重要固有名詞
        general_entities = re.findall(r'\\b[A-Z][a-zA-Z]{3,15}\\b', content)
        for entity in general_entities:
            if len(entity) >= 4 and not re.match(r'^[A-Z]{3,4}$', entity):
                entities.add(entity)
        
        return entities
    
    def _get_category_base_tags(self, category: str) -> list:
        """Layer 2: カテゴリベースタグ定義"""
        category_base_tags = {
            'education': ['中学受験', '国語指導', '過去問分析', '入試対策', '読解指導', '表現指導'],
            'tech': ['プログラミング', 'AI開発', 'システム構築', 'API連携', 'データ分析', 'プロンプトエンジニアリング'],
            'media': ['SNS戦略', 'SNS運用', 'コンテンツ分析', 'インフルエンサー分析', 'エンゲージメント分析'],
            'business': ['ビジネス戦略', 'マーケティング戦略', '売上分析', '顧客獲得', 'ブランディング'],
            'ideas': ['アイデア創出', '企画立案', 'ブレインストーミング'],
            'general': ['メモ', '記録', '整理']
        }
        return category_base_tags.get(category, [])
    
    def _get_category_keywords(self, category: str, tag: str) -> list:
        """カテゴリ・タグ別キーワード取得"""
        keyword_map = {
            'education': {
                '中学受験': ['中学受験', '受験', '入試', '合格'],
                '国語指導': ['国語', '読解', '表現', '文章'],
                '過去問分析': ['過去問', '出題傾向', '分析'],
            },
            'tech': {
                'プログラミング': ['プログラミング', 'コード', '開発'],
                'AI開発': ['AI', '機械学習', 'Claude', 'ChatGPT'],
                'API連携': ['API', '連携', '接続'],
            },
            'media': {
                'SNS戦略': ['SNS', '戦略', 'X', 'Twitter'],
                'エンゲージメント分析': ['エンゲージメント', 'いいね', 'フォロワー'],
            }
        }
        return keyword_map.get(category, {}).get(tag, [])
    
    def _extract_action_tags_enhanced(self, content: str) -> set:
        """Layer 3: アクション・動作タグ抽出"""
        actions = set()
        action_patterns = {
            '学習': ['学習', '勉強', '習得', '理解'],
            '分析': ['分析', '解析', '調査', '検証'],
            '記録': ['記録', 'メモ', '保存', '整理'],
            '計画': ['計画', '戦略', '設計', '企画'],
            '実行': ['実行', '実施', '実装', '開発'],
            '評価': ['評価', '検討', '判断', '確認']
        }
        
        for action, keywords in action_patterns.items():
            if any(keyword in content for keyword in keywords):
                actions.add(action)
        
        return actions
    
    def _extract_emotion_tags_enhanced(self, content: str) -> set:
        """Layer 4: 感情・トーンタグ抽出"""
        emotions = set()
        emotion_patterns = {
            '重要': ['重要', '大切', '必須', '!', '！'],
            '疑問': ['？', '?', 'どう', 'なぜ', 'どのように'],
            'ポジティブ': ['素晴らしい', '良い', '成功', '改善'],
            '課題': ['課題', '問題', '改善', '対策'],
            '発見': ['発見', '気づき', '学び', 'ひらめき']
        }
        
        for emotion, keywords in emotion_patterns.items():
            if any(keyword in content for keyword in keywords):
                emotions.add(emotion)
        
        return emotions
    
    def _extract_content_type_tags_enhanced(self, content: str) -> set:
        """Layer 5: コンテンツタイプタグ抽出"""
        content_types = set()
        type_patterns = {
            'アイデア': ['アイデア', '案', '提案', '思いつき'],
            'レポート': ['結果', '報告', 'レポート', 'まとめ'],
            'メモ': ['メモ', '覚書', '備忘録'],
            'ツール': ['ツール', '道具', 'アプリ', 'サービス'],
            'プロセス': ['手順', 'ステップ', 'プロセス', '方法']
        }
        
        for content_type, keywords in type_patterns.items():
            if any(keyword in content for keyword in keywords):
                content_types.add(content_type)
        
        return content_types
    
    def _extract_frequent_terms_enhanced(self, content: str) -> set:
        """Layer 6: 頻出語タグ抽出（2回以上出現）"""
        frequent_terms = set()
        
        # 日本語の意味のある語（3文字以上）
        japanese_words = re.findall(r'[ぁ-んァ-ヶー一-龯]{3,8}', content)
        word_counts = Counter(japanese_words)
        
        for word, count in word_counts.items():
            if (count >= 2 and len(word) >= 3 and 
                not re.match(r'^[あいうえおかきくけこさしすせそたちつてとなにぬねのはひふへほまみむめもやゆよらりるれろわをん]+$', word)):
                frequent_terms.add(word)
        
        return frequent_terms
    
    def _prioritize_and_select_tags(self, tags: set, content: str) -> list:
        """優先度に基づいてタグをソート・選択"""
        prioritized_tags = []
        
        # 優先度順でタグを処理
        priority_order = ['PRIORITY:', 'CATEGORY:', '']
        
        for prefix in priority_order:
            matching_tags = [tag for tag in tags if tag.startswith(prefix)]
            
            # プレフィックスを除去してクリーンなタグに
            clean_tags = []
            for tag in matching_tags:
                clean_tag = tag.replace('PRIORITY:', '').replace('CATEGORY:', '')
                if len(clean_tag) >= 2:
                    clean_tags.append(f"#{clean_tag}")
            
            prioritized_tags.extend(clean_tags)
        
        # 重複除去して順序保持
        seen = set()
        final_tags = []
        for tag in prioritized_tags:
            if tag not in seen:
                seen.add(tag)
                final_tags.append(tag)
        
        return final_tags
    
    def _extract_priority_terms(self, content: str, category: str) -> set:
        """カテゴリ別の最優先固有名詞抽出（フォールバック用）"""
        tags = set()
        
        if category == 'education':
            # 学校名を最優先で抽出
            school_names = ['開成', '麻布', '駒東', '桜蔭', '女子学院', '雙葉', '筑駒', '渋幕', '渋渋', '武蔵', '海城']
            for school in school_names:
                if school in content:
                    tags.add(school)
            
            # 重要な教育用語
            key_terms = ['中学受験', '国語', '過去問', '入試', '分析', '傾向', '対策', 'SAPIX', 'サピックス', '四谷大塚', '日能研']
            for term in key_terms:
                if term in content:
                    tags.add(term)
                    
        elif category == 'tech':
            # 重要な技術用語
            key_tech = ['GitHub', 'Git', 'Python', 'JavaScript', 'API', 'ChatGPT', 'Claude', 'AI', 'システム', 'アプリ', 'プログラミング', '開発', 'トークン', '認証']
            for term in key_tech:
                if term in content or term.lower() in content.lower():
                    tags.add(term)
                    
        elif category == 'media':
            # 重要なメディア・SNS用語
            key_media = ['X', 'Twitter', 'SNS', 'アカウント', 'ポスト', 'フォロワー', 'インフルエンサー', '分析', '西村創一朗', '西川将史', '梶谷健人', 'エンゲージメント']
            for term in key_media:
                if term in content:
                    tags.add(term)
        
        return tags

    def _find_related_files(self, content: str, title: str) -> dict:
        """file-organizer式強化関連ファイル検索"""
        
        try:
            vault_path = Path(self.obsidian_path)
            relations = []
            
            # 既存のmarkdownファイルを検索
            md_files = list(vault_path.rglob('*.md'))
            
            for md_file in md_files:
                try:
                    # ファイル内容を読み込み
                    with open(md_file, 'r', encoding='utf-8') as f:
                        file_content = f.read()
                    
                    # タイトルを抽出
                    file_title = md_file.stem
                    
                    # 関連度を計算（階層的アプローチ）
                    relation_score = self._calculate_hierarchical_relation_score(
                        content, file_content, title, file_title
                    )
                    
                    # カテゴリ別の厳格な閾値設定（関連度向上）
                    threshold = self._get_relation_threshold(title, file_title)
                    
                    if relation_score > threshold:
                        # 星評価を計算
                        star_rating = self._calculate_star_rating(relation_score)
                        
                        relations.append({
                            'file_path': str(md_file),
                            'file_name': file_title,
                            'score': relation_score,
                            'star_rating': star_rating,
                            'relation_type': self._determine_relation_type_enhanced(content, file_content),
                            'preview': file_content[:100] + "..." if len(file_content) > 100 else file_content
                        })
                
                except Exception as e:
                    continue
            
            # スコア順でソート
            relations.sort(key=lambda x: x['score'], reverse=True)
            
            return {
                'relations': relations[:3],  # 上位3件（精度向上）
                'count': len(relations),
                'total_files_checked': len(md_files)
            }
            
        except Exception as e:
            return {
                'relations': [],
                'count': 0,
                'error': str(e)
            }
    
    def _calculate_hierarchical_relation_score(self, content1: str, content2: str, title1: str, title2: str) -> float:
        """file-organizer式階層的関連度スコア計算"""
        max_score = 0.0
        
        # 1. タイトル類似度（最重要）
        title_similarity = self._calculate_title_similarity(title1, title2)
        if title_similarity > 0.3:  # タイトル類似度閾値
            max_score = max(max_score, title_similarity * 1.5)  # 重み付け
        
        # 2. タグ類似度
        tags1 = self._extract_simple_tags(content1)
        tags2 = self._extract_simple_tags(content2)
        tag_similarity = self._calculate_jaccard_similarity(tags1, tags2)
        if tag_similarity > 0.2:
            max_score = max(max_score, tag_similarity * 1.2)
        
        # 3. コンテンツ類似度
        jaccard_similarity = self._calculate_content_jaccard_similarity(content1, content2)
        
        # カテゴリ別の厳格な閾値設定（関連度向上）
        if self._is_sns_analysis_file(title1) and self._is_sns_analysis_file(title2):
            if jaccard_similarity > 0.15:  # SNS分析同士：より厳格
                max_score = max(max_score, jaccard_similarity)
        elif self._is_tech_file(title1) and self._is_tech_file(title2):
            if jaccard_similarity > 0.12:  # Tech系同士：より厳格  
                max_score = max(max_score, jaccard_similarity)
        else:
            if jaccard_similarity > 0.18:  # 一般ファイル：より厳格
                max_score = max(max_score, jaccard_similarity)
        
        return max_score
    
    def _calculate_title_similarity(self, title1: str, title2: str) -> float:
        """タイトル類似度計算"""
        words1 = set(re.findall(r'[ぁ-んァ-ヶー一-龯A-Za-z]{2,}', title1.lower()))
        words2 = set(re.findall(r'[ぁ-んァ-ヶー一-龯A-Za-z]{2,}', title2.lower()))
        
        # 一般語除外
        common_words = {'について', 'に関して', 'の方法', 'について', 'まとめ', 'メモ'}
        words1 = words1 - common_words
        words2 = words2 - common_words
        
        if not words1 or not words2:
            return 0.0
        
        intersection = len(words1 & words2)
        union = len(words1 | words2)
        return intersection / union if union > 0 else 0.0
    
    def _extract_simple_tags(self, content: str) -> set:
        """簡易タグ抽出"""
        words = re.findall(r'[ぁ-んァ-ヶー一-龯]{3,8}', content)
        word_counts = Counter(words)
        return {word for word, count in word_counts.items() if count >= 2}
    
    def _calculate_jaccard_similarity(self, set1: set, set2: set) -> float:
        """Jaccard係数計算"""
        if not set1 or not set2:
            return 0.0
        intersection = len(set1 & set2)
        union = len(set1 | set2)
        return intersection / union if union > 0 else 0.0
    
    def _calculate_content_jaccard_similarity(self, content1: str, content2: str) -> float:
        """コンテンツのJaccard類似度計算"""
        words1 = set(re.findall(r'[ぁ-んァ-ヶー一-龯]{3,}', content1.lower()))
        words2 = set(re.findall(r'[ぁ-んァ-ヶー一-龯]{3,}', content2.lower()))
        
        # 一般的すぎる語を除外
        common_words = {'について', 'に関して', 'ができる', 'である', 'ている', 'ました', 'します', 'された'}
        words1 = words1 - common_words
        words2 = words2 - common_words
        
        return self._calculate_jaccard_similarity(words1, words2)
    
    def _is_sns_analysis_file(self, title: str) -> bool:
        """SNS分析ファイル判定"""
        sns_keywords = ['X投稿', 'SNS', 'アカウント分析', 'ポスト分析', 'フォロワー', 'インフルエンサー']
        return any(keyword in title for keyword in sns_keywords)
    
    def _is_tech_file(self, title: str) -> bool:
        """技術ファイル判定"""
        tech_keywords = ['API', 'プログラミング', 'システム', 'GitHub', 'Python', 'AI', 'Claude', 'コード']
        return any(keyword in title for keyword in tech_keywords)
    
    def _get_relation_threshold(self, title1: str, title2: str) -> float:
        """カテゴリ別関連閾値取得"""
        if self._is_sns_analysis_file(title1) and self._is_sns_analysis_file(title2):
            return 0.15  # SNS分析同士：厳格
        elif self._is_tech_file(title1) and self._is_tech_file(title2):
            return 0.12  # Tech系同士：厳格
        else:
            return 0.18  # 一般：より厳格
    
    def _calculate_star_rating(self, score: float) -> str:
        """スコアから星評価を計算"""
        if score >= 0.7:
            return "★★★★★"
        elif score >= 0.5:
            return "★★★★"
        elif score >= 0.3:
            return "★★★"
        elif score >= 0.2:
            return "★★"
        else:
            return "★"
    
    def _determine_relation_type_enhanced(self, content1: str, content2: str) -> str:
        """関連タイプを判定"""
        
        # 簡易的な関連タイプ判定
        if any(word in content1 and word in content2 for word in ['教育', '指導', '授業']):
            return 'educational'
        elif any(word in content1 and word in content2 for word in ['技術', 'API', 'システム']):
            return 'technical'
        elif any(word in content1 and word in content2 for word in ['ビジネス', '戦略', 'マーケティング']):
            return 'business'
        else:
            return 'general'
    
    def _build_preview_info(self, category_result: dict, title_result: dict, 
                           tags_result: dict, relations_result: dict) -> dict:
        """プレビュー表示用情報構築"""
        
        return {
            'category_display': f"{category_result['name']} (信頼度: {category_result['confidence']:.1%})",
            'title_display': title_result['title'],
            'tags_display': ' '.join(tags_result['tags'][:5]),  # 最初の5個
            'relations_display': f"{relations_result['count']}件の関連ファイル",
            'full_analysis': {
                'category_scores': category_result.get('scores', {}),
                'title_alternatives': title_result.get('alternatives', []),
                'tag_sources': tags_result.get('sources', {}),
                'relation_details': relations_result.get('relations', [])
            }
        }
    
    # ユーティリティメソッド群
    def _is_meaningless_phrase(self, phrase: str) -> bool:
        """無意味なフレーズかチェック"""
        meaningless = ['このシーン', 'そうですね', 'わかる', 'ですね', 'ます', 'です']
        return any(m in phrase for m in meaningless)
    
    def _clean_title_text(self, text: str) -> str:
        """タイトルテキストをクリーンアップ"""
        text = re.sub(r'[はがをにでと]$', '', text)
        text = re.sub(r'について$|に関して$|では$', '', text)
        # 引用符の処理（途中で切れたものも含む）
        text = re.sub(r'^[「『]', '', text)
        text = re.sub(r'[」』]$', '', text)
        text = re.sub(r'」と「', 'と', text)  # 「A」と「B」→AとB
        text = re.sub(r'』と『', 'と', text)  # 『A』と『B』→AとB
        # 適切な長さに調整（30文字まで）
        cleaned = text.strip()
        if len(cleaned) > 30:
            cleaned = cleaned[:27] + "..."
        return cleaned
    
    def _is_common_word(self, word: str) -> bool:
        """一般的な語かチェック"""
        common = {'ある', 'いる', 'する', 'なる', 'です', 'ます', 'この', 'その', 'あの', 'それ', 'これ', 'あれ'}
        return word in common
    
    def _get_category_base_tags(self, category: str) -> list:
        """カテゴリベースタグ"""
        base_tags = {
            'education': ['#教育', '#学習', '#指導'],
            'tech': ['#Tech', '#技術', '#開発'],
            'business': ['#ビジネス', '#戦略', '#マーケティング'],
            'ideas': ['#アイデア', '#企画', '#創作'],
            'general': ['#メモ', '#記録']
        }
        return base_tags.get(category, ['#メモ'])
    
    def _detect_content_type(self, content: str) -> str:
        """コンテンツタイプ検出"""
        if re.search(r'https?://', content):
            return 'web_reference'
        elif re.search(r'アイデア|企画|提案', content):
            return 'idea'
        elif re.search(r'授業|指導|学習', content):
            return 'learning'
        elif re.search(r'TODO|タスク|やること', content):
            return 'todo'
        else:
            return 'general'
    
    def _get_content_type_tags(self, content_type: str) -> list:
        """コンテンツタイプ別タグ"""
        type_tags = {
            'web_reference': ['#参考資料', '#Web記事'],
            'idea': ['#発想', '#思考'],
            'learning': ['#学習記録', '#授業ノート'],
            'todo': ['#TODO', '#タスク'],
            'general': []
        }
        return type_tags.get(content_type, [])
    
    def _extract_frequent_word_tags(self, content: str) -> list:
        """頻出語タグ抽出"""
        words = re.findall(r'[ぁ-んァ-ヶー一-龯]{2,8}', content)
        word_freq = Counter(words)
        
        frequent_tags = []
        for word, freq in word_freq.items():
            if freq >= 2 and len(word) > 2 and not self._is_common_word(word):
                frequent_tags.append(f"#{word}")
        
        return frequent_tags[:3]
    
    def _extract_emotion_tags(self, content: str) -> list:
        """感情タグ抽出"""
        emotion_patterns = {
            '#ポジティブ': r'素晴らしい|いい|良い|楽し|嬉し',
            '#ネガティブ': r'困った|悪い|残念|惜しい',
            '#疑問': r'なぜ|どうして|わからない|\?|？',
            '#重要': r'重要|大切|ポイント|核心'
        }
        
        tags = []
        for tag, pattern in emotion_patterns.items():
            if re.search(pattern, content):
                tags.append(tag)
        return tags
    
    def _extract_action_tags(self, content: str) -> list:
        """アクションタグ抽出"""
        action_patterns = {
            '#学習': r'学ぶ|覚える|理解|習得',
            '#分析': r'分析|検討|調査|考察',
            '#記録': r'記録|保存|メモ|ノート'
        }
        
        tags = []
        for tag, pattern in action_patterns.items():
            if re.search(pattern, content):
                tags.append(tag)
        return tags
    
    def _extract_entity_tags(self, content: str) -> list:
        """固有名詞タグ抽出"""
        entities = []
        
        # 英語固有名詞
        english_entities = re.findall(r'[A-Z][a-z]+|ChatGPT|Python|API|JavaScript|React|Vue|Node|Git|GitHub|Docker|AWS|Azure|GCP', content)
        entities.extend(english_entities)
        
        # カタカナ固有名詞（3文字以上）
        katakana_entities = re.findall(r'[ア-ヶー]{3,10}', content)
        # よくある一般語を除外
        common_katakana = {'アイデア', 'メモ', 'ファイル', 'フォルダ', 'ページ', 'サイト', 'システム', 'データ', 'ユーザー', 'サービス'}
        katakana_entities = [e for e in katakana_entities if e not in common_katakana]
        entities.extend(katakana_entities)
        
        # 重複除去して最大5個
        unique_entities = list(dict.fromkeys(entities))[:5]
        return [f"#{entity}" for entity in unique_entities]
    
    def _prioritize_tags(self, tags: list, content: str, sources: dict) -> list:
        """タグの優先順位付け"""
        tag_scores = {}
        
        for tag in tags:
            score = 1.0
            
            # ソースによる重み付け
            source = sources.get(tag, 'unknown')
            if source == 'category':
                score += 2.0
            elif source == 'frequent_words':
                score += 1.0
            elif source == 'emotion':
                score += 0.5
            
            # 出現頻度による重み付け
            tag_word = tag.replace('#', '')
            frequency = content.lower().count(tag_word.lower())
            score += frequency * 0.3
            
            tag_scores[tag] = score
        
        # スコア順でソート
        return sorted(tag_scores.keys(), key=lambda x: tag_scores[x], reverse=True)


    def save_memo(self, content: str) -> dict:
        """メモを実際に保存"""
        try:
            # プレビュー分析を再実行
            analysis = self.preview_analysis(content)
            
            if not analysis['success']:
                return analysis
            
            # ファイル保存
            file_path = self._save_memo_file(
                analysis['title']['title'], 
                content, 
                analysis['category']['name'],
                analysis['tags']['tags'],
                analysis['relations']['relations']
            )
            
            # Obsidian [[]] リンクを追加
            if analysis['relations']['relations']:
                self._add_obsidian_links(str(file_path), analysis['relations']['relations'])
            
            return {
                'success': True,
                'file_path': str(file_path),
                'title': analysis['title']['title'],
                'category': analysis['category']['name'],
                'tags_count': len(analysis['tags']['tags']),
                'relations_count': len(analysis['relations']['relations'])
            }
            
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def _save_memo_file(self, title: str, content: str, category: str, tags: list, relations: list) -> Path:
        """メモファイルを保存"""
        
        # ディレクトリ設定
        folder_name = self.category_folders.get(category, '4_General')
        save_dir = Path(self.obsidian_path) / self.inbox_path / folder_name
        save_dir.mkdir(parents=True, exist_ok=True)
        
        # ファイル名生成
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        safe_title = re.sub(r'[<>:"/\\|?*]', '', title)
        safe_title = re.sub(r'\s+', '_', safe_title)
        filename = f"{timestamp}_{safe_title}.md"
        
        # ファイルパス
        file_path = save_dir / filename
        
        # ファイル内容構築
        file_content = self._build_markdown_content(title, content, category, tags, relations)
        
        # ファイル保存
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(file_content)
        
        return file_path
    
    def _build_markdown_content(self, title: str, content: str, category: str, tags: list, relations: list) -> str:
        """Markdownファイル内容を構築"""
        
        lines = []
        
        # YAMLフロントマター
        lines.append('---')
        lines.append(f'title: "{title}"')
        lines.append(f'category: {category}')
        lines.append(f'tags: {json.dumps(tags, ensure_ascii=False)}')
        lines.append(f'created: {datetime.now().isoformat()}')
        lines.append('---')
        lines.append('')
        
        # タイトル
        lines.append(f'# {title}')
        lines.append('')
        
        # タグ表示
        if tags:
            lines.append(f'**タグ**: {" ".join(tags)}')
            lines.append('')
        
        # 関連ファイル
        if relations:
            lines.append('## 関連ファイル')
            lines.append('')
            for relation in relations:
                score_pct = int(relation['score'] * 100)
                lines.append(f'- [[{relation["file_name"]}]] - {relation["relation_type"]} (類似度: {score_pct}%)')
            lines.append('')
        
        # メイン内容
        lines.append('## 内容')
        lines.append('')
        lines.append(content)
        
        return '\n'.join(lines)
    
    def _add_obsidian_links(self, target_file_path: str, related_files: list):
        """Obsidianファイルに相互リンクを追加"""
        try:
            target_path = Path(target_file_path)
            
            if not target_path.exists():
                return
            
            # 既存の内容を読み込み
            with open(target_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # 関連ファイルセクションを追加/更新
            updated_content = self._add_new_links_section(content, related_files)
            
            # ファイルに書き戻し
            with open(target_path, 'w', encoding='utf-8') as f:
                f.write(updated_content)
            
            print(f"📎 {target_path.name}に関連リンクを追加")
            
            # 関連ファイル側にも逆リンクを追加
            self._add_reverse_links(target_path, related_files)
            
        except Exception as e:
            print(f"⚠️ リンク追加エラー: {e}")
    
    def _add_new_links_section(self, content: str, related_files: list) -> str:
        """新しい関連ファイルセクションを追加"""
        
        # 既存の関連ファイルセクションを削除
        content = re.sub(r'\n\n## 関連ファイル\n\n.*?(?=\n\n##|\n\n---|$)', '', content, flags=re.DOTALL)
        content = re.sub(r'\n\n## 関連ファイル\n\n.*?$', '', content, flags=re.DOTALL)
        
        if not related_files:
            return content
        
        # 新しい関連ファイルセクションを構築
        links_section = "\n\n## 関連ファイル\n\n"
        
        for rel_file in related_files:
            file_name = rel_file['file_name']
            star_rating = rel_file.get('star_rating', '★★★')
            
            # 関連タイプに基づいてコメントを追加
            relation_type = rel_file.get('relation_type', 'general')
            if relation_type == 'educational':
                comment = '(教育関連)'
            elif relation_type == 'technical':
                comment = '(技術関連)'
            elif relation_type == 'business':
                comment = '(ビジネス関連)'
            elif relation_type == 'media':
                comment = '(メディア関連)'
            else:
                comment = '(相互リンク)'
            
            links_section += f"- [[{file_name}]] {star_rating} {comment}\n"
        
        return content + links_section
    
    def _add_reverse_links(self, source_file: Path, related_files: list):
        """関連ファイル側に逆リンクを追加"""
        source_name = source_file.stem
        
        for rel_file in related_files:
            try:
                rel_file_path = Path(rel_file['file_path'])
                
                if not rel_file_path.exists():
                    continue
                
                # 関連ファイルの内容を読み込み
                with open(rel_file_path, 'r', encoding='utf-8') as f:
                    rel_content = f.read()
                
                # 既に相互リンクがあるかチェック
                if f"[[{source_name}]]" in rel_content:
                    continue
                
                # 関連ファイルセクションがあるかチェック
                if "## 関連ファイル" in rel_content:
                    # 既存のセクションに追加
                    star_rating = rel_file.get('star_rating', '★★★')
                    new_link = f"- [[{source_name}]] {star_rating} (相互リンク)\n"
                    
                    # 関連ファイルセクションの最後に追加
                    rel_content = re.sub(
                        r'(## 関連ファイル\n\n(?:.*\n)*)',
                        r'\1' + new_link,
                        rel_content
                    )
                else:
                    # 新しいセクションを作成
                    star_rating = rel_file.get('star_rating', '★★★')
                    new_section = f"\n\n## 関連ファイル\n\n- [[{source_name}]] {star_rating} (相互リンク)\n"
                    rel_content += new_section
                
                # ファイルに書き戻し
                with open(rel_file_path, 'w', encoding='utf-8') as f:
                    f.write(rel_content)
                
                print(f"📎 {rel_file_path.name}に逆リンクを追加")
                
            except Exception as e:
                print(f"⚠️ 逆リンク追加エラー ({rel_file['file_name']}): {e}")
                continue


def main():
    """メイン実行関数"""
    
    if len(sys.argv) < 3:
        print("使用方法: python3 preview_enhanced_memo.py [preview|save] <content>")
        return
    
    command = sys.argv[1]
    memo_content = " ".join(sys.argv[2:])
    
    if not memo_content.strip():
        print("❌ メモ内容が空です")
        return
    
    processor = IntegratedMemoProcessor()
    
    if command == "preview":
        # プレビュー分析実行
        result = processor.preview_analysis(memo_content)
        
        # AppleScript用の単純な形式で出力
        print("RESULT_START")
        print(f"TITLE:{result['title']['title']}")
        print(f"CATEGORY:{result['category']['name']}")
        
        # タグを単純な形式で出力
        tags_list = result['tags']['tags']
        tags_str = ",".join(tags_list) if tags_list else "なし"
        print(f"TAGS:{tags_str}")
        
        # 関連ファイルを単純な形式で出力
        relations_list = result['relations']['relations']
        if relations_list:
            relation_names = [rel['file_name'] for rel in relations_list[:3]]
            relations_str = f"{len(relations_list)}件:" + ",".join(relation_names)
        else:
            relations_str = "なし"
        print(f"RELATIONS:{relations_str}")
        print("RESULT_END")
        
        # デバッグ用にJSON形式も出力
        print("JSON_START")
        print(json.dumps(result, ensure_ascii=False, indent=2))
        print("JSON_END")
        
    elif command == "save":
        # 実際の保存処理
        result = processor.save_memo(memo_content)
        
        if result['success']:
            print(f"✅ メモ保存完了!")
            print(f"📋 タイトル: {result['title']}")
            print(f"📂 カテゴリ: {result['category']}")
            print(f"🏷️ タグ数: {result['tags_count']}")
            print(f"🔗 関連数: {result['relations_count']}")
            print(f"💾 ファイル: {Path(result['file_path']).name}")
        else:
            print(f"❌ 保存エラー: {result['error']}")
    
    else:
        print("❌ 不明なコマンド。'preview' または 'save' を指定してください。")


if __name__ == "__main__":
    main()