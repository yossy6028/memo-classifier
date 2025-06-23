#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
コンテンツフォーマッター - メモ内容に適切な見出しを付けて整形
"""

import re
from typing import List, Tuple

class ContentFormatter:
    """メモ内容を整形し、見出しを適切に配置"""
    
    def format_content(self, content: str) -> str:
        """メモ内容を整形"""
        
        # 行ごとに分割
        lines = content.strip().split('\n')
        formatted_lines = []
        
        for line in lines:
            formatted_line = self._format_line(line)
            formatted_lines.append(formatted_line)
        
        # 空行の調整
        result = '\n'.join(formatted_lines)
        
        # 連続する空行を1つに
        result = re.sub(r'\n\n\n+', '\n\n', result)
        
        # 見出しが全くない場合は自動的に見出しを追加
        if not self._has_heading(result):
            result = self._add_auto_headings(result)
        
        return result.strip()
    
    def _format_line(self, line: str) -> str:
        """1行を整形"""
        
        line = line.strip()
        
        # 空行はそのまま
        if not line:
            return ''
        
        # ■で始まる行をMarkdownの見出しに変換
        if line.startswith('■'):
            # ■の数で見出しレベルを決定
            heading_level = 2  # デフォルトは##
            heading_text = line.lstrip('■').strip()
            
            # 特定のキーワードがある場合は見出しレベルを調整
            if any(keyword in heading_text for keyword in ['概要', '目的', 'フェーズ', 'Phase']):
                heading_level = 2
            elif any(keyword in heading_text for keyword in ['詳細', '内容', '手法', '対象']):
                heading_level = 3
            
            return '#' * heading_level + ' ' + heading_text
        
        # 【】で囲まれた部分を見出しに変換
        if line.startswith('【') and '】' in line:
            match = re.match(r'【([^】]+)】(.*)$', line)
            if match:
                heading_text = match.group(1)
                rest_text = match.group(2).strip()
                
                # 内容がある場合は見出し+内容
                if rest_text:
                    return f"### {heading_text}\n{rest_text}"
                else:
                    return f"### {heading_text}"
        
        # 箇条書きの整形
        # ・や◆を-に統一
        if line.startswith(('・', '◆', '◇', '●', '○')):
            return '- ' + line[1:].strip()
        
        # 番号付きリストの整形
        if re.match(r'^\d+[\.、]', line):
            return re.sub(r'^(\d+)[\.、]', r'\1.', line)
        
        # 絵文字で始まる行は見出し候補
        emoji_pattern = r'^[\U0001F300-\U0001F9FF]'
        if re.match(emoji_pattern, line):
            # 短い行（20文字以下）なら見出しとして扱う
            if len(line) <= 20:
                return '## ' + line
        
        return line
    
    def _has_heading(self, content: str) -> bool:
        """見出しが含まれているかチェック"""
        return bool(re.search(r'^#+\s', content, re.MULTILINE))
    
    def _add_auto_headings(self, content: str) -> str:
        """自動的に見出しを追加"""
        
        lines = content.split('\n')
        sections = self._identify_sections(lines)
        
        # セクションごとに見出しを追加
        result_lines = []
        for section_type, section_lines in sections:
            if section_type and section_lines:
                result_lines.append(f"## {section_type}")
            result_lines.extend(section_lines)
            if section_lines:  # 空でないセクションの後には空行
                result_lines.append('')
        
        return '\n'.join(result_lines).strip()
    
    def _identify_sections(self, lines: List[str]) -> List[Tuple[str, List[str]]]:
        """内容からセクションを識別"""
        
        sections = []
        current_section = []
        
        for line in lines:
            line_lower = line.lower()
            
            # セクションを識別するキーワード
            if any(keyword in line_lower for keyword in ['目的', '概要', 'overview']):
                if current_section:
                    sections.append(('', current_section))
                    current_section = []
                sections.append(('概要', [line]))
            elif any(keyword in line_lower for keyword in ['手法', '方法', 'method']):
                if current_section:
                    sections.append(('', current_section))
                    current_section = []
                sections.append(('方法', [line]))
            elif any(keyword in line_lower for keyword in ['結果', 'result']):
                if current_section:
                    sections.append(('', current_section))
                    current_section = []
                sections.append(('結果', [line]))
            elif re.match(r'^(phase|フェーズ|ステップ|step)\s*\d+', line_lower):
                if current_section:
                    sections.append(('', current_section))
                    current_section = []
                sections.append(('フェーズ', [line]))
            else:
                current_section.append(line)
        
        # 残りの行を追加
        if current_section:
            # 最初のセクションで見出しがなければ「内容」とする
            if not sections:
                sections.append(('内容', current_section))
            else:
                sections.append(('', current_section))
        
        return sections


# テスト
if __name__ == "__main__":
    formatter = ContentFormatter()
    
    test_content = """■PoC計画：思考力教材の地域モデル検証＠クレオスタディ三田校
🧭 概要
目的：現在20名の受講者を倍増（40名）し、再現可能な運営モデルを確立

対象教材：MiLAi study × 読むとくメソッド®ことばの学校

期間：3〜6ヶ月（短期効果＋継続率を検証）

実施校：クレオスタディ三田校（嶋村氏運営）

■PoC設計フェーズ
【Phase 1｜現状分析と課題仮説】
対象：現受講生／指導者／保護者"""
    
    formatted = formatter.format_content(test_content)
    print(formatted)