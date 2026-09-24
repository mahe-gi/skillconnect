import os
from werkzeug.middleware.proxy_fix import ProxyFix

from app import create_app
from app.config import DevelopmentConfig, ProductionConfig

# Use ProductionConfig when FLASK_ENV=production (e.g. on Railway/Render/Fly),
# otherwise fall back to DevelopmentConfig for local dev.
_env = os.getenv("FLASK_ENV", "development")
config = ProductionConfig if _env == "production" else DevelopmentConfig

app = create_app(config)

# Railway (and most PaaS platforms) sit behind a reverse proxy that terminates
# TLS. Without ProxyFix, Flask sees http:// instead of https://, which breaks:
#   • CSRF token validation (origin mismatch)
#   • Session cookies (Secure flag not set)
#   • url_for(_external=True) generating http:// links
# x_for=1, x_proto=1, x_host=1 trusts one hop of proxy headers.
app.wsgi_app = ProxyFix(app.wsgi_app, x_for=1, x_proto=1, x_host=1)
