#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
普遍的メモ分析システム - エントリーポイント
キーワードに依存しない普遍的分析でタイトル・カテゴリ・タグを生成
"""

import sys
import os
import logging
from datetime import datetime

# ログ設定
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# モジュールをインポート
try:
    from universal_analyzer import UniversalAnalyzer
    from content_formatter import ContentFormatter
except ImportError as e:
    logger.error(f"モジュールインポートエラー: {e}")
    print(f"ERROR: モジュールインポートに失敗しました: {e}")
    sys.exit(1)

def create_obsidian_file(content: str, analysis_result: dict) -> str:
    """Obsidianファイルを作成"""
    
    try:
        result = analysis_result.get('result', {})
        title = result.get('title', 'メモ')
        category = result.get('category', 'others')
        tags = result.get('tags', ['メモ'])
        
        # フォルダ名を決定（02_Inbox配下の既存フォルダに合わせる）
        folder_map = {
            'consulting': 'Consulting',
            'tech': 'Tech', 
            'education': 'Education',
            'kindle': 'kindle',  # 既存フォルダは小文字
            'music': 'Music',
            'media': 'Media',
            'others': 'Others'
        }
        folder = folder_map.get(category, 'Others')
        
        # ファイル名を生成（安全な文字のみ）
        safe_title = "".join(c for c in title if c.isalnum() or c in (' ', '-', '_')).strip()
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{safe_title}_{timestamp}.md"
        
        # Obsidianの02_Inboxディレクトリ
        obsidian_base = "/Users/yoshiikatsuhiko/Library/Mobile Documents/iCloud~md~obsidian/Documents"
        folder_path = os.path.join(obsidian_base, "02_Inbox", folder)
        
        # フォルダが存在しない場合は作成
        os.makedirs(folder_path, exist_ok=True)
        
        # ファイルパス
        file_path = os.path.join(folder_path, filename)
        
        # YAMLフロントマターとコンテンツを作成
        formatter = ContentFormatter()
        formatted_content = formatter.format_content(content)
        
        # タグをYAML形式に変換
        tags_yaml = "\n".join([f"  - {tag}" for tag in tags])
        
        file_content = f"""---
title: {title}
category: {category}
tags:
{tags_yaml}
created: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
---

# {title}

{formatted_content}
"""
        
        # ファイルに書き込み
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(file_content)
        
        logger.info(f"ファイル作成成功: {file_path}")
        return file_path
        
    except Exception as e:
        logger.error(f"ファイル作成エラー: {e}")
        return ""

def calculate_relevance_score(content: str, file_title: str, file_tags: list) -> int:
    """関連度スコアを計算（1-3星）"""
    score = 0
    content_lower = content.lower()
    title_lower = file_title.lower()
    
    # タイトルキーワードマッチング
    content_words = set(content_lower.split())
    title_words = set(title_lower.split())
    common_words = content_words.intersection(title_words)
    
    # スコア計算
    if len(common_words) >= 3:
        score = 3  # 高関連度
    elif len(common_words) >= 2:
        score = 2  # 中関連度
    elif len(common_words) >= 1:
        score = 1  # 低関連度
    
    # タグによる関連度アップ
    if file_tags:
        for tag in file_tags:
            if tag.lower() in content_lower:
                score = min(3, score + 1)
                break
    
    return max(1, min(3, score))  # 1-3の範囲に制限

def find_related_files(content: str, category: str) -> str:
    """関連ファイルを検索（関連度星印付き）"""
    try:
        # Obsidianの02_Inboxディレクトリを検索
        obsidian_base = "/Users/yoshiikatsuhiko/Library/Mobile Documents/iCloud~md~obsidian/Documents"
        folder_map = {
            'consulting': 'Consulting',
            'tech': 'Tech', 
            'education': 'Education',
            'kindle': 'kindle',
            'music': 'Music',
            'media': 'Media',
            'others': 'Others'
        }
        
        # 同カテゴリのフォルダを検索
        target_folder = folder_map.get(category, 'Others')
        search_path = os.path.join(obsidian_base, "02_Inbox", target_folder)
        
        if not os.path.exists(search_path):
            return "関連ファイルなし"
        
        # 最近の3件のファイルを取得してタイトル・タグを分析
        files = []
        for file in os.listdir(search_path):
            if file.endswith('.md') and not file.startswith('.'):
                file_path = os.path.join(search_path, file)
                file_title = file.replace('.md', '')
                
                # ファイルのYAMLフロントマターからタグを抽出
                file_tags = []
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        file_content = f.read()
                        if file_content.startswith('---'):
                            yaml_end = file_content.find('---', 3)
                            if yaml_end > 0:
                                yaml_content = file_content[3:yaml_end]
                                for line in yaml_content.split('\n'):
                                    if line.strip().startswith('- '):
                                        file_tags.append(line.strip()[2:])
                except:
                    pass
                
                # 関連度スコアを計算
                relevance_score = calculate_relevance_score(content, file_title, file_tags)
                star_rating = "★" * relevance_score
                
                files.append((file_title, os.path.getmtime(file_path), star_rating))
        
        # 時系列でソートして最新3件
        files.sort(key=lambda x: x[1], reverse=True)
        recent_files = [(f[0], f[2]) for f in files[:3]]
        
        if recent_files:
            file_list = [f"{title} {stars}" for title, stars in recent_files[:2]]
            return f"同カテゴリ最新: {', '.join(file_list)}"
        else:
            return "関連ファイルなし"
            
    except Exception as e:
        return "関連ファイルなし"

def main():
    """メイン処理"""
    
    if len(sys.argv) < 3:
        print("ERROR: 引数が不足しています")
        print("使用方法: python universal_analysis.py [preview|save] [メモ内容] [API_KEY(optional)]")
        sys.exit(1)
    
    mode = sys.argv[1]
    content = sys.argv[2]
    
    # 抜本的解決：API keyを直接インポート
    try:
        from api_config import get_api_key
        api_key = get_api_key()
        os.environ['GEMINI_API_KEY'] = api_key
        logger.info(f"API Key loaded from api_config.py")
    except ImportError as e:
        logger.error(f"Failed to import API config: {e}")
        raise Exception("API設定ファイルが見つかりません")
    
    if not content.strip():
        print("ERROR: メモ内容が空です")
        sys.exit(1)
    
    # カテゴリリスト
    categories = ['consulting', 'tech', 'education', 'kindle', 'music', 'media', 'others']
    
    try:
        # 普遍的分析実行
        analyzer = UniversalAnalyzer()
        analysis_result = analyzer.analyze(content, categories)
        
        if not analysis_result.get('success'):
            print("ERROR: 分析に失敗しました")
            sys.exit(1)
        
        result = analysis_result.get('result', {})
        
        if mode == "preview":
            # プレビュー結果を出力
            print("RESULT_START")
            print(f"TITLE:{result.get('title', 'メモ')}")
            print(f"CATEGORY:{result.get('category', 'others')}")
            
            # フォルダ名（02_Inbox配下）
            folder_map = {
                'consulting': 'Consulting',
                'tech': 'Tech',
                'education': 'Education', 
                'kindle': 'kindle',  # 既存フォルダは小文字
                'music': 'Music',
                'media': 'Media',
                'others': 'Others'
            }
            folder = folder_map.get(result.get('category', 'others'), 'Others')
            print(f"FOLDER:{folder}")
            
            # タグ
            tags = result.get('tags', ['メモ'])
            print(f"TAGS:{' '.join(tags)}")
            
            # 関連ファイル検索（簡易版）
            related_files = find_related_files(content, result.get('category', 'others'))
            print(f"RELATIONS:{related_files}")
            print("RESULT_END")
            
        elif mode == "save":
            # ファイル保存
            file_path = create_obsidian_file(content, analysis_result)
            if file_path:
                print("SUCCESS")
            else:
                print("ERROR: ファイル保存に失敗しました")
                sys.exit(1)
        
        else:
            print(f"ERROR: 不明なモード: {mode}")
            sys.exit(1)
            
    except Exception as e:
        logger.error(f"メイン処理エラー: {e}")
        print(f"ERROR: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()