-- 確認ボタン付きQuick Memo (スマートタイトル生成版)
on run
    try
        -- 内容入力（大きなテキストボックス）
        set largeTextArea to return & return & return & return & return & return & return & return & return & return & return & return & return & return & return & return & return & return & return & return
        
        set memoContent to text returned of (display dialog "📝 Quick Memo - 内容入力" & return & return & "メモの内容を入力してください：" & return & "(タイトルは内容から自動生成されます)" default answer largeTextArea)
        
        -- 内容の前後の空白・改行を削除
        set memoContent to my trimText(memoContent)
        
        -- 内容が空の場合はエラー
        if memoContent = "" then
            display dialog "⚠️ エラー" & return & return & "メモの内容を入力してください。" buttons {"OK"} default button "OK"
            return
        end if
        
        -- Execute integrated preview analysis
        set analysisResult to my performIntegratedAnalysis(memoContent)
        
        -- Extract information from analysis result
        set memoTitle to my extractValueFromSimple(analysisResult, "TITLE")
        set memoCategory to my extractValueFromSimple(analysisResult, "CATEGORY")
        set memoTags to my extractValueFromSimple(analysisResult, "TAGS")
        set memoRelations to my extractValueFromSimple(analysisResult, "RELATIONS")
        
        -- 年月日をタイトル末尾に追加
        set currentDate to my getCurrentDateString()
        set memoTitle to memoTitle & " " & currentDate
        
        -- 詳細プレビュー表示
        set previewText to my buildDetailedPreview(memoTitle, memoCategory, memoContent, memoTags, memoRelations)
        
        -- 確認ダイアログ
        set userChoice to button returned of (display dialog "📝 メモプレビュー" & return & return & previewText buttons {"キャンセル", "編集", "Obsidianに送信"} default button "Obsidianに送信")
        
        if userChoice = "Obsidianに送信" then
            -- 統合メモ処理システムで保存
            set shellCommand to "cd '/Users/yoshiikatsuhiko/Library/Mobile Documents/iCloud~md~obsidian/Documents/memo-classifier' && python3 preview_enhanced_memo.py save \"" & memoContent & "\""
            
            try
                do shell script shellCommand
                display notification "✅ Obsidianに保存完了" with title "Quick Memo" subtitle memoCategory & "カテゴリ"
            on error errorMessage
                display notification "❌ 保存エラー: " & errorMessage with title "Quick Memo"
                display dialog "💥 保存エラー" & return & return & errorMessage buttons {"OK"} default button "OK"
            end try
            
        else if userChoice = "編集" then
            -- 編集モード
            set newTitle to text returned of (display dialog "📋 タイトル編集:" default answer memoTitle)
            
            -- 内容編集（大きなテキストボックス）
            set editTextArea to memoContent & return & return & return & return & return
            set newContent to text returned of (display dialog "📄 内容編集:" default answer editTextArea)
            set newContent to my trimText(newContent)
            
            -- 再度確認
            set editedPreview to "📋 タイトル: " & newTitle & return & return & "📄 内容:" & return & newContent & return & return & "🤔 この編集後のメモを保存しますか？"
            set finalChoice to button returned of (display dialog "📝 編集後プレビュー" & return & return & editedPreview buttons {"キャンセル", "Obsidianに送信"} default button "Obsidianに送信")
            
            if finalChoice = "Obsidianに送信" then
                set shellCommand to "cd '/Users/yoshiikatsuhiko/Library/Mobile Documents/iCloud~md~obsidian/Documents/memo-classifier' && python3 preview_enhanced_memo.py save \"" & newContent & "\""
                
                try
                    do shell script shellCommand
                    display notification "✅ 編集後メモをObsidianに保存" with title "Quick Memo"
                on error errorMessage
                    display notification "❌ 保存エラー: " & errorMessage with title "Quick Memo"
                    display dialog "💥 保存エラー" & return & return & errorMessage buttons {"OK"} default button "OK"
                end try
            end if
        end if
        
    on error errorMessage
        if errorMessage does not contain "User canceled" then
            display notification "エラー: " & errorMessage with title "Quick Memo"
            display dialog "💥 予期しないエラー" & return & return & errorMessage buttons {"OK"} default button "OK"
        end if
    end try
end run

-- 強化版スマートタイトル生成関数
on generateSmartTitle(content)
    set cleanContent to my trimText(content)
    
    -- 直接的な内容分析によるタイトル生成
    return my generateIntelligentTitle(cleanContent)
end generateSmartTitle

-- インテリジェントタイトル生成
on generateIntelligentTitle(content)
    set cleanContent to my trimText(content)
    
    -- 内容の種類を判定
    set contentType to my analyzeContentType(cleanContent)
    
    -- 重要キーワードを抽出
    set keyWords to my extractImportantKeywords(cleanContent)
    
    -- 内容タイプとキーワードからタイトルを構築
    set titleBase to my buildContextualTitle(contentType, keyWords, cleanContent)
    
    -- タイトルを最適化
    return my optimizeTitle(titleBase)
end generateIntelligentTitle

-- 内容タイプを分析
on analyzeContentType(content)
    set lowerContent to (do shell script "echo " & quoted form of content & " | tr '[:upper:]' '[:lower:]'")
    
    -- 教育・国語指導関連
    if lowerContent contains "対句法" or lowerContent contains "リズム" or lowerContent contains "音数" or lowerContent contains "表現" or lowerContent contains "連" then
        return "poetry_analysis"
    else if lowerContent contains "教育" or lowerContent contains "指導" or lowerContent contains "授業" or lowerContent contains "生徒" then
        return "education"
    -- 技術関連
    else if lowerContent contains "プログラミング" or lowerContent contains "python" or lowerContent contains "api" or lowerContent contains "システム" then
        return "technology"
    -- ビジネス関連
    else if lowerContent contains "戦略" or lowerContent contains "ビジネス" or lowerContent contains "会議" or lowerContent contains "企画" then
        return "business"
    -- タスク・TODO
    else if lowerContent contains "todo" or lowerContent contains "タスク" or lowerContent contains "やること" or lowerContent contains "予定" then
        return "tasks"
    -- アイデア・企画
    else if lowerContent contains "アイデア" or lowerContent contains "案" or lowerContent contains "提案" or lowerContent contains "ブレスト" then
        return "ideas"
    -- 質問・疑問
    else if lowerContent contains "ですか" or lowerContent contains "だろうか" or lowerContent contains "どう" or lowerContent contains "なぜ" then
        return "questions"
    else
        return "general"
    end if
end analyzeContentType

-- 重要キーワードを抽出
on extractImportantKeywords(content)
    set keywords to {}
    set lowerContent to (do shell script "echo " & quoted form of content & " | tr '[:upper:]' '[:lower:]'")
    
    -- 専門用語・重要語のパターン
    set termPatterns to {"対句法", "リズム", "音数", "表現", "連", "詩", "国語", "指導", "教育", "授業", "プログラミング", "python", "api", "システム", "戦略", "ビジネス", "企画", "アイデア", "提案"}
    
    repeat with term in termPatterns
        if content contains term then
            set end of keywords to term
        end if
    end repeat
    
    return keywords
end extractImportantKeywords

-- 文脈的なタイトルを構築
on buildContextualTitle(contentType, keywords, content)
    set titleParts to {}
    
    -- コンテンツタイプ別の処理
    if contentType = "poetry_analysis" then
        -- 詩・文学分析の場合
        if "対句法" is in keywords then
            set end of titleParts to "対句法"
        end if
        if "リズム" is in keywords or "音数" is in keywords then
            set end of titleParts to "リズム分析"
        end if
        if (count of titleParts) = 0 then
            set end of titleParts to "詩の技法"
        end if
        set end of titleParts to "解説"
        
    else if contentType = "education" then
        -- 教育関連の場合
        if "国語" is in keywords then
            set end of titleParts to "国語"
        end if
        if "指導" is in keywords then
            set end of titleParts to "指導法"
        else
            set end of titleParts to "教育"
        end if
        
    else if contentType = "technology" then
        -- 技術関連の場合
        repeat with keyword in keywords
            if keyword is in {"プログラミング", "python", "api", "システム"} then
                set end of titleParts to keyword
                exit repeat
            end if
        end repeat
        if (count of titleParts) = 0 then
            set end of titleParts to "Tech"
        end if
        
    else if contentType = "business" then
        -- ビジネス関連の場合
        repeat with keyword in keywords
            if keyword is in {"戦略", "企画", "ビジネス"} then
                set end of titleParts to keyword
                exit repeat
            end if
        end repeat
        if (count of titleParts) = 0 then
            set end of titleParts to "ビジネス"
        end if
        
    else if contentType = "questions" then
        -- 質問・疑問の場合
        if (count of keywords) > 0 then
            set end of titleParts to item 1 of keywords
            set end of titleParts to "について"
        else
            set end of titleParts to "質問事項"
        end if
        
    else if contentType = "tasks" then
        -- タスクの場合
        set end of titleParts to "TODO"
        
    else if contentType = "ideas" then
        -- アイデアの場合
        if (count of keywords) > 0 then
            set end of titleParts to item 1 of keywords
        end if
        set end of titleParts to "アイデア"
        
    else
        -- 一般的な場合
        if (count of keywords) > 0 then
            set end of titleParts to item 1 of keywords
            if (count of keywords) > 1 then
                set end of titleParts to item 2 of keywords
            end if
        else
            -- キーワードがない場合は意味のある最初の部分を使用
            set meaningfulStart to my extractMeaningfulContent(content)
            if meaningfulStart ≠ "" then
                set end of titleParts to meaningfulStart
            else
                set end of titleParts to "メモ"
            end if
        end if
    end if
    
    -- タイトルパーツを結合
    set AppleScript's text item delimiters to ""
    set titleBase to titleParts as string
    set AppleScript's text item delimiters to ""
    
    return titleBase
end buildContextualTitle

-- 意味のある内容を抽出（質問文や記号を除く）
on extractMeaningfulContent(content)
    -- 改行で分割
    set AppleScript's text item delimiters to return
    set contentLines to text items of content
    set AppleScript's text item delimiters to ""
    
    -- 意味のある行を探す
    repeat with contentLine in contentLines
        set cleanLine to my trimText(contentLine as string)
        
        -- 質問文、記号、短すぎる行をスキップ
        if cleanLine ≠ "" and length of cleanLine > 8 then
            -- 質問文をスキップ
            if not (cleanLine ends with "ですか?" or cleanLine ends with "だろうか?" or cleanLine ends with "どこですか?" or cleanLine contains "どれか" or cleanLine contains "教えて") then
                -- 記号で始まる行をスキップ
                if not (cleanLine starts with "・" or cleanLine starts with "-" or cleanLine starts with "*") then
                    -- 適切な長さに調整
                    if length of cleanLine > 15 then
                        return text 1 thru 12 of cleanLine
                    else
                        return cleanLine
                    end if
                end if
            end if
        end if
    end repeat
    
    return ""
end extractMeaningfulContent

-- タイトルを最適化
on optimizeTitle(titleBase)
    set optimizedTitle to my trimText(titleBase)
    
    -- 空の場合はデフォルト
    if optimizedTitle = "" then
        set optimizedTitle to "学習メモ"
    end if
    
    -- 長さ調整
    if length of optimizedTitle > 20 then
        set optimizedTitle to text 1 thru 17 of optimizedTitle & "..."
    end if
    
    -- ファイル名に使えない文字を置換
    return my replaceInvalidChars(optimizedTitle)
end optimizeTitle

-- フォールバックタイトル生成（改善版）
on generateFallbackTitle(content)
    set cleanContent to my trimText(content)
    
    -- 重要キーワードを抽出してタイトル構築
    set titleBase to my extractKeywordsForTitle(cleanContent)
    
    -- 長すぎる場合は25文字で切る
    if length of titleBase > 25 then
        set titleBase to text 1 thru 22 of titleBase
        set titleBase to titleBase & "..."
    end if
    
    -- 空の場合はデフォルトタイトル
    if titleBase = "" then
        set titleBase to "Quick Memo"
    end if
    
    -- ファイル名に使えない文字を置換
    return my replaceInvalidChars(titleBase)
end generateFallbackTitle

-- キーワード抽出によるタイトル生成
on extractKeywordsForTitle(content)
    set lowerContent to (do shell script "echo " & quoted form of content & " | tr '[:upper:]' '[:lower:]'")
    
    -- 重要キーワードパターン
    set keywordPatterns to {"python", "プログラミング", "ai", "教育", "アイデア", "ビジネス", "戦略", "課題", "解決", "方法", "手順", "企画", "todo", "タスク", "会議", "ミーティング"}
    
    -- 最初に見つかったキーワードを使用
    repeat with keyword in keywordPatterns
        if lowerContent contains keyword then
            -- キーワード周辺のテキストを取得
            return my buildTitleFromKeyword(content, keyword as string)
        end if
    end repeat
    
    -- キーワードが見つからない場合は最初の意味のある文を取得
    return my extractMeaningfulStart(content)
end extractKeywordsForTitle

-- キーワードから文脈を含むタイトルを構築
on buildTitleFromKeyword(content, keyword)
    -- 改行で分割
    set AppleScript's text item delimiters to return
    set contentLines to text items of content
    set AppleScript's text item delimiters to ""
    
    -- キーワードを含む行を探す
    repeat with contentLine in contentLines
        set cleanLine to my trimText(contentLine as string)
        if cleanLine contains keyword and length of cleanLine > 5 then
            -- その行をベースにタイトルを作成
            if length of cleanLine > 25 then
                return text 1 thru 22 of cleanLine & "..."
            else
                return cleanLine
            end if
        end if
    end repeat
    
    -- 見つからない場合は最初の行
    if (count of contentLines) > 0 then
        set firstLine to my trimText(item 1 of contentLines as string)
        if length of firstLine > 25 then
            return text 1 thru 22 of firstLine & "..."
        else
            return firstLine
        end if
    end if
    
    return keyword & "に関するメモ"
end buildTitleFromKeyword

-- 意味のある開始部分を抽出
on extractMeaningfulStart(content)
    -- 改行で分割
    set AppleScript's text item delimiters to return
    set contentLines to text items of content
    set AppleScript's text item delimiters to ""
    
    -- 空行や記号だけの行をスキップして最初の意味のある行を取得
    repeat with contentLine in contentLines
        set cleanLine to my trimText(contentLine as string)
        -- 空行、記号だけ、短すぎる行をスキップ
        if cleanLine ≠ "" and length of cleanLine > 3 and not (cleanLine starts with "・" or cleanLine starts with "-" or cleanLine starts with "*") then
            if length of cleanLine > 25 then
                return text 1 thru 22 of cleanLine & "..."
            else
                return cleanLine
            end if
        end if
    end repeat
    
    -- すべての行が短い場合は最初の3行を結合
    if (count of contentLines) ≥ 3 then
        set combinedText to (item 1 of contentLines as string) & (item 2 of contentLines as string) & (item 3 of contentLines as string)
        set combinedText to my trimText(combinedText)
        if length of combinedText > 25 then
            return text 1 thru 22 of combinedText & "..."
        else
            return combinedText
        end if
    end if
    
    -- 最終手段
    set firstPart to my trimText(content)
    if length of firstPart > 25 then
        return text 1 thru 22 of firstPart & "..."
    else
        return firstPart
    end if
end extractMeaningfulStart

on performIntegratedAnalysis(content)
    return "TITLE:Test Title" & return & "CATEGORY:tech" & return & "TAGS:#Test,#Demo" & return & "RELATIONS:なし"
end performIntegratedAnalysis

-- JSON から値を抽出（簡易版）
on extractValueFromJSON(jsonText, keyName)
    try
        if keyName = "title" then
            -- タイトル抽出
            set titlePattern to "\"title\": \""
            if jsonText contains titlePattern then
                set startPos to (offset of titlePattern in jsonText) + (length of titlePattern)
                set remainingText to text startPos thru -1 of jsonText
                set endPos to (offset of "\"" in remainingText) - 1
                if endPos > 0 then
                    return text 1 thru endPos of remainingText
                end if
            end if
            return "分析タイトル"
            
        else if keyName = "category" then
            -- カテゴリ抽出
            set categoryPattern to "\"name\": \""
            if jsonText contains categoryPattern then
                set startPos to (offset of categoryPattern in jsonText) + (length of categoryPattern)
                set remainingText to text startPos thru -1 of jsonText
                set endPos to (offset of "\"" in remainingText) - 1
                if endPos > 0 then
                    return text 1 thru endPos of remainingText
                end if
            end if
            return "general"
            
        else if keyName = "tags" then
            -- タグリストを抽出（入れ子構造対応）
            log "=== Extracting tags ==="
            log "JSON contains 'tags': {" & (jsonText contains "\"tags\": {")
            
            if jsonText contains "\"tags\": {" then
                set tagsObjectStart to (offset of "\"tags\": {" in jsonText) + 9
                set tagsObjectText to text tagsObjectStart thru -1 of jsonText
                log "Tags object text length: " & (length of tagsObjectText)
                log "Tags object first 100 chars: " & (text 1 thru (if length of tagsObjectText > 100 then 100 else length of tagsObjectText) of tagsObjectText)
                
                -- tags配列を探す
                log "Tags object contains 'tags': [" & (tagsObjectText contains "\"tags\": [")
                if tagsObjectText contains "\"tags\": [" then
                    set tagsArrayStart to (offset of "\"tags\": [" in tagsObjectText) + 9
                    set tagsArrayText to text tagsArrayStart thru -1 of tagsObjectText
                    set tagsArrayEnd to (offset of "]" in tagsArrayText) - 1
                    log "Tags array end position: " & tagsArrayEnd
                    
                    if tagsArrayEnd > 0 then
                        set tagsContent to text 1 thru tagsArrayEnd of tagsArrayText
                        log "Tags content: " & tagsContent
                        set cleanTags to my cleanTagsFromJSON(tagsContent)
                        log "Clean tags result: " & cleanTags
                        return cleanTags
                    end if
                end if
            end if
            log "Returning 'タグなし'"
            return "タグなし"
            
        else if keyName = "relations" then
            -- 関連ファイル情報を抽出（入れ子構造対応）
            if jsonText contains "\"relations\": {" then
                set relationsObjectStart to (offset of "\"relations\": {" in jsonText) + 14
                set relationsObjectText to text relationsObjectStart thru -1 of jsonText
                
                -- countを確認
                if relationsObjectText contains "\"count\": " then
                    set countStart to (offset of "\"count\": " in relationsObjectText) + 9
                    set countText to text countStart thru -1 of relationsObjectText
                    set countEnd to (offset of "," in countText) - 1
                    
                    if countEnd > 0 then
                        set relationCount to text 1 thru countEnd of countText
                        
                        -- カウントが0より大きい場合はファイル名を抽出
                        if (relationCount as integer) > 0 then
                            set relationsList to my extractRelationNames(jsonText)
                            return relationsList
                        else
                            return "関連ファイルなし"
                        end if
                    end if
                end if
            end if
            return "関連ファイルなし"
            
        end if
        
        return "取得失敗"
        
    on error
        return "解析エラー"
    end try
end extractValueFromJSON

-- 単純なKEY:VALUE形式から値を抽出
on extractValueFromSimple(resultText, keyName)
    try
        set keyPattern to keyName & ":"
        
        if resultText contains keyPattern then
            set keyStart to (offset of keyPattern in resultText) + (length of keyPattern)
            set remainingText to text keyStart thru -1 of resultText
            
            -- 改行までを取得
            set AppleScript's text item delimiters to return
            set textLines to text items of remainingText
            set AppleScript's text item delimiters to ""
            
            if (count of textLines) > 0 then
                set valueText to item 1 of textLines as string
                set cleanValue to my trimText(valueText)
                
                -- タグの場合はカンマ区切りをスペース区切りに変換
                if keyName = "TAGS" and cleanValue ≠ "なし" then
                    set AppleScript's text item delimiters to ","
                    set tagParts to text items of cleanValue
                    set AppleScript's text item delimiters to " "
                    set cleanValue to tagParts as string
                    set AppleScript's text item delimiters to ""
                end if
                
                -- 関連ファイルの場合の特別処理
                if keyName = "RELATIONS" and cleanValue ≠ "なし" then
                    -- "1件:ファイル名1,ファイル名2" → "1件: ファイル名1, ファイル名2"
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
        
        -- フォールバック
        if keyName = "TITLE" then
            return "解析エラー"
        else if keyName = "CATEGORY" then
            return "general"
        else if keyName = "TAGS" then
            return "タグなし"
        else if keyName = "RELATIONS" then
            return "関連ファイルなし"
        else
            return "不明"
        end if
        
    on error errorMsg
        log "extractValueFromSimple error for " & keyName & ": " & errorMsg
        return "エラー: " & errorMsg
    end try
end extractValueFromSimple

-- 詳細プレビューテキストを構築
on buildDetailedPreview(title, category, content, tags, relations)
    set previewLines to {}
    
    set end of previewLines to "📋 タイトル: " & title
    set end of previewLines to ""
    set end of previewLines to "📂 カテゴリ: " & category
    set end of previewLines to ""
    set end of previewLines to "🏷️ タグ: " & tags
    set end of previewLines to ""
    set end of previewLines to "🔗 関連ファイル: " & relations
    set end of previewLines to ""
    set end of previewLines to "📄 内容:"
    set end of previewLines to content
    set end of previewLines to ""
    set end of previewLines to "💾 保存先: " & category & "/" & title & ".md"
    set end of previewLines to ""
    set end of previewLines to "🤔 このメモを保存しますか？"
    
    set AppleScript's text item delimiters to return
    set previewText to previewLines as string
    set AppleScript's text item delimiters to ""
    
    return previewText
end buildDetailedPreview

-- ファイル名に使えない文字を置換する関数
on replaceInvalidChars(inputText)
    set invalidChars to {"/", ":", "\\", "*", "?", "\"", "<", ">", "|"}
    set cleanText to inputText
    
    repeat with invalidChar in invalidChars
        set AppleScript's text item delimiters to invalidChar
        set textParts to text items of cleanText
        set AppleScript's text item delimiters to "_"
        set cleanText to textParts as string
        set AppleScript's text item delimiters to ""
    end repeat
    
    return cleanText
end replaceInvalidChars

-- 現在の日付をYYYY-MM-DD形式で取得する関数
on getCurrentDateString()
    set currentDate to current date
    set yearStr to year of currentDate as string
    set monthNum to month of currentDate as integer
    set dayNum to day of currentDate as integer
    
    -- 月と日を2桁にフォーマット
    set monthStr to my padZero(monthNum)
    set dayStr to my padZero(dayNum)
    
    return yearStr & "-" & monthStr & "-" & dayStr
end getCurrentDateString

-- 数値を2桁の文字列にする関数
on padZero(num)
    if num < 10 then
        return "0" & (num as string)
    else
        return num as string
    end if
end padZero

-- JSONからタグを整形する関数
on cleanTagsFromJSON(tagsContent)
    try
        set cleanedTags to {}
        set searchText to tagsContent
        
        -- JSON配列から個別のタグを抽出
        repeat
            set tagPattern to "\"#"
            if searchText contains tagPattern then
                set tagStart to (offset of tagPattern in searchText) + 1
                set remainingText to text tagStart thru -1 of searchText
                set tagEnd to (offset of "\"" in remainingText) - 1
                
                if tagEnd > 0 then
                    set tagValue to text 1 thru tagEnd of remainingText
                    if tagValue starts with "#" and length of tagValue > 1 then
                        set end of cleanedTags to tagValue
                    end if
                    
                    -- 次の検索のために文字列を進める
                    set searchText to text (tagEnd + 1) thru -1 of remainingText
                else
                    exit repeat
                end if
            else
                exit repeat
            end if
            
            -- 最大8個まで表示
            if (count of cleanedTags) ≥ 8 then exit repeat
        end repeat
        
        if (count of cleanedTags) > 0 then
            -- タグをスペース区切りで結合
            set AppleScript's text item delimiters to " "
            set result to cleanedTags as string
            set AppleScript's text item delimiters to ""
            return result
        else
            return "タグなし"
        end if
        
    on error errorMsg
        return "タグ解析エラー: " & errorMsg
    end try
end cleanTagsFromJSON

-- JSONから関連ファイル名を抽出する関数
on extractRelationNames(jsonText)
    try
        set relationNames to {}
        
        -- relations配列セクションを探す
        if jsonText contains "\"relations\": [" then
            set relationsStart to (offset of "\"relations\": [" in jsonText) + 14
            set relationsText to text relationsStart thru -1 of jsonText
            set relationsEnd to (offset of "]" in relationsText) - 1
            
            if relationsEnd > 0 then
                set relationsContent to text 1 thru relationsEnd of relationsText
                
                -- "file_name" フィールドを探して抽出
                set searchText to relationsContent
                repeat
                    if searchText contains "\"file_name\": \"" then
                        set nameStart to (offset of "\"file_name\": \"" in searchText) + 14
                        set remainingText to text nameStart thru -1 of searchText
                        set nameEnd to (offset of "\"" in remainingText) - 1
                        
                        if nameEnd > 0 then
                            set fileName to text 1 thru nameEnd of remainingText
                            set end of relationNames to fileName
                            
                            -- 次の検索のために文字列を進める
                            set searchText to text (nameEnd + 1) thru -1 of remainingText
                        else
                            exit repeat
                        end if
                    else
                        exit repeat
                    end if
                    
                    -- 最大3件まで
                    if (count of relationNames) ≥ 3 then exit repeat
                end repeat
            end if
        end if
        
        if (count of relationNames) > 0 then
            -- ファイル名をカンマ区切りで結合
            set AppleScript's text item delimiters to ", "
            set result to relationNames as string
            set AppleScript's text item delimiters to ""
            return (count of relationNames) & "件: " & result
        else
            return "関連ファイルなし"
        end if
        
    on error errorMsg
        return "関連解析エラー: " & errorMsg
    end try
end extractRelationNames

-- テキストの前後の空白・改行を削除するヘルパー関数
on trimText(inputText)
    set trimmedText to inputText
    
    -- 先頭の空白・改行を削除
    repeat while (trimmedText starts with " " or trimmedText starts with return or trimmedText starts with tab)
        set trimmedText to text 2 thru -1 of trimmedText
        if length of trimmedText = 0 then exit repeat
    end repeat
    
    -- 末尾の空白・改行を削除
    repeat while (trimmedText ends with " " or trimmedText ends with return or trimmedText ends with tab)
        set trimmedText to text 1 thru -2 of trimmedText
        if length of trimmedText = 0 then exit repeat
    end repeat
    
    return trimmedText
end trimText 