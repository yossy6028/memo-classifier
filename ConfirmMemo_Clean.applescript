-- Enhanced Memo Confirmation App with Preview Editing
on run
    try
        -- Get memo content with large text area (restored from previous version)
        set largeTextArea to return & return & return & return & return & return & return & return & return & return & return & return & return & return & return & return & return & return & return & return & return & return & return & return & return & return & return & return & return & return
        set displayText to "📝 Quick Memo - 内容入力" & return & return & "メモの内容を入力してください：" & return & "(タイトルは内容から自動生成されます)"
        set memoContent to text returned of (display dialog displayText default answer largeTextArea)
        
        -- Clean content
        set memoContent to my trimText(memoContent)
        
        if memoContent = "" then
            display dialog "⚠️ エラー" & return & return & "メモの内容を入力してください。" buttons {"OK"} default button "OK"
            return
        end if
        
        -- Show preview and handle editing loop
        my showPreviewWithEditing(memoContent)
        
    on error errorMessage
        if errorMessage does not contain "User canceled" then
            display notification "エラー: " & errorMessage with title "Quick Memo"
        end if
    end try
end run

on showPreviewWithEditing(originalContent)
    set loopCount to 0
    repeat
        set loopCount to loopCount + 1
        if loopCount > 10 then
            display dialog "処理を中断します（ループ制限）" buttons {"OK"} default button "OK"
            exit repeat
        end if
        
        try
            -- Get analysis with timeout
            display notification "分析中... (" & loopCount & "回目)" with title "Quick Memo"
            set analysisResult to my getAnalysis(originalContent)
            
            if analysisResult = "" then
                display dialog "分析に失敗しました。直接保存しますか？" buttons {"キャンセル", "保存"} default button "保存"
                if button returned of result = "保存" then
                    my saveMemo(originalContent)
                end if
                exit repeat
            end if
            
            set memoTitle to my getValue(analysisResult, "TITLE")
            set memoCategory to my getValue(analysisResult, "CATEGORY")
            set memoFolder to my getValue(analysisResult, "FOLDER")
            set memoTags to my getValue(analysisResult, "TAGS")
            set memoRelations to my getValue(analysisResult, "RELATIONS")
            set memoSummary to my getValue(analysisResult, "SUMMARY")
            set memoBulletPoints to my getValue(analysisResult, "BULLET_POINTS")
            
            -- Add date to title
            set currentDate to my getDateString()
            set finalTitle to memoTitle & " " & currentDate
            
            -- Build preview
            set previewText to my buildPreview(finalTitle, memoCategory, memoFolder, originalContent, memoTags, memoRelations, memoSummary, memoBulletPoints)
            
            -- Show confirmation with scroll support for long content
            set userChoice to my showPreviewWithScroll(previewText)
            
            if userChoice = "Obsidianに送信" then
                -- Save memo
                my saveMemo(originalContent)
                -- 通知はsaveMemo内で表示されるため、ここでは表示しない
                exit repeat
                
            else if userChoice = "編集" then
                -- Show editing options in secondary dialog (3-button limit workaround)
                set editChoice to button returned of (display dialog "📝 編集方法を選択してください" & return & return & "プレビュー編集: タイトル、カテゴリ、タグを編集" & return & "原文編集: メモの内容を直接編集" buttons {"キャンセル", "プレビュー編集", "原文編集"} default button "プレビュー編集")
                
                if editChoice = "プレビュー編集" then
                    -- Edit preview items
                    try
                        set editResult to my editPreviewItems(memoTitle, memoCategory, memoTags, memoSummary)
                        if editResult is not false then
                            -- Apply edits via API and continue loop
                            my applyPreviewEdits(originalContent, editResult)
                        end if
                    on error editError
                        display notification "編集エラー: " & editError with title "Quick Memo"
                        -- Continue loop
                    end try
                    
                else if editChoice = "原文編集" then
                    -- Edit original content
                    try
                        set newContent to text returned of (display dialog "📄 原文編集:" & return & "メモの内容を編集してください：" default answer originalContent)
                        set originalContent to my trimText(newContent)
                        if originalContent = "" then
                            display dialog "⚠️ エラー" & return & return & "メモの内容を入力してください。" buttons {"OK"} default button "OK"
                            exit repeat
                        end if
                    on error errorMessage
                        if errorMessage does not contain "User canceled" then
                            display notification "原文編集エラー: " & errorMessage with title "Quick Memo"
                        end if
                        exit repeat
                    end try
                end if
                
            else
                -- Cancel
                exit repeat
            end if
            
        on error loopError
            display notification "ループエラー: " & loopError with title "Quick Memo"
            display dialog "エラーが発生しました：" & return & loopError buttons {"OK"} default button "OK"
            exit repeat
        end try
    end repeat
end showPreviewWithEditing

on editPreviewItems(currentTitle, currentCategory, currentTags, currentSummary)
    try
        -- Edit title
        set newTitle to text returned of (display dialog "📋 タイトル編集:" & return & return & "タイトルを編集してください：" default answer currentTitle)
        set newTitle to my trimText(newTitle)
        
        -- Edit category
        set categoryChoices to {"education", "tech", "business", "media", "ideas", "music", "general"}
        set currentCategoryIndex to 1
        repeat with i from 1 to count of categoryChoices
            if item i of categoryChoices = currentCategory then
                set currentCategoryIndex to i
                exit repeat
            end if
        end repeat
        
        set categoryDialog to "📂 カテゴリ選択:" & return & return
        set categoryDialog to categoryDialog & "1. Education (教育)" & return
        set categoryDialog to categoryDialog & "2. Tech (技術)" & return  
        set categoryDialog to categoryDialog & "3. Business (ビジネス)" & return
        set categoryDialog to categoryDialog & "4. Media (メディア)" & return
        set categoryDialog to categoryDialog & "5. Ideas (アイデア)" & return
        set categoryDialog to categoryDialog & "6. Music (音楽)" & return
        set categoryDialog to categoryDialog & "7. General (一般)" & return & return
        set categoryDialog to categoryDialog & "番号を入力してください："
        
        set categoryChoice to text returned of (display dialog categoryDialog default answer (currentCategoryIndex as string))
        set categoryIndex to categoryChoice as integer
        if categoryIndex < 1 or categoryIndex > 7 then set categoryIndex to currentCategoryIndex
        set newCategory to item categoryIndex of categoryChoices
        
        -- Edit tags
        set newTags to text returned of (display dialog "🏷️ タグ編集:" & return & return & "タグを編集してください（スペース区切り）：" default answer currentTags)
        set newTags to my trimText(newTags)
        
        -- Edit summary  
        set newSummary to text returned of (display dialog "📝 要約編集:" & return & return & "要約を編集してください：" default answer currentSummary)
        set newSummary to my trimText(newSummary)
        
        -- Return edited values
        return {newTitle, newCategory, newTags, newSummary}
        
    on error
        return false
    end try
end editPreviewItems

on applyPreviewEdits(originalContent, editedValues)
    try
        set editedTitle to item 1 of editedValues
        set editedCategory to item 2 of editedValues  
        set editedTags to item 3 of editedValues
        set editedSummary to item 4 of editedValues
        
        -- Convert tags to list format for API
        set AppleScript's text item delimiters to " "
        set tagList to text items of editedTags
        set AppleScript's text item delimiters to ""
        
        -- Build JSON for API call
        set jsonData to "{" & return
        set jsonData to jsonData & "  \"content\": " & my escapeJSON(originalContent) & "," & return
        set jsonData to jsonData & "  \"edited_title\": " & my escapeJSON(editedTitle) & "," & return  
        set jsonData to jsonData & "  \"edited_category\": " & my escapeJSON(editedCategory) & "," & return
        set jsonData to jsonData & "  \"edited_tags\": [" & my tagsToJSON(tagList) & "]" & return
        set jsonData to jsonData & "}"
        
        -- Save to temp file
        set tempFile to "/tmp/memo_edit.json"
        do shell script "echo " & quoted form of jsonData & " > " & quoted form of tempFile
        
        -- Call edit API
        set curlCmd to "curl -X POST http://localhost:8080/edit-suggestion -H 'Content-Type: application/json' -d @" & quoted form of tempFile
        set apiResponse to do shell script curlCmd
        
        -- Clean up
        do shell script "rm -f " & quoted form of tempFile
        
        -- Check response
        if apiResponse contains "\"success\": true" then
            display notification "✅ プレビュー編集を適用しました" with title "Quick Memo"
        else
            display notification "⚠️ 編集の適用に失敗しました" with title "Quick Memo"
        end if
        
    on error errorMsg
        display notification "❌ API呼び出しエラー: " & errorMsg with title "Quick Memo"
    end try
end applyPreviewEdits

on escapeJSON(inputText)
    set escapedText to inputText
    set escapedText to my replaceText(escapedText, "\\", "\\\\")
    set escapedText to my replaceText(escapedText, "\"", "\\\"")
    set escapedText to my replaceText(escapedText, return, "\\n")
    set escapedText to my replaceText(escapedText, tab, "\\t")
    return "\"" & escapedText & "\""
end escapeJSON

on tagsToJSON(tagList)
    set jsonTags to ""
    repeat with i from 1 to count of tagList
        if i > 1 then set jsonTags to jsonTags & ", "
        set jsonTags to jsonTags & my escapeJSON(item i of tagList)
    end repeat
    return jsonTags
end tagsToJSON

on replaceText(inputText, searchText, replaceText)
    set AppleScript's text item delimiters to searchText
    set textItems to text items of inputText
    set AppleScript's text item delimiters to replaceText
    set outputText to textItems as string
    set AppleScript's text item delimiters to ""
    return outputText
end replaceText

-- Existing helper functions (getAnalysis, getValue, buildPreview, etc.)
on getAnalysis(content)
    try
        set shellCmd to "cd '/Users/yoshiikatsuhiko/Library/Mobile Documents/iCloud~md~obsidian/Documents/memo-classifier' && python3 preview_enhanced_memo.py preview " & quoted form of content
        set output to do shell script shellCmd
        
        if output contains "RESULT_START" and output contains "RESULT_END" then
            set startPos to (offset of "RESULT_START" in output) + 12
            set endPos to (offset of "RESULT_END" in output) - 1
            return text startPos thru endPos of output
        else
            return "TITLE:メモ" & return & "CATEGORY:general" & return & "TAGS:なし" & return & "RELATIONS:なし"
        end if
    on error
        return "TITLE:メモ" & return & "CATEGORY:general" & return & "TAGS:なし" & return & "RELATIONS:なし"
    end try
end getAnalysis

on getValue(resultText, keyName)
    try
        set keyPattern to keyName & ":"
        if resultText contains keyPattern then
            set keyStart to (offset of keyPattern in resultText) + (length of keyPattern)
            set remainingText to text keyStart thru -1 of resultText
            
            -- 改行文字（CR、LF、CRLF）を統一的に処理
            set AppleScript's text item delimiters to {return, linefeed, return & linefeed}
            set textLines to text items of remainingText
            set AppleScript's text item delimiters to ""
            
            if (count of textLines) > 0 then
                -- 最初の非空行を取得
                set valueText to ""
                repeat with i from 1 to count of textLines
                    set currentLine to item i of textLines as string
                    set trimmedLine to my trimText(currentLine)
                    if trimmedLine ≠ "" then
                        set valueText to trimmedLine
                        exit repeat
                    end if
                end repeat
                
                if valueText = "" then
                    return "なし"
                end if
                
                set cleanValue to valueText
                
                -- Format tags
                if keyName = "TAGS" and cleanValue ≠ "なし" then
                    set AppleScript's text item delimiters to ","
                    set tagParts to text items of cleanValue
                    set AppleScript's text item delimiters to " "
                    set cleanValue to tagParts as string
                    set AppleScript's text item delimiters to ""
                end if
                
                -- Format relations
                if keyName = "RELATIONS" and cleanValue ≠ "なし" then
                    if cleanValue contains "件:" then
                        set colonPos to (offset of ":" in cleanValue)
                        set beforeColon to text 1 thru (colonPos - 1) of cleanValue
                        set afterColon to text (colonPos + 1) thru -1 of cleanValue
                        set cleanValue to beforeColon & ": " & my trimText(afterColon)
                    end if
                end if
                
                return cleanValue
            end if
        end if
        return "なし"
    on error
        return "なし"
    end try
end getValue

on showPreviewWithScroll(previewText)
    -- 長いコンテンツの場合はスクロール可能な表示を使用
    try
        -- コンテンツ長をチェック（AppleScriptの文字数制限考慮）
        set contentLength to count of characters in previewText
        
        if contentLength > 1500 then
            -- 非常に長いコンテンツの場合：編集可能フィールドでスクロール表示
            try
                set scrollDialog to display dialog "📝 メモプレビュー（スクロール可能）" & return & return & "以下のフィールドで全内容をスクロールして確認できます:" default answer previewText buttons {"キャンセル", "編集", "Obsidianに送信"} default button "Obsidianに送信"
                set userChoice to button returned of scrollDialog
            on error
                -- フォールバック：標準表示
                set shortPreview to text 1 thru 1000 of previewText & return & return & "... (内容が長いため省略されました)"
                set userChoice to button returned of (display dialog "📝 メモプレビュー" & return & return & shortPreview buttons {"キャンセル", "編集", "Obsidianに送信"} default button "Obsidianに送信")
            end try
        else if contentLength > 800 then
            -- 中程度の長さ：短縮版とフル表示のオプション
            set shortPreview to text 1 thru 600 of previewText & return & return & "... (続きを見るには「詳細表示」を選択)"
            set viewChoice to button returned of (display dialog "📝 メモプレビュー" & return & return & shortPreview buttons {"キャンセル", "詳細表示", "そのまま送信"} default button "そのまま送信")
            
            if viewChoice = "詳細表示" then
                -- 全文をスクロール表示
                try
                    set scrollDialog to display dialog "📝 メモプレビュー（全文）" default answer previewText buttons {"キャンセル", "編集", "Obsidianに送信"} default button "Obsidianに送信"
                    set userChoice to button returned of scrollDialog
                on error
                    set userChoice to "Obsidianに送信"
                end try
            else if viewChoice = "そのまま送信" then
                set userChoice to "Obsidianに送信"
            else
                set userChoice to "キャンセル"
            end if
        else
            -- 通常の長さ：標準表示
            set userChoice to button returned of (display dialog "📝 メモプレビュー" & return & return & previewText buttons {"キャンセル", "編集", "Obsidianに送信"} default button "Obsidianに送信")
        end if
        
        return userChoice
        
    on error errorMsg
        -- エラー時のフォールバック
        display notification "表示エラーが発生しました: " & errorMsg with title "Quick Memo"
        set userChoice to button returned of (display dialog "📝 メモプレビュー（簡易表示）" & return & return & "プレビュー表示でエラーが発生しました。続行しますか？" buttons {"キャンセル", "編集", "Obsidianに送信"} default button "Obsidianに送信")
        return userChoice
    end try
end showPreviewWithScroll

on buildPreview(title, category, folder, content, tags, relations, summary, bulletPoints)
    set preview to "📋 タイトル: " & title & return & return
    set preview to preview & "📂 カテゴリ: " & category & return & return
    set preview to preview & "🏷️ タグ: " & tags & return & return
    
    if relations ≠ "なし" then
        set preview to preview & "🔗 関連ファイル: " & relations & return & return
    end if
    
    set preview to preview & "📄 内容:" & return & content & return & return
    
    if summary ≠ "なし" then
        set preview to preview & "📝 要約:" & return & summary & return & return
    end if
    
    if bulletPoints ≠ "なし" then
        set preview to preview & "📌 ポイント:" & return
        -- 箇条書きをパイプ区切りから改行区切りに変換
        set AppleScript's text item delimiters to " | "
        set bulletList to text items of bulletPoints
        set AppleScript's text item delimiters to ""
        
        repeat with bullet in bulletList
            set preview to preview & "  • " & bullet & return
        end repeat
        set preview to preview & return
    end if
    
    set preview to preview & "💾 保存先: " & folder & "/" & title & ".md"
    
    return preview
end buildPreview

on saveMemo(content)
    try
        if content = "" then
            display notification "保存エラー: 空のメモは保存できません" with title "Quick Memo"
            return
        end if
        
        -- デバッグ用ラッパーを使用
        set shellCmd to "cd '/Users/yoshiikatsuhiko/Library/Mobile Documents/iCloud~md~obsidian/Documents/memo-classifier' && /usr/bin/python3 debug_save.py " & quoted form of content
        
        -- 実行
        try
            set saveResult to do shell script shellCmd
            
            -- シンプルな成功判定
            if saveResult contains "SUCCESS" then
                display notification "✅ 保存完了" with title "Quick Memo"
                display dialog "保存が完了しました！" & return & return & "Obsidianでファイルを確認してください。" buttons {"OK"} default button "OK"
            else
                display notification "❌ 保存失敗: " & saveResult with title "Quick Memo"
                -- デバッグ情報を表示
                set debugInfo to do shell script "cat /tmp/memo_save_debug.log | tail -20"
                display dialog "保存失敗の詳細:" & return & return & debugInfo buttons {"OK"} default button "OK"
            end if
            
        on error shellError
            -- エラーの場合
            display notification "❌ エラー発生" with title "Quick Memo"
            -- デバッグログを確認
            try
                set debugLog to do shell script "cat /tmp/memo_save_debug.log | tail -20"
                display dialog "エラー詳細:" & return & return & shellError & return & return & "デバッグログ:" & return & debugLog buttons {"OK"} default button "OK"
            on error
                display dialog "保存エラー:" & return & return & shellError buttons {"OK"} default button "OK"
            end try
        end try
        
    on error errorMessage
        display notification "❌ 保存エラー: " & errorMessage with title "Quick Memo"
        display dialog "保存に失敗しました" & return & return & "エラー詳細: " & errorMessage buttons {"OK"} default button "OK"
    end try
end saveMemo

on getDateString()
    set currentDate to current date
    set yearValue to year of currentDate as string
    set monthValue to (month of currentDate as integer)
    set dayValue to day of currentDate as integer
    
    set monthStr to monthValue as string
    if monthValue < 10 then set monthStr to "0" & monthStr
    
    set dayStr to dayValue as string  
    if dayValue < 10 then set dayStr to "0" & dayStr
    
    return yearValue & "-" & monthStr & "-" & dayStr
end getDateString

on trimText(inputText)
    if inputText = "" then return ""
    
    -- Remove leading whitespace
    repeat while (length of inputText > 0) and (character 1 of inputText is in {" ", tab, return, linefeed})
        set inputText to text 2 thru -1 of inputText
    end repeat
    
    -- Remove trailing whitespace
    repeat while (length of inputText > 0) and (character -1 of inputText is in {" ", tab, return, linefeed})
        set inputText to text 1 thru -2 of inputText
    end repeat
    
    return inputText
end trimText