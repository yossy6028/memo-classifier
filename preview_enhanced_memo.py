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

# Ultrathinking統合
try:
    from ultrathinking_analyzer import UltrathinkingAnalyzer
    ULTRATHINKING_AVAILABLE = True
    print("✅ Ultrathinking統合モード有効")
except ImportError:
    ULTRATHINKING_AVAILABLE = False
    print("⚠️ 通常モードで動作（Ultrathinking無効）")


class IntegratedMemoProcessor:
    """統合メモプロセッサー（プレビュー対応）"""
    
    def __init__(self):
        # 基本設定
        self.obsidian_path = "/Users/yoshiikatsuhiko/Library/Mobile Documents/iCloud~md~obsidian/Documents"
        self.inbox_path = "02_Inbox"
        
        # 編集された分析結果を保持
        self._last_edited_analysis = None
        
        # 音声入力用カタカナ→英語変換辞書
        self.katakana_to_english = {
            # 技術系
            'チャットGPT': 'ChatGPT',
            'チャットジーピーティー': 'ChatGPT',
            'ちゃっとGPT': 'ChatGPT',
            'オブシディアン': 'Obsidian',
            'カーソル': 'Cursor',
            'パイソン': 'Python',
            'ジャバスクリプト': 'JavaScript',
            'ギットハブ': 'GitHub',
            'ギット': 'Git',
            'エーアイ': 'AI',
            'エーピーアイ': 'API',
            'ディーエックス': 'DX',
            'デジタルトランスフォーメーション': 'DX',
            # ビジネス系
            'クライアント': 'Client',
            'プロジェクト': 'Project',
            'コンサル': 'Consulting',
            'コンサルティング': 'Consulting',
            'アプローチ': 'Approach',
            'マーケティング': 'Marketing',
            'ミーティング': 'Meeting',
            'アドバンスド': 'Advanced',
            'ボイスモード': 'Voice Mode',
            # SNS系
            'ツイッター': 'Twitter',
            'エックス': 'X',
            'フェイスブック': 'Facebook',
            'インスタグラム': 'Instagram',
            'リンクトイン': 'LinkedIn',
            # 音楽系
            'ディミニッシュ': 'Diminished',
            'セブンス': '7th',
            'コード': 'Chord',
            'スケール': 'Scale',
            'メジャー': 'Major',
            'マイナー': 'Minor'
        }
        
        # カテゴリマッピング（実際のObsidianフォルダ構造に合わせて修正）
        self.category_folders = {
            'education': 'Education',
            'tech': 'Tech', 
            'business': 'Consulting',  # businessカテゴリはConsultingフォルダに
            'ideas': 'Others',  # ideasカテゴリはOthersフォルダに
            'music': 'Music',
            'media': 'Media',  # mediaカテゴリを追加
            'general': 'Others',
            'kindle': 'kindle',  # 小文字のまま
            'readwise': 'Others'  # readwiseはOthersに統合
        }
        
        # 強化されたカテゴリ判定キーワード
        self.category_keywords = {
            'music': [
                # 基本音楽理論
                'コード', 'スケール', 'ディミニッシュ', 'ハーモニー', '音階', '楽理',
                # コード種類
                'マイナーコード', 'メジャーコード', 'セブンスコード', '7thコード', 'sus4', 'add9',
                # スケール種類
                'ホールハーフディミニッシュ', 'ハーフホールディミニッシュ', 'クロマチック', 'ペンタトニック',
                # 音楽用語
                'ルート', 'サード', 'フィフス', 'セブンス', '着地音', 'コードトーン', '進行',
                # 楽器・演奏
                'ピアノ', 'ギター', 'ベース', 'ドラム', '楽器', '演奏', '弾く', '奏でる'
            ],
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
                # 五感・感覚（メロディーは音楽カテゴリに移動）
                '聴覚', '視覚', '触覚', '嗅覚', '味覚', '五感', '感覚', '体の部分'
            ],
            'tech': [
                'プログラミング', 'API', 'システム', 'アプリ', 'python', 'javascript', 
                'tech', '技術', '開発', 'コード', 'データ', 'AI', '機械学習', 'ChatGPT', 
                'チャットGPT', 'プロジェクト機能', 'ボイスモード', 'アドバンスド', 'ツール'
            ],
            'business': [
                'ビジネス', 'マーケティング', '戦略', '営業', '集客', 'SEO', 'SNS', 
                '広告', '売上', '収益', '顧客', '市場', 'コンサル', 'コンサルティング', 
                'クライアント', 'プロジェクト', '会議', 'アドバイス', '提案', '資料'
            ],
            'media': [
                'SNS', 'X', 'Twitter', 'Instagram', 'Facebook', 'YouTube', 'TikTok',
                'インフルエンサー', 'フォロワー', 'エンゲージメント', 'ポスト', 'アカウント',
                'メディア', 'コンテンツ', '動画', '配信', 'ライブ'
            ],
            'ideas': [
                'アイデア', '企画', '提案', '案', 'プロジェクト', '創作', '発想', 
                'ブレスト', 'コンセプト', 'プラン'
            ]
        }
    
    def _convert_katakana_to_english(self, text: str) -> str:
        """音声入力のカタカナを英語に変換"""
        converted = text
        # 長い語句から順に変換（部分一致を防ぐため）
        for katakana, english in sorted(self.katakana_to_english.items(), key=lambda x: len(x[0]), reverse=True):
            converted = converted.replace(katakana, english)
        return converted
    
    def _extract_person_names(self, text: str) -> list:
        """統一された人名抽出メソッド"""
        person_names = []
        
        # 統一された人名抽出パターン
        person_patterns = [
            # パターン1: 文脈考慮での人名抽出
            r'(?:^|[、。\s]|展開中の|との|への|による)([ぁ-ん一-龥]{2,6})(?:さん|様|氏)',
            r'(?:^|[、。\s]|展開中の|との|への|による)([ァ-ヶー]{2,6})(?:さん|様|氏)',
            r'(?:^|[、。\s]|展開中の|との|への|による)([A-Za-z]{3,10})(?:さん|様|氏)',
            # パターン2: 一般的な助詞の後の人名
            r'(?:と|に|へ|の)([ぁ-ん一-龥]{2,6})(?:さん|様|氏)',
            r'(?:と|に|へ|の)([ァ-ヶー]{2,6})(?:さん|様|氏)',
            r'(?:と|に|へ|の)([A-Za-z]{3,10})(?:さん|様|氏)'
        ]
        
        # 除外すべき文字列
        exclude_patterns = ['を展開', '中の', 'を使', 'について', 'では', 'との']
        
        for pattern in person_patterns:
            matches = re.findall(pattern, text)
            for match in matches:
                # 除外条件をチェック
                if not any(exclude in match for exclude in exclude_patterns):
                    # 適切な長さの人名のみ採用
                    if 2 <= len(match) <= 6 and match not in person_names:
                        person_names.append(match)
        
        return person_names
    
    def _extract_concrete_headings(self, content: str) -> list:
        """実際の見出し語から具体的な話題を抽出"""
        headings = []
        # ## 見出し から具体的なトピックを抽出
        heading_matches = re.findall(r'^##\s+(.+)$', content, re.MULTILINE)
        for heading in heading_matches:
            if len(heading) > 3 and heading not in ['要約', 'ポイント', '関連ファイル', '内容']:
                # 見出しをそのまま具体的なポイントとして使用
                headings.append(f"「{heading}」の具体的な解説と実践方法")
        return headings
    
    def _extract_key_paragraph_summaries(self, content: str) -> list:
        """重要な段落から具体的な要約を抽出"""
        paragraphs = []
        # 段落単位で分割（改行2つ以上で区切り）
        para_blocks = re.split(r'\n\s*\n', content)
        
        for para in para_blocks:
            if len(para.strip()) >= 100:  # 十分な長さの段落
                # 段落の最初の1-2文を要約として抽出
                sentences = re.split(r'[。．]', para.strip())
                if sentences and len(sentences[0]) > 20:
                    summary = sentences[0]
                    if len(summary) > 50:
                        summary = summary[:47] + "..."
                    paragraphs.append(summary)
        
        return paragraphs[:3]
    
    def _extract_concrete_contextual_points(self, content: str) -> list:
        """文脈から具体的なキーワードと関連性を抽出"""
        points = []
        
        # 重要な固有名詞 + 具体的な動作パターン
        patterns = [
            r'([A-Z][a-zA-Z\s]+)(?:を使った|による|での)([^。]{10,50})',
            r'([ァ-ヶー一-龯]{3,})(?:システム|手法|方法|ガイド)(?:の|を)([^。]{10,40})',
        ]
        
        for pattern in patterns:
            matches = re.findall(pattern, content)
            for match in matches:
                if len(match) == 2:
                    points.append(f"{match[0]}を活用した{match[1].strip()}")
        
        # 具体的な成果・効果の記述
        effect_patterns = [
            r'([^。]{15,50})(?:の効果|が確認|を実現|が向上)',
            r'([^。]{15,50})(?:することで|により)[、，]?([^。]{10,30})',
        ]
        
        for pattern in effect_patterns:
            matches = re.findall(pattern, content)
            for match in matches:
                if len(match) >= 1:
                    effect_text = match[0].strip()
                    if len(effect_text) > 10:
                        points.append(f"{effect_text}による具体的な改善効果")
        
        return points[:3]
    
    def _filter_and_deduplicate_points(self, points: list) -> list:
        """ポイントの重複除去と品質フィルタリング"""
        filtered_points = []
        seen = set()
        
        for point in points:
            if not point or len(point.strip()) < 10:
                continue
            
            # 重複チェック（類似度ベース）
            is_duplicate = False
            for seen_point in seen:
                # 簡易類似度チェック（共通語数）
                point_words = set(point.split())
                seen_words = set(seen_point.split())
                overlap = len(point_words & seen_words)
                if overlap > len(point_words) * 0.7:  # 70%以上重複
                    is_duplicate = True
                    break
            
            if not is_duplicate:
                filtered_points.append(point.strip())
                seen.add(point.strip())
        
        return filtered_points[:6]  # 最大6個
    
    def preview_analysis(self, content: str) -> dict:
        """プレビュー用の完全分析（編集状態保持対応）"""
        try:
            # 🔧 編集済み分析結果がある場合はそれを返す（上書き防止）
            if self._last_edited_analysis:
                print("📝 編集済み分析結果を使用（上書き防止）")
                return self._last_edited_analysis
            
            print("🔄 統合分析開始...")
            
            # 音声入力対応：カタカナを英語に変換
            content = self._convert_katakana_to_english(content)
            
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
            
            # 5. 内容要約生成
            summary_result = self._generate_content_summary(content)
            print(f"📝 要約生成: 完了")
            
            # 6. 統合結果構築
            result = {
                'success': True,
                'category': category_result,
                'title': title_result,
                'tags': tags_result,
                'relations': relations_result,
                'summary': summary_result,
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
        """強化されたカテゴリ分析（Ultrathinking統合版）"""
        
        # Ultrathinking分析を最初に試行
        if ULTRATHINKING_AVAILABLE:
            try:
                print("🧠 Ultrathinking カテゴリ分析中...")
                analyzer = UltrathinkingAnalyzer()
                ultra_result = analyzer.analyze_content(content)
                
                if ultra_result and ultra_result.get('category'):
                    category = ultra_result.get('category', 'general')
                    confidence = 0.9  # Ultrathinking の高い信頼度
                    
                    print(f"🎯 Ultrathinking判定: {category} (信頼度: {confidence})")
                    
                    return {
                        'name': category,
                        'confidence': confidence,
                        'scores': {category: 10.0},  # 高スコア
                        'pattern_matches': {},
                        'keyword_matches': {},
                        'method': 'ultrathinking'
                    }
                    
            except Exception as e:
                print(f"⚠️ Ultrathinking分析エラー: {e}")
                print("📊 従来分析にフォールバック")
        
        # 従来の分析方式（フォールバック）
        print("📊 従来方式でカテゴリ分析中...")
        
        content_lower = content.lower()
        
        # 個人との打ち合わせ判定（最優先）
        person_meeting_patterns = [
            r'([ぁ-ん一-龥ァ-ヶーA-Za-z]+)(?:さん|様|氏)(?:との|へ|と)(?:打ち合わせ|会議|相談|ミーティング)',
            r'([ぁ-ん一-龥ァ-ヶーA-Za-z]+)(?:さん|様|氏)(?:に|への)(?:提案|報告|連絡)',
            r'([ぁ-ん一-龥ァ-ヶーA-Za-z]+)(?:さん|様|氏)(?:関連|について)',
            r'([ぁ-ん一-龥ァ-ヶーA-Za-z]+)(?:さん|様|氏)(?:と|との)(?:協議|検討|相談)'
        ]
        
        # 個人との打ち合わせかチェック
        is_person_meeting = False
        for pattern in person_meeting_patterns:
            if re.search(pattern, content):
                is_person_meeting = True
                break
        
        # 個人との打ち合わせの場合は強制的にビジネス（コンサルティング）に分類
        if is_person_meeting:
            return {
                'name': 'business',
                'confidence': 1.0,
                'scores': {'business': 10, 'education': 0, 'tech': 0, 'media': 0, 'ideas': 0, 'music': 0},
                'pattern_matches': {'business': 10},
                'keyword_matches': {},
                'special_rule': 'person_meeting_detected'
            }
        
        # ビジネス優先キーワード判定（教育系でも強制的にbusiness/techに）
        business_priority_keywords = [
            'コンサル', 'コンサルティング', 'Consulting', 'consulting',
            'AI導入', 'DX', 'AI活用', 'システム導入', 'デジタル化',
            'クライアント', 'Client', 'client',
            'ビジネス戦略', 'マーケティング', '売上', '収益',
            'プロジェクト管理', 'Project管理'
        ]
        
        tech_priority_keywords = [
            'ChatGPT', 'API', 'システム開発', 'プログラミング',
            'GitHub', 'github', 'Obsidian', 'obsidian',
            'アプリ開発', 'ツール開発', 'データ分析'
        ]
        
        # AI関連は文脈で判定
        ai_context_business = ['AI導入', 'AI活用', 'AIコンサル', 'AI戦略']
        ai_context_tech = ['AI開発', 'AI技術', 'AIシステム', 'AIプログラム']
        
        # ビジネス優先キーワードチェック
        has_business_priority = any(keyword in content for keyword in business_priority_keywords)
        has_tech_priority = any(keyword in content for keyword in tech_priority_keywords)
        
        # AI文脈判定
        has_ai_business_context = any(keyword in content for keyword in ai_context_business)
        has_ai_tech_context = any(keyword in content for keyword in ai_context_tech)
        
        # 単純な「AI」が含まれている場合の文脈判定
        if 'AI' in content and not has_ai_business_context and not has_ai_tech_context:
            # 他のビジネスキーワードがあればビジネス、技術キーワードがあればテック
            if any(word in content for word in ['導入', 'コンサル', 'クライアント', '戦略']):
                has_business_priority = True
            elif any(word in content for word in ['開発', 'プログラム', 'システム', 'ツール']):
                has_tech_priority = True
        
        # AI文脈優先判定
        if has_ai_business_context:
            return {
                'name': 'business',
                'confidence': 1.0,
                'scores': {'business': 9, 'education': 0, 'tech': 0, 'media': 0, 'ideas': 0, 'music': 0},
                'pattern_matches': {'business': 9},
                'keyword_matches': {},
                'special_rule': 'ai_business_context_detected'
            }
        
        if has_ai_tech_context:
            return {
                'name': 'tech',
                'confidence': 1.0,
                'scores': {'tech': 9, 'education': 0, 'business': 0, 'media': 0, 'ideas': 0, 'music': 0},
                'pattern_matches': {'tech': 9},
                'keyword_matches': {},
                'special_rule': 'ai_tech_context_detected'
            }
        
        if has_business_priority:
            return {
                'name': 'business',
                'confidence': 1.0,
                'scores': {'business': 8, 'education': 0, 'tech': 0, 'media': 0, 'ideas': 0, 'music': 0},
                'pattern_matches': {'business': 8},
                'keyword_matches': {},
                'special_rule': 'business_priority_keyword_detected'
            }
        
        if has_tech_priority:
            return {
                'name': 'tech',
                'confidence': 1.0,
                'scores': {'tech': 8, 'education': 0, 'business': 0, 'media': 0, 'ideas': 0, 'music': 0},
                'pattern_matches': {'tech': 8},
                'keyword_matches': {},
                'special_rule': 'tech_priority_keyword_detected'
            }
        
        # 教育パターンマッチング（厳密化）
        education_patterns = [
            r'[ぁ-んー]+くん[はがをにで、。]|[ぁ-んー]+さん[はがをにで、。]',  # 生徒名（文脈付き）
            r'わかる？|わかりますか？|理解できた？',  # 教師の確認
            r'正解です|不正解です|よくできました',  # 明確な評価
            r'選びなさい|答えなさい|書きなさい',  # 明確な指示
            r'テスト|試験|授業|宿題|課題',  # 教育文脈
            r'国語|算数|理科|社会|英語',  # 教科
        ]
        
        # ビジネスパターンマッチング
        business_patterns = [
            r'Client|Consulting|Project|Meeting',  # ビジネス英語
            r'会議|打ち合わせ|商談|提案',  # ビジネス日本語
            r'資料|レポート|プレゼン',  # ビジネス文書
            r'戦略|施策|方針|計画',  # ビジネス計画
        ]
        
        # テックパターンマッチング
        tech_patterns = [
            r'ChatGPT|AI|API|GitHub|Obsidian',  # テック固有名詞
            r'機能|ツール|システム|アプリ',  # テック一般用語
            r'アップロード|ダウンロード|インストール',  # テック動作
        ]
        
        # パターンマッチングスコア
        pattern_scores = defaultdict(int)
        
        # 教育パターン
        for pattern in education_patterns:
            if re.search(pattern, content):
                pattern_scores['education'] += 2  # スコアを適正化
        
        # ビジネスパターン
        for pattern in business_patterns:
            if re.search(pattern, content):
                pattern_scores['business'] += 3  # ビジネスは高スコア
        
        # テックパターン
        for pattern in tech_patterns:
            if re.search(pattern, content):
                pattern_scores['tech'] += 3  # テックも高スコア
        
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
            
            # 音楽カテゴリは音楽理論用語で高スコア
            if category == 'music':
                music_theory_terms = ['ディミニッシュ', 'スケール', 'コード', 'セブンス', 'ルート', 'サード', 'フィフス']
                music_bonus = sum(2 for term in music_theory_terms if term in content)
                total_scores[category] = pattern_score + keyword_score + music_bonus
            # 教育カテゴリの特別扱いを削除
            elif category == 'education':
                total_scores[category] = pattern_score + keyword_score
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
        """知的タイトル生成（Ultrathinking統合版）"""
        
        # Ultrathinking タイトル生成を最初に試行
        if ULTRATHINKING_AVAILABLE:
            try:
                print("🧠 Ultrathinking タイトル生成中...")
                analyzer = UltrathinkingAnalyzer()
                ultra_result = analyzer.analyze_content(content)
                
                if ultra_result and ultra_result.get('title'):
                    title = ultra_result.get('title', '')
                    confidence = 0.95  # 非常に高い信頼度
                    
                    print(f"🎯 Ultrathinking タイトル: {title}")
                    
                    return {
                        'title': title,
                        'method': 'ultrathinking',
                        'alternatives': [],
                        'confidence': confidence
                    }
                    
            except Exception as e:
                print(f"⚠️ Ultrathinking タイトル生成エラー: {e}")
                print("📊 従来方式にフォールバック")
        
        # 従来のタイトル生成方式（フォールバック）
        print("📊 従来方式でタイトル生成中...")
        
        # 複数の手法を試行
        methods = []
        
        # 0. 最初の文から主題を抽出（最優先）
        first_sentence_title = self._extract_first_sentence_theme(content)
        if first_sentence_title:
            methods.append({'method': 'first_sentence', 'title': first_sentence_title, 'score': 4.0})
        
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
    
    def _extract_first_sentence_theme(self, content: str) -> str:
        """最初の文から主題を抽出して言い切り形のタイトル生成（20-50文字）"""
        # 最初の文を取得
        sentences = re.split(r'[。．！？\n]', content)
        if not sentences:
            return ""
        
        first_sentence = sentences[0].strip()
        if len(first_sentence) < 5:
            return ""
        
        # 冗長な表現を削除
        clean_sentence = re.sub(r'(ので|ため|のように|というのは|ということで|といった|など|と思います|なのかなと思っているところです|に向き合っていこうと思います)', '', first_sentence)
        
        # 統一された人名抽出（タイトル・要約共通）
        person_names = self._extract_person_names(clean_sentence)
        
        # 重要な固有名詞と概念を抽出（人名以外）
        entities = re.findall(r'(?:ChatGPT|Project機能|Project|プロジェクト機能|プロジェクト|Consulting|コンサルティング|Client|クライアント|Voice Mode|ボイスモード|アドバンストボイスモード)', clean_sentence)
        actions = re.findall(r'(?:活用|利用|導入|実装|検討|分析|評価|運用|改善|蓄積|立ち上げ|打ち合わせ|会議|相談|報告|確認|依頼)', clean_sentence)
        targets = re.findall(r'(?:課題解決|会議履歴|議事録|資料|やりとり|ミーティング|サービス|戦略|方針|計画|提案)', clean_sentence)
        
        # 言い切り形タイトルの生成（人名を最優先）
        if person_names:
            # 人名がある場合は必ず含める
            main_person = person_names[0]
            
            if actions and targets:
                # 人名 + アクション + 対象
                main_action = actions[0]
                main_target = targets[0]
                title = f"{main_person}さんとの{main_target}{main_action}録"
            elif actions:
                # 人名 + アクション
                main_action = actions[0]
                if main_action in ['打ち合わせ', '会議', '相談']:
                    title = f"{main_person}さんとの{main_action}メモ"
                else:
                    title = f"{main_person}さんへの{main_action}内容"
            elif targets:
                # 人名 + 対象
                main_target = targets[0]
                title = f"{main_person}さん関連{main_target}まとめ"
            else:
                # 人名のみ
                title = f"{main_person}さんとの協議事項"
                
        elif entities and actions and targets:
            # 3要素揃った場合：「ChatGPTを活用した課題解決手法」
            main_entity = entities[0].replace('の', '')
            main_action = actions[0]
            main_target = targets[0]
            title = f"{main_entity}を{main_action}した{main_target}手法"
            
        elif entities and actions:
            # 2要素の場合：「ChatGPTプロジェクト機能の活用方法」
            main_entity = entities[0].replace('の', '')
            main_action = actions[0]
            title = f"{main_entity}の{main_action}方法"
            
        elif entities:
            # 固有名詞のみの場合
            main_entity = entities[0].replace('の', '')
            if 'コンサル' in clean_sentence or 'クライアント' in clean_sentence:
                title = f"{main_entity}を活用したコンサルティング戦略"
            elif 'プロジェクト' in clean_sentence or 'Project' in clean_sentence:
                title = f"{main_entity}プロジェクト管理の実践法"
            else:
                title = f"{main_entity}の効果的活用法"
                
        else:
            # フォールバック：重要語句から構成
            important_phrases = re.findall(r'[ぁ-んァ-ヶー一-龯]{4,12}', clean_sentence)
            if len(important_phrases) >= 2:
                title = f"{important_phrases[0]}と{important_phrases[1]}の連携手法"
            elif important_phrases:
                title = f"{important_phrases[0]}の実践的アプローチ"
            else:
                title = "新しい業務改善手法"
        
        # 文字数調整（20-50文字）
        if len(title) < 20:
            # 短すぎる場合は補完
            if 'ChatGPT' in title:
                title = title.replace('の', '機能の').replace('を', 'ツールを')
            # 人名が含まれている場合は過度な補完を避ける
            elif not person_names and len(title) < 20:
                title += "による業務効率化"
                
        elif len(title) > 50:
            # 長すぎる場合は短縮
            title = title[:47] + "..."
        
        return self._clean_title_text(title)
    
    def _create_natural_method_summary(self, methods: list) -> str:
        """複数の手段を自然な日本語に統合"""
        if not methods:
            return ""
        
        # カテゴリ別に分類
        project_methods = [m for m in methods if 'プロジェクト' in m or 'Project' in m]
        data_methods = [m for m in methods if '資料' in m or '議事録' in m or '蓄積' in m]
        comm_methods = [m for m in methods if 'チャット' in m or 'ボイス' in m]
        
        summary_parts = []
        
        if project_methods:
            summary_parts.append("プロジェクト管理")
        
        if data_methods:
            summary_parts.append("情報の一元管理")
        
        if comm_methods:
            summary_parts.append("多様なコミュニケーション")
        
        # フォールバック
        if not summary_parts:
            summary_parts = methods[:2]
        
        return "・".join(summary_parts[:2])
    
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
               word in ['開発', '設計', '実装', '分析', '検討', '構築', '生成', '連携', '活用', '解釈', '理解', '指導', '学習', '授業', '記録']:
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
        """file-organizer式6層タグ生成システム（Ultrathinking統合版）"""
        
        # Ultrathinking タグ生成を最初に試行
        if ULTRATHINKING_AVAILABLE:
            try:
                print("🧠 Ultrathinking タグ生成中...")
                analyzer = UltrathinkingAnalyzer()
                ultra_result = analyzer.analyze_content(content)
                
                if ultra_result and ultra_result.get('tags'):
                    ultra_tags = ultra_result.get('tags', [])
                    confidence = 0.9
                    
                    print(f"🏷️ Ultrathinking タグ: {ultra_tags[:5]}...")  # 最初の5個表示
                    
                    return {
                        'tags': ultra_tags,
                        'count': len(ultra_tags),
                        'layer_info': 'ultrathinking_enhanced',
                        'method': 'ultrathinking',
                        'confidence': confidence
                    }
                    
            except Exception as e:
                print(f"⚠️ Ultrathinking タグ生成エラー: {e}")
                print("📊 従来方式にフォールバック")
        
        # 従来のタグ生成方式（フォールバック）
        print("📊 従来方式でタグ生成中...")
        
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
        
        # 全カテゴリ共通の重要固有名詞を先にチェック
        universal_entities = {
            'ChatGPT': ['ChatGPT', 'chatgpt', 'Chat GPT'],
            'GitHub': ['GitHub', 'github', 'Github'],
            'Obsidian': ['Obsidian', 'obsidian'],
            'AI': ['AI', 'A.I.'],
            'API': ['API'],
            'Claude': ['Claude', 'claude'],
            'Python': ['Python', 'python'],
            'JavaScript': ['JavaScript', 'javascript', 'JS'],
            'Project': ['Project', 'プロジェクト'],
            'Client': ['Client', 'クライアント'],
            'Consulting': ['Consulting', 'コンサル', 'コンサルティング']
        }
        
        for entity, patterns in universal_entities.items():
            if any(pattern in content for pattern in patterns):
                entities.add(entity)
        
        # カテゴリ別の追加抽出
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
        
        # 日本語の意味のある語（3文字以上）を抽出、ただし音楽用語は適切に処理
        japanese_words = re.findall(r'[ぁ-んァ-ヶー一-龯]{3,8}', content)
        
        # 音楽理論用語の特別処理
        music_terms = ['ディミニッシュスケール', 'ホールハーフディミニッシュ', 'ハーフホールディミニッシュ']
        for term in music_terms:
            if term in content:
                frequent_terms.add(term)
        
        word_counts = Counter(japanese_words)
        
        for word, count in word_counts.items():
            if (count >= 2 and len(word) >= 3 and 
                not re.match(r'^[あいうえおかきくけこさしすせそたちつてとなにぬねのはひふへほまみむめもやゆよらりるれろわをん]+$', word) and
                word not in ['ディミニ', 'ッシュス', 'ールハー']):  # 不完全な切断語は除外
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
    
    def _extract_important_terms(self, content: str) -> list:
        """重要な用語を抽出（カテゴリ不問）"""
        important_terms = []
        
        # 全カテゴリ共通の重要固有名詞
        universal_entities = {
            'ChatGPT': ['ChatGPT', 'chatgpt', 'Chat GPT', 'チャットGPT'],
            'GitHub': ['GitHub', 'github', 'Github'],
            'Obsidian': ['Obsidian', 'obsidian', 'オブシディアン'],
            'AI': ['AI', 'A.I.', 'エーアイ'],
            'API': ['API', 'エーピーアイ'],
            'Claude': ['Claude', 'claude'],
            'Python': ['Python', 'python', 'パイソン'],
            'JavaScript': ['JavaScript', 'javascript', 'JS', 'ジャバスクリプト'],
            'Project': ['Project', 'プロジェクト'],
            'Client': ['Client', 'クライアント'],
            'Consulting': ['Consulting', 'コンサル', 'コンサルティング']
        }
        
        # 固有名詞のマッチング
        for entity, patterns in universal_entities.items():
            if any(pattern in content for pattern in patterns):
                important_terms.append(entity)
        
        # 技術関連の重要用語
        tech_terms = ['システム', 'アプリ', 'プログラミング', '開発', 'データ', '機械学習', 'ツール']
        for term in tech_terms:
            if term in content:
                important_terms.append(term)
        
        # 教育関連の重要用語
        education_terms = ['教育', '学習', '指導', '授業', '国語', '分析', '対策', '中学受験']
        for term in education_terms:
            if term in content:
                important_terms.append(term)
        
        # ビジネス関連の重要用語
        business_terms = ['ビジネス', 'マーケティング', '戦略', '営業', '集客', 'SEO', 'SNS']
        for term in business_terms:
            if term in content:
                important_terms.append(term)
        
        # メディア関連の重要用語
        media_terms = ['X', 'Twitter', 'Instagram', 'フォロワー', 'エンゲージメント', 'ポスト', 'アカウント']
        for term in media_terms:
            if term in content:
                important_terms.append(term)
        
        # 頻出する日本語の重要語を追加
        japanese_words = re.findall(r'[ぁ-んァ-ヶー一-龯]{3,8}', content)
        word_counts = Counter(japanese_words)
        
        # 2回以上出現し、一般的でない語を追加
        for word, count in word_counts.items():
            if (count >= 2 and len(word) >= 3 and 
                not self._is_common_word(word) and
                word not in important_terms):
                important_terms.append(word)
        
        # 重複を除去して返す
        return list(dict.fromkeys(important_terms))

    def _find_related_files(self, content: str, title: str) -> dict:
        """file-organizer式強化関連ファイル検索"""
        
        try:
            vault_path = Path(self.obsidian_path)
            relations = []
            
            # 既存のmarkdownファイルを検索（プログラム関連ファイルを除外）
            all_md_files = list(vault_path.rglob('*.md'))
            md_files = self._filter_non_program_files(all_md_files)
            
            # デバッグ用：ChatGPT関連ファイルの検出
            chatgpt_files_found = 0
            files_processed = 0
            
            for md_file in md_files:
                try:
                    files_processed += 1
                    
                    # ファイル内容を読み込み
                    with open(md_file, 'r', encoding='utf-8') as f:
                        file_content = f.read()
                    
                    # ChatGPT関連ファイルの検出
                    if any(keyword in file_content for keyword in ['ChatGPT', 'チャットGPT', 'chatgpt']):
                        chatgpt_files_found += 1
                    
                    # タイトルを抽出
                    file_title = md_file.stem
                    
                    # 関連度を計算（階層的アプローチ）
                    relation_score = self._calculate_hierarchical_relation_score(
                        content, file_content, title, file_title
                    )
                    
                    # カテゴリ別の厳格な閾値設定（関連度向上）
                    threshold = self._get_relation_threshold(title, file_title)
                    
                    # デバッグ情報（開発時のみ有効）
                    # if any(keyword in file_content for keyword in ['ChatGPT', 'チャットGPT', 'chatgpt']):
                    #     print(f"🔍 ChatGPT関連ファイル: {file_title}")
                    #     print(f"   スコア: {relation_score:.3f}, 閾値: {threshold:.3f}")
                    
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
                    print(f"⚠️ ファイル読み込みエラー ({md_file}): {e}")
                    continue
            
            # 開発デバッグ情報（本番では無効）
            # print(f"📊 ChatGPT関連ファイル数: {chatgpt_files_found}/{files_processed}")
            # print(f"📊 関連ファイル検出数: {len(relations)}")
            
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
    
    def _filter_non_program_files(self, md_files: list) -> list:
        """プログラム関連ファイルを除外して関連ファイル候補をフィルタリング"""
        filtered_files = []
        
        # 除外すべきファイル名パターン
        program_file_patterns = [
            # README系
            r'^README.*',
            r'^readme.*',
            r'^Readme.*',
            
            # 設定・構成ファイル
            r'^CHANGELOG.*',
            r'^LICENSE.*',
            r'^CONTRIBUTING.*',
            r'^INSTALL.*',
            r'^USAGE.*',
            
            # プログラム・スクリプト関連
            r'.*\.py\.md$',
            r'.*\.js\.md$',
            r'.*\.ts\.md$',
            r'.*\.json\.md$',
            r'.*\.yaml\.md$',
            r'.*\.yml\.md$',
            
            # 技術文書（API仕様等）
            r'^API.*',
            r'^api.*',
            r'.*_api\.md$',
            r'.*-api\.md$',
            
            # 開発者向け文書
            r'^DEVELOPER.*',
            r'^developer.*',
            r'^DEV.*',
            r'^dev.*',
        ]
        
        # 除外すべきディレクトリパターン
        program_dir_patterns = [
            r'.*[/\\]\.git[/\\].*',
            r'.*[/\\]node_modules[/\\].*',
            r'.*[/\\]__pycache__[/\\].*',
            r'.*[/\\]\.vscode[/\\].*',
            r'.*[/\\]\.idea[/\\].*',
            r'.*[/\\]docs[/\\]api[/\\].*',
            r'.*[/\\]documentation[/\\].*',
        ]
        
        for md_file in md_files:
            file_name = md_file.name
            file_path_str = str(md_file)
            
            # ファイル名チェック
            is_program_file = any(re.match(pattern, file_name, re.IGNORECASE) 
                                for pattern in program_file_patterns)
            
            # ディレクトリパスチェック
            is_in_program_dir = any(re.match(pattern, file_path_str, re.IGNORECASE) 
                                  for pattern in program_dir_patterns)
            
            # 内容チェック（README等の確実な除外）
            is_program_content = self._is_program_related_content(md_file)
            
            if not (is_program_file or is_in_program_dir or is_program_content):
                filtered_files.append(md_file)
        
        print(f"📁 ファイルフィルタリング: {len(md_files)} → {len(filtered_files)} (プログラム関連除外)")
        return filtered_files
    
    def _is_program_related_content(self, file_path: Path) -> bool:
        """ファイル内容からプログラム関連文書かを判定"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()[:500]  # 最初の500文字のみチェック
            
            # プログラム関連キーワード
            program_keywords = [
                '# Installation', '## Installation', '# Usage', '## Usage',
                '# API', '## API', '```bash', '```shell', '```sh',
                'npm install', 'pip install', 'yarn add', 'composer install',
                '## Quick Start', '## Getting Started', '# Getting Started',
                'git clone', 'docker run', 'docker-compose',
                '# Requirements', '## Requirements', '# Dependencies',
                '# Configuration', '## Configuration'
            ]
            
            # 3個以上のプログラム関連キーワードがある場合は除外
            keyword_count = sum(1 for keyword in program_keywords if keyword in content)
            return keyword_count >= 3
            
        except Exception:
            return False
    
    def _calculate_hierarchical_relation_score(self, content1: str, content2: str, title1: str, title2: str) -> float:
        """file-organizer式階層的関連度スコア計算（強化版）"""
        max_score = 0.0
        
        # 0. 重要キーワード直接マッチング（最優先）
        important_keywords = [
            'ChatGPT', 'チャットGPT', 'chatgpt', 'API', 'GitHub', 'Obsidian', 'AI', 'Claude',
            'Project', 'プロジェクト', 'Consulting', 'コンサル', 'Client', 'クライアント',
            'Python', 'JavaScript', 'MCP', 'Zapier', 'Notion'
        ]
        
        keyword_matches = 0
        for keyword in important_keywords:
            if keyword in content1 and keyword in content2:
                keyword_matches += 1
        
        # 重要キーワードマッチがある場合は高スコア保証
        if keyword_matches > 0:
            keyword_score = min(0.3 + keyword_matches * 0.2, 0.9)
            max_score = max(max_score, keyword_score)
        
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
        
        # 3. コンテンツ類似度（改良済み）
        jaccard_similarity = self._calculate_content_jaccard_similarity(content1, content2)
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
        """コンテンツのJaccard類似度計算（英語対応強化）"""
        # 日本語の単語（3文字以上）
        jp_words1 = set(re.findall(r'[ぁ-んァ-ヶー一-龯]{3,}', content1.lower()))
        jp_words2 = set(re.findall(r'[ぁ-んァ-ヶー一-龯]{3,}', content2.lower()))
        
        # 英語の単語（2文字以上）+ 重要固有名詞
        en_words1 = set(re.findall(r'[A-Za-z]{2,}', content1))
        en_words2 = set(re.findall(r'[A-Za-z]{2,}', content2))
        
        # 重要キーワードの直接マッチング（大幅加点）
        important_keywords = {
            'ChatGPT', 'chatgpt', 'チャットGPT', 'API', 'GitHub', 'Obsidian', 'AI', 'Claude',
            'Project', 'プロジェクト', 'Consulting', 'コンサル', 'Client', 'クライアント',
            'Python', 'JavaScript', 'Tech', 'ビジネス', 'アイデア'
        }
        
        keyword_matches = 0
        for keyword in important_keywords:
            if keyword in content1 and keyword in content2:
                keyword_matches += 1
        
        # 一般的すぎる語を除外
        common_words = {'について', 'に関して', 'ができる', 'である', 'ている', 'ました', 'します', 'された', 'the', 'and', 'of', 'to', 'in', 'is', 'it'}
        jp_words1 = jp_words1 - common_words
        jp_words2 = jp_words2 - common_words
        en_words1 = en_words1 - common_words
        en_words2 = en_words2 - common_words
        
        # 全単語セットの組み合わせ
        all_words1 = jp_words1 | en_words1
        all_words2 = jp_words2 | en_words2
        
        jaccard_sim = self._calculate_jaccard_similarity(all_words1, all_words2)
        
        # 重要キーワードマッチに大幅ボーナス
        if keyword_matches > 0:
            bonus = min(keyword_matches * 0.3, 0.8)  # 最大0.8のボーナス
            jaccard_sim = min(1.0, jaccard_sim + bonus)
        
        return jaccard_sim
    
    def _is_sns_analysis_file(self, title: str) -> bool:
        """SNS分析ファイル判定"""
        sns_keywords = ['X投稿', 'SNS', 'アカウント分析', 'ポスト分析', 'フォロワー', 'インフルエンサー']
        return any(keyword in title for keyword in sns_keywords)
    
    def _is_tech_file(self, title: str) -> bool:
        """技術ファイル判定"""
        tech_keywords = ['API', 'プログラミング', 'システム', 'GitHub', 'Python', 'AI', 'Claude', 'コード', 'ChatGPT', 'チャットGPT', 'MCP', 'Zapier', 'Obsidian', 'Tech', '技術', '開発']
        return any(keyword in title for keyword in tech_keywords)
    
    def _get_relation_threshold(self, title1: str, title2: str) -> float:
        """カテゴリ別関連閾値取得"""
        if self._is_sns_analysis_file(title1) and self._is_sns_analysis_file(title2):
            return 0.08  # SNS分析同士：緩和
        elif self._is_tech_file(title1) and self._is_tech_file(title2):
            return 0.06  # Tech系同士：緩和
        else:
            return 0.05  # 一般：大幅緩和（実用的なレベルに）
    
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
        
        # 実際の保存先フォルダを取得
        actual_folder = self.category_folders.get(category_result['name'], 'Others')
        
        return {
            'category_display': f"{category_result['name']} (信頼度: {category_result['confidence']:.1%})",
            'title_display': title_result['title'],
            'tags_display': ' '.join(tags_result['tags'][:5]),  # 最初の5個
            'relations_display': f"{relations_result['count']}件の関連ファイル",
            'folder_path': actual_folder,  # 実際の保存先フォルダを追加
            'save_path_display': f"{actual_folder}/{title_result['title']} {datetime.now().strftime('%Y-%m-%d')}.md",
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
        # 適切な長さに調整（35文字まで拡張）
        cleaned = text.strip()
        if len(cleaned) > 35:
            # 単語の途中で切らないように調整
            cut_point = 32
            while cut_point > 20 and cleaned[cut_point] not in ['の', 'を', 'に', 'と', 'で', ' ', '、']:
                cut_point -= 1
            cleaned = cleaned[:cut_point] + "..."
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
    
    def _generate_content_summary(self, content: str) -> dict:
        """メモ内容の要約と箇条書きを生成（改善版：3-6個の詳細な箇条書き）"""
        
        # 文全体を理解するための前処理
        clean_content = re.sub(r'(ので|のように|ということで|なのかなと思っているところです)', '', content)
        sentences = re.split(r'[。．！？\n]', content)
        sentences = [s.strip() for s in sentences if s.strip() and len(s.strip()) > 10]
        
        # 重要な固有名詞と概念の抽出
        important_terms = self._extract_important_terms(content)
        
        # === 要約生成（論理的構造で整理）===
        
        # 1. 主要目的の特定
        purpose = ""
        purpose_patterns = [
            r'(ChatGPT[のプロジェクト機能]*|Project[機能]*|プロジェクト[機能]*)[をに](.{5,20})(したい|する|活用|利用)',
            r'(.{10,25})[をに](.{5,15})(に向き合|活用|利用)(していこう|したい)'
        ]
        
        for pattern in purpose_patterns:
            match = re.search(pattern, content)
            if match:
                groups = match.groups()
                if len(groups) >= 3:
                    tool = groups[0]
                    action = groups[2] if len(groups) > 2 else groups[1]
                    purpose = f"{tool}を{action}"
                    break
        
        if not purpose:
            # メモの最初の部分から主要な目的を抽出
            if sentences:
                first_sentence = sentences[0]
                # 統一された人名抽出を使用
                person_names_summary = self._extract_person_names(first_sentence)
                if person_names_summary:
                    person_name = person_names_summary[0]
                    if 'AI' in content or 'DX' in content:
                        purpose = f"{person_name}さんへのAI・DX導入支援"
                    elif '教育' in content or '学習' in content or '国語' in content or '算数' in content:
                        purpose = f"{person_name}さんとの教育事業連携"
                    elif 'コンサル' in content or 'コンサルティング' in content:
                        purpose = f"{person_name}さんへのコンサルティング提案"
                    else:
                        purpose = f"{person_name}さんとの協業検討"
                else:
                    # 人名がない場合は内容から主要テーマを抽出
                    if 'AI' in content and '導入' in content:
                        purpose = "AI導入支援プロジェクト"
                    elif 'ChatGPT' in content or 'Project' in content:
                        purpose = "ChatGPTプロジェクト機能の活用"
                    else:
                        purpose = "業務改善・効率化の検討"
            else:
                purpose = "業務改善・効率化の検討"
        
        # 2. 具体的手段の抽出（文脈を保持して自然な表現に）
        methods = []
        
        # クライアント関連の手段
        client_patterns = [
            r'(クライアント|Client)ごとに(.{5,30}?)(?:を立ち上げ|プロジェクト)',
            r'(クライアント|Client)(?:ごと|別)に(.{5,25}?)(?:する|管理|運用)'
        ]
        
        for pattern in client_patterns:
            match = re.search(pattern, content)
            if match:
                action = match.group(2).strip()
                # 不完全な文字列をクリーンアップ
                action = re.sub(r'[、。].*$', '', action)  # 句読点以降を削除
                if len(action) > 3 and 'を' not in action[-2:]:  # 助詞で終わらないように
                    methods.append(f"クライアント別{action}管理")
                break
        
        # 蓄積・管理関連の手段（より具体的に）
        if '資料' in content and '蓄積' in content:
            methods.append("資料の一元管理")
        if '議事録' in content and '蓄積' in content:
            methods.append("議事録の蓄積")
        
        # コミュニケーション手段
        if 'チャット' in content and ('やりとり' in content or '課題' in content):
            methods.append("チャットでのやりとり")
        
        # ボイスモード関連
        if 'ボイスモード' in content or 'Voice Mode' in content:
            methods.append("ボイスモードでの相談")
        
        # 3. 期待効果の抽出（自然な表現で）
        effects = []
        
        # 課題解決関連
        if '課題' in content and ('解決' in content or '抽出' in content):
            effects.append("課題解決の実現")
        
        # 議題検討関連
        if 'ミーティング' in content and '議題' in content:
            effects.append("効率的な会議運営")
        
        # その他の効果
        if '方法' in content and '見出す' in content:
            effects.append("新手法の発見")
        
        # 要約の組み立て（自然な日本語になるよう調整）
        summary_parts = []
        
        # 主目的
        summary_parts.append(purpose)
        
        # 手段（最大2個、自然に繋がるように）
        if methods:
            if len(methods) == 1:
                summary_parts.append(methods[0])
            else:
                # 複数の手段を自然に統合
                method_summary = self._create_natural_method_summary(methods[:3])
                summary_parts.append(method_summary)
        
        # 効果
        if effects:
            summary_parts.append(effects[0])
        
        # 文字数制限と自然性チェック
        summary = " / ".join(summary_parts)
        
        # 不完全な文字列をクリーンアップ
        summary = self._clean_summary_text(summary)
            
        # === 段落・見出し語ベースの具体的ポイント生成 ===
        bullet_points = []
        
        # 1. 見出し構造の抽出（具体的な話題・セクション）
        headings = self._extract_concrete_headings(content)
        
        # 2. 重要な段落の要約抽出（50文字以上の意味のある段落）
        key_paragraphs = self._extract_key_paragraph_summaries(content)
        
        # 3. 具体的なキーワードと文脈の抽出
        concrete_points = self._extract_concrete_contextual_points(content)
        
        # 優先順位: 見出し > 段落要約 > 具体的ポイント
        bullet_points.extend(headings[:3])  # 最大3個の見出し
        bullet_points.extend(key_paragraphs[:3])  # 最大3個の段落要約
        bullet_points.extend(concrete_points[:3])  # 最大3個の具体ポイント
        
        # 重複除去と品質フィルタリング
        bullet_points = self._filter_and_deduplicate_points(bullet_points)
        
        # 最低3個を保証するフォールバック
        if len(bullet_points) < 3:
            fallback_points = [
                "重要なコンテンツの詳細な分析",
                "主要な議題と検討事項の整理", 
                "具体的なアクションプランの策定"
            ]
            for point in fallback_points:
                if len(bullet_points) < 3:
                    bullet_points.append(point)
        
        # 最大6個に制限
        bullet_points = bullet_points[:6]
        
        return {
            'bullet_points': bullet_points,
            'key_terms': important_terms[:5]
        }
    
    def _clean_summary_text(self, text: str) -> str:
        """要約テキストのクリーニング（不完全文字列の修正含む）"""
        # 不要な接続詞や冗長な表現を削除
        text = re.sub(r'^(また|そして|それから|つまり|要するに)', '', text)
        text = re.sub(r'(という|とか|など|みたい|ような)$', '', text)
        text = re.sub(r'。$', '', text)
        
        # 不完全な文字列を修正
        # "提供した資料をP" のような途切れた部分を修正
        text = re.sub(r'[をに][A-Za-z](?:[、/]|$)', 'の管理', text)  # "をP" → "の管理"
        text = re.sub(r'[をに][、]', 'と', text)  # "を、" → "と"
        
        # 連続する句読点を整理
        text = re.sub(r'[、]+', '、', text)
        text = re.sub(r'[。]+', '。', text)
        
        # 末尾の不完全な助詞を削除
        text = re.sub(r'[をにが、]$', '', text)
        
        return text.strip()
    
    def _clean_bullet_point(self, text: str) -> str:
        """箇条書きテキストのクリーニング"""
        # 括弧や引用符を削除
        text = re.sub(r'[「」『』（）()]', '', text)
        # 冗長な助詞を削除
        text = re.sub(r'(とか|など|みたいな|ような)$', '', text)
        # 連続する助詞を整理
        text = re.sub(r'(を|に|で|と|の){2,}', r'\1', text)
        return text.strip()
    
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
        """メモを実際に保存（編集内容保持対応）"""
        try:
            import tempfile
            from pathlib import Path
            import json
            
            # まず一時ファイルから編集済み分析結果を確認
            temp_edit_file = Path(tempfile.gettempdir()) / "memo_classifier_edited_analysis.json"
            if temp_edit_file.exists():
                try:
                    with open(temp_edit_file, 'r', encoding='utf-8') as f:
                        analysis = json.load(f)
                    print(f"💾 一時ファイルから編集済み内容を読み込み: {temp_edit_file}")
                    # 使用後は削除
                    temp_edit_file.unlink()
                except Exception as e:
                    print(f"⚠️ 一時ファイル読み込みエラー: {e}")
                    analysis = None
            else:
                analysis = None
            
            # 一時ファイルがない場合は通常の処理
            if not analysis:
                # 編集された分析結果があればそれを使用、なければ新規分析
                if self._last_edited_analysis:
                    print("💾 編集済み内容で保存実行...")
                    analysis = self._last_edited_analysis
                    # 保存成功後にクリアするため、ここではクリアしない
                else:
                    print("💾 新規分析で保存実行...")
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
                analysis['relations']['relations'],
                analysis.get('summary', {})  # 要約・箇条書きデータを追加
            )
            
            # Obsidian [[]] リンクを追加
            if analysis['relations']['relations']:
                self._add_obsidian_links(str(file_path), analysis['relations']['relations'])
            
            # 保存成功後に編集状態をクリア
            if self._last_edited_analysis:
                print("🗑️ 編集状態をクリア（保存完了）")
                self._last_edited_analysis = None
            
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
    
    def _save_memo_file(self, title: str, content: str, category: str, tags: list, relations: list, summary_data: dict = None) -> Path:
        """メモファイルを保存"""
        
        # ディレクトリ設定（実際のObsidianフォルダ構造に合わせて修正）
        folder_name = self.category_folders.get(category, 'Others')
        save_dir = Path(self.obsidian_path) / self.inbox_path / folder_name
        save_dir.mkdir(parents=True, exist_ok=True)
        
        # ファイル名生成（日付のみ、時分秒なし）
        timestamp = datetime.now().strftime('%Y%m%d')
        safe_title = re.sub(r'[<>:"/\\|?*]', '', title)
        safe_title = re.sub(r'\s+', '_', safe_title)
        filename = f"{timestamp}_{safe_title}.md"
        
        # ファイルパス
        file_path = save_dir / filename
        
        # ファイル内容構築
        file_content = self._build_markdown_content(title, content, category, tags, relations, summary_data)
        
        # ファイル保存
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(file_content)
        
        return file_path
    
    def _build_markdown_content(self, title: str, content: str, category: str, tags: list, relations: list, summary_data: dict = None) -> str:
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
        
        # 関連ファイル（冒頭に移動）
        if relations:
            lines.append('## 関連ファイル')
            lines.append('')
            for relation in relations:
                file_name = relation["file_name"]
                star_rating = relation.get('star_rating', '★★★')
                relation_type = relation.get("relation_type", "相互リンク")
                lines.append(f'- [[{file_name}]] {star_rating} ({relation_type})')
            lines.append('')
        
        # タグ表示
        if tags:
            lines.append(f'**タグ**: {" ".join(tags)}')
            lines.append('')
        
        # 具体的なポイント（段落・見出し語ベース）
        if summary_data and summary_data.get('bullet_points'):
            lines.append('## ポイント')
            lines.append('')
            for point in summary_data['bullet_points']:
                lines.append(f'- {point}')
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
        
        # 既存の関連ファイルセクションを安全に削除
        # 関連ファイルセクションの開始から次のセクションまたはファイル終端まで
        content = re.sub(r'\n## 関連ファイル\n.*?(?=\n## |\n---\n|$)', '', content, flags=re.DOTALL)
        # 末尾にある関連ファイルセクションも削除
        content = re.sub(r'\n## 関連ファイル\n.*$', '', content, flags=re.DOTALL)
        
        if not related_files:
            return content
        
        # 関連ファイルセクションを冒頭に配置するため、コンテンツを分析
        lines = content.split('\n')
        
        # タイトル行を見つける（# で始まる行）
        title_line_index = -1
        for i, line in enumerate(lines):
            if line.strip().startswith('# ') and not line.strip().startswith('##'):
                title_line_index = i
                break
        
        # 新しい関連ファイルセクションを構築
        links_section_lines = ["", "## 関連ファイル", ""]
        
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
            
            links_section_lines.append(f"- [[{file_name}]] {star_rating} {comment}")
        
        # タイトルの直後に関連ファイルセクションを挿入
        if title_line_index >= 0:
            # タイトル行の後に関連ファイルセクションを挿入
            new_lines = lines[:title_line_index + 1] + links_section_lines + lines[title_line_index + 1:]
            return '\n'.join(new_lines)
        else:
            # タイトル行が見つからない場合は末尾に追加（フォールバック）
            return content + '\n\n' + '\n'.join(links_section_lines)
    
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
                    new_link = f"- [[{source_name}]] {star_rating} (相互リンク)"
                    
                    # 関連ファイルセクションの最後に追加
                    rel_content = re.sub(
                        r'(## 関連ファイル\n\n(?:[^\n]*\n)*)',
                        r'\1' + new_link + '\n',
                        rel_content
                    )
                else:
                    # 新しいセクションをタイトル直後に作成
                    star_rating = rel_file.get('star_rating', '★★★')
                    rel_lines = rel_content.split('\n')
                    
                    # タイトル行を見つける
                    title_line_index = -1
                    for i, line in enumerate(rel_lines):
                        if line.strip().startswith('# ') and not line.strip().startswith('##'):
                            title_line_index = i
                            break
                    
                    if title_line_index >= 0:
                        # タイトル直後に関連ファイルセクションを挿入
                        links_section = ["", "## 関連ファイル", "", f"- [[{source_name}]] {star_rating} (相互リンク)"]
                        new_lines = rel_lines[:title_line_index + 1] + links_section + rel_lines[title_line_index + 1:]
                        rel_content = '\n'.join(new_lines)
                    else:
                        # フォールバック: 末尾に追加
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
        
        # 実際の保存先フォルダを追加
        actual_folder = processor.category_folders.get(result['category']['name'], 'Others')
        print(f"FOLDER:{actual_folder}")
        
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
        
        # 要約情報を出力
        summary_info = result.get('summary', {})
        summary_text = summary_info.get('summary', '')
        bullet_points = summary_info.get('bullet_points', [])
        
        print(f"SUMMARY:{summary_text}")
        if bullet_points:
            print(f"BULLET_POINTS:{' | '.join(bullet_points)}")
        else:
            print("BULLET_POINTS:なし")
            
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