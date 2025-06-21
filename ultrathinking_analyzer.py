#!/usr/bin/env python3
"""
Ultrathinking Analyzer - 深層的な文書分析モジュール
文脈理解と関係性分析により、より正確なタイトル生成とタグ付けを実現
"""

import re
from typing import Dict, List, Set, Tuple, Any
from collections import Counter, defaultdict
import json
from datetime import datetime


class UltrathinkingAnalyzer:
    """Ultrathinking による深層的な内容分析"""
    
    def __init__(self):
        # ドキュメントタイプ認識パターン
        self.document_patterns = {
            'report': {
                'markers': ['レポート', '分析', '概要', '調査', '結果', '報告書'],
                'structure_patterns': [
                    r'【.*】',  # セクションヘッダー
                    r'^\d+\.',  # 番号付きリスト
                    r'■|▶|◆|📊|📈|📋',  # 構造化マーカー
                    r'^#{1,3}\s',  # Markdownヘッダー
                ],
                'content_patterns': [
                    'データ', '指標', '結果', '成果', '評価', '数値', '統計', 'KPI'
                ]
            },
            'meeting_notes': {
                'markers': ['会議', '打ち合わせ', 'ミーティング', '議事録', '相談', '面談'],
                'structure_patterns': [
                    r'日時[:：]', r'参加者[:：]', r'議題[:：]', r'場所[:：]'
                ],
                'content_patterns': [
                    '決定事項', '次回', 'アクション', 'TODO', '宿題', '確認事項'
                ]
            },
            'analysis': {
                'markers': ['分析', '考察', '評価', '検証', '診断', '検討'],
                'structure_patterns': [
                    r'課題[:：]', r'解決策[:：]', r'提案[:：]', r'原因[:：]'
                ],
                'content_patterns': [
                    '問題点', '改善', '効果', '影響', '要因', '対策'
                ]
            },
            'plan': {
                'markers': ['計画', '予定', 'プラン', '戦略', 'ロードマップ'],
                'structure_patterns': [
                    r'目標[:：]', r'期限[:：]', r'ステップ\d+', r'フェーズ\d+'
                ],
                'content_patterns': [
                    '目標', '達成', 'マイルストーン', '期限', 'スケジュール'
                ]
            },
            'memo': {
                'markers': ['メモ', '備忘録', 'ノート', '記録'],
                'structure_patterns': [
                    r'^・', r'^-\s', r'^\*\s'  # 箇条書き
                ],
                'content_patterns': [
                    '思考', 'アイデア', '気づき', '注意', '覚え'
                ]
            }
        }
        
        # 関係性パターン
        self.relation_patterns = {
            'causal': [
                r'(.+?)のため(.+?)',
                r'(.+?)により(.+?)',
                r'(.+?)の結果(.+?)',
                r'(.+?)が原因で(.+?)'
            ],
            'temporal': [
                r'(.+?)の後(.+?)',
                r'(.+?)する前に(.+?)',
                r'(.+?)してから(.+?)',
                r'まず(.+?)、次に(.+?)'
            ],
            'conditional': [
                r'もし(.+?)なら(.+?)',
                r'(.+?)の場合(.+?)',
                r'(.+?)すると(.+?)'
            ]
        }
    
    def analyze_content(self, content: str) -> Dict[str, Any]:
        """多層的な内容分析"""
        
        # Phase 1: 表層分析
        surface_analysis = self._surface_analysis(content)
        
        # Phase 2: 文脈理解
        context_analysis = self._context_analysis(content)
        
        # Phase 3: 関係性分析
        relation_analysis = self._relation_analysis(content)
        
        # Phase 4: 意味統合
        semantic_integration = self._semantic_integration(
            surface_analysis, context_analysis, relation_analysis, content
        )
        
        # Phase 5: 出力生成
        return self._generate_intelligent_output(
            surface_analysis, context_analysis, relation_analysis, semantic_integration, content
        )
    
    def _surface_analysis(self, content: str) -> Dict[str, Any]:
        """表層的な要素の抽出"""
        return {
            'sentence_count': len(re.split(r'[。．！？\n]', content)),
            'word_frequency': self._calculate_word_frequency(content),
            'sentence_structures': self._analyze_sentence_structures(content),
            'key_phrases': self._extract_key_phrases(content)
        }
    
    def _context_analysis(self, content: str) -> Dict[str, Any]:
        """文脈の理解"""
        return {
            'document_type': self._identify_document_type(content),
            'main_topic': self._extract_main_topic(content),
            'subtopics': self._extract_subtopics(content),
            'intent': self._detect_intent(content),
            'domain': self._identify_domain(content),
            'tone': self._analyze_tone(content)
        }
    
    def _relation_analysis(self, content: str) -> Dict[str, Any]:
        """関係性の分析"""
        return {
            'entity_relations': self._analyze_entity_relations(content),
            'temporal_flow': self._analyze_temporal_flow(content),
            'causal_relations': self._extract_causal_relations(content),
            'hierarchical_structure': self._analyze_hierarchy(content)
        }
    
    def _semantic_integration(self, surface: Dict, context: Dict, 
                            relation: Dict, content: str) -> Dict[str, Any]:
        """意味の統合"""
        return {
            'coherent_theme': self._integrate_themes(surface, context),
            'key_insights': self._extract_key_insights(relation),
            'implicit_meanings': self._infer_implicit_meanings(content, context),
            'action_items': self._extract_action_items(content)
        }
    
    def _identify_document_type(self, content: str) -> Dict[str, Any]:
        """文書タイプの高精度識別"""
        scores = {}
        
        for doc_type, patterns in self.document_patterns.items():
            score = 0
            matched_patterns = []
            
            # マーカーの存在確認
            for marker in patterns['markers']:
                if marker in content:
                    score += 3
                    matched_patterns.append(f"marker:{marker}")
            
            # 構造パターンの確認
            for pattern in patterns['structure_patterns']:
                matches = re.findall(pattern, content, re.MULTILINE)
                if matches:
                    score += 2 * len(matches)
                    matched_patterns.append(f"structure:{pattern}")
            
            # 内容パターンの確認
            for pattern in patterns['content_patterns']:
                if pattern in content:
                    score += 1
                    matched_patterns.append(f"content:{pattern}")
            
            scores[doc_type] = {
                'score': score,
                'matched_patterns': matched_patterns
            }
        
        # 最高スコアのタイプを決定
        if scores:
            best_type = max(scores, key=lambda x: scores[x]['score'])
            total_score = sum(s['score'] for s in scores.values())
            confidence = scores[best_type]['score'] / total_score if total_score > 0 else 0
            
            return {
                'type': best_type,
                'confidence': confidence,
                'scores': scores,
                'matched_patterns': scores[best_type]['matched_patterns']
            }
        else:
            return {
                'type': 'general',
                'confidence': 0.1,
                'scores': {},
                'matched_patterns': []
            }
    
    def _extract_main_topic(self, content: str) -> Dict[str, Any]:
        """文書の主題を知的に抽出"""
        title_candidates = []
        
        # パターン1: 明示的なタイトル表記
        explicit_patterns = [
            (r'【(.+?)】', 0.9),
            (r'^#\s+(.+?)$', 0.85),
            (r'^##\s+(.+?)$', 0.8),
            (r'■\s*(.+?)(?:\n|$)', 0.75)
        ]
        
        for pattern, confidence in explicit_patterns:
            match = re.search(pattern, content, re.MULTILINE)
            if match:
                title_candidates.append({
                    'text': match.group(1).strip(),
                    'confidence': confidence,
                    'method': 'explicit_title',
                    'position': match.start()
                })
        
        # パターン2: 第一文の主題（固有名詞保護）
        sentences = re.split(r'[。．！？\n]', content)
        
        # メタデータ行をスキップするパターン
        metadata_patterns = [
            r'^作成日[:：]\s*\d{4}-\d{2}-\d{2}',
            r'^更新日[:：]\s*\d{4}-\d{2}-\d{2}',
            r'^実装者[:：]',
            r'^ステータス[:：]',
            r'^日時[:：]',
            r'^場所[:：]',
            r'^参加者[:：]',
            r'^タグ[:：]',
            r'^カテゴリ[:：]',
            r'^作成者[:：]',
            r'^著者[:：]',
            r'^修正日[:：]',
            r'^version[:：]',
            r'^Version[:：]',
            r'^バージョン[:：]',
            r'^Created[:：]',
            r'^Updated[:：]',
            r'^Date[:：]',
            r'^Tags[:：]',
            r'^Category[:：]'
        ]
        
        # メタデータでない最初の意味のある文を見つける
        first_meaningful_sentence = None
        for sentence in sentences:
            sentence_stripped = sentence.strip()
            if not sentence_stripped:
                continue
            
            # メタデータ行かチェック
            is_metadata = False
            for meta_pattern in metadata_patterns:
                if re.match(meta_pattern, sentence_stripped):
                    is_metadata = True
                    break
            
            if not is_metadata and 10 < len(sentence_stripped) < 100:
                first_meaningful_sentence = sentence_stripped
                break
        
        if first_meaningful_sentence:
                # 固有名詞を含む場合は優先度を上げる
                confidence = 0.7
                tech_keywords = ['Claude Code', 'ChatGPT', 'GitHub', 'Anthropic', 'OpenAI']
                if any(keyword in first_meaningful_sentence for keyword in tech_keywords):
                    confidence = 0.85
                
                # 主語と述語の関係を分析
                subject_predicate = self._extract_subject_predicate(first_meaningful_sentence)
                if subject_predicate:
                    title_text = self._format_title_from_sp(subject_predicate)
                    title_candidates.append({
                        'text': title_text,
                        'confidence': confidence,
                        'method': 'subject_predicate',
                        'position': 0
                    })
                else:
                    # 主語述語抽出に失敗した場合、第一文をそのまま使用
                    title_candidates.append({
                        'text': first_meaningful_sentence,
                        'confidence': confidence * 0.8,
                        'method': 'first_sentence_direct',
                        'position': 0
                    })
        
        # パターン3: キーフレーズの組み合わせ
        key_phrases = self._extract_key_phrases(content)
        if key_phrases:
            combined_title = self._combine_key_phrases_to_title(key_phrases)
            if combined_title:
                title_candidates.append({
                    'text': combined_title,
                    'confidence': 0.5,
                    'method': 'key_phrase_combination',
                    'position': -1
                })
        
        # 最適な候補を選択
        if title_candidates:
            # 位置（前の方が高い）と信頼度を考慮
            best_candidate = max(title_candidates, 
                               key=lambda x: x['confidence'] - (x['position'] / 1000 if x['position'] >= 0 else 0))
            return best_candidate
        else:
            return {
                'text': 'メモ',
                'confidence': 0.1,
                'method': 'fallback',
                'position': -1
            }
    
    def _extract_subject_predicate(self, sentence: str) -> Dict[str, str]:
        """文から主語と述語を抽出（品質チェック強化版）"""
        # 品質チェック：不正な断片化を防ぐ
        if not sentence or len(sentence.strip()) < 8:
            return None
        
        # 英語・技術固有名詞の保護パターン
        protected_words = [
            'Consulting', 'ChatGPT', 'Claude Code', 'Claude', 'GitHub', 'Obsidian', 
            'Twitter', 'Instagram', 'Facebook', 'LinkedIn', 'TikTok', 'YouTube', 
            'Google', 'Microsoft', 'Apple', 'Amazon', 'Netflix', 'Spotify',
            'Anthropic', 'OpenAI', 'React', 'TypeScript', 'JavaScript', 'Python',
            'Docker', 'Kubernetes', 'AWS', 'Azure', 'GCP'
        ]
        
        # 簡易的な主語・述語抽出
        patterns = [
            r'(.+?[はがを])(.+)',
            r'(.+?)について(.+)',
            r'(.+?)に関する(.+)',
            r'(.+?)における(.+)'
        ]
        
        for pattern in patterns:
            match = re.match(pattern, sentence)
            if match:
                subject = match.group(1).strip()
                predicate = match.group(2).strip()
                
                # 主語から助詞を除去
                subject = re.sub(r'[はがを]$', '', subject)
                
                # 品質チェック：不正な断片化防止
                if self._is_fragmented_word(subject, protected_words):
                    continue
                
                # 品質チェック：短すぎる断片を排除
                if len(subject) < 3 or len(predicate) < 2:
                    continue
                
                # 品質チェック：意味のない断片を排除
                if self._is_meaningless_fragment(subject) or self._is_meaningless_fragment(predicate):
                    continue
                
                # 長すぎる場合は短縮（日本語に適した長さ）
                if len(subject) > 50:
                    subject = subject[:47] + '...'
                if len(predicate) > 60:
                    predicate = predicate[:57] + '...'
                
                return {
                    'subject': subject,
                    'predicate': predicate
                }
        
        return None
    
    def _is_fragmented_word(self, fragment: str, protected_words: List[str]) -> bool:
        """固有名詞の断片化を検出"""
        fragment_lower = fragment.lower()
        for word in protected_words:
            word_lower = word.lower()
            # 固有名詞の一部が断片として抽出された場合を検出
            if (fragment_lower in word_lower and 
                fragment_lower != word_lower and 
                len(fragment) < len(word) * 0.8):
                return True
        return False
    
    def _is_meaningless_fragment(self, fragment: str) -> bool:
        """意味のない断片を検出"""
        meaningless_patterns = [
            r'^[ぁ-ん]{1,2}$',     # ひらがな1-2文字
            r'^[。、！？]+$',        # 句読点のみ
            r'^[0-9]+$',           # 数字のみ
            r'^[a-zA-Z]{1,3}$',    # 短い英字
            r'^[ー・]+$'           # 記号のみ
        ]
        
        for pattern in meaningless_patterns:
            if re.match(pattern, fragment.strip()):
                return True
        return False
    
    def _format_title_from_sp(self, sp: Dict[str, str]) -> str:
        """主語述語からタイトルを生成"""
        subject = sp['subject']
        predicate = sp['predicate']
        
        # 述語の活用形を名詞形に変換
        predicate_noun = self._convert_to_noun_form(predicate)
        
        # より自然なタイトル形式を選択
        total_length = len(subject) + len(predicate_noun)
        
        # 述語が空の場合は主語のみ
        if not predicate_noun or predicate_noun.strip() == '':
            return subject
        
        if total_length < 45:
            # 短い場合は「の」で接続
            if predicate_noun and predicate_noun != predicate:
                return f"{subject}の{predicate_noun}"
            else:
                # 述語が変換されなかった場合は適切に結合
                return f"{subject}：{predicate_noun}"
        else:
            # 長い場合は「-」で接続
            return f"{subject} - {predicate_noun}"
    
    def _convert_to_noun_form(self, predicate: str) -> str:
        """述語を名詞形に変換"""
        # より自然な変換規則（空になることを防ぐ）
        conversions = {
            'しました': 'の実施',
            'します': 'の実施', 
            'した': '',
            'する': '',
            'です': '',
            'ます': '',
            'ました': 'の完了',
            'ています': '中',
            'ている': '中',
            'でした': '',
            'である': '',
            'について': '',
            'に関して': '',
            'に関する': ''
        }
        
        # まず語尾を除去
        cleaned = predicate
        for pattern, replacement in conversions.items():
            if cleaned.endswith(pattern):
                cleaned = cleaned[:-len(pattern)] + replacement
                break
        
        # 空になった場合は元の述語を使用
        if not cleaned.strip():
            cleaned = predicate
        
        return cleaned
    
    def _extract_causal_relations(self, content: str) -> List[Dict[str, Any]]:
        """因果関係の抽出"""
        relations = []
        
        for relation_type, patterns in self.relation_patterns.items():
            for pattern in patterns:
                matches = re.finditer(pattern, content)
                for match in matches:
                    if len(match.groups()) >= 2:
                        relations.append({
                            'type': relation_type,
                            'from': match.group(1).strip(),
                            'to': match.group(2).strip() if len(match.groups()) >= 2 else '',
                            'pattern': pattern,
                            'position': match.start()
                        })
        
        return relations
    
    def _generate_contextual_tags(self, analysis_results: Dict[str, Any]) -> List[str]:
        """Ultrathinking: AIによる動的内容理解に基づくタグ生成"""
        try:
            # 元のコンテンツを取得（後方互換性確保）
            content = analysis_results.get('original_content', '')
            if not content:
                # フォールバック：従来のロジックを使用
                return self._generate_fallback_tags(analysis_results)
            
            # AI判断による意味的タグ生成
            semantic_tags = self._generate_semantic_tags(content)
            
            # 技術固有名詞の検出
            tech_tags = self._extract_technical_terms(content)
            
            # 一般的すぎるタグの除外
            filtered_tags = self._filter_meaningful_tags(semantic_tags + tech_tags, content)
            
            # ログ出力
            print(f"🏷️ Ultrathinking タグ生成: {filtered_tags[:6]}...")
            
            return filtered_tags[:8]  # 上位8個に限定
            
        except Exception as e:
            print(f"⚠️ タグ生成エラー: {e}")
            # エラー時は従来方式にフォールバック
            return self._generate_fallback_tags(analysis_results)
    
    def _generate_fallback_tags(self, analysis_results: Dict[str, Any]) -> List[str]:
        """従来方式のタグ生成（フォールバック用）"""
        tags = []
        tag_scores = defaultdict(float)
        
        # 一般的すぎるタグのブラックリスト（拡張版）
        generic_tags = {
            # 基本的すぎる語彙
            '#メモ', '#記録', '#ノート', '#思考', '#内容', '#情報', '#データ', 
            '#こと', '#もの', '#とき', '#ところ', '#ため', '#よう', '#時間',
            '#状況', '#方法', '#結果', '#場合', '#問題', '#理由', '#必要',
            '#重要', '#確認', '#関係', '#会社', '#仕事', '#今回', '#今日',
            '#最近', '#現在', '#以下', '#以上', '#について', '#一般', '#全体',
            '#分析', '#レポート', '#TODO', '#アクション', '#因果関係', '#課題',
            # 追加: 過度に一般的な語彙
            '#考察', '#検討', '#実践', '#活用', '#効率', '#改善', '#対策',
            '#過去', '#将来', '#管理', '#システム', '#ツール', '#機能',
            '#作成', '#設定', '#操作', '#処理', '#対応', '#実施', '#導入',
            '#作業中', '#一時ファイル', '#詳細', '#概要', '#基本', '#応用'
        }
        
        # 特定性の高いタグの優先スコア
        specific_bonus = {
            'proper_nouns': 3.0,    # 固有名詞
            'technical_terms': 2.5, # 技術用語
            'domain_specific': 2.0,  # ドメイン特化
            'unique_concepts': 1.5   # 独特の概念
        }
        
        # 1. ドキュメントタイプに基づくタグ
        doc_type = analysis_results['context_analysis']['document_type']['type']
        doc_confidence = analysis_results['context_analysis']['document_type']['confidence']
        
        if doc_confidence > 0.5:
            doc_type_tags = {
                'report': ['#レポート', '#分析'],
                'meeting_notes': ['#会議', '#議事録'],
                'analysis': ['#分析', '#考察'],
                'plan': ['#計画', '#戦略'],
                'memo': ['#メモ', '#備忘録']
            }
            for tag in doc_type_tags.get(doc_type, []):
                tag_scores[tag] += 3.0 * doc_confidence
        
        # 2. 主題に基づくタグ
        main_topic = analysis_results['context_analysis']['main_topic']
        if main_topic['confidence'] > 0.5:
            # 主題から重要な名詞を抽出
            topic_nouns = self._extract_nouns_from_text(main_topic['text'])
            for noun in topic_nouns[:3]:
                candidate_tag = f"#{noun}"
                # 一般的すぎるタグと文字数チェック
                if candidate_tag not in generic_tags and len(noun) >= 2:
                    tag_scores[candidate_tag] += 2.5
        
        # 3. キーフレーズからのタグ
        key_phrases = analysis_results['surface_analysis'].get('key_phrases', [])
        for phrase in key_phrases[:5]:
            if 2 <= len(phrase) <= 10:
                candidate_tag = f"#{phrase}"
                # 一般的すぎるタグをチェック
                if candidate_tag not in generic_tags:
                    tag_scores[candidate_tag] += 2.0
        
        # 4. 関係性に基づくタグ（一般的タグを避ける）
        relations = analysis_results['relation_analysis'].get('causal_relations', [])
        if relations:
            # 「因果関係」や「分析」は一般的すぎるので除外
            pass
        
        # 5. アクションアイテムタグ（一般的タグを避ける）
        action_items = analysis_results['semantic_integration'].get('action_items', [])
        if action_items:
            # 「TODO」や「アクション」は一般的すぎるので除外
            pass
        
        # 6. 特定性評価とボーナス適用
        for tag, score in tag_scores.items():
            tag_content = tag[1:] if tag.startswith('#') else tag
            
            # 固有名詞ボーナス（英語、カタカナ、人名等）
            if re.match(r'^[A-Z][a-zA-Z]+$', tag_content) or re.match(r'^[ァ-ヶー]{3,}$', tag_content):
                tag_scores[tag] += specific_bonus['proper_nouns']
            
            # 技術用語ボーナス（強化版）
            tech_patterns = [
                'AI', 'DX', 'API', 'ChatGPT', 'Claude Code', 'Claude', 'GitHub', 
                'Anthropic', 'OpenAI', 'Python', 'JavaScript', 'TypeScript', 'React',
                'Docker', 'Kubernetes', 'AWS', 'Azure', 'GCP', 'プロンプト',
                'エンジニアリング', 'プログラミング', 'アーキテクチャ', 'フレームワーク',
                'ライブラリ', 'リポジトリ', 'コマンドライン', 'CLI', 'IDE',
                'デバッグ', 'リファクタリング', 'CI/CD', 'DevOps'
            ]
            if any(pattern in tag_content for pattern in tech_patterns):
                tag_scores[tag] += specific_bonus['technical_terms']
            
            # ドメイン特化ボーナス
            domain_patterns = ['塾', '講師', '独立', '教育', 'Consulting', 'EdTech']
            if any(pattern in tag_content for pattern in domain_patterns):
                tag_scores[tag] += specific_bonus['domain_specific']
        
        # 7. 最終フィルタリング: 一般的すぎるタグを除外
        filtered_tag_scores = {}
        for tag, score in tag_scores.items():
            # 一般的タグと低スコアタグを除外
            if tag not in generic_tags and score >= 2.0:  # 閾値を2.0に上げて品質重視
                # 単一文字や記号のみのタグも除外
                tag_content = tag[1:] if tag.startswith('#') else tag
                if len(tag_content) >= 2 and not tag_content.isdigit():
                    # 追加の品質チェック
                    if not self._is_too_generic(tag_content):
                        filtered_tag_scores[tag] = score
        
        # スコアでソートして上位を選択
        sorted_tags = sorted(filtered_tag_scores.items(), key=lambda x: x[1], reverse=True)
        unique_tags = []
        seen = set()
        
        for tag, score in sorted_tags:
            if tag not in seen and len(unique_tags) < 6:  # 最大6個に制限
                unique_tags.append(tag)
                seen.add(tag)
        
        return unique_tags
    
    def _generate_semantic_tags(self, content: str) -> List[str]:
        """Ultrathinking: 内容の意味的理解に基づくタグ生成"""
        tags = []
        content_lower = content.lower()
        
        # 固有名詞・技術用語の優先抽出
        if 'Claude Code' in content:
            tags.append('#Claude Code')
        if 'ChatGPT' in content:
            tags.append('#ChatGPT')
        if 'Anthropic' in content:
            tags.append('#Anthropic')
        if 'OpenAI' in content:
            tags.append('#OpenAI')
        
        # 技術領域の特定的タグ
        if any(term in content_lower for term in ['プロンプトエンジニアリング', 'プロンプト設計']):
            tags.append('#プロンプトエンジニアリング')
        if any(term in content_lower for term in ['ナレッジマネジメント', '知見管理', '知識蓄積']):
            tags.append('#ナレッジマネジメント')
        if any(term in content_lower for term in ['開発手法', '開発プロセス']):
            tags.append('#開発手法')
        
        # ビジネス領域の特定的タグ
        if any(term in content_lower for term in ['snsマーケティング', 'sns戦略', 'ソーシャルメディア']):
            tags.append('#SNSマーケティング')
        if any(term in content_lower for term in ['フォロワー獲得', 'エンゲージメント戦略']):
            tags.append('#SNS戦略')
        if any(term in content_lower for term in ['教育ビジネス', '塾経営', '講師ビジネス']):
            tags.append('#教育ビジネス')
        
        # 学習・教育領域の特定的タグ
        if any(term in content_lower for term in ['教育dx', '学習塾dx', 'edtech']):
            tags.append('#教育DX')
        if any(term in content_lower for term in ['講師独立', '教育起業', '塾講師独立']):
            tags.append('#講師独立')
        if any(term in content_lower for term in ['学習支援', '個別指導', 'オンライン授業']):
            tags.append('#学習支援')
        
        # コンサルティング領域の特定的タグ
        if any(term in content_lower for term in ['戦略コンサルティング', 'ビジネス戦略']):
            tags.append('#戦略コンサルティング')
        if any(term in content_lower for term in ['業務改善', 'プロセス改善']):
            tags.append('#業務改善')
        
        # 情報管理・思考法領域の特定的タグ
        if any(term in content_lower for term in ['手書き', '手書きの有用性', '手書きメモ']):
            tags.append('#手書き')
        if any(term in content_lower for term in ['デジタル化', 'デジタル管理', 'アナログとデジタル']):
            tags.append('#デジタル化')
        if any(term in content_lower for term in ['情報整理', '情報管理', '整理手法']):
            tags.append('#情報整理手法')
        if any(term in content_lower for term in ['アナログ', 'アナログ思考', '手書き思考']):
            tags.append('#アナログ思考')
        if any(term in content_lower for term in ['思考整理', '発想法', '思考プロセス']):
            tags.append('#思考プロセス')
        
        return tags[:4]  # セマンティックタグは最大4個
    
    def _extract_technical_terms(self, content: str) -> List[str]:
        """Ultrathinking: 技術固有名詞の抽出"""
        tags = []
        
        # 技術ツール・サービス
        tech_terms = {
            'Claude Code': '#Claude Code',
            'Claude': '#Claude', 
            'ChatGPT': '#ChatGPT',
            'GitHub': '#GitHub',
            'Obsidian': '#Obsidian',
            'Anthropic': '#Anthropic',
            'OpenAI': '#OpenAI',
            'Python': '#Python',
            'JavaScript': '#JavaScript',
            'TypeScript': '#TypeScript',
            'React': '#React',
            'Docker': '#Docker',
            'Kubernetes': '#Kubernetes'
        }
        
        for term, tag in tech_terms.items():
            if term in content:
                tags.append(tag)
        
        # 技術概念
        tech_concepts = {
            'プロンプトエンジニアリング': '#プロンプトエンジニアリング',
            'AIアシスタント': '#AIアシスタント',
            'コマンドライン': '#CLI',
            'デバッグ': '#デバッグ',
            'リファクタリング': '#リファクタリング',
            'アーキテクチャ': '#アーキテクチャ'
        }
        
        for concept, tag in tech_concepts.items():
            if concept in content:
                tags.append(tag)
        
        return tags[:3]  # 技術用語タグは最大3個
    
    def _filter_meaningful_tags(self, candidate_tags: List[str], content: str) -> List[str]:
        """Ultrathinking: 意味のあるタグのみをフィルタリング"""
        
        # 包括的な一般的タグ・断片タグの除外リスト
        generic_blacklist = {
            # 基本的すぎる語彙（ユーザー指摘の「重要」「アイデア」「記録」を強化）
            '#メモ', '#記録', '#ノート', '#思考', '#内容', '#情報', '#データ',
            '#分析', '#レポート', '#TODO', '#アクション', '#因果関係', '#課題',
            '#考察', '#検討', '#実践', '#活用', '#効率', '#改善', '#対策',
            '#管理', '#システム', '#ツール', '#機能', '#処理', '#対応', '#実行',
            '#作成', '#設定', '#操作', '#確認', '#重要', '#評価', '#品質',
            '#アイデア', '#発想', '#思考', '#感情', '#印象', '#違和感', '#ニュアンス',
            '#一般', '#普遍', '#基本', '#単語', '#概念', '#要素', '#項目',
            
            # 文脈断片タグ（ユーザー指摘事項）
            '#過去の試行錯誤', '#で効率的に開発するた', '#めの知見管理',
            '#作業中の一時ファ', '#の背景', '#チーム連携の改善',
            '#技術選定理由', '#品質の向上',
            
            # 時間・状況の一般語
            '#今回', '#今日', '#最近', '#現在', '#以下', '#以上', '#について',
            '#一般', '#全体', '#場合', '#時間', '#状況', '#方法', '#結果',
            
            # 動作の一般語
            '#する', '#した', '#なる', '#ある', '#いる', '#使う', '#見る'
        }
        
        # 重複除去と品質チェック
        filtered_tags = []
        seen_tags = set()
        
        for tag in candidate_tags:
            if tag and tag not in seen_tags and tag not in generic_blacklist:
                # 文字数チェック（短すぎる・長すぎるタグを除外）
                tag_content = tag[1:] if tag.startswith('#') else tag
                if 2 <= len(tag_content) <= 20:  # 範囲を拡張
                    # 断片・一般語チェック
                    if not self._is_meaningless_fragment(tag_content):
                        filtered_tags.append(tag)
                        seen_tags.add(tag)
        
        return filtered_tags[:6]  # 最終的に最大6個まで
    
    def _is_too_generic(self, tag_content: str) -> bool:
        """タグが一般的すぎるかを判定"""
        # 一般的すぎる動詞
        generic_verbs = ['する', 'した', 'なる', 'ある', 'いる', '使う', '見る', '来る']
        
        # 一般的すぎる名詞
        generic_nouns = ['事', '物', '人', '所', '時', '話', '事項', '内容', '状態', '状況']
        
        # 短すぎる、または一般的すぎる場合は除外
        if len(tag_content) <= 1:
            return True
        
        if tag_content in generic_verbs or tag_content in generic_nouns:
            return True
        
        # ひらがなのみで3文字以下は除外
        if re.match(r'^[ぁ-ん]{1,3}$', tag_content):
            return True
        
        # 数字のみ、記号のみは除外
        if tag_content.isdigit() or not re.search(r'[ぁ-んァ-ヶー一-龯A-Za-z]', tag_content):
            return True
        
        return False
    
    def _is_meaningless_fragment(self, tag_content: str) -> bool:
        """意味のない断片タグかを判定"""
        # 部分的な語句や助詞が含まれている断片
        fragment_patterns = [
            r'^(で|の|に|が|を|は|と|から|まで|より|など).*',  # 助詞で始まる
            r'.*(で|の|に|が|を|は|と|から|まで|より)$',     # 助詞で終わる
            r'^(た|て|だ|で|する|した|なる|ある)$',          # 動詞活用のみ
            r'^[ぁ-ん]{1,2}$',                           # ひらがな1-2文字
            r'^(一時|作業中|背景|理由|向上|改善)$'            # 一般的すぎる単語
        ]
        
        for pattern in fragment_patterns:
            if re.match(pattern, tag_content):
                return True
        
        # 意味不明な短縮形
        if len(tag_content) <= 2 and not re.match(r'^[A-Z]{2,}$|^[ァ-ヶー]{2,}$', tag_content):
            return True
        
        return False
    
    def _extract_proper_nouns(self, content: str) -> List[str]:
        """固有名詞の抽出（技術用語・サービス名優先）"""
        proper_nouns = []
        
        # 技術サービス・ツール名（完全一致）
        tech_services = [
            'Claude Code', 'ChatGPT', 'GitHub Copilot', 'Anthropic', 'OpenAI',
            'Google Bard', 'Microsoft Copilot', 'Notion AI', 'Cursor', 'Replit',
            'Vercel', 'Netlify', 'Supabase', 'Firebase', 'AWS', 'Azure', 'GCP'
        ]
        
        for service in tech_services:
            if service in content:
                proper_nouns.append(service)
        
        # プログラミング言語・フレームワーク
        tech_terms = [
            'Python', 'JavaScript', 'TypeScript', 'React', 'Vue.js', 'Angular',
            'Node.js', 'Express', 'Django', 'Flask', 'Spring Boot', 'Laravel',
            'Docker', 'Kubernetes', 'PostgreSQL', 'MongoDB', 'Redis'
        ]
        
        for term in tech_terms:
            if term in content:
                proper_nouns.append(term)
        
        # カタカナ固有名詞（3文字以上）
        katakana_pattern = r'[ァ-ヶー]{3,}(?:[ァ-ヶー\s]*[ァ-ヶー]{1,})*'
        katakana_matches = re.findall(katakana_pattern, content)
        for match in katakana_matches:
            clean_match = match.strip()
            if len(clean_match) >= 3:
                proper_nouns.append(clean_match)
        
        # 英語固有名詞（大文字開始、2文字以上）
        english_pattern = r'\b[A-Z][a-zA-Z]{1,}(?:\s+[A-Z][a-zA-Z]+)*\b'
        english_matches = re.findall(english_pattern, content)
        for match in english_matches:
            if len(match) >= 2 and not match.lower() in ['the', 'and', 'for', 'with']:
                proper_nouns.append(match)
        
        # 重複除去と優先度順ソート
        unique_nouns = []
        seen = set()
        
        # 技術サービス優先
        for noun in proper_nouns:
            if noun not in seen and noun in tech_services:
                unique_nouns.append(noun)
                seen.add(noun)
        
        # その他の固有名詞
        for noun in proper_nouns:
            if noun not in seen:
                unique_nouns.append(noun)
                seen.add(noun)
        
        return unique_nouns[:3]  # 上位3つまで
    
    def _extract_meaningful_title(self, content: str, proper_nouns: List[str]) -> str:
        """コンテンツの中核キーワードと関連語で完結した意味のあるタイトルを生成"""
        content_lower = content.lower()
        
        # 中核となるキーワードを特定
        core_keywords = self._identify_core_keywords(content, proper_nouns)
        
        # パターン1: 目的・方法論を示すフレーズ（完結した文として）
        purpose_patterns = [
            r'(.{10,50}?)のための(.{5,30}?)(?:方法|手法|システム|ツール|ガイド|コツ)',
            r'(.{5,30}?)で(.{5,30}?)(?:を実現|を効率化|を管理|を活用)(?:する|させる)?',
            r'(.{5,30}?)による(.{5,30}?)(?:の|を)(.{5,30}?)(?:管理|運用|活用|構築)',
        ]
        
        for pattern in purpose_patterns:
            matches = re.findall(pattern, content, re.MULTILINE)
            for match in matches:
                if len(match) >= 2:
                    parts = [part.strip() for part in match if part.strip()]
                    # 固有名詞を含む場合は優先
                    if any(any(noun in part for noun in proper_nouns) for part in parts):
                        if len(parts) == 2:
                            return f"{parts[0]}による{parts[1]}"
                        elif len(parts) >= 3:
                            return f"{parts[0]}による{parts[1]}の{parts[2]}"
        
        # パターン2: 完結した説明文構造
        explanation_patterns = [
            r'(.{5,40}?)(?:について|に関する|における)(.{5,30}?)(?:の|を)(.{5,30}?)(?:方法|手法|ガイド|システム)',
            r'(.{5,40}?)(?:での|による|を使った)(.{5,30}?)(?:の|を)(.{5,30}?)(?:実践|活用|運用|管理)',
        ]
        
        for pattern in explanation_patterns:
            matches = re.findall(pattern, content)
            for match in matches:
                parts = [part.strip() for part in match if part.strip()]
                # 固有名詞を含む場合は優先
                if any(any(noun in part for noun in proper_nouns) for part in parts):
                    if len(parts) >= 3:
                        return f"{parts[0]}による{parts[1]}の{parts[2]}"
                    elif len(parts) == 2:
                        return f"{parts[0]}での{parts[1]}"
        
        # パターン3: 記事構造から中核内容を抽出（「本記事では」を除去）
        if any(phrase in content for phrase in ['本記事では', '本稿では', 'この記事では']):
            # 記事導入部から実質的な内容を抽出
            content_extraction_patterns = [
                r'(?:本記事|本稿|この記事)では[、，]?(.{5,40}?)(?:を使った|による|での)(.{5,30}?)(?:の|を)(.{5,30}?)(?:を|について)?(.{5,30}?)(?:紹介|説明|解説)',
                r'(?:本記事|本稿|この記事)では[、，]?(.{5,40}?)(?:の|による)(.{5,30}?)(?:を|について)(.{5,30}?)(?:紹介|説明|解説)',
            ]
            
            for pattern in content_extraction_patterns:
                match = re.search(pattern, content)
                if match:
                    groups = [g.strip() for g in match.groups() if g and g.strip()]
                    # 固有名詞を含む場合は優先
                    if any(any(noun in group for noun in proper_nouns) for group in groups):
                        if len(groups) >= 3:
                            # 完結したタイトルとして構成
                            return f"{groups[0]}による{groups[1]}の{groups[2]}"
                        elif len(groups) == 2:
                            return f"{groups[0]}での{groups[1]}"
        
        # パターン4: 課題解決型タイトル
        problem_solution_patterns = [
            r'(.{5,40}?)(?:の|を)(?:課題|問題)(?:を|について)(.{5,30}?)(?:解決|対応|改善)(?:する|させる)?',
            r'(.{5,40}?)(?:使い始めると|を導入すると)[、，]?(.{5,30}?)(?:課題|問題)(?:に|と)(.{5,30}?)',
        ]
        
        for pattern in problem_solution_patterns:
            matches = re.findall(pattern, content)
            for match in matches:
                parts = [part.strip() for part in match if part.strip()]
                if any(any(noun in part for noun in proper_nouns) for part in parts):
                    if len(parts) >= 2:
                        return f"{parts[0]}における{parts[1]}の解決方法"
        
        return ''
    
    def _identify_core_keywords(self, content: str, proper_nouns: List[str]) -> List[str]:
        """Ultrathinking: コンテンツの中核となるキーワードを特定"""
        core_keywords = []
        content_lower = content.lower()
        
        # 固有名詞は最優先
        core_keywords.extend(proper_nouns[:2])
        
        # 動作・目的語の抽出
        action_patterns = [
            r'(?:を|について)(.{3,15}?)(?:する|させる|実現|管理|運用|活用|構築|開発)',
            r'(.{3,15}?)(?:の|を)(?:管理|運用|活用|構築|開発|改善|解決)',
            r'(?:効率的に|上手く|適切に)(.{3,15}?)(?:する|活用|運用)',
        ]
        
        for pattern in action_patterns:
            matches = re.findall(pattern, content)
            for match in matches:
                keyword = match.strip()
                if len(keyword) >= 3 and keyword not in core_keywords:
                    core_keywords.append(keyword)
        
        # 概念・手法の抽出
        concept_patterns = [
            r'(.{3,15}?)(?:システム|手法|方法|ガイド|コツ|戦略|アプローチ)',
            r'(.{3,15}?)(?:について|に関する|における)(?:課題|問題|解決)',
        ]
        
        for pattern in concept_patterns:
            matches = re.findall(pattern, content)
            for match in matches:
                keyword = match.strip()
                if len(keyword) >= 3 and keyword not in core_keywords:
                    core_keywords.append(keyword)
        
        return core_keywords[:4]
    
    def _is_fragmented_title(self, title: str) -> bool:
        """タイトルが断片化・不完全・不適切かチェック"""
        if not title or not title.strip():
            return True
            
        title_clean = title.strip()
        
        # 基本的な断片化パターン
        fragment_indicators = [
            r'^[、，。．]',  # 句読点で始まる
            r'[、，。．]$',  # 句読点で終わる
            r'^[ぁ-ん]{1,2}$',  # ひらがな1-2文字のみ
            r'^[、，].*',  # カンマで始まる
            r'.*[、，]{2,}.*',  # 連続カンマ
            r'.*・$',  # 中点で終わる（不完全）
        ]
        
        for pattern in fragment_indicators:
            if re.match(pattern, title_clean):
                return True
        
        # 不適切な接頭語
        inappropriate_prefixes = [
            r'^本記事では[、，]?',
            r'^この記事では[、，]?',
            r'^本稿では[、，]?',
            r'^以下[、，]?',
        ]
        
        for pattern in inappropriate_prefixes:
            if re.match(pattern, title_clean):
                return True
        
        # 文として不完全（動詞なし、助詞で終わる等）
        incomplete_patterns = [
            r'.*[のをにがはで]$',  # 助詞で終わる
            r'.*について$',  # 「について」で終わる（不完全）
            r'.*に関する$',  # 「に関する」で終わる（不完全）
            r'.*・$',  # 中点で終わる
        ]
        
        for pattern in incomplete_patterns:
            if re.match(pattern, title_clean):
                return True
        
        # 短すぎる、または長すぎる
        if len(title_clean) <= 3 or len(title_clean) > 60:
            return True
            
        return False
    
    def _generate_title_from_content_meaning(self, content: str, main_noun: str) -> str:
        """Ultrathinking + ラテラルシンキング: 普遍的な視点でタイトルを生成"""
        content_lower = content.lower()
        
        # ラテラルシンキング: 問題を一般化
        universal_patterns = self._identify_universal_patterns(content_lower)
        core_keywords = self._identify_core_keywords(content, [main_noun])
        
        # パターン1: 課題解決型（普遍的アプローチ）
        if any(word in content_lower for word in ['課題', '問題', '解決', '改善', '対策']):
            if len(core_keywords) >= 2:
                # 文法チェック: 助詞重複を防ぐ
                clean_keyword = self._clean_grammatical_particles(core_keywords[1])
                return f"{main_noun}による{clean_keyword}課題の解決手法"
            else:
                return f"{main_noun}を活用した課題解決アプローチ"
        
        # パターン2: 知見・ナレッジ系（普遍的知識管理）
        if any(word in content_lower for word in ['知見', 'ナレッジ', '管理', '蓄積', '活用']):
            action_words = self._extract_action_concepts(content_lower)
            if action_words and '運用' in action_words:
                return f"{main_noun}による効果的な運用管理手法"
            elif action_words:
                return f"{main_noun}での実践的な{action_words[0]}システム"
            else:
                return f"{main_noun}による知見活用の実践方法"
        
        # パターン3: 開発・実装系（普遍的手法論）
        if any(word in content_lower for word in ['開発', '実装', '構築', '設計']):
            if '効率' in content_lower:
                return f"{main_noun}による効率的な開発手法"
            else:
                return f"{main_noun}を使った実践的な開発アプローチ"
        
        # パターン4: 分析・評価系（普遍的分析手法）
        if any(word in content_lower for word in ['分析', 'レポート', 'データ', '解析', '評価']):
            return f"{main_noun}による包括的分析手法"
        
        # パターン5: 戦略・計画系（普遍的戦略論）
        if any(word in content_lower for word in ['戦略', '計画', 'マーケティング', 'ビジネス']):
            return f"{main_noun}を活用した戦略的アプローチ"
        
        # パターン6: 学習・教育系（普遍的学習論）
        if any(word in content_lower for word in ['学習', '教育', '指導', '研修']):
            return f"{main_noun}による効果的な学習手法"
        
        # パターン7: 普遍的活用論（デフォルト）
        if core_keywords and len(core_keywords) >= 2:
            # 文法チェック適用
            clean_keyword = self._clean_grammatical_particles(core_keywords[1])
            return f"{main_noun}による{clean_keyword}の実践活用法"
        else:
            return f"{main_noun}の効果的な活用手法"
    
    def _identify_universal_patterns(self, content_lower: str) -> List[str]:
        """ラテラルシンキング: 普遍的なパターンを特定"""
        patterns = []
        
        # 普遍的な概念カテゴリ
        universal_concepts = {
            'problem_solving': ['課題', '問題', '解決', '改善', '対策', '修正'],
            'knowledge_management': ['知見', 'ナレッジ', '蓄積', '管理', '活用', '共有'],
            'efficiency': ['効率', '最適化', '改善', '向上', 'スピード', '生産性'],
            'methodology': ['手法', '方法', 'アプローチ', '戦略', 'フレームワーク'],
            'learning': ['学習', '習得', '理解', '把握', '身につける'],
            'implementation': ['実装', '実践', '導入', '構築', '開発', '適用']
        }
        
        for pattern_type, keywords in universal_concepts.items():
            if any(keyword in content_lower for keyword in keywords):
                patterns.append(pattern_type)
        
        return patterns
    
    def _extract_action_concepts(self, content_lower: str) -> List[str]:
        """行動・動作に関する概念を抽出"""
        action_concepts = []
        
        # 動作を表す語彙
        action_words = ['運用', '管理', '活用', '構築', '開発', '改善', '解決', '実践', '導入']
        
        for word in action_words:
            if word in content_lower:
                action_concepts.append(word)
        
        return action_concepts[:2]  # 上位2つまで
    
    def _clean_grammatical_particles(self, text: str) -> str:
        """包括的文法チェック: 助詞の重複やおかしな文法を修正"""
        if not text or not text.strip():
            return text
        
        cleaned = text.strip()
        
        # 日本語助詞の重複パターンを検出・修正
        particle_duplications = [
            # 「による」+「使った」→「使った」
            (r'による(.{0,5}?)使った', r'\1使った'),
            (r'による(.{0,5}?)での', r'\1での'),
            (r'による(.{0,5}?)を使った', r'\1を使った'),
            (r'による(.{0,5}?)による', r'\1による'),
            
            # 「を」の重複
            (r'を(.{0,5}?)を', r'を\1'),
            
            # 「で」の重複
            (r'で(.{0,5}?)で', r'で\1'),
            
            # 「に」の重複
            (r'に(.{0,5}?)に', r'に\1'),
            
            # 「の」の重複（3回以上）
            (r'の(.{0,5}?)の(.{0,5}?)の', r'の\1\2'),
        ]
        
        for pattern, replacement in particle_duplications:
            cleaned = re.sub(pattern, replacement, cleaned)
        
        # 不自然な助詞連続を修正
        unnatural_sequences = [
            # 「による使った」→「を使った」
            (r'による使った', r'を使った'),
            # 「での使った」→「で使った」  
            (r'での使った', r'で使った'),
            # 「を使ったの」→「を使った」
            (r'を使ったの(?=課題|問題|解決)', r'を使った'),
        ]
        
        for pattern, replacement in unnatural_sequences:
            cleaned = re.sub(pattern, replacement, cleaned)
        
        # 助詞の欠落を修正（重要な追加）
        missing_particles = [
            # 「Claude Code使った」→「Claude Codeを使った」
            (r'([A-Za-z\s]+)使った', r'\1を使った'),
            # 「システム開発した」→「システムを開発した」  
            (r'([ァ-ヶー一-龯]{2,})開発した', r'\1を開発した'),
            # 「プロジェクト管理する」→「プロジェクトを管理する」
            (r'([ァ-ヶー一-龯]{3,})管理する', r'\1を管理する'),
            # 「データ分析する」→「データを分析する」
            (r'([ァ-ヶー一-龯]{2,})分析する', r'\1を分析する'),
        ]
        
        for pattern, replacement in missing_particles:
            cleaned = re.sub(pattern, replacement, cleaned)
        
        # 語彙の重複除去
        word_duplications = [
            # 同じ単語の重複
            (r'(.{2,}?)\1', r'\1'),  # 「開発開発」→「開発」
        ]
        
        for pattern, replacement in word_duplications:
            cleaned = re.sub(pattern, replacement, cleaned)
        
        return cleaned
    
    def _validate_japanese_grammar(self, title: str) -> bool:
        """日本語文法の妥当性をチェック"""
        if not title or not title.strip():
            return False
        
        # 基本的な文法エラーパターン
        grammar_errors = [
            r'による.{0,10}?使った',  # 「による」+「使った」
            r'を.{0,5}?を',           # 「を」の重複
            r'で.{0,5}?で',           # 「で」の重複  
            r'に.{0,5}?に',           # 「に」の重複
            r'の.{0,5}?の.{0,5}?の',  # 「の」の3回以上重複
        ]
        
        for pattern in grammar_errors:
            if re.search(pattern, title):
                return False
        
        # 助詞欠落の検出
        missing_particle_errors = [
            r'[A-Za-z\s]+(?<!を)使った',  # 英語名詞+使った（をなし）
            r'[ァ-ヶー一-龯]{2,}(?<!を)開発した',  # 日本語名詞+開発した（をなし）
            r'[ァ-ヶー一-龯]{3,}(?<!を)管理する',  # 日本語名詞+管理する（をなし）
        ]
        
        for pattern in missing_particle_errors:
            if re.search(pattern, title):
                return False
        
        return True
    
    def _extract_nouns_from_text(self, text: str) -> List[str]:
        """テキストから名詞を抽出（簡易版）"""
        # カタカナ、漢字、ひらがなの組み合わせで2-10文字の単語を抽出
        pattern = r'[ァ-ヶー一-龯ぁ-ん]{2,10}'
        candidates = re.findall(pattern, text)
        
        # 一般的すぎる単語を除外
        common_words = {'こと', 'もの', 'とき', 'ところ', 'ため', 'よう', 'さん', 'くん', 'ちゃん'}
        
        return [word for word in candidates if word not in common_words]
    
    def _extract_key_phrases(self, content: str) -> List[str]:
        """キーフレーズの抽出"""
        # 名詞句パターン
        noun_phrase_patterns = [
            r'[ァ-ヶー一-龯]+(?:の[ァ-ヶー一-龯]+)+',  # 「〜の〜」
            r'[ァ-ヶー一-龯]+(?:[化成型式])',  # 「〜化」「〜成」など
            r'[A-Za-z]+[ァ-ヶー一-龯]+',  # 英語+日本語
            r'[ァ-ヶー一-龯]+[A-Za-z]+',  # 日本語+英語
        ]
        
        phrases = []
        for pattern in noun_phrase_patterns:
            matches = re.findall(pattern, content)
            phrases.extend(matches)
        
        # 頻度でソート
        phrase_counter = Counter(phrases)
        return [phrase for phrase, count in phrase_counter.most_common(10) if count >= 1]
    
    def _calculate_word_frequency(self, content: str) -> Dict[str, int]:
        """単語頻度の計算"""
        # 単語抽出（簡易版）
        words = re.findall(r'[ァ-ヶー一-龯ぁ-んA-Za-z]+', content)
        return dict(Counter(words).most_common(20))
    
    def _analyze_sentence_structures(self, content: str) -> List[str]:
        """文構造の分析"""
        structures = []
        sentences = re.split(r'[。．！？\n]', content)
        
        for sentence in sentences[:10]:  # 最初の10文まで
            if not sentence.strip():
                continue
                
            structure = []
            if re.search(r'[はがを]', sentence):
                structure.append('主語あり')
            if re.search(r'[。．！？]$', sentence):
                structure.append('完結文')
            if re.search(r'ので|ため|から', sentence):
                structure.append('理由説明')
            if re.search(r'しかし|でも|ただし', sentence):
                structure.append('逆接')
                
            structures.append('_'.join(structure) if structure else '単純文')
        
        return structures
    
    def _extract_subtopics(self, content: str) -> List[str]:
        """サブトピックの抽出"""
        subtopics = []
        
        # セクションヘッダーからの抽出
        section_patterns = [
            r'■\s*(.+?)(?:\n|$)',
            r'▶\s*(.+?)(?:\n|$)',
            r'・\s*(.+?)(?:\n|$)',
            r'\d+\.\s*(.+?)(?:\n|$)'
        ]
        
        for pattern in section_patterns:
            matches = re.findall(pattern, content, re.MULTILINE)
            subtopics.extend(matches)
        
        return subtopics[:10]  # 最大10個
    
    def _detect_intent(self, content: str) -> str:
        """文書の意図を検出"""
        intent_patterns = {
            'inform': ['お知らせ', '報告', '共有', '連絡'],
            'request': ['お願い', '依頼', 'してください', 'していただけ'],
            'analyze': ['分析', '検証', '考察', '評価'],
            'plan': ['計画', '予定', '企画', 'する予定'],
            'record': ['記録', 'メモ', '備忘', '覚え']
        }
        
        intent_scores = {}
        for intent, keywords in intent_patterns.items():
            score = sum(1 for keyword in keywords if keyword in content)
            intent_scores[intent] = score
        
        if intent_scores:
            return max(intent_scores, key=intent_scores.get)
        return 'general'
    
    def _identify_domain(self, content: str) -> str:
        """ドメインの識別"""
        # X/SNS関連の特別判定を最初に実行
        x_sns_patterns = [
            r'(?:X|Twitter|SNS|ソーシャル).*?(?:分析|レポート|アカウント|戦略)',
            r'(?:フォロワー|エンゲージメント|インプレッション).*?(?:分析|獲得|数値)',
            r'(?:マーケティング|プロモーション|ブランド).*?(?:戦略|分析|効果)',
            r'アカウント.*?(?:分析|完全分析|レポート)',
            r'(?:投稿|ポスト).*?(?:分析|戦略|傾向)'
        ]
        
        for pattern in x_sns_patterns:
            if re.search(pattern, content, re.IGNORECASE):
                return 'business'  # 確実にビジネスと判定
        
        domain_keywords = {
            'business': [
                'ビジネス', '営業', '売上', '戦略', 'マーケティング', '経営',
                'SNS', 'アカウント', 'フォロワー', 'エンゲージメント', 'インプレッション',
                'リーチ', 'ブランディング', '集客', '顧客', 'ターゲット', 'コンバージョン',
                'ROI', 'KPI', '効果測定', 'プロモーション', '広告', 'キャンペーン',
                'Twitter', 'X', 'Instagram', 'Facebook', 'LinkedIn', 'TikTok',
                '分析レポート', 'データ分析', '競合分析', '市場分析', 'トレンド分析'
            ],
            'tech': ['プログラミング', 'AI', 'システム', '開発', 'コード', 'API'],
            'education': ['教育', '学習', '授業', '生徒', '講師', '塾'],
            'health': ['健康', '医療', '診断', '治療', '症状'],
            'finance': ['金融', '投資', '予算', '資金', '収支']
        }
        
        # 複合キーワードの重み付けパターン
        compound_patterns = {
            'business': [
                (r'(?:X|Twitter|SNS|ソーシャル).*?(?:分析|レポート|アカウント)', 5),
                (r'(?:フォロワー|エンゲージメント|インプレッション).*?(?:分析|数値|データ)', 4),
                (r'(?:マーケティング|プロモーション|ブランド).*?(?:戦略|分析|効果)', 4),
                (r'(?:アカウント|プロフィール).*?(?:分析|レポート|診断)', 3)
            ]
        }
        
        domain_scores = {}
        
        # 基本キーワードスコアリング
        for domain, keywords in domain_keywords.items():
            score = sum(2 if keyword in content else 0 for keyword in keywords)
            domain_scores[domain] = score
        
        # 複合パターンスコアリング
        for domain, patterns in compound_patterns.items():
            if domain not in domain_scores:
                domain_scores[domain] = 0
            for pattern, weight in patterns:
                if re.search(pattern, content, re.IGNORECASE):
                    domain_scores[domain] += weight
        
        # 特別な判定ロジック：X/Twitter関連の分析は必ずbusiness
        x_twitter_patterns = [
            r'(?:X|Twitter).*?(?:アカウント|分析|レポート)',
            r'(?:フォロワー|ツイート|リツイート).*?(?:分析|データ)',
            r'(?:SNS|ソーシャルメディア).*?(?:分析|戦略|マーケティング)'
        ]
        
        for pattern in x_twitter_patterns:
            if re.search(pattern, content, re.IGNORECASE):
                domain_scores['business'] = max(domain_scores.get('business', 0), 10)
                break
        
        if domain_scores:
            best_domain = max(domain_scores, key=domain_scores.get)
            if domain_scores[best_domain] > 0:
                return best_domain
        
        return 'general'
    
    def _analyze_tone(self, content: str) -> str:
        """文書のトーンを分析"""
        tone_patterns = {
            'formal': ['です', 'ます', 'ございます', 'いたします'],
            'casual': ['だね', 'かな', 'よね', 'っぽい'],
            'analytical': ['分析', '考察', '結果', '評価'],
            'instructional': ['してください', '必要です', '重要です', 'べき']
        }
        
        tone_scores = {}
        for tone, patterns in tone_patterns.items():
            score = sum(1 for pattern in patterns if pattern in content)
            tone_scores[tone] = score
        
        if tone_scores:
            return max(tone_scores, key=tone_scores.get)
        return 'neutral'
    
    def _analyze_entity_relations(self, content: str) -> List[Dict[str, Any]]:
        """エンティティ間の関係を分析"""
        # 簡易的な実装
        entities = self._extract_entities(content)
        relations = []
        
        # 同じ文に出現するエンティティは関連があると仮定
        sentences = re.split(r'[。．！？\n]', content)
        for sentence in sentences:
            sentence_entities = [e for e in entities if e in sentence]
            if len(sentence_entities) >= 2:
                for i in range(len(sentence_entities)):
                    for j in range(i + 1, len(sentence_entities)):
                        relations.append({
                            'entity1': sentence_entities[i],
                            'entity2': sentence_entities[j],
                            'type': 'co-occurrence',
                            'context': sentence[:50] + '...' if len(sentence) > 50 else sentence
                        })
        
        return relations[:10]  # 最大10個
    
    def _extract_entities(self, content: str) -> List[str]:
        """エンティティの抽出"""
        # 固有名詞パターン（簡易版）
        patterns = [
            r'[A-Z][a-zA-Z]+',  # 英語の固有名詞
            r'[ァ-ヶー]{3,}',  # カタカナの固有名詞
            r'(?:株式会社|有限会社)[ァ-ヶー一-龯]+',  # 会社名
            r'[一-龯]{2,4}(?:さん|様|氏)',  # 人名
        ]
        
        entities = []
        for pattern in patterns:
            matches = re.findall(pattern, content)
            entities.extend(matches)
        
        return list(set(entities))
    
    def _analyze_temporal_flow(self, content: str) -> List[Dict[str, str]]:
        """時系列の流れを分析"""
        temporal_markers = {
            'past': ['昨日', '先週', '先月', '以前', '過去'],
            'present': ['今日', '現在', '今', '本日'],
            'future': ['明日', '来週', '来月', '今後', '将来']
        }
        
        temporal_flow = []
        sentences = re.split(r'[。．！？\n]', content)
        
        for i, sentence in enumerate(sentences):
            for time_type, markers in temporal_markers.items():
                if any(marker in sentence for marker in markers):
                    temporal_flow.append({
                        'sentence_index': i,
                        'time_type': time_type,
                        'sentence': sentence[:50] + '...' if len(sentence) > 50 else sentence
                    })
                    break
        
        return temporal_flow
    
    def _analyze_hierarchy(self, content: str) -> Dict[str, Any]:
        """階層構造の分析"""
        hierarchy = {
            'depth': 0,
            'structure': []
        }
        
        # インデントレベルの検出
        lines = content.split('\n')
        current_depth = 0
        
        for line in lines:
            if not line.strip():
                continue
                
            # インデントの深さを計算
            indent = len(line) - len(line.lstrip())
            
            # 構造マーカーの検出
            if re.match(r'^#{1,6}\s', line):
                level = len(re.match(r'^(#+)', line).group(1))
                hierarchy['structure'].append({
                    'type': 'heading',
                    'level': level,
                    'text': line.strip()
                })
                hierarchy['depth'] = max(hierarchy['depth'], level)
            elif re.match(r'^\s*[-*+]\s', line):
                hierarchy['structure'].append({
                    'type': 'list_item',
                    'level': indent // 2,
                    'text': line.strip()
                })
            elif re.match(r'^\s*\d+\.\s', line):
                hierarchy['structure'].append({
                    'type': 'numbered_item',
                    'level': indent // 2,
                    'text': line.strip()
                })
        
        return hierarchy
    
    def _integrate_themes(self, surface: Dict, context: Dict) -> str:
        """テーマの統合（簡潔版）"""
        # 主題を中心とした統合（過度な追加語彙を避ける）
        main_topic = context.get('main_topic', {}).get('text', '')
        
        # 主題が十分に具体的な場合はそのまま使用
        if main_topic and len(main_topic) > 8:
            return main_topic
        
        # 主題が短い場合のみ、選択的に高頻度語を追加
        high_freq_words = list(surface.get('word_frequency', {}).keys())[:3]
        if main_topic and high_freq_words:
            # 意味のある語句のみを選択的に追加
            meaningful_words = [
                w for w in high_freq_words 
                if (w not in main_topic and 
                    len(w) > 2 and 
                    w not in ['について', 'に関する', 'である', 'です', 'ます', 'した', 'する'])
            ][:1]  # 最大1語のみ
            
            if meaningful_words:
                return f"{main_topic}・{meaningful_words[0]}"
        
        return main_topic or 'メモ'
    
    def _extract_key_insights(self, relation: Dict) -> List[str]:
        """重要な洞察の抽出"""
        insights = []
        
        # 因果関係からの洞察
        causal_relations = relation.get('causal_relations', [])
        if causal_relations:
            for rel in causal_relations[:3]:
                if rel['type'] == 'causal':
                    insights.append(f"{rel['from']} → {rel['to']}")
        
        # エンティティ関係からの洞察
        entity_relations = relation.get('entity_relations', [])
        if entity_relations:
            for rel in entity_relations[:2]:
                insights.append(f"{rel['entity1']} - {rel['entity2']}の関連")
        
        return insights
    
    def _infer_implicit_meanings(self, content: str, context: Dict) -> List[str]:
        """暗黙的な意味の推論"""
        implicit_meanings = []
        
        # 文書タイプと意図から推論
        doc_type = context.get('document_type', {}).get('type', '')
        intent = context.get('intent', '')
        
        if doc_type == 'meeting_notes' and intent == 'record':
            implicit_meanings.append('決定事項の確認と共有が必要')
        elif doc_type == 'analysis' and intent == 'analyze':
            implicit_meanings.append('改善策の検討が求められている')
        elif doc_type == 'report' and '問題' in content:
            implicit_meanings.append('課題解決のアクションが必要')
        
        return implicit_meanings
    
    def _extract_action_items(self, content: str) -> List[str]:
        """アクションアイテムの抽出"""
        action_items = []
        
        # アクションを示すパターン
        action_patterns = [
            r'(?:TODO|ToDo|todo)[:：]\s*(.+?)(?:\n|$)',
            r'(?:宿題|課題|タスク)[:：]\s*(.+?)(?:\n|$)',
            r'(.+?)(?:する必要がある|しなければならない|すること)',
            r'(.+?)(?:を検討|を確認|を準備|を作成|を修正)'
        ]
        
        for pattern in action_patterns:
            matches = re.findall(pattern, content, re.MULTILINE)
            action_items.extend(matches)
        
        # 重複を除去して返す
        return list(dict.fromkeys(action_items))[:5]
    
    def _generate_intelligent_output(self, surface: Dict, context: Dict, 
                                   relation: Dict, semantic: Dict, content: str) -> Dict[str, Any]:
        """分析結果を統合して出力を生成"""
        
        # タイトル生成（固有名詞優先）
        title = self._generate_final_title(context, semantic, content)
        
        # タグ生成（元のコンテンツも渡す）
        tags = self._generate_contextual_tags({
            'surface_analysis': surface,
            'context_analysis': context,
            'relation_analysis': relation,
            'semantic_integration': semantic,
            'original_content': content  # 元のコンテンツを追加
        })
        
        # カテゴリ決定（コンテンツも考慮）
        category = self._determine_final_category(context, content)
        
        # 要約生成
        summary = self._generate_summary(semantic, context)
        
        return {
            'title': title,
            'tags': tags,
            'category': category,
            'summary': summary,
            'analysis_details': {
                'document_type': context.get('document_type', {}),
                'main_topic': context.get('main_topic', {}),
                'key_insights': semantic.get('key_insights', []),
                'action_items': semantic.get('action_items', [])
            }
        }
    
    def _generate_final_title(self, context: Dict, semantic: Dict, content: str = '') -> str:
        """意味理解に基づくタイトル生成"""
        # 固有名詞の検出
        proper_nouns = self._extract_proper_nouns(content)
        
        # コンテンツの真の意味を分析
        title = self._extract_meaningful_title(content, proper_nouns)
        
        # フォールバック: 既存のロジック
        if not title or len(title.strip()) < 5:
            main_topic = context.get('main_topic', {})
            if main_topic.get('confidence', 0) > 0.7:
                candidate_title = main_topic.get('text', '')
                # 断片化チェック
                if len(candidate_title) > 5 and not self._is_fragmented_title(candidate_title):
                    title = candidate_title
                else:
                    title = semantic.get('coherent_theme', '')
            else:
                title = semantic.get('coherent_theme', '')
        
        # 最終品質チェック
        if not title or len(title.strip()) < 3 or self._is_fragmented_title(title):
            # 固有名詞ベースでタイトル生成
            if proper_nouns:
                title = self._generate_title_from_content_meaning(content, proper_nouns[0])
            else:
                title = 'メモ'
        
        title = title.strip()
        
        # 包括的文法チェック: 助詞重複・文法エラーを修正
        title = self._clean_grammatical_particles(title)
        
        # 文法妥当性の最終確認
        if not self._validate_japanese_grammar(title):
            # 文法エラーがある場合は安全なフォールバック
            if proper_nouns:
                title = f"{proper_nouns[0]}活用ガイド"
            else:
                title = 'メモ'
        
        # 不正な接尾辞の除去
        unwanted_suffixes = ['他 -', '他-', '他、', '他。', 'の他', ' -', '- ', '他']
        for suffix in unwanted_suffixes:
            if title.endswith(suffix):
                title = title[:-len(suffix)].strip()
        
        # タイトルの長さ調整（日本語に適した長さ）
        if len(title) > 45:
            # 単語の境界で切る
            cut_point = 42
            while cut_point > 20 and title[cut_point] not in ['の', 'を', 'に', 'と', 'で', ' ', '、', 'て', 'た', '・']:
                cut_point -= 1
            title = title[:cut_point]
            # 末尾の句読点を整理
            title = title.rstrip('・、。')
        
        # 最終的な品質チェック
        if len(title) < 3:
            title = 'メモ'
        
        return title
    
    def _determine_final_category(self, context: Dict, content: str = '') -> str:
        """分野横断的なカテゴリ決定システム"""
        content_lower = content.lower()
        main_topic = context.get('main_topic', {}).get('text', '').lower()
        
        # 技術・開発分野の判定
        tech_indicators = [
            'claude code', 'chatgpt', 'ai', 'プログラミング', 'エンジニアリング', 'github',
            'python', 'javascript', 'typescript', 'react', 'docker', 'api', 'システム開発',
            'プロンプトエンジニアリング', 'コーディング', 'デバッグ', 'リファクタリング'
        ]
        if any(term in content_lower or term in main_topic for term in tech_indicators):
            return 'tech'
        
        # ビジネス・コンサルティング分野の判定
        business_indicators = [
            'コンサルティング', 'マーケティング', '戦略', 'ビジネス', 'sns', 'フォロワー',
            'エンゲージメント', '売上', '収益', '顧客', 'クライアント', '営業', '経営'
        ]
        if any(term in content_lower or term in main_topic for term in business_indicators):
            return 'business'
        
        # 教育分野の判定
        education_indicators = [
            '教育', '学習', '講師', '塾', '授業', '生徒', '学生', '指導', '研修',
            '教材', 'edtech', '学習支援', 'オンライン授業'
        ]
        if any(term in content_lower or term in main_topic for term in education_indicators):
            return 'education'
        
        # 分析・レポート分野の判定
        analysis_indicators = [
            '分析', '評価', '考察', '検証', 'レポート', '調査', '研究', 'データ',
            '統計', '指標', 'kpi', '成果測定', '効果検証'
        ]
        if any(term in content_lower or term in main_topic for term in analysis_indicators):
            return 'analysis'
        
        # プロジェクト・計画分野の判定
        project_indicators = [
            'プロジェクト', '計画', 'プラン', '戦略', '目標', 'ロードマップ',
            'マイルストーン', 'スケジュール', 'タスク', 'todo'
        ]
        if any(term in content_lower or term in main_topic for term in project_indicators):
            return 'projects'
        
        # 参考資料・メモ分野（デフォルト）
        return 'reference'
    
    def _generate_summary(self, semantic: Dict, context: Dict) -> List[str]:
        """要約の生成"""
        summary_points = []
        
        # キーインサイトを追加
        insights = semantic.get('key_insights', [])
        summary_points.extend(insights[:2])
        
        # アクションアイテムを追加
        actions = semantic.get('action_items', [])
        if actions:
            summary_points.append(f"TODO: {actions[0]}")
        
        # 暗黙的な意味を追加
        implicit = semantic.get('implicit_meanings', [])
        if implicit:
            summary_points.append(implicit[0])
        
        # 最低3個、最大6個にする
        while len(summary_points) < 3:
            summary_points.append(f"{context.get('intent', 'メモ')}の記録")
        
        return summary_points[:6]
    
    def _combine_key_phrases_to_title(self, key_phrases: List[str]) -> str:
        """キーフレーズを組み合わせてタイトルを生成"""
        if not key_phrases:
            return ""
        
        # 最も重要な2-3個のフレーズを選択
        selected = key_phrases[:3]
        
        # 接続詞で結合
        if len(selected) == 1:
            return selected[0]
        elif len(selected) == 2:
            return f"{selected[0]}と{selected[1]}"
        else:
            return f"{selected[0]}・{selected[1]}他"