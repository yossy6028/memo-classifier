#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
統一ログ管理
"""

import logging
import os
from datetime import datetime
from typing import Optional


class LoggerSetup:
    """ログ設定のセットアップ"""
    
    @staticmethod
    def setup_logger(
        name: str, 
        log_file: Optional[str] = None,
        level: int = logging.INFO,
        console: bool = True
    ) -> logging.Logger:
        """統一ログ設定"""
        
        logger = logging.getLogger(name)
        
        # すでに設定済みの場合はそのまま返す
        if logger.handlers:
            return logger
        
        logger.setLevel(level)
        
        # フォーマッター
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        
        # コンソールハンドラ
        if console:
            console_handler = logging.StreamHandler()
            console_handler.setLevel(level)
            console_handler.setFormatter(formatter)
            logger.addHandler(console_handler)
        
        # ファイルハンドラ
        if log_file:
            # ログディレクトリが存在しない場合は作成
            log_dir = os.path.dirname(log_file)
            if log_dir:
                os.makedirs(log_dir, exist_ok=True)
            
            file_handler = logging.FileHandler(log_file, encoding='utf-8')
            file_handler.setLevel(level)
            file_handler.setFormatter(formatter)
            logger.addHandler(file_handler)
        
        return logger


def get_logger(name: str) -> logging.Logger:
    """アプリケーション用ログ取得"""
    # ログファイルパス
    base_dir = os.path.dirname(os.path.dirname(__file__))
    log_file = os.path.join(base_dir, "logs", f"memo_classifier_{datetime.now().strftime('%Y%m%d')}.log")
    
    return LoggerSetup.setup_logger(
        name=name,
        log_file=log_file,
        level=logging.INFO,
        console=False  # ファイルのみ
    )


def get_debug_logger(name: str) -> logging.Logger:
    """デバッグ用ログ取得"""
    base_dir = os.path.dirname(os.path.dirname(__file__))
    log_file = os.path.join(base_dir, "debug.log")
    
    return LoggerSetup.setup_logger(
        name=f"debug.{name}",
        log_file=log_file,
        level=logging.DEBUG,
        console=True  # コンソールとファイル両方
    )