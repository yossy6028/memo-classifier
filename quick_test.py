#!/usr/bin/env python3
"""
memo-classifier API 起動確認スクリプト
"""

def main():
    print("🚀 memo-classifier iOS Shortcuts API - Mac側セットアップ")
    print("=" * 60)
    
    # 1. 依存関係確認
    print("📦 依存関係確認...")
    try:
        import fastapi
        import uvicorn
        import pydantic
        print("   ✅ FastAPI, Uvicorn, Pydantic - インストール済み")
    except ImportError as e:
        print(f"   ❌ 依存関係エラー: {e}")
        return
    
    # 2. preview_enhanced_memo確認
    print("🔧 memo-classifier コア機能確認...")
    try:
        from preview_enhanced_memo import IntegratedMemoProcessor
        processor = IntegratedMemoProcessor()
        print("   ✅ IntegratedMemoProcessor - 正常読み込み")
    except Exception as e:
        print(f"   ❌ コア機能エラー: {e}")
        return
    
    # 3. 簡易テスト
    print("🧪 API機能テスト...")
    try:
        test_content = "Claude CodeとGitHubの技術メモです"
        result = processor.preview_analysis(test_content)
        
        if result['success']:
            print("   ✅ 分析機能正常")
            print(f"   📋 タイトル: {result['title']['title']}")
            print(f"   📂 カテゴリ: {result['category']['name']}")
            print(f"   🏷️ タグ数: {len(result['tags']['tags'])}")
        else:
            print("   ❌ 分析機能エラー")
            return
            
    except Exception as e:
        print(f"   ❌ テストエラー: {e}")
        return
    
    # 4. ネットワーク情報
    print("🌐 ネットワーク設定...")
    import subprocess
    try:
        result = subprocess.run(['ifconfig'], capture_output=True, text=True)
        lines = result.stdout.split('\n')
        
        ips = []
        for line in lines:
            if 'inet ' in line and '127.0.0.1' not in line and '169.254' not in line:
                ip = line.split()[1]
                if ip.startswith(('192.168', '10.', '172.')):
                    ips.append(ip)
        
        if ips:
            print("   ✅ 検出されたIPアドレス:")
            for ip in ips:
                print(f"      📱 iPhone接続URL: http://{ip}:8080")
        else:
            print("   ⚠️ プライベートIPアドレスが見つかりません")
            
    except Exception as e:
        print(f"   ⚠️ ネットワーク情報取得エラー: {e}")
    
    # 5. 起動コマンド案内
    print("\n🚀 APIサーバー起動方法:")
    print("   Option 1: ./start_server.sh")
    print("   Option 2: python3 api_server.py")
    
    print("\n📱 iPhone Shortcuts設定:")
    print("   1. Shortcuts.appで新しいショートカット作成")
    print("   2. 'Get Contents of URL'アクション追加")
    print("   3. URL: http://[上記のIP]:8080/quick-analyze")
    print("   4. Method: POST")
    print("   5. Request Body: JSON")
    print("   6. Content: {\"content\": \"[入力テキスト]\", \"action\": \"preview\"}")
    
    print("\n✅ Mac側セットアップ準備完了！")
    print("🎯 次のステップ: python3 api_server.py でサーバー起動")

if __name__ == "__main__":
    main()