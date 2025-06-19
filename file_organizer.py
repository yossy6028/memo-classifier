#!/usr/bin/env python3
"""
ファイル整理システム
Obsidian Vault内のファイルを適切なカテゴリフォルダに整理
"""

import sys
import os
import re
import json
import shutil
from pathlib import Path
from datetime import datetime
from preview_enhanced_memo import IntegratedMemoProcessor


class FileOrganizer:
    """ファイル整理システム"""
    
    def __init__(self):
        self.obsidian_path = "/Users/yoshiikatsuhiko/Library/Mobile Documents/iCloud~md~obsidian/Documents"
        self.inbox_path = "02_Inbox"
        self.processor = IntegratedMemoProcessor()
        
        # 整理対象のフォルダ
        self.source_folders = [
            "02_Inbox",
            "01_Daily",
            # 他の整理対象フォルダがあれば追加
        ]
        
        # 除外するファイルパターン
        self.exclude_patterns = [
            r'\.DS_Store',
            r'\.git',
            r'__pycache__',
            r'\.tmp',
            r'\.temp'
        ]
    
    def organize_files(self) -> dict:
        """ファイル整理のメイン処理"""
        results = {
            'success_count': 0,
            'failure_count': 0,
            'processed_files': [],
            'errors': []
        }
        
        try:
            vault_path = Path(self.obsidian_path)
            
            # 各ソースフォルダから整理対象ファイルを収集
            target_files = []
            for folder_name in self.source_folders:
                folder_path = vault_path / folder_name
                if folder_path.exists():
                    target_files.extend(self._collect_files(folder_path))
            
            print(f"🔍 整理対象ファイル: {len(target_files)}件")
            
            # 各ファイルを処理
            for file_path in target_files:
                try:
                    result = self._organize_single_file(file_path)
                    
                    if result['success']:
                        results['success_count'] += 1
                        results['processed_files'].append({
                            'file': str(file_path),
                            'destination': result.get('destination', ''),
                            'category': result.get('category', ''),
                            'action': result.get('action', 'moved')
                        })
                        print(f"✅ {file_path.name} -> {result.get('category', 'unknown')}")
                    else:
                        results['failure_count'] += 1
                        results['errors'].append({
                            'file': str(file_path),
                            'error': result.get('error', 'Unknown error')
                        })
                        print(f"❌ {file_path.name}: {result.get('error', 'Unknown error')}")
                        
                except Exception as e:
                    results['failure_count'] += 1
                    results['errors'].append({
                        'file': str(file_path),
                        'error': str(e)
                    })
                    print(f"❌ {file_path.name}: {str(e)}")
            
            return results
            
        except Exception as e:
            results['errors'].append({'system_error': str(e)})
            return results
    
    def _collect_files(self, folder_path: Path) -> list:
        """フォルダからMarkdownファイルを収集"""
        files = []
        
        try:
            for file_path in folder_path.rglob('*.md'):
                # 除外パターンをチェック
                if not any(re.search(pattern, str(file_path)) for pattern in self.exclude_patterns):
                    # 既に適切なカテゴリフォルダに配置されているファイルはスキップ
                    if not self._is_in_category_folder(file_path):
                        files.append(file_path)
        
        except Exception as e:
            print(f"⚠️ フォルダ収集エラー ({folder_path}): {e}")
        
        return files
    
    def _is_in_category_folder(self, file_path: Path) -> bool:
        """ファイルが既にカテゴリフォルダに配置されているかチェック"""
        category_folders = set(self.processor.category_folders.values())
        
        # ファイルの親フォルダパスをチェック
        relative_path = file_path.relative_to(Path(self.obsidian_path))
        path_parts = relative_path.parts
        
        # Inboxフォルダ内のカテゴリフォルダをチェック
        # パターン: 02_Inbox/カテゴリフォルダ/ファイル.md
        if len(path_parts) >= 3 and path_parts[0] == self.inbox_path:
            # Inbox内のカテゴリフォルダにある場合は整理済み
            if path_parts[1] in category_folders:
                return True
        
        # その他のカテゴリフォルダもチェック
        for part in path_parts[:-1]:  # ファイル名を除く
            if part in category_folders:
                return True
        
        return False
    
    def _organize_single_file(self, file_path: Path) -> dict:
        """単一ファイルの整理処理"""
        try:
            # ファイル内容を読み込み
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # すでにYAMLフロントマターがある場合は既存のメタデータを使用
            existing_meta = self._extract_yaml_metadata(content)
            if existing_meta and 'category' in existing_meta:
                category = existing_meta['category']
            else:
                # コンテンツを分析してカテゴリを決定
                analysis = self.processor.preview_analysis(content)
                if not analysis['success']:
                    return {'success': False, 'error': 'Analysis failed'}
                
                category = analysis['category']['name']
            
            # 移動先フォルダを決定
            destination_folder = self.processor.category_folders.get(category, '4_General')
            destination_path = Path(self.obsidian_path) / self.inbox_path / destination_folder
            
            # 移動先フォルダを作成（存在しない場合）
            destination_path.mkdir(parents=True, exist_ok=True)
            
            # ファイル移動
            new_file_path = destination_path / file_path.name
            
            # 同名ファイルが存在する場合はタイムスタンプを付加
            if new_file_path.exists():
                timestamp = datetime.now().strftime('%H%M%S')
                stem = new_file_path.stem
                suffix = new_file_path.suffix
                new_file_path = destination_path / f"{stem}_{timestamp}{suffix}"
            
            # ファイル移動実行
            shutil.move(str(file_path), str(new_file_path))
            
            return {
                'success': True,
                'destination': str(new_file_path),
                'category': category,
                'action': 'moved'
            }
            
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def _extract_yaml_metadata(self, content: str) -> dict:
        """YAMLフロントマターからメタデータを抽出"""
        try:
            if content.startswith('---'):
                end_marker = content.find('---', 3)
                if end_marker != -1:
                    yaml_content = content[3:end_marker].strip()
                    
                    # 簡易YAML解析（categoryのみ）
                    metadata = {}
                    for line in yaml_content.split('\n'):
                        if ':' in line:
                            key, value = line.split(':', 1)
                            key = key.strip()
                            value = value.strip().strip('"\'')
                            metadata[key] = value
                    
                    return metadata
        except:
            pass
        
        return {}


def main():
    """メイン実行関数"""
    print("🔄 ファイル整理システム開始...")
    
    organizer = FileOrganizer()
    results = organizer.organize_files()
    
    # 結果出力
    print("\n" + "="*50)
    print("📊 ファイル整理結果")
    print("="*50)
    print(f"成功: {results['success_count']}件")
    print(f"失敗: {results['failure_count']}件")
    
    if results['processed_files']:
        print("\n✅ 整理完了ファイル:")
        for file_info in results['processed_files']:
            print(f"  • {Path(file_info['file']).name} -> {file_info['category']}")
    
    if results['errors']:
        print("\n❌ エラーファイル:")
        for error_info in results['errors']:
            if 'file' in error_info:
                print(f"  • {Path(error_info['file']).name}: {error_info['error']}")
            else:
                print(f"  • システムエラー: {error_info.get('system_error', 'Unknown')}")
    
    print("\n🎉 ファイル整理完了!")
    
    # AppleScript用の出力形式も追加
    print(f"\nAPPLESCRIPT_RESULT: 成功: {results['success_count']}件, 失敗: {results['failure_count']}件")


if __name__ == "__main__":
    main()