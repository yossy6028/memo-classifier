#!/usr/bin/env python3
"""
保存処理の統合スクリプト
"""
import sys
import os
import datetime
from pathlib import Path

# ログファイル
LOG_FILE = "/tmp/memo_save_debug.log"

def log(message):
    """デバッグログを出力"""
    with open(LOG_FILE, 'a') as f:
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        f.write(f"[{timestamp}] {message}\n")

def main():
    log("=== debug_save.py 開始 ===")
    log(f"引数: {sys.argv}")
    log(f"現在のディレクトリ: {os.getcwd()}")
    log(f"Pythonパス: {sys.executable}")
    
    if len(sys.argv) < 2:
        log("エラー: 引数がありません")
        print("ERROR: No content")
        return 1
    
    content = " ".join(sys.argv[1:])
    log(f"コンテンツ: {content[:200]}...")
    
    # 直接保存処理を実行
    try:
        # preview_enhanced_memo.pyを使用して保存
        sys.path.append(os.path.dirname(os.path.abspath(__file__)))
        from preview_enhanced_memo import IntegratedMemoProcessor
        
        log("IntegratedMemoProcessor初期化中...")
        processor = IntegratedMemoProcessor()
        
        log("保存処理開始...")
        result = processor.save_memo(content)
        
        log(f"保存結果: {result}")
        
        if result and result.get('success', False):
            print("SUCCESS")
            log("保存成功")
            return 0
        else:
            error_msg = result.get('error', 'Unknown error') if result else 'No result'
            print(f"ERROR: {error_msg}")
            log(f"保存失敗: {error_msg}")
            return 1
        
    except Exception as e:
        log(f"例外発生: {str(e)}")
        import traceback
        log(f"トレースバック: {traceback.format_exc()}")
        print(f"ERROR: {str(e)}")
        return 1

if __name__ == "__main__":
    sys.exit(main())