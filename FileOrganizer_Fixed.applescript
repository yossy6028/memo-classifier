-- File Organizer Fixed Script
-- ファイル整理の結果を適切な形式で返すスクリプト

on run
    try
        -- ファイル整理処理を呼び出し
        set organizationResult to my organizeFiles()
        
        -- 結果を表示
        display dialog "📁 ファイル整理結果" & return & return & organizationResult buttons {"OK"} default button "OK"
        
        return organizationResult
        
    on error errorMessage
        set errorResult to "❌ ファイル整理エラー" & return & return & errorMessage
        display dialog errorResult buttons {"OK"} default button "OK"
        return errorResult
    end try
end run

-- ファイル整理のメイン処理
on organizeFiles()
    try
        -- Python スクリプトを呼び出してファイル整理を実行
        set shellCommand to "cd '/Users/yoshiikatsuhiko/Library/Mobile Documents/iCloud~md~obsidian/Documents/memo-classifier' && /usr/bin/python3 file_organizer.py 2>&1"
        
        set organizationOutput to do shell script shellCommand
        
        -- 出力を解析して結果を返す
        return my parseOrganizationResult(organizationOutput)
        
    on error errorMessage
        -- エラーが発生した場合の処理
        set errorResult to "❌ 整理処理エラー:" & return & return & errorMessage & return & return
        
        -- 詳細情報を追加
        try
            set debugInfo to do shell script "ls -la '/Users/yoshiikatsuhiko/Library/Mobile Documents/iCloud~md~obsidian/Documents/memo-classifier/file_organizer.py'"
            set errorResult to errorResult & "ファイル情報: " & debugInfo
        on error
            set errorResult to errorResult & "ファイル確認失敗"
        end try
        
        return errorResult
    end try
end organizeFiles

-- 整理結果を解析する関数
on parseOrganizationResult(output)
    try
        -- 出力から成功・失敗の件数を抽出
        set successCount to 0
        set failureCount to 0
        
        -- APPLESCRIPT_RESULT行を優先的に解析
        if output contains "APPLESCRIPT_RESULT:" then
            set resultStart to (offset of "APPLESCRIPT_RESULT:" in output) + 18
            set resultLine to text resultStart thru -1 of output
            
            -- "成功: X件, 失敗: Y件" の形式を解析
            if resultLine contains "成功:" and resultLine contains "件" then
                set successStart to (offset of "成功:" in resultLine) + 3
                set successEnd to (offset of "件" in (text successStart thru -1 of resultLine)) - 1
                if successEnd > 0 then
                    try
                        set successCount to (text successStart thru (successStart + successEnd - 1) of resultLine) as integer
                    end try
                end if
            end if
            
            if resultLine contains "失敗:" and resultLine contains "件" then
                set failureStart to (offset of "失敗:" in resultLine) + 3
                set remainingText to text failureStart thru -1 of resultLine
                set failureEnd to (offset of "件" in remainingText) - 1
                if failureEnd > 0 then
                    try
                        set failureCount to (text 1 thru failureEnd of remainingText) as integer
                    end try
                end if
            end if
        else
            -- フォールバック: 従来の解析方法
            if output contains "成功:" then
                set successStart to (offset of "成功:" in output) + 3
                set remainingText to text successStart thru -1 of output
                set spacePos to (offset of " " in remainingText)
                if spacePos > 0 then
                    try
                        set successCount to (text 1 thru (spacePos - 1) of remainingText) as integer
                    end try
                end if
            end if
            
            if output contains "失敗:" then
                set failureStart to (offset of "失敗:" in output) + 3
                set remainingText to text failureStart thru -1 of output
                set spacePos to (offset of " " in remainingText)
                if spacePos > 0 then
                    try
                        set failureCount to (text 1 thru (spacePos - 1) of remainingText) as integer
                    end try
                end if
            end if
        end if
        
        -- 結果を整形して返す
        set resultMessage to "✅ ファイル整理完了" & return & return
        set resultMessage to resultMessage & "📊 処理結果:" & return
        set resultMessage to resultMessage & "• 成功: " & (successCount as string) & "件" & return
        set resultMessage to resultMessage & "• 失敗: " & (failureCount as string) & "件" & return & return
        
        if successCount > 0 then
            set resultMessage to resultMessage & "🎉 " & (successCount as string) & "個のファイルが正常に整理されました"
        else if failureCount > 0 then
            set resultMessage to resultMessage & "⚠️ すべてのファイルで問題が発生しました"
        else
            set resultMessage to resultMessage & "📝 整理対象のファイルはありませんでした"
        end if
        
        return resultMessage
        
    on error parseError
        -- 解析に失敗した場合はエラー情報も含めて返す
        return "📁 ファイル整理実行結果:" & return & return & output & return & return & "解析エラー: " & parseError
    end try
end parseOrganizationResult