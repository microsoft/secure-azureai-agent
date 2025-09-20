"""
統合アプリケーション - FastAPI + Chainlit
Azure App Service で単一のアプリとして動作するための統合アプリケーション
"""

import os
import sys
import asyncio
import signal
import subprocess
import logging
from pathlib import Path
from typing import Optional

from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import RedirectResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import StreamingResponse, Response
import httpx
import uvicorn

# ロギング設定
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# パス設定
CURRENT_DIR = Path(__file__).parent
BACKEND_DIR = CURRENT_DIR / "backend"
FRONTEND_DIR = CURRENT_DIR / "frontend"

# バックエンドのパスを追加
sys.path.insert(0, str(BACKEND_DIR / "src"))

# バックエンドアプリをインポート
try:
    from backend.src.main import app as backend_app
    logger.info("✅ Backend app imported successfully")
except ImportError as e:
    logger.error(f"❌ Failed to import backend app: {e}")
    raise

# 環境変数設定
PORT = int(os.getenv("PORT", 8000))
CHAINLIT_PORT = int(os.getenv("CHAINLIT_PORT", 8501))
ENVIRONMENT = os.getenv("ENVIRONMENT", "development")

class ChainlitManager:
    """Chainlit プロセスの管理"""
    
    def __init__(self):
        self.process: Optional[subprocess.Popen] = None
        self.is_running = False
    
    async def start_chainlit(self):
        """Chainlit を開始"""
        try:
            logger.info(f"🚀 Starting Chainlit on port {CHAINLIT_PORT}")
            
            # Chainlit の起動コマンド
            cmd = [
                sys.executable, "-m", "chainlit", "run",
                str(FRONTEND_DIR / "app.py"),
                "--port", str(CHAINLIT_PORT),
                "--host", "0.0.0.0",
                "--headless"  # ヘッドレスモードで実行
            ]
            
            # 環境変数を設定
            env = os.environ.copy()
            env["BACKEND_API_URL"] = f"http://localhost:{PORT}"
            
            self.process = subprocess.Popen(
                cmd,
                cwd=str(FRONTEND_DIR),
                env=env,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE
            )
            
            # 少し待ってからステータスを確認
            await asyncio.sleep(3)
            
            if self.process.poll() is None:
                self.is_running = True
                logger.info("✅ Chainlit started successfully")
            else:
                stdout, stderr = self.process.communicate()
                logger.error(f"❌ Chainlit failed to start:")
                logger.error(f"STDOUT: {stdout.decode()}")
                logger.error(f"STDERR: {stderr.decode()}")
                raise RuntimeError("Chainlit process failed to start")
                
        except Exception as e:
            logger.error(f"❌ Error starting Chainlit: {e}")
            raise
    
    def stop_chainlit(self):
        """Chainlit を停止"""
        if self.process and self.is_running:
            logger.info("🛑 Stopping Chainlit process")
            self.process.terminate()
            try:
                self.process.wait(timeout=10)
            except subprocess.TimeoutExpired:
                logger.warning("⚠️ Chainlit process didn't terminate, killing it")
                self.process.kill()
            
            self.is_running = False
            self.process = None

class ProxyMiddleware(BaseHTTPMiddleware):
    """Chainlit への プロキシミドルウェア"""
    
    def __init__(self, app, chainlit_manager: ChainlitManager):
        super().__init__(app)
        self.chainlit_manager = chainlit_manager
        self.chainlit_url = f"http://localhost:{CHAINLIT_PORT}"
    
    async def dispatch(self, request: Request, call_next):
        path = request.url.path
        
        # バックエンド API のパスはそのまま処理
        if (path.startswith("/api/") or 
            path.startswith("/health") or 
            path.startswith("/docs") or 
            path.startswith("/openapi.json")):
            return await call_next(request)
        
        # Chainlit が起動していない場合はエラーページを表示
        if not self.chainlit_manager.is_running:
            return HTMLResponse(
                content="""
                <html>
                    <head><title>Service Starting</title></head>
                    <body>
                        <h1>🚀 Service is Starting</h1>
                        <p>Please wait while the frontend service is loading...</p>
                        <script>
                            setTimeout(function() {
                                window.location.reload();
                            }, 5000);
                        </script>
                    </body>
                </html>
                """,
                status_code=503
            )
        
        # その他のリクエストは Chainlit にプロキシ
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                # リクエストURLを構築
                url = f"{self.chainlit_url}{path}"
                if request.url.query:
                    url += f"?{request.url.query}"
                
                # リクエストをプロキシ
                response = await client.request(
                    method=request.method,
                    url=url,
                    headers=dict(request.headers),
                    content=await request.body()
                )
                
                # WebSocketの場合は特別な処理が必要だが、今回は簡略化
                return Response(
                    content=response.content,
                    status_code=response.status_code,
                    headers=dict(response.headers),
                    media_type=response.headers.get("content-type")
                )
                
        except httpx.ConnectError:
            logger.warning("⚠️ Cannot connect to Chainlit, showing error page")
            return HTMLResponse(
                content="""
                <html>
                    <head><title>Frontend Unavailable</title></head>
                    <body>
                        <h1>⚠️ Frontend Service Unavailable</h1>
                        <p>The frontend service is temporarily unavailable. Please try again in a moment.</p>
                        <script>
                            setTimeout(function() {
                                window.location.reload();
                            }, 10000);
                        </script>
                    </body>
                </html>
                """,
                status_code=503
            )
        except Exception as e:
            logger.error(f"❌ Proxy error: {e}")
            raise HTTPException(status_code=502, detail="Proxy error")

# Chainlit マネージャーのインスタンス
chainlit_manager = ChainlitManager()

# メインアプリケーション
app = FastAPI(
    title="Azure Troubleshoot Agent - Unified App",
    description="FastAPI + Chainlit integrated application for Azure troubleshooting",
    version="1.0.0"
)

# バックエンドアプリをマウント
app.mount("/api", backend_app)

# プロキシミドルウェアを追加
app.add_middleware(ProxyMiddleware, chainlit_manager=chainlit_manager)

# ヘルスチェックエンドポイント
@app.get("/health")
async def health_check():
    """アプリケーションのヘルスチェック"""
    return {
        "status": "healthy",
        "backend": "running",
        "frontend": "running" if chainlit_manager.is_running else "starting",
        "port": PORT,
        "chainlit_port": CHAINLIT_PORT
    }

# ルートパスの処理
@app.get("/")
async def root():
    """ルートパスは Chainlit にリダイレクト"""
    return RedirectResponse(url="/", status_code=302)

# アプリケーションのライフサイクル管理
@app.on_event("startup")
async def startup_event():
    """アプリケーション起動時の処理"""
    logger.info("🚀 Starting unified application")
    try:
        await chainlit_manager.start_chainlit()
        logger.info("✅ Unified application started successfully")
    except Exception as e:
        logger.error(f"❌ Failed to start Chainlit: {e}")
        # Chainlit が起動しなくても、バックエンド API は使用可能

@app.on_event("shutdown")
async def shutdown_event():
    """アプリケーション終了時の処理"""
    logger.info("🛑 Shutting down unified application")
    chainlit_manager.stop_chainlit()

# シグナルハンドラー
def signal_handler(sig, frame):
    """シグナル受信時の処理"""
    logger.info(f"📨 Received signal {sig}")
    chainlit_manager.stop_chainlit()
    sys.exit(0)

signal.signal(signal.SIGINT, signal_handler)
signal.signal(signal.SIGTERM, signal_handler)

if __name__ == "__main__":
    logger.info(f"🚀 Starting unified app on port {PORT}")
    uvicorn.run(
        "app:app",
        host="0.0.0.0",
        port=PORT,
        workers=1,  # 単一ワーカーで実行（サブプロセス管理のため）
        access_log=True,
        log_level="info"
    )