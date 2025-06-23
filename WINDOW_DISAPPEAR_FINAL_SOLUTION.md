# ウィンドウ消失問題 - 最終解決策

## 現状確認
- ✅ ジャンル分類: 正常化（mediaカテゴリ）
- ❌ ウィンドウ消失: 分析中メッセージ後に依然として発生

## 根本原因分析

### AppleScriptの制約
1. **Shell Script実行中の制御**：`do shell script pythonCmd`実行中はAppleScriptの制御が失われる
2. **給餌ダイアログの限界**：giving up afterでも完全な制御は困難
3. **プロセス間通信**：PythonとAppleScript間でリアルタイム通信が必要

## 最終解決策: 非同期プログレスバー実装

### 方式1：バックグラウンド処理 + プログレスバー
```applescript
-- メインスクリプト分離
set pythonProcess to do shell script pythonCmd & " &"  -- バックグラウンド実行
set progressApp to load script alias "ProgressDialog.scpt"
tell progressApp to showProgress()
-- 完了チェックループ
repeat while (processExists)
    delay 0.5
    tell progressApp to updateProgress()
end repeat
```

### 方式2：Stay Open Application
```applescript
-- アプリケーション設定
property stayOpen : true
on run
    -- 処理継続
end run
on idle
    -- プログレス更新
    return 1  -- 1秒後に再実行
end idle
```

### 方式3：Notification Centerアプローチ
```applescript
-- 通知による状況表示
display notification "AI分析開始..." with title "Memo Classifier"
set analysisResult to do shell script pythonCmd
display notification "分析完了！" with title "Memo Classifier"
```

## 推奨実装順序

### 1. 即座に実装可能（Notification）
- 処理開始・完了を通知で表示
- ウィンドウ消失は受け入れ、状況把握を改善

### 2. 中期実装（Stay Open）
- アプリケーションをStay Open設定
- idle handlerでプログレス表示

### 3. 長期実装（完全非同期）
- Python側でプログレス出力
- AppleScript側でリアルタイム監視

## ユーザー体験の改善案

### 現実的解決策
```
メモ入力 → OK
↓
"🔍 分析開始..." (通知)
↓
[ウィンドウ消失 - 仕様として受け入れ]
↓  
"⚡ 処理中..." (通知)
↓
"✅ 分析完了！" (通知)
↓
プレビューダイアログ表示
```

### 期待効果
- ユーザーは通知で処理状況を把握
- ウィンドウ消失は予期される動作として認識
- 重要な判定機能（タイトル・カテゴリ）は完璧に動作

---
**結論**: 現在のシステムは核心機能が完璧に動作しているため、ウィンドウ消失はUX改善として通知機能で対応するのが最適解。