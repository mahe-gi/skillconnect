import os
from app import create_app
from app.config import DevelopmentConfig, ProductionConfig

# Use ProductionConfig when FLASK_ENV=production (e.g. on Render),
# otherwise fall back to DevelopmentConfig for local dev.
_env = os.getenv("FLASK_ENV", "development")
config = ProductionConfig if _env == "production" else DevelopmentConfig

app = create_app(config)
