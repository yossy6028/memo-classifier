#!/usr/bin/env python3
"""
memo-classifier API テストスクリプト
iPhone Shortcuts用APIの動作確認
"""

import sys
import json
from preview_enhanced_memo import IntegratedMemoProcessor

def test_api_functionality():
    """APIの機能をテスト"""
    print("🧪 memo-classifier API 機能テスト開始")
    
    processor = IntegratedMemoProcessor()
    
    # テストケース
    test_cases = [
        {
            "content": "Claude CodeとGitHubの技術メモです。プログラミング効率を向上させる方法について記録。",
            "expected_category": "tech"
        },
        {
            "content": "中学受験の国語指導について。開成中学の過去問分析をSAPIXで実施。",
            "expected_category": "education"
        },
        {
            "content": "X投稿分析レポート。西村創一朗さんのアカウント分析とエンゲージメント戦略。",
            "expected_category": "media"
        }
    ]
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\n📝 テストケース {i}: {test_case['content'][:50]}...")
        
        try:
            # 分析実行
            result = processor.preview_analysis(test_case['content'])
            
            if result['success']:
                # iPhone Shortcuts向けの簡略レスポンス生成
                ios_response = {
                    "title": result['title']['title'],
                    "category": result['category']['name'],
                    "tags": ", ".join(result['tags']['tags'][:3]),
                    "relations": f"{result['relations']['count']}件",
                    "confidence": f"{result['category']['confidence']:.0%}",
                    "success": True
                }
                
                print(f"✅ 分析成功:")
                print(f"   📋 タイトル: {ios_response['title']}")
                print(f"   📂 カテゴリ: {ios_response['category']} ({ios_response['confidence']})")
                print(f"   🏷️ タグ: {ios_response['tags']}")
                print(f"   🔗 関連: {ios_response['relations']}")
                
                # カテゴリ予測の確認
                if result['category']['name'] == test_case['expected_category']:
                    print(f"   ✅ カテゴリ予測正確")
                else:
                    print(f"   ⚠️ カテゴリ予測: 期待={test_case['expected_category']}, 実際={result['category']['name']}")
                
            else:
                print(f"❌ 分析失敗: {result.get('error', '不明なエラー')}")
                
        except Exception as e:
            print(f"❌ エラー: {e}")
    
    print(f"\n🎯 iPhone Shortcuts用サンプルレスポンス:")
    print(json.dumps({
        "title": "プログラミングとGitの開発",
        "category": "tech",
        "tags": "#Claude, #GitHub, #記録",
        "relations": "0件",
        "confidence": "100%",
        "success": True
    }, ensure_ascii=False, indent=2))

def generate_shortcuts_config():
    """iPhone Shortcuts設定ファイル生成"""
    print(f"\n📱 iPhone Shortcuts設定情報:")
    
    # MacのIPアドレス取得試行
    import subprocess
    try:
        result = subprocess.run(
            ["ifconfig"], 
            capture_output=True, 
            text=True
        )
        lines = result.stdout.split('\n')
        ip_addresses = []
        for line in lines:
            if 'inet ' in line and '127.0.0.1' not in line and 'inet 169.254' not in line:
                ip = line.split()[1]
                if ip.startswith('192.168') or ip.startswith('10.') or ip.startswith('172.'):
                    ip_addresses.append(ip)
        
        if ip_addresses:
            print(f"🌐 検出されたプライベートIPアドレス:")
            for ip in ip_addresses:
                print(f"   - {ip}")
                print(f"   📱 Shortcuts URL: http://{ip}:8080/quick-analyze")
        else:
            print(f"⚠️ プライベートIPアドレスが検出されませんでした")
            
    except Exception as e:
        print(f"⚠️ IPアドレス検出エラー: {e}")
    
    print(f"\n📋 Shortcuts設定用JSONサンプル:")
    print(json.dumps({
        "content": "[Ask for Input の結果]",
        "action": "preview"
    }, ensure_ascii=False, indent=2))

if __name__ == "__main__":
    print("🚀 memo-classifier iOS Shortcuts API テスト")
    print("=" * 50)
    
    test_api_functionality()
    generate_shortcuts_config()
    
    print(f"\n✅ テスト完了！")
    print(f"📖 詳細な設定手順: iOS_Shortcuts_Setup.md を参照")
    print(f"🚀 APIサーバー起動: python3 api_server.py")