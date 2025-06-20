-- Clean Memo Confirmation App with Simple Format
on run
    try
        -- Get memo content with large text area
        set largeTextArea to return & return & return & return & return & return & return & return & return & return & return & return & return & return & return & return & return & return & return & return
        set displayText to "📝 Quick Memo - 内容入力" & return & return & "メモの内容を入力してください：" & return & "(タイトルは内容から自動生成されます)"
        set memoContent to text returned of (display dialog displayText default answer largeTextArea)
        
        -- Clean content
        set memoContent to my trimText(memoContent)
        
        if memoContent = "" then
            display dialog "⚠️ エラー" & return & return & "メモの内容を入力してください。" buttons {"OK"} default button "OK"
            return
        end if
        
        -- Get analysis
        set analysisResult to my getAnalysis(memoContent)
        set memoTitle to my getValue(analysisResult, "TITLE")
        set memoCategory to my getValue(analysisResult, "CATEGORY")
        set memoFolder to my getValue(analysisResult, "FOLDER")
        set memoTags to my getValue(analysisResult, "TAGS")
        set memoRelations to my getValue(analysisResult, "RELATIONS")
        set memoSummary to my getValue(analysisResult, "SUMMARY")
        set memoBulletPoints to my getValue(analysisResult, "BULLET_POINTS")
        
        -- Add date to title
        set currentDate to my getDateString()
        set memoTitle to memoTitle & " " & currentDate
        
        -- Build preview
        set previewText to my buildPreview(memoTitle, memoCategory, memoFolder, memoContent, memoTags, memoRelations, memoSummary, memoBulletPoints)
        
        -- Show confirmation
        set userChoice to button returned of (display dialog "📝 メモプレビュー" & return & return & previewText buttons {"キャンセル", "編集", "Obsidianに送信"} default button "Obsidianに送信")
        
        if userChoice = "Obsidianに送信" then
            -- Save memo
            my saveMemo(memoContent)
            display notification "✅ Obsidianに保存完了" with title "Quick Memo" subtitle memoCategory & "カテゴリ"
            
        else if userChoice = "編集" then
            -- Edit mode with cursor positioned at start
            set newContent to text returned of (display dialog "📄 内容編集:" & return & "既存の内容を編集してください：" default answer memoContent)
            my saveMemo(newContent)
            display notification "✅ 編集後メモをObsidianに保存" with title "Quick Memo"
        end if
        
    on error errorMessage
        if errorMessage does not contain "User canceled" then
            display notification "エラー: " & errorMessage with title "Quick Memo"
        end if
    end try
end run

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
            
            set AppleScript's text item delimiters to return
            set textLines to text items of remainingText
            set AppleScript's text item delimiters to ""
            
            if (count of textLines) > 0 then
                set valueText to item 1 of textLines as string
                set cleanValue to my trimText(valueText)
                
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
                        set countPart to text 1 thru colonPos of cleanValue
                        set namesPart to text (colonPos + 1) thru -1 of cleanValue
                        
                        set AppleScript's text item delimiters to ","
                        set nameParts to text items of namesPart
                        set AppleScript's text item delimiters to ", "
                        set formattedNames to nameParts as string
                        set AppleScript's text item delimiters to ""
                        
                        set cleanValue to countPart & " " & formattedNames
                    end if
                end if
                
                if cleanValue = "なし" then
                    if keyName = "TAGS" then
                        return "タグなし"
                    else if keyName = "RELATIONS" then
                        return "関連ファイルなし"
                    else
                        return "なし"
                    end if
                else
                    return cleanValue
                end if
            end if
        end if
        
        -- Fallback
        if keyName = "TITLE" then
            return "メモ"
        else if keyName = "CATEGORY" then
            return "general"
        else if keyName = "FOLDER" then
            return "Others"
        else if keyName = "TAGS" then
            return "タグなし"
        else if keyName = "RELATIONS" then
            return "関連ファイルなし"
        else
            return "不明"
        end if
        
    on error
        return "エラー"
    end try
end getValue

on buildPreview(title, category, folder, content, tags, relations, summary, bulletPoints)
    set previewLines to {}
    
    -- カテゴリの日本語表示名を取得
    set categoryDisplay to my getCategoryDisplayName(category)
    
    set end of previewLines to "📋 タイトル: " & title
    set end of previewLines to ""
    set end of previewLines to "📂 カテゴリ: " & categoryDisplay
    set end of previewLines to ""
    set end of previewLines to "🏷️ タグ: " & tags
    set end of previewLines to ""
    set end of previewLines to "🔗 関連ファイル: " & relations
    set end of previewLines to ""
    set end of previewLines to "📄 内容:"
    set end of previewLines to content
    set end of previewLines to ""
    set end of previewLines to "📝 要約:"
    if summary ≠ "" and summary ≠ "なし" then
        -- 改行を含む要約をそのまま表示（改行は自動処理）
        set end of previewLines to summary
    else
        set end of previewLines to "（要約なし）"
    end if
    set end of previewLines to ""
    
    -- 箇条書きポイントを追加
    if bulletPoints ≠ "" and bulletPoints ≠ "なし" then
        set end of previewLines to "📌 ポイント:"
        -- パイプ区切りの箇条書きを分解
        set AppleScript's text item delimiters to " | "
        set bulletList to text items of bulletPoints
        set AppleScript's text item delimiters to ""
        
        repeat with bulletItem in bulletList
            set end of previewLines to "  • " & bulletItem
        end repeat
        set end of previewLines to ""
    end if
    
    set end of previewLines to "💾 保存先: " & folder & "/" & title & ".md"
    set end of previewLines to ""
    set end of previewLines to "🤔 このメモを保存しますか？"
    
    set AppleScript's text item delimiters to return
    set previewText to previewLines as string
    set AppleScript's text item delimiters to ""
    
    return previewText
end buildPreview

on saveMemo(content)
    try
        do shell script "cd '/Users/yoshiikatsuhiko/Library/Mobile Documents/iCloud~md~obsidian/Documents/memo-classifier' && python3 preview_enhanced_memo.py save " & quoted form of content
    on error
        display dialog "保存エラーが発生しました" buttons {"OK"} default button "OK"
    end try
end saveMemo

on getDateString()
    set currentDate to current date
    set yearStr to year of currentDate as string
    set monthNum to month of currentDate as integer
    set dayNum to day of currentDate as integer
    
    set monthStr to my padZero(monthNum)
    set dayStr to my padZero(dayNum)
    
    return yearStr & "-" & monthStr & "-" & dayStr
end getDateString

on padZero(num)
    if num < 10 then
        return "0" & (num as string)
    else
        return num as string
    end if
end padZero

on trimText(inputText)
    set trimmedText to inputText
    
    repeat while (trimmedText starts with " " or trimmedText starts with return or trimmedText starts with tab)
        set trimmedText to text 2 thru -1 of trimmedText
        if length of trimmedText = 0 then exit repeat
    end repeat
    
    repeat while (trimmedText ends with " " or trimmedText ends with return or trimmedText ends with tab)
        set trimmedText to text 1 thru -2 of trimmedText
        if length of trimmedText = 0 then exit repeat
    end repeat
    
    return trimmedText
end trimText

on getCategoryDisplayName(category)
    -- カテゴリの英語名を日本語表示名に変換
    if category = "business" then
        return "ビジネス/コンサルティング"
    else if category = "tech" then
        return "技術/開発"
    else if category = "education" then
        return "教育/学習"
    else if category = "music" then
        return "音楽/音楽理論"
    else if category = "media" then
        return "メディア/コンテンツ"
    else if category = "ideas" then
        return "アイデア/発想"
    else if category = "general" then
        return "一般/その他"
    else if category = "kindle" then
        return "Kindle/読書"
    else
        return category
    end if
end getCategoryDisplayName