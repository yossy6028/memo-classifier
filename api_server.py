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