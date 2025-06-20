#!/bin/bash
# memo-classifier API Server 起動スクリプト

echo "🚀 memo-classifier iOS Shortcuts API Server"
echo "=================================================="

# 現在のディレクトリ確認
echo "📁 作業ディレクトリ: $(pwd)"

# MacのIPアドレス取得
echo "🌐 MacのIPアドレス:"
ifconfig | grep -E "inet [0-9]" | grep -v "127.0.0.1" | grep -v "169.254" | while read line; do
    IP=$(echo $line | awk '{print $2}')
    echo "   📱 iPhone接続URL: http://$IP:8080"
done

echo ""
echo "📖 API エンドポイント:"
echo "   - http://localhost:8080/health (ヘルスチェック)"
echo "   - http://localhost:8080/docs (API文書)"
echo "   - http://localhost:8080/quick-analyze (iPhone用クイック分析)"
echo ""

# 既存のプロセスをチェック
if lsof -ti:8080 > /dev/null 2>&1; then
    echo "⚠️  ポート8080は既に使用されています"
    echo "🔄 既存プロセスを終了します..."
    lsof -ti:8080 | xargs kill -9 2>/dev/null || true
    sleep 2
fi

echo "🚀 APIサーバーを起動中..."
echo "💡 終了するには Ctrl+C を押してください"
echo "=================================================="

# APIサーバー起動
python3 api_server.py