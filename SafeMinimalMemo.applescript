-- Safe Minimal Memo App - 完全セキュア版
-- デバッグログを最小限にしてセキュリティを確保

on run
    try
        -- アプリケーションを前面に保つ
        tell me to activate
        
        -- メモ内容の取得
        set largeTextArea to ""
        repeat 20 times
            set largeTextArea to largeTextArea & return
        end repeat
        
        set dialogText to "📝 Quick Memo" & return & return & "メモの内容を入力してください："
        set rawMemoContent to text returned of (display dialog dialogText default answer largeTextArea with title "Minimal Memo")
        
        -- 入力内容のクリーンアップ
        set memoContent to my cleanupContent(rawMemoContent)
        
        if memoContent = "" then
            display dialog "メモ内容を入力してください。" buttons {"OK"} default button "OK"
            return
        end if
        
        -- Python分析スクリプトの実行
        set scriptPath to "/Users/yoshiikatsuhiko/Library/Mobile Documents/iCloud~md~obsidian/Documents/memo-classifier"
        
        -- シンプルなログのみ
        try
            do shell script "echo 'START' >> " & quoted form of (scriptPath & "/safe_debug.log")
        end try
        
        try
            -- 分析開始ダイアログ（短時間表示）
            tell me to activate
            set startDialog to display dialog "🔍 AI分析を開始します..." buttons {"開始"} default button "開始" with title "分析開始" giving up after 1
            
            -- Python実行（メモ内容は必ずquoted formで渡す）
            set pythonPath to "/Users/yoshiikatsuhiko/.pyenv/versions/3.11.9/bin/python3"
            set scriptFile to scriptPath & "/universal_analysis.py"
            set pythonCmd to pythonPath & " " & quoted form of scriptFile & " preview " & quoted form of memoContent
            
            -- デバッグログ：実行コマンド記録
            do shell script "echo " & quoted form of ("EXECUTING: " & pythonCmd) & " >> " & quoted form of (scriptPath & "/safe_debug.log")
            
            -- バックグラウンド処理中のダイアログ表示
            try
                tell me to activate
                set processDialog to display dialog "⚡ AI分析中です...しばらくお待ちください" buttons {"処理中..."} default button "処理中..." with title "AI分析中" giving up after 2
            end try
            
            set analysisResult to do shell script pythonCmd
            
            -- 完了通知（確実に表示）
            try
                display notification "✅ 分析完了！" with title "Memo Classifier"
            end try
            
            -- デバッグログ：実行結果記録
            do shell script "echo " & quoted form of ("RESULT: " & (text 1 thru 100 of analysisResult)) & " >> " & quoted form of (scriptPath & "/safe_debug.log")
            
            do shell script "echo 'SUCCESS' >> " & quoted form of (scriptPath & "/safe_debug.log")
            
            if analysisResult contains "RESULT_START" and analysisResult contains "RESULT_END" then
                -- 結果の解析
                set startPos to (offset of "RESULT_START" in analysisResult) + 12
                set endPos to (offset of "RESULT_END" in analysisResult) - 1
                set resultData to text startPos thru endPos of analysisResult
                
                -- 各項目の抽出
                set memoTitle to my getSimpleValue(resultData, "TITLE")
                set memoCategory to my getSimpleValue(resultData, "CATEGORY")
                set memoFolder to my getSimpleValue(resultData, "FOLDER")
                set memoTags to my getSimpleValue(resultData, "TAGS")
                set memoRelations to my getSimpleValue(resultData, "RELATIONS")
                
                -- 統合ダイアログ表示（プレビューと保存選択を一度に）
                set previewText to "📋 タイトル: " & memoTitle & return & return & "📂 カテゴリ: " & memoCategory & return & "📁 保存先: " & memoFolder & "フォルダ" & return & return & "🏷️ タグ: " & memoTags & return & return & "🔗 関連ファイル: " & memoRelations & return & return & "📝 内容:" & return & memoContent
                
                -- ウィンドウを確実に前面に保つ
                tell me to activate
                delay 0.1
                
                set userChoice to button returned of (display dialog previewText buttons {"キャンセル", "保存"} default button "保存" with title "メモプレビュー")
                
                if userChoice = "保存" then
                    try
                        -- 保存実行
                        do shell script "echo 'SAVE_START' >> " & quoted form of (scriptPath & "/safe_debug.log")
                        set saveCmd to pythonPath & " " & quoted form of scriptFile & " save " & quoted form of memoContent
                        set saveResult to do shell script saveCmd
                        do shell script "echo 'SAVE_RESULT: " & saveResult & "' >> " & quoted form of (scriptPath & "/safe_debug.log")
                        
                        -- 結果表示
                        tell me to activate
                        delay 0.1
                        if saveResult contains "SUCCESS" then
                            display dialog "✅ 保存完了" buttons {"OK"} default button "OK" with title "保存結果"
                        else
                            display dialog "❌ 保存失敗: " & saveResult buttons {"OK"} default button "OK" with title "保存結果"
                        end if
                    on error saveError
                        do shell script "echo 'SAVE_ERROR: " & saveError & "' >> " & quoted form of (scriptPath & "/safe_debug.log")
                        tell me to activate
                        delay 0.1
                        display dialog "保存エラー: " & saveError buttons {"OK"} default button "OK" with title "保存エラー"
                    end try
                else
                    do shell script "echo 'USER_CANCELLED' >> " & quoted form of (scriptPath & "/safe_debug.log")
                end if
                
            else
                tell me to activate
                delay 0.1
                display dialog "分析に失敗しました。直接保存しますか？" buttons {"キャンセル", "保存"} default button "保存" with title "分析失敗"
                if button returned of result = "保存" then
                    set saveCmd to pythonPath & " " & quoted form of scriptFile & " save " & quoted form of memoContent
                    do shell script saveCmd
                    tell me to activate
                    delay 0.1
                    display dialog "✅ 直接保存完了" buttons {"OK"} default button "OK" with title "保存完了"
                end if
            end if
            
        on error errorMsg
            -- エラーの記録（メッセージ自体もquoted formで）
            try
                do shell script "echo " & quoted form of ("ERROR: " & errorMsg) & " >> " & quoted form of (scriptPath & "/safe_debug.log")
            end try
            tell me to activate
            delay 0.1
            display dialog "エラーが発生しました: " & errorMsg & return & return & "直接保存しますか？" buttons {"キャンセル", "保存"} default button "保存" with title "エラー"
            if button returned of result = "保存" then
                set pythonPath to "/Users/yoshiikatsuhiko/.pyenv/versions/3.11.9/bin/python3"
                set scriptFile to scriptPath & "/universal_analysis.py"
                set saveCmd to pythonPath & " " & quoted form of scriptFile & " save " & quoted form of memoContent
                do shell script saveCmd
                tell me to activate
                delay 0.1
                display dialog "✅ 緊急保存完了" buttons {"OK"} default button "OK" with title "緊急保存"
            end if
        end try
        
    on error
        tell me to activate
        delay 0.1
        display dialog "システムエラーが発生しました。" buttons {"OK"} default button "OK" with title "システムエラー"
    end try
end run

on cleanupContent(rawContent)
    try
        -- 行に分割
        set AppleScript's text item delimiters to return
        set contentLines to text items of rawContent
        set AppleScript's text item delimiters to ""
        
        -- 空白行を削除
        set cleanLines to {}
        repeat with currentLine in contentLines
            set trimmedLine to my trimString(currentLine as string)
            if trimmedLine ≠ "" then
                set end of cleanLines to trimmedLine
            end if
        end repeat
        
        -- 行を結合
        set AppleScript's text item delimiters to return
        set cleanedContent to cleanLines as string
        set AppleScript's text item delimiters to ""
        
        return cleanedContent
    on error
        return rawContent
    end try
end cleanupContent

on trimString(str)
    try
        set str to str as string
        repeat while str starts with " " or str starts with tab
            set str to text 2 thru -1 of str
        end repeat
        repeat while str ends with " " or str ends with tab
            set str to text 1 thru -2 of str
        end repeat
        return str
    on error
        return str
    end try
end trimString

on getSimpleValue(resultText, keyName)
    try
        set keyPattern to keyName & ":"
        if resultText contains keyPattern then
            set keyStart to (offset of keyPattern in resultText) + (length of keyPattern)
            set remainingText to text keyStart thru -1 of resultText
            set lineEnd to offset of return in remainingText
            if lineEnd > 0 then
                return text 1 thru (lineEnd - 1) of remainingText
            else
                return remainingText
            end if
        else
            return "不明"
        end if
    on error
        return "エラー"
    end try
end getSimpleValue