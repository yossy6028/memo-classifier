#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
設定管理
"""

import os
import yaml
from typing import Dict, Any
from pathlib import Path

from .models import CategoryConfig, CategoryPriority


class Config:
    """アプリケーション設定管理"""
    
    def __init__(self, config_path: str = None):
        if config_path is None:
            config_path = os.path.join(os.path.dirname(__file__), '..', 'config.yaml')
        
        self.config_path = config_path
        self._config = self._load_config()
    
    def _load_config(self) -> Dict[str, Any]:
        """設定ファイルを読み込み"""
        try:
            with open(self.config_path, 'r', encoding='utf-8') as f:
                return yaml.safe_load(f)
        except FileNotFoundError:
            # デフォルト設定を返す
            return self._get_default_config()
    
    def _get_default_config(self) -> Dict[str, Any]:
        """デフォルト設定"""
        return {
            'obsidian': {
                'base_path': "/Users/yoshiikatsuhiko/Library/Mobile Documents/iCloud~md~obsidian/Documents",
                'inbox_path': "02_Inbox"
            },
            'gemini': {
                'model': "gemini-2.0-flash-thinking-exp"
            },
            'categories': {
                'consulting': {'folder': 'Consulting', 'priority': CategoryPriority.CONSULTING},
                'tech': {'folder': 'Tech', 'priority': CategoryPriority.TECH},
                'education': {'folder': 'Education', 'priority': CategoryPriority.EDUCATION},
                'kindle': {'folder': 'kindle', 'priority': CategoryPriority.KINDLE},
                'music': {'folder': 'Music', 'priority': CategoryPriority.MUSIC},
                'media': {'folder': 'Media', 'priority': CategoryPriority.MEDIA},
                'others': {'folder': 'Others', 'priority': CategoryPriority.OTHERS}
            },
            'analysis': {
                'max_tags': 5,
                'confidence_threshold': 0.7
            }
        }
    
    @property
    def obsidian_base_path(self) -> str:
        """Obsidianベースパス"""
        return self._config['obsidian']['base_path']
    
    @property
    def obsidian_inbox_path(self) -> str:
        """Obsidian受信箱パス"""
        return os.path.join(self.obsidian_base_path, self._config['obsidian']['inbox_path'])
    
    @property
    def gemini_model(self) -> str:
        """Geminiモデル名"""
        return self._config['gemini']['model']
    
    def get_category_config(self, category: str) -> CategoryConfig:
        """カテゴリ設定を取得"""
        category_data = self._config['categories'].get(category, {})
        return CategoryConfig(
            name=category,
            folder=category_data.get('folder', 'Others'),
            priority=category_data.get('priority', CategoryPriority.OTHERS)
        )
    
    def get_category_folder_path(self, category: str) -> str:
        """カテゴリのフォルダパスを取得"""
        config = self.get_category_config(category)
        return os.path.join(self.obsidian_inbox_path, config.folder)
    
    def get_all_categories(self) -> Dict[str, CategoryConfig]:
        """全カテゴリ設定を取得"""
        categories = {}
        for category_name in self._config['categories']:
            categories[category_name] = self.get_category_config(category_name)
        return categories
    
    @property
    def max_tags(self) -> int:
        """最大タグ数"""
        return self._config['analysis']['max_tags']
    
    @property
    def confidence_threshold(self) -> float:
        """信頼度閾値"""
        return self._config['analysis']['confidence_threshold']
    
    def save_config(self) -> None:
        """設定をファイルに保存"""
        os.makedirs(os.path.dirname(self.config_path), exist_ok=True)
        with open(self.config_path, 'w', encoding='utf-8') as f:
            yaml.dump(self._config, f, default_flow_style=False, allow_unicode=True)


# グローバル設定インスタンス
_config_instance = None

def get_config() -> Config:
    """設定インスタンスを取得（シングルトン）"""
    global _config_instance
    if _config_instance is None:
        _config_instance = Config()
    return _config_instance