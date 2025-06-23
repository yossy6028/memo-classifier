import google.generativeai as genai
import os
import yaml
import json
import logging

logger = logging.getLogger()

class GeminiClient:
    """
    Gemini APIと連携してメモ分析を行うクライアント
    """
    def __init__(self, config_path='config.yaml'):
        """
        APIキーを読み込み、Geminiモデルを初期化
        """
        try:
            logging.info("GeminiClient: Initializing...")
            # オフラインモードの初期化
            self.offline_mode = False
            
            # APIキーを環境変数から取得
            api_key = os.getenv('GEMINI_API_KEY')
            if not api_key:
                # 設定ファイルからのフォールバック（非推奨）
                try:
                    with open(config_path, 'r') as f:
                        config = yaml.safe_load(f)
                    api_key = config.get('gemini', {}).get('api_key')
                except:
                    pass
                
                if not api_key or api_key == "YOUR_GEMINI_API_KEY":
                    logging.warning("GeminiClient: API key not found. Running in offline mode.")
                    self.model = None
                    self.offline_mode = True
                    return
            
            logging.info("GeminiClient: API Key found. Configuring genai...")
            genai.configure(api_key=api_key)
            logging.info("GeminiClient: genai configured successfully.")
            
            # 最新モデルを試行し、失敗時は順次フォールバック
            models_to_try = [
                ('gemini-2.0-flash-thinking-exp-1219', 'Gemini 2.0 Flash Thinking (最新実験版)'),
                ('gemini-exp-1206', 'Gemini Experimental 1206'),
                ('gemini-2.0-flash-exp', 'Gemini 2.0 Flash (実験版)'),
                ('gemini-1.5-flash-latest', 'Gemini 1.5 Flash (安定版)')
            ]
            
            for model_name, description in models_to_try:
                try:
                    self.model = genai.GenerativeModel(model_name)
                    logging.info(f"GeminiClient: {description} モデルを使用")
                    break
                except Exception as model_error:
                    logging.warning(f"{description} 使用不可: {model_error}")
                    continue
            else:
                raise Exception("利用可能なGeminiモデルが見つかりません")
            
            logging.info(f"GeminiClient: Model '{self.model._model_name}' initialized.")

        except Exception as e:
            logging.error(f"GeminiClient: Initialization failed. Error: {e}", exc_info=True)
            raise

    def analyze_memo(self, content: str, categories: list) -> dict:
        """
        メモの内容を分析し、タイトル、カテゴリ、タグを生成
        """
        # オフラインモードの場合はフォールバック分析
        if self.offline_mode or self.model is None:
            return self._offline_analysis(content, categories)
        
        category_list = ", ".join(categories)

        prompt = f"""
        あなたは文章解析の専門家です。以下のメモ内容の主題を正確に特定し、適切なタイトル、カテゴリ、タグ、関連ファイル検索用のキーワードをJSON形式で提案してください。

        # 根本的分析手順
        1. **文章全体を3回読み返す**: 全体像を把握してから詳細を分析
        2. **中心的主題の特定**: 文章が何について説明しているかを1文で要約
        3. **具体的内容の抽出**: 抽象的概念ではなく文章で実際に扱われている具体的事項
        4. **誤解しやすいパターンの回避**: 「AI」「教育」などの単語だけで判断せず、文脈を重視

        # タイトル生成の厳格なルール
        - 文章の中心的主題を正確に反映すること（例: セキュリティ対策なら「AIセキュリティ対策」）
        - 抽象的で曖昧なタイトルは絶対に避けること（例: 「AI活用法」「教育プログラム」等）
        - 体言止め（名詞で終わる）にすること
        - 10-20文字程度で簡潔にすること

        # カテゴリ分類の厳格なルール（優先順位順）
        - 個人名や打ち合わせ・会議・ビジネス戦略・コンサルティング → consulting（最優先）
        - プログラミング、システム、技術解説 → tech  
        - 教育手法、学習方法、指導法 → education
        - 書籍内容、読書記録 → kindle
        - 音楽理論、演奏技術 → music
        - SNS・YouTube・note等外部発信、コンテンツ制作、メディア → media
        - 上記以外 → others

        # 利用可能なカテゴリ
        {category_list}

        # タイトル生成の原則
        
        **絶対ルール**: 
        1. 与えられたメモ内容の中から具体的なキーワードを抽出してタイトルを構成する
        2. メモに含まれていない単語や概念をタイトルに使わない
        3. 料金・プランに関する内容の場合、具体的なプラン名やサービス名を含める
        4. 汎用的なタイトル（「活用法」「解説」等）を避け、内容の特徴を捉える
        
        # タイトル生成の思考プロセス（参考）
        
        ステップ1: メモから重要な固有名詞を抽出
        - 例: Opus, Sonnet, Claude, Obsidian, Proプランなど
        
        ステップ2: メモの主題を表す動作や状態を特定
        - 例: 料金体系、使用制限、比較、構築、管理など
        
        ステップ3: 固有名詞と主題を組み合わせてタイトル化
        - 例: 「Opus/Sonnet料金体系」「Proプラン使用制限」
        
        **注意**: 上記はあくまで思考プロセスの例であり、実際のタイトルはメモ内容に即して生成すること。

        # カテゴリ分類の優先ルール（厳格な優先順位）
        **重要**: ビジネス要素がある場合は必ずconsultingを優先
        - 個人の名前（嶋村氏など）や打ち合わせ・会議・ビジネス戦略・経営・マーケティング → consulting（最優先）
        - プログラミング、AI、技術的内容 → tech
        - 教育・学習・指導内容（ビジネス要素なし） → education
        - 読書・Kindle・本の内容 → kindle
        - 音楽・演奏・楽器関連 → music
        - SNS・YouTube・note等外部発信、コンテンツ制作（ビジネス要素なし） → media
        - その他 → others

        # メモ内容
        ---
        {content}
        ---

        # 出力形式 (JSON)
        {{
          "title": "（体言止めのタイトル）",
          "category": "（カテゴリリストから選択）",
          "tags": ["（タグ1）", "（タグ2）", "..."],
          "related_files_keywords": ["（キーワード1）", "（キーワード2）", "..."]
        }}
        """
        logging.info("--- Geminiへのプロンプト ---\n%s\n--------------------------", prompt)

        try:
            logging.info("GeminiClient: Calling model.generate_content...")
            response = self.model.generate_content(prompt)
            logging.info("GeminiClient: model.generate_content call finished.")
            
            raw_text = response.text
            logging.info(f"--- Geminiからの生の応答 ---\n{raw_text}\n--------------------------")
            
            json_text = raw_text.strip().lstrip('```json').lstrip('```').rstrip('```')
            result = json.loads(json_text)
            logging.info(f"パースされたJSON結果: {result}")
            return result
        except Exception as e:
            logging.error(f"Gemini APIの呼び出しまたはJSONパース中にエラーが発生: {e}", exc_info=True)
            return self._offline_analysis(content, categories)
    
    def _offline_analysis(self, content: str, categories: list) -> dict:
        """
        APIキーが設定されていない場合のフォールバック分析
        """
        logging.info("GeminiClient: Running offline analysis...")
        
        # 簡易的なキーワード分析
        content_lower = content.lower()
        
        # カテゴリ判定（簡易版）
        category = "others"
        if any(word in content_lower for word in ['コンサル', '戦略', '営業', '打ち合わせ']):
            category = "consulting"
        elif any(word in content_lower for word in ['プログラミング', 'システム', 'api', 'ai']):
            category = "tech"
        elif any(word in content_lower for word in ['教育', '学習', '指導']):
            category = "education"
        elif any(word in content_lower for word in ['音楽', '楽器', '演奏']):
            category = "music"
        elif any(word in content_lower for word in ['sns', 'youtube', 'ブログ', 'メディア']):
            category = "media"
        elif any(word in content_lower for word in ['本', '書籍', 'kindle']):
            category = "kindle"
        
        # タイトル生成（簡易版）
        lines = content.strip().split('\n')
        first_line = lines[0] if lines else content
        title = first_line[:20] + "..." if len(first_line) > 20 else first_line
        
        # タグ生成（簡易版）
        words = content.split()
        tags = [word for word in words if len(word) > 2 and word.isalpha()][:3]
        
        return {
            "title": title or "無題メモ",
            "category": category,
            "tags": tags or ["メモ"],
            "related_files_keywords": tags[:2] or ["メモ"]
        } 