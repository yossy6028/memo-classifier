#!/usr/bin/env python3
"""
memo-classifier iOS Shortcuts API Server
iPhone Shortcuts.appから呼び出し可能なHTTP APIサーバー
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import uvicorn
import json
from datetime import datetime
from preview_enhanced_memo import IntegratedMemoProcessor
from pathlib import Path
import tempfile
from typing import List, Optional


# FastAPI アプリケーション初期化
app = FastAPI(
    title="memo-classifier API",
    description="iPhone Shortcuts対応のメモ分析・分類API",
    version="1.0.0"
)

# CORS設定（iPhone Shortcutsからのアクセスを許可）
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# リクエストモデル
class MemoRequest(BaseModel):
    content: str
    action: str = "preview"  # "preview" or "save"

class MemoResponse(BaseModel):
    success: bool
    title: str
    category: str
    tags: list
    relations_count: int
    message: str
    timestamp: str

class EditSuggestionRequest(BaseModel):
    content: str
    edited_title: str = None
    edited_category: str = None
    edited_tags: list = None

# グローバルなプロセッサーインスタンス
processor = IntegratedMemoProcessor()

@app.get("/")
async def root():
    """APIステータス確認"""
    return {
        "message": "memo-classifier API for iOS Shortcuts",
        "status": "running",
        "version": "1.0.0",
        "timestamp": datetime.now().isoformat()
    }

@app.get("/health")
async def health_check():
    """ヘルスチェック"""
    return {"status": "healthy", "timestamp": datetime.now().isoformat()}

@app.post("/analyze", response_model=MemoResponse)
async def analyze_memo(request: MemoRequest):
    """
    メモ分析API - iPhone Shortcutsのメインエンドポイント
    """
    try:
        if not request.content.strip():
            raise HTTPException(status_code=400, detail="メモ内容が空です")
        
        print(f"📱 iPhone Shortcutsからのリクエスト: {request.action}")
        print(f"📝 コンテンツ: {request.content[:100]}...")
        
        if request.action == "preview":
            # プレビュー分析
            result = processor.preview_analysis(request.content)
            
            if not result['success']:
                raise HTTPException(status_code=500, detail="分析エラーが発生しました")
            
            return MemoResponse(
                success=True,
                title=result['title']['title'],
                category=result['category']['name'],
                tags=result['tags']['tags'][:5],  # iPhone表示用に5個に制限
                relations_count=result['relations']['count'],
                message=f"分析完了！カテゴリ: {result['category']['name']}",
                timestamp=datetime.now().isoformat()
            )
            
        elif request.action == "save":
            # 実際の保存
            result = processor.save_memo(request.content)
            
            if not result['success']:
                raise HTTPException(status_code=500, detail=f"保存エラー: {result.get('error', '不明なエラー')}")
            
            return MemoResponse(
                success=True,
                title=result['title'],
                category=result['category'],
                tags=[],  # 保存時は簡略化
                relations_count=result['relations_count'],
                message=f"メモを保存しました！ファイル: {result['file_path'].split('/')[-1]}",
                timestamp=datetime.now().isoformat()
            )
        
        else:
            raise HTTPException(status_code=400, detail="無効なアクション。'preview' または 'save' を指定してください")
            
    except Exception as e:
        print(f"❌ API エラー: {e}")
        raise HTTPException(status_code=500, detail=f"内部エラー: {str(e)}")

@app.post("/quick-analyze")
async def quick_analyze(request: MemoRequest):
    """
    クイック分析API - iPhone Shortcuts用簡略版
    """
    try:
        if not request.content.strip():
            return {"error": "メモ内容が空です"}
        
        result = processor.preview_analysis(request.content)
        
        if not result['success']:
            return {"error": "分析に失敗しました"}
        
        # iPhone表示用に簡略化
        return {
            "title": result['title']['title'],
            "category": result['category']['name'],
            "tags": ", ".join(result['tags']['tags'][:3]),
            "relations": f"{result['relations']['count']}件",
            "confidence": f"{result['category']['confidence']:.0%}",
            "success": True
        }
        
    except Exception as e:
        return {"error": f"エラー: {str(e)}", "success": False}

@app.post("/edit-suggestion", response_model=MemoResponse)
async def edit_suggestion(request: EditSuggestionRequest):
    """
    サジェッション編集API - プレビュー結果を編集して再分析
    """
    try:
        if not request.content.strip():
            raise HTTPException(status_code=400, detail="メモ内容が空です")
        
        print(f"✏️ サジェッション編集リクエスト")
        print(f"📝 編集タイトル: {request.edited_title}")
        print(f"📂 編集カテゴリ: {request.edited_category}")
        print(f"🏷️ 編集タグ: {request.edited_tags}")
        
        # まず通常のプレビュー分析を実行
        result = processor.preview_analysis(request.content)
        
        if not result['success']:
            raise HTTPException(status_code=500, detail="分析エラーが発生しました")
        
        # 編集内容を反映
        if request.edited_title:
            result['title']['title'] = request.edited_title
        
        if request.edited_category:
            result['category']['name'] = request.edited_category
            result['category']['confidence'] = 1.0  # 手動設定なので100%
        
        if request.edited_tags is not None:
            result['tags']['tags'] = request.edited_tags
            result['tags']['count'] = len(request.edited_tags)
        
        # 編集された内容で保存用データを準備
        processor._last_edited_analysis = result
        
        # 編集内容を一時ファイルに保存（プロセス間共有のため）
        import json
        import tempfile
        temp_edit_file = Path(tempfile.gettempdir()) / "memo_classifier_edited_analysis.json"
        with open(temp_edit_file, 'w', encoding='utf-8') as f:
            json.dump(result, f, ensure_ascii=False, indent=2)
        print(f"💾 編集内容を一時保存: {temp_edit_file}")
        
        return MemoResponse(
            success=True,
            title=result['title']['title'],
            category=result['category']['name'],
            tags=result['tags']['tags'][:5],
            relations_count=result['relations']['count'],
            message=f"編集完了！カテゴリ: {result['category']['name']}",
            timestamp=datetime.now().isoformat()
        )
        
    except Exception as e:
        print(f"❌ サジェッション編集エラー: {e}")
        raise HTTPException(status_code=500, detail=f"編集エラー: {str(e)}")

if __name__ == "__main__":
    print("🚀 memo-classifier API Server for iOS Shortcuts")
    print("📱 iPhone Shortcuts.appから http://[MacのIPアドレス]:8080 でアクセス可能")
    print("💡 ヘルスチェック: http://localhost:8080/health")
    print("📖 API文書: http://localhost:8080/docs")
    
    # サーバー起動
    uvicorn.run(
        app, 
        host="0.0.0.0",  # すべてのネットワークインターフェースで待ち受け
        port=8080,
        reload=True,
        log_level="info"
    )