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
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request, HTTPException, WebSocket
from fastapi.responses import RedirectResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import StreamingResponse, Response
from starlette.websockets import WebSocketDisconnect
import httpx
import websockets
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
        
        # WebSocket接続は特別に処理（ミドルウェアでは処理できないため、別途ルートで処理）
        if path.startswith("/ws") or path.startswith("/chat/ws") or "websocket" in request.headers.get("upgrade", "").lower():
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
                
                # レスポンスヘッダーを適切に処理
                headers = dict(response.headers)
                
                # Content-Length ヘッダーを削除して自動計算させる
                headers.pop("content-length", None)
                headers.pop("transfer-encoding", None)
                
                # WebSocketの場合は特別な処理が必要だが、今回は簡略化
                return Response(
                    content=response.content,
                    status_code=response.status_code,
                    headers=headers,
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

@asynccontextmanager
async def lifespan(app: FastAPI):
    """アプリケーションのライフサイクル管理"""
    # Startup
    logger.info("🚀 Starting unified application")
    try:
        await chainlit_manager.start_chainlit()
        logger.info("✅ Unified application started successfully")
    except Exception as e:
        logger.error(f"❌ Failed to start Chainlit: {e}")
        # Chainlit が起動しなくても、バックエンド API は使用可能
    
    yield
    
    # Shutdown
    logger.info("🛑 Shutting down unified application")
    chainlit_manager.stop_chainlit()

# メインアプリケーション
app = FastAPI(
    title="Azure Troubleshoot Agent - Unified App",
    description="FastAPI + Chainlit integrated application for Azure troubleshooting",
    version="1.0.0",
    lifespan=lifespan
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

# WebSocket プロキシエンドポイント
@app.websocket("/ws/{path:path}")
async def websocket_proxy(websocket: WebSocket, path: str):
    """WebSocket 接続を Chainlit にプロキシ"""
    if not chainlit_manager.is_running:
        await websocket.close(code=1001, reason="Service is starting")
        return
    
    await websocket.accept()
    
    # Chainlit WebSocket URL
    chainlit_ws_url = f"ws://localhost:{CHAINLIT_PORT}/ws/{path}"
    
    try:
        async with websockets.connect(chainlit_ws_url) as chainlit_ws:
            # 双方向でメッセージを転送
            async def forward_to_chainlit():
                try:
                    while True:
                        data = await websocket.receive_text()
                        await chainlit_ws.send(data)
                except WebSocketDisconnect:
                    await chainlit_ws.close()
            
            async def forward_from_chainlit():
                try:
                    async for message in chainlit_ws:
                        await websocket.send_text(message)
                except websockets.exceptions.ConnectionClosed:
                    await websocket.close()
            
            # 両方のタスクを並行して実行
            await asyncio.gather(
                forward_to_chainlit(),
                forward_from_chainlit(),
                return_exceptions=True
            )
            
    except Exception as e:
        logger.error(f"WebSocket proxy error: {e}")
        await websocket.close(code=1011, reason="Internal error")

# Chainlit の WebSocket エンドポイント用
@app.websocket("/chat/ws")
async def chat_websocket_proxy(websocket: WebSocket):
    """Chat WebSocket を Chainlit にプロキシ"""
    if not chainlit_manager.is_running:
        await websocket.close(code=1001, reason="Service is starting")
        return
    
    await websocket.accept()
    
    # Chainlit WebSocket URL
    chainlit_ws_url = f"ws://localhost:{CHAINLIT_PORT}/chat/ws"
    
    try:
        async with websockets.connect(chainlit_ws_url) as chainlit_ws:
            # 双方向でメッセージを転送
            async def forward_to_chainlit():
                try:
                    while True:
                        data = await websocket.receive_text()
                        await chainlit_ws.send(data)
                except WebSocketDisconnect:
                    await chainlit_ws.close()
            
            async def forward_from_chainlit():
                try:
                    async for message in chainlit_ws:
                        await websocket.send_text(message)
                except websockets.exceptions.ConnectionClosed:
                    await websocket.close()
            
            # 両方のタスクを並行して実行
            await asyncio.gather(
                forward_to_chainlit(),
                forward_from_chainlit(),
                return_exceptions=True
            )
            
    except Exception as e:
        logger.error(f"Chat WebSocket proxy error: {e}")
        await websocket.close(code=1011, reason="Internal error")

# シグナルハンドラー
def signal_handler(sig, frame):
    """シグナル受信時の処理"""
    logger.info(f"📨 Received signal {sig}")
    chainlit_manager.stop_chainlit()
    # 通常の終了プロセスに任せる（exit()の代わりにraiseを使用）
    raise KeyboardInterrupt()

signal.signal(signal.SIGINT, signal_handler)
signal.signal(signal.SIGTERM, signal_handler)

if __name__ == "__main__":
    logger.info(f"🚀 Starting unified app on port {PORT}")
    try:
        uvicorn.run(
            "app:app",
            host="0.0.0.0",
            port=PORT,
            workers=1,  # 単一ワーカーで実行（サブプロセス管理のため）
            access_log=True,
            log_level="info"
        )
    except KeyboardInterrupt:
        logger.info("👋 Received keyboard interrupt, shutting down gracefully")
    except Exception as e:
        logger.error(f"❌ Application error: {e}")
    finally:
        chainlit_manager.stop_chainlit()
        logger.info("✅ Application shutdown complete")