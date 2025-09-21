"""
ASGI/WSGI 互換性エントリーポイント
Azure App Service での自動検出問題に対応
"""

from app import app

# FastAPIアプリケーション（ASGI）
application = app

# WSGI互換のためのラッパー（非推奨だが後方互換性のため）
def create_wsgi_app():
    """WSGI互換アプリケーションの作成（非推奨）"""
    from asgiref.wsgi import WsgiToAsgi
    import warnings
    
    warnings.warn(
        "WSGIモードでの実行は非推奨です。ASGIモード（uvicorn）での実行を推奨します。",
        DeprecationWarning,
        stacklevel=2
    )
    
    # ASGIアプリをWSGIラッパーでラップ
    return WsgiToAsgi(app)

# gunicorn等のWSGI サーバー用（自動検出対策）
wsgi_app = create_wsgi_app()

# ASGI サーバー用（推奨）
asgi_app = app

# デフォルトエクスポート
app = application