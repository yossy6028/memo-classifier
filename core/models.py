#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
データモデル定義
"""

from dataclasses import dataclass
from typing import List, Optional, Dict, Any
from datetime import datetime


@dataclass
class AnalysisResult:
    """分析結果のデータモデル"""
    title: str
    category: str
    tags: List[str]
    folder: str
    relations: str
    confidence: float = 0.0
    model: str = "unknown"
    timestamp: datetime = None
    
    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.now()
    
    def to_dict(self) -> Dict[str, Any]:
        """辞書形式に変換"""
        return {
            'title': self.title,
            'category': self.category,
            'tags': self.tags,
            'folder': self.folder,
            'relations': self.relations,
            'confidence': self.confidence,
            'model': self.model,
            'timestamp': self.timestamp.isoformat()
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'AnalysisResult':
        """辞書から作成"""
        return cls(
            title=data['title'],
            category=data['category'],
            tags=data['tags'],
            folder=data['folder'],
            relations=data['relations'],
            confidence=data.get('confidence', 0.0),
            model=data.get('model', 'unknown'),
            timestamp=datetime.fromisoformat(data['timestamp']) if 'timestamp' in data else None
        )


@dataclass
class MemoContent:
    """メモ内容のデータモデル"""
    raw_content: str
    formatted_content: Optional[str] = None
    word_count: int = 0
    
    def __post_init__(self):
        self.word_count = len(self.raw_content)
    
    def is_empty(self) -> bool:
        return not self.raw_content.strip()


@dataclass
class RelatedFile:
    """関連ファイルのデータモデル"""
    title: str
    relevance_score: int  # 1-3 stars
    category: str
    tags: List[str] = None
    
    def __post_init__(self):
        if self.tags is None:
            self.tags = []
    
    @property
    def star_rating(self) -> str:
        """星印評価を返す"""
        return "★" * max(1, min(3, self.relevance_score))
    
    def __str__(self) -> str:
        return f"{self.title} {self.star_rating}"


@dataclass
class CategoryConfig:
    """カテゴリ設定のデータモデル"""
    name: str
    folder: str
    priority: int = 0
    keywords: List[str] = None
    
    def __post_init__(self):
        if self.keywords is None:
            self.keywords = []


class ProcessingMode:
    """処理モードの定数"""
    PREVIEW = "preview"
    SAVE = "save"
    TEST = "test"


class CategoryPriority:
    """カテゴリ優先度の定数"""
    CONSULTING = 1  # 最優先
    TECH = 2
    EDUCATION = 3
    KINDLE = 4
    MUSIC = 5
    MEDIA = 6
    OTHERS = 7  # 最低優先