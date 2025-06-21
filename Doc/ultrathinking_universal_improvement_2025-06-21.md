# Ultrathinking による普遍的なタグ付け・タイトル設定の改善設計
作成日: 2025-06-21

## 🎯 問題の本質分析

### 現在の問題点（X分析メモを例に）
1. **タイトルの不一致**: 「Consultingの分析方法による業務効率化」→ 実際は「X（Twitter）アカウント分析レポート」
2. **不適切なタグ**: 「#タント」（誤変換）、「#ヶ月後目標」（断片的）、「#課題」「#分析」（一般的すぎる）
3. **文脈理解の欠如**: メモの真の内容（SNS分析レポート）を理解できていない

### 根本原因
- **表層的な単語抽出**: 文の構造や文脈を考慮せず、単語の出現頻度のみに依存
- **ドメイン知識の不足**: 業界特有の用語や文脈を理解できない
- **関係性の見落とし**: 単語間の意味的関係を把握できない

## 🧠 Ultrathinking アプローチによる改善設計

### 1. 多層的文脈理解システム

```python
class UltrathinkingAnalyzer:
    """Ultrathinking による深層的な内容分析"""
    
    def analyze_content(self, content: str) -> dict:
        """多層的な内容分析"""
        
        # Phase 1: 表層分析（既存の処理を強化）
        surface_analysis = {
            'raw_entities': self._extract_all_entities(content),
            'raw_keywords': self._extract_keywords(content),
            'sentence_structures': self._analyze_sentence_structures(content)
        }
        
        # Phase 2: 文脈理解（新規追加）
        context_analysis = {
            'document_type': self._identify_document_type(content),  # レポート、議事録、メモ等
            'main_topic': self._extract_main_topic(content),         # 主要トピック
            'subtopics': self._extract_subtopics(content),          # サブトピック
            'intent': self._detect_intent(content),                  # 分析、報告、計画等
            'domain': self._identify_domain(content)                 # ビジネス、技術、教育等
        }
        
        # Phase 3: 関係性分析（新規追加）
        relation_analysis = {
            'entity_relations': self._analyze_entity_relations(content),
            'temporal_flow': self._analyze_temporal_flow(content),
            'causal_relations': self._extract_causal_relations(content),
            'hierarchical_structure': self._analyze_hierarchy(content)
        }
        
        # Phase 4: 意味統合（新規追加）
        semantic_integration = {
            'coherent_theme': self._integrate_themes(surface_analysis, context_analysis),
            'key_insights': self._extract_key_insights(relation_analysis),
            'implicit_meanings': self._infer_implicit_meanings(content, context_analysis)
        }
        
        # Phase 5: 出力生成
        return self._generate_intelligent_output(
            surface_analysis, 
            context_analysis, 
            relation_analysis, 
            semantic_integration
        )
```

### 2. ドキュメントタイプ認識の強化

```python
def _identify_document_type(self, content: str) -> dict:
    """文書タイプの高精度識別"""
    
    document_patterns = {
        'report': {
            'markers': ['レポート', '分析', '概要', '調査', '結果'],
            'structure_patterns': [
                r'【.*】',  # セクションヘッダー
                r'^\d+\.',  # 番号付きリスト
                r'■|▶|◆',  # 構造化マーカー
            ],
            'content_patterns': [
                'データ', '指標', '結果', '成果', '評価'
            ]
        },
        'meeting_notes': {
            'markers': ['会議', '打ち合わせ', 'ミーティング', '議事録'],
            'structure_patterns': [
                r'日時[:：]', r'参加者[:：]', r'議題[:：]'
            ],
            'content_patterns': [
                '決定事項', '次回', 'アクション', 'TODO'
            ]
        },
        'analysis': {
            'markers': ['分析', '考察', '評価', '検証'],
            'structure_patterns': [
                r'課題[:：]', r'解決策[:：]', r'提案[:：]'
            ],
            'content_patterns': [
                '問題点', '改善', '効果', '影響'
            ]
        }
    }
    
    scores = {}
    for doc_type, patterns in document_patterns.items():
        score = 0
        # マーカーの存在確認
        for marker in patterns['markers']:
            if marker in content:
                score += 3
        
        # 構造パターンの確認
        for pattern in patterns['structure_patterns']:
            if re.search(pattern, content, re.MULTILINE):
                score += 2
        
        # 内容パターンの確認
        for pattern in patterns['content_patterns']:
            if pattern in content:
                score += 1
        
        scores[doc_type] = score
    
    # 最高スコアのタイプを返す
    best_type = max(scores, key=scores.get)
    confidence = scores[best_type] / sum(scores.values()) if sum(scores.values()) > 0 else 0
    
    return {
        'type': best_type,
        'confidence': confidence,
        'scores': scores
    }
```

### 3. 主題抽出の知的化

```python
def _extract_main_topic(self, content: str) -> dict:
    """文書の主題を知的に抽出"""
    
    # 1. タイトル候補の抽出
    title_candidates = []
    
    # パターン1: 明示的なタイトル表記
    explicit_title = re.search(r'【(.+?)】', content)
    if explicit_title:
        title_candidates.append({
            'text': explicit_title.group(1),
            'confidence': 0.9,
            'method': 'explicit_title'
        })
    
    # パターン2: 第一文の主題
    first_sentence = content.split('。')[0]
    if first_sentence:
        # 主語と述語の関係を分析
        subject_predicate = self._extract_subject_predicate(first_sentence)
        if subject_predicate:
            title_candidates.append({
                'text': f"{subject_predicate['subject']}の{subject_predicate['predicate']}",
                'confidence': 0.7,
                'method': 'subject_predicate'
            })
    
    # パターン3: 最頻出の実体 + アクション
    entities = self._extract_named_entities(content)
    actions = self._extract_action_verbs(content)
    if entities and actions:
        main_entity = max(entities.items(), key=lambda x: x[1])[0]
        main_action = max(actions.items(), key=lambda x: x[1])[0]
        title_candidates.append({
            'text': f"{main_entity}の{main_action}",
            'confidence': 0.5,
            'method': 'entity_action'
        })
    
    # 最適な候補を選択
    if title_candidates:
        best_candidate = max(title_candidates, key=lambda x: x['confidence'])
        return best_candidate
    else:
        return {
            'text': 'メモ',
            'confidence': 0.1,
            'method': 'fallback'
        }
```

### 4. タグ生成の文脈考慮型アプローチ

```python
def _generate_contextual_tags(self, content: str, analysis_results: dict) -> list:
    """文脈を考慮したタグ生成"""
    
    tags = []
    
    # 1. ドキュメントタイプに基づくタグ
    doc_type = analysis_results['context_analysis']['document_type']['type']
    if doc_type == 'report':
        tags.extend(['#レポート', '#分析結果'])
    elif doc_type == 'meeting_notes':
        tags.extend(['#会議', '#議事録'])
    
    # 2. 主要エンティティのタグ化（固有名詞優先）
    entities = analysis_results['surface_analysis']['raw_entities']
    # 固有名詞を優先的に抽出
    proper_nouns = self._filter_proper_nouns(entities)
    for noun in proper_nouns[:5]:  # 上位5個
        tags.append(f"#{noun}")
    
    # 3. アクション/目的タグ
    actions = self._extract_meaningful_actions(content)
    for action in actions[:3]:  # 上位3個
        tags.append(f"#{action}")
    
    # 4. ドメイン特化タグ
    domain = analysis_results['context_analysis']['domain']
    domain_tags = self._get_domain_specific_tags(content, domain)
    tags.extend(domain_tags[:3])
    
    # 5. 時系列タグ（もしあれば）
    temporal_tags = self._extract_temporal_tags(content)
    tags.extend(temporal_tags)
    
    # 重複削除と優先順位付け
    unique_tags = self._prioritize_tags(tags, content)
    
    return unique_tags[:12]  # 最大12個
```

### 5. 継続的改善のためのフィードバックループ

```python
class FeedbackLearner:
    """ユーザーフィードバックから学習するシステム"""
    
    def __init__(self):
        self.feedback_db = self._load_feedback_database()
        self.pattern_corrections = {}
        
    def record_correction(self, original: dict, corrected: dict, content: str):
        """ユーザーの修正を記録"""
        feedback_entry = {
            'timestamp': datetime.now(),
            'original_title': original.get('title'),
            'corrected_title': corrected.get('title'),
            'original_tags': original.get('tags'),
            'corrected_tags': corrected.get('tags'),
            'content_snippet': content[:200],
            'content_features': self._extract_content_features(content)
        }
        
        self.feedback_db.append(feedback_entry)
        self._update_patterns(feedback_entry)
        
    def _update_patterns(self, feedback: dict):
        """パターンを更新して精度を向上"""
        # タイトルパターンの学習
        if feedback['corrected_title'] != feedback['original_title']:
            self._learn_title_pattern(feedback)
        
        # タグパターンの学習
        if set(feedback['corrected_tags']) != set(feedback['original_tags']):
            self._learn_tag_pattern(feedback)
    
    def apply_learned_patterns(self, content: str, original_results: dict) -> dict:
        """学習したパターンを適用"""
        improved_results = original_results.copy()
        
        # 類似コンテンツのフィードバックを検索
        similar_feedbacks = self._find_similar_feedbacks(content)
        
        if similar_feedbacks:
            # タイトルの改善
            improved_results['title'] = self._improve_title_with_feedback(
                content, original_results['title'], similar_feedbacks
            )
            
            # タグの改善
            improved_results['tags'] = self._improve_tags_with_feedback(
                content, original_results['tags'], similar_feedbacks
            )
        
        return improved_results
```

## 📋 実装手順

### Phase 1: 基盤強化（1週間）
1. `UltrathinkingAnalyzer`クラスの実装
2. 既存の`preview_enhanced_memo.py`への統合
3. ドキュメントタイプ認識の実装

### Phase 2: 文脈理解（1週間）
1. 主題抽出アルゴリズムの実装
2. 関係性分析の実装
3. ドメイン知識の組み込み

### Phase 3: フィードバック学習（2週間）
1. フィードバック記録システムの構築
2. パターン学習アルゴリズムの実装
3. 継続的改善のための仕組み作り

### Phase 4: テストと調整（1週間）
1. 各種ドキュメントタイプでのテスト
2. エッジケースの対応
3. パフォーマンス最適化

## 🎨 期待される効果

1. **タイトル精度向上**: 文書の真の内容を反映した適切なタイトル
2. **タグの質向上**: 文脈を理解した意味のあるタグ付け
3. **継続的改善**: ユーザーフィードバックによる自動的な精度向上
4. **汎用性**: あらゆるタイプのメモに対応可能

## 📊 成功指標

- タイトル一致率: 80%以上
- タグ適切性: 85%以上
- ユーザー修正率: 20%以下
- 処理時間: 現在の150%以内

## 🔄 継続的改善サイクル

1. **週次レビュー**: フィードバックデータの分析
2. **月次更新**: パターンとアルゴリズムの調整
3. **四半期評価**: 全体的な精度と効果の測定